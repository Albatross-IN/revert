/** @odoo-module **/

import { Component, onMounted, onWillStart, onWillUnmount, useEffect, useRef, useState } from "@odoo/owl";
import { loadBundle } from "@web/core/assets";
import { Dialog } from "@web/core/dialog/dialog";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

// Semantic, not decorative: blue is still to do, red is late, green is settled.
// No greys — a grey segment is unreadable against the dark theme's ground.
const STATUS_COLORS = {
    open: "#4B7BE5",
    overdue: "#E2504B",
    done: "#3FA37A",
};

// The preview is sized from the viewport rather than fixed, so it fills a
// useful share of a large screen while still fitting a laptop one.
const PREVIEW_MIN = 380;
const PREVIEW_MAX = 760;

function previewSize() {
    return Math.round(
        Math.max(
            PREVIEW_MIN,
            Math.min(PREVIEW_MAX, window.innerWidth * 0.42, window.innerHeight * 0.82)
        )
    );
}

// Chart colours follow the filter they set: whatever is filtered in stays
// solid and everything else fades to this, so the chart reads back the
// selection the user just made on it.
const FADED_ALPHA = 0.22;

function withAlpha(hex, alpha) {
    const value = parseInt(hex.slice(1), 16);
    const red = (value >> 16) & 255;
    const green = (value >> 8) & 255;
    const blue = value & 255;
    return `rgba(${red}, ${green}, ${blue}, ${alpha})`;
}

function paint(hex, isActive) {
    return isActive ? hex : withAlpha(hex, FADED_ALPHA);
}

// First and last day of a "YYYY-MM" bucket, as the date inputs hold them.
function monthRange(key) {
    const [year, month] = key.split("-").map(Number);
    const lastDay = new Date(Date.UTC(year, month, 0)).getUTCDate();
    const prefix = `${year}-${String(month).padStart(2, "0")}`;
    return { from: `${prefix}-01`, to: `${prefix}-${String(lastDay).padStart(2, "0")}` };
}

const KPI_TILES = [
    { key: "total", label: "Entries", hint: "Show every status" },
    { key: "open", label: "Open", hint: "Only open entries" },
    { key: "overdue", label: "Overdue", hint: "Only overdue entries" },
    { key: "done", label: "Closed", hint: "Only closed entries" },
    { key: "contacts", label: "Contacts", hint: "Filter by Related To" },
    { key: "photos", label: "With photo", hint: "Only entries with a site photo" },
];

function emptyFilters() {
    return {
        status: "all",
        date_from: "",
        date_to: "",
        partner_ids: [],
        user_ids: [],
        task_ids: [],
        visit_nos: [],
        with_photo: false,
        offset: 0,
    };
}

/**
 * One canvas, one Chart instance. The instance is destroyed on every data
 * change and on unmount, otherwise Chart.js keeps the old canvas alive and
 * tooltips from the previous render bleed into the new one.
 */
export class MomChart extends Component {
    static template = "revert_customizations.MomChart";
    static props = {
        type: String,
        chartData: Object,
        options: { type: Object, optional: true },
        height: { type: Number, optional: true },
        // Called with the clicked element's { index, datasetIndex }. Its
        // presence is what makes the chart clickable.
        onSelect: { type: Function, optional: true },
    };

    setup() {
        this.canvasRef = useRef("canvas");
        useEffect(
            () => {
                this.renderChart();
            },
            () => [this.props.chartData]
        );
        onWillUnmount(() => this.destroyChart());
    }

    destroyChart() {
        if (this.chart) {
            this.chart.destroy();
            this.chart = null;
        }
    }

    /**
     * Chart.js defaults to a fixed dark grey for labels, gridlines and
     * legends, which disappears against Odoo's dark theme. Read the theme's
     * own colours off the dashboard element and hand them to Chart.js so the
     * chrome follows the bundle Odoo compiled.
     */
    applyThemeDefaults() {
        const styles = getComputedStyle(this.canvasRef.el);
        const ink = styles.getPropertyValue("--mom-ink").trim();
        const rule = styles.getPropertyValue("--mom-rule").trim();
        if (ink) {
            window.Chart.defaults.color = ink;
        }
        if (rule) {
            window.Chart.defaults.borderColor = rule;
        }
        window.Chart.defaults.font.family = styles.fontFamily;
    }

    renderChart() {
        this.destroyChart();
        if (!this.canvasRef.el) {
            return;
        }
        this.applyThemeDefaults();
        const options = Object.assign(
            {
                responsive: true,
                maintainAspectRatio: false,
            },
            this.props.options || {}
        );
        if (this.props.onSelect) {
            options.onClick = (event, elements) => {
                if (elements.length) {
                    const { index, datasetIndex } = elements[0];
                    this.props.onSelect({ index, datasetIndex });
                }
            };
            options.onHover = (event, elements) => {
                event.native.target.style.cursor = elements.length ? "pointer" : "default";
            };
        }
        this.chart = new window.Chart(this.canvasRef.el, {
            type: this.props.type,
            data: this.props.chartData,
            options,
        });
    }
}

/**
 * Closing note for an entry being marked done. The note is not decoration:
 * action_feedback posts it to the task's chatter, so it is the record of why
 * the point was closed.
 */
export class MomDoneDialog extends Component {
    static template = "revert_customizations.MomDoneDialog";
    static components = { Dialog };
    static props = {
        entry: Object,
        onConfirm: Function,
        close: Function,
    };

    setup() {
        this.state = useState({ feedback: "", busy: false });
        this.textareaRef = useRef("feedback");
        onMounted(() => this.textareaRef.el && this.textareaRef.el.focus());
    }

    async confirm() {
        // The dialog stays open until the server has actually closed the
        // entry, so a failure surfaces here rather than looking like success.
        if (this.state.busy) {
            return;
        }
        this.state.busy = true;
        try {
            await this.props.onConfirm(this.state.feedback.trim());
            this.props.close();
        } finally {
            this.state.busy = false;
        }
    }
}

export class MomDashboard extends Component {
    static template = "revert_customizations.MomDashboard";
    static components = { MomChart };
    static props = ["*"];

    setup() {
        this.orm = useService("orm");
        this.action = useService("action");
        this.dialog = useService("dialog");

        const params = this.props.action.params || {};
        const context = this.props.action.context || {};
        this.projectId = params.project_id || context.active_id;

        this.state = useState({
            loading: true,
            error: null,
            data: null,
            filters: emptyFilters(),
            openPanel: null,
            preview: null,
        });

        onWillStart(async () => {
            // Chart.js ships as a lazy bundle in Odoo 18 — without this the
            // dashboard renders and then dies on the first chart.
            await loadBundle("web.chartjs_lib");
            await this.load();
        });
    }

    // ------------------------------------------------------------------
    // Navigation
    // ------------------------------------------------------------------

    /**
     * Always lands on the Projects kanban, whichever route reached the
     * dashboard — the card menu, the card button, or the project form's stat
     * button. clearBreadcrumbs resets the stack so Projects becomes the root
     * rather than piling another entry onto the breadcrumb trail.
     */
    goBack() {
        this.action.doAction("project.open_view_project_all", {
            clearBreadcrumbs: true,
        });
    }

    /**
     * Prints every entry matching the current filters, not just the page on
     * screen: the server rebuilds the rows from the same filter state.
     */
    async printEntries() {
        const action = await this.orm.call(
            "project.project",
            "action_print_mom_entries",
            [[this.projectId], Object.assign({}, this.state.filters)]
        );
        await this.action.doAction(action);
    }

    onBackKeydown(ev) {
        if (ev.key === "Enter" || ev.key === " ") {
            ev.preventDefault();
            this.goBack();
        }
    }

    // ------------------------------------------------------------------
    // Data
    // ------------------------------------------------------------------

    async load() {
        this.state.loading = true;
        this.state.error = null;
        try {
            this.state.data = await this.orm.call(
                "project.project",
                "get_mom_dashboard_data",
                [[this.projectId], Object.assign({}, this.state.filters)]
            );
        } catch (error) {
            this.state.error = error.message || error.toString();
            throw error;
        } finally {
            this.state.loading = false;
        }
    }

    async reload({ keepOffset = false } = {}) {
        if (!keepOffset) {
            this.state.filters.offset = 0;
        }
        await this.load();
    }

    // ------------------------------------------------------------------
    // Filters
    // ------------------------------------------------------------------

    get filterOptions() {
        return this.state.data
            ? this.state.data.filter_options
            : { partners: [], users: [], tasks: [], visits: [] };
    }

    get activeFilterCount() {
        const f = this.state.filters;
        let count = 0;
        if (f.status !== "all") count++;
        if (f.date_from || f.date_to) count++;
        count += f.partner_ids.length ? 1 : 0;
        count += f.user_ids.length ? 1 : 0;
        count += f.task_ids.length ? 1 : 0;
        count += f.visit_nos.length ? 1 : 0;
        if (f.with_photo) count++;
        return count;
    }

    togglePanel(name) {
        this.state.openPanel = this.state.openPanel === name ? null : name;
    }

    async setStatus(status) {
        this.state.filters.status = status;
        await this.reload();
    }

    /** A second click on the status that is already filtering clears it. */
    async toggleStatus(status) {
        await this.setStatus(this.state.filters.status === status ? "all" : status);
    }

    // ------------------------------------------------------------------
    // KPI tiles
    // ------------------------------------------------------------------

    get kpiTiles() {
        return KPI_TILES;
    }

    /**
     * A tile is "pressed" while the filter it stands for is on. Entries
     * never presses: it is the way back to every status, not a filter.
     */
    kpiActive(key) {
        const f = this.state.filters;
        switch (key) {
            case "open":
            case "overdue":
            case "done":
                return f.status === key;
            case "contacts":
                return f.partner_ids.length > 0;
            case "photos":
                return f.with_photo;
            default:
                return false;
        }
    }

    async onKpiClick(key) {
        switch (key) {
            case "total":
                return this.setStatus("all");
            case "open":
            case "overdue":
            case "done":
                return this.toggleStatus(key);
            case "contacts":
                // No single contact to filter on, so open the picker instead.
                return this.togglePanel("partner_ids");
            case "photos":
                return this.toggleWithPhoto();
        }
    }

    async setDate(which, ev) {
        this.state.filters[which] = ev.target.value || "";
        await this.reload();
    }

    isSelected(field, id) {
        return this.state.filters[field].includes(id);
    }

    async toggleSelection(field, id) {
        const selected = this.state.filters[field];
        const index = selected.indexOf(id);
        if (index === -1) {
            selected.push(id);
        } else {
            selected.splice(index, 1);
        }
        await this.reload();
    }

    async clearSelection(field) {
        this.state.filters[field] = [];
        await this.reload();
    }

    async toggleWithPhoto() {
        this.state.filters.with_photo = !this.state.filters.with_photo;
        await this.reload();
    }

    async resetFilters() {
        this.state.filters = emptyFilters();
        this.state.openPanel = null;
        await this.load();
    }

    selectionLabel(field, options, fallback) {
        const selected = this.state.filters[field];
        if (!selected.length) {
            return fallback;
        }
        if (selected.length === 1) {
            const match = options.find((option) => option.id === selected[0]);
            return match ? match.name : fallback;
        }
        return `${fallback} (${selected.length})`;
    }

    // ------------------------------------------------------------------
    // Charts
    // ------------------------------------------------------------------

    /**
     * Whether a doughnut segment is inside the current status filter. The
     * segments are due-later / overdue / closed, while the Open filter spans
     * the first two, so this is not a plain equality.
     */
    statusSegmentActive(key) {
        const status = this.state.filters.status;
        if (status === "all") {
            return true;
        }
        if (status === "open") {
            return key !== "done";
        }
        if (status === "due_later") {
            return key === "open";
        }
        return key === status;
    }

    get statusChartData() {
        const rows = this.state.data.by_status;
        return {
            labels: rows.map((row) => row.label),
            datasets: [
                {
                    data: rows.map((row) => row.value),
                    backgroundColor: rows.map((row) =>
                        paint(STATUS_COLORS[row.key], this.statusSegmentActive(row.key))
                    ),
                    borderWidth: 0,
                },
            ],
        };
    }

    async onStatusSelect({ index }) {
        const key = this.state.data.by_status[index].key;
        // The "Due later" segment is keyed open for its colour, but as a
        // filter it means open-and-not-overdue.
        await this.toggleStatus(key === "open" ? "due_later" : key);
    }

    get statusChartOptions() {
        return {
            cutout: "62%",
            plugins: { legend: { position: "right" } },
        };
    }

    get partnerChartData() {
        const rows = this.state.data.by_partner;
        const selected = this.state.filters.partner_ids;
        return {
            labels: rows.map((row) => row.label),
            datasets: [
                {
                    label: "Entries",
                    data: rows.map((row) => row.value),
                    // Colours come from the server so the PDF can highlight
                    // Related To with the same one the bar is drawn in.
                    backgroundColor: rows.map((row) =>
                        paint(row.color, !selected.length || selected.includes(row.id))
                    ),
                    borderWidth: 0,
                },
            ],
        };
    }

    async onPartnerSelect({ index }) {
        await this.toggleSelection("partner_ids", this.state.data.by_partner[index].id);
    }

    get partnerChartOptions() {
        return {
            indexAxis: "y",
            plugins: { legend: { display: false } },
            scales: { x: { beginAtZero: true, ticks: { precision: 0 } } },
        };
    }

    /** The month bucket the date range currently sits on exactly, if any. */
    get selectedPeriodKey() {
        const { date_from, date_to } = this.state.filters;
        if (!date_from || !date_to) {
            return null;
        }
        const match = this.state.data.by_period.find((row) => {
            const range = monthRange(row.key);
            return range.from === date_from && range.to === date_to;
        });
        return match ? match.key : null;
    }

    get periodChartData() {
        const rows = this.state.data.by_period;
        const status = this.state.filters.status;
        const selectedKey = this.selectedPeriodKey;
        const monthActive = (row) => !selectedKey || row.key === selectedKey;
        // A bar segment is lit when both its month and its status are in.
        const openIn = status !== "done";
        const doneIn = status === "all" || status === "done";
        return {
            labels: rows.map((row) => row.label),
            datasets: [
                {
                    label: "Open",
                    data: rows.map((row) => row.open),
                    backgroundColor: rows.map((row) =>
                        paint(STATUS_COLORS.open, openIn && monthActive(row))
                    ),
                },
                {
                    label: "Closed",
                    data: rows.map((row) => row.done),
                    backgroundColor: rows.map((row) =>
                        paint(STATUS_COLORS.done, doneIn && monthActive(row))
                    ),
                },
            ],
        };
    }

    /**
     * A segment is one month of one status, so clicking it sets both the
     * date range and the status. Clicking the segment that is already the
     * filter clears both again.
     */
    async onPeriodSelect({ index, datasetIndex }) {
        const row = this.state.data.by_period[index];
        const range = monthRange(row.key);
        const status = datasetIndex === 0 ? "open" : "done";
        const f = this.state.filters;
        const alreadySet =
            f.date_from === range.from && f.date_to === range.to && f.status === status;
        if (alreadySet) {
            f.date_from = "";
            f.date_to = "";
            f.status = "all";
        } else {
            f.date_from = range.from;
            f.date_to = range.to;
            f.status = status;
        }
        await this.reload();
    }

    get periodChartOptions() {
        return {
            plugins: { legend: { position: "bottom" } },
            scales: {
                x: { stacked: true, grid: { display: false } },
                y: { stacked: true, beginAtZero: true, ticks: { precision: 0 } },
            },
        };
    }

    // ------------------------------------------------------------------
    // Table
    // ------------------------------------------------------------------

    photoUrl(entryId, size = "48x48") {
        return `/web/image/mail.activity/${entryId}/mom_site_photo/${size}`;
    }

    /**
     * The enlarged photo is rendered once at the root of the dashboard and
     * positioned against the viewport, not nested beside the thumbnail: the
     * entries table scrolls horizontally, and an inline preview would be
     * clipped at the edge of that container.
     */
    showPreview(entry, ev) {
        if (!entry.has_photo) {
            return;
        }
        const size = previewSize();
        const rect = ev.currentTarget.getBoundingClientRect();
        const margin = 12;
        // Prefer the left of the thumbnail — the photo column sits near the
        // right edge — and fall back to the right when there is no room.
        let left = rect.left - size - margin;
        if (left < margin) {
            left = Math.min(rect.right + margin, window.innerWidth - size - margin);
        }
        const top = Math.max(
            margin,
            Math.min(
                rect.top + rect.height / 2 - size / 2,
                window.innerHeight - size - margin
            )
        );
        this.state.preview = {
            url: this.photoUrl(entry.id, "1024x1024"),
            summary: entry.summary,
            top,
            left,
            size,
        };
    }

    hidePreview() {
        this.state.preview = null;
    }

    get pageStart() {
        return this.state.data.entries.length ? this.state.data.offset + 1 : 0;
    }

    get pageEnd() {
        return this.state.data.offset + this.state.data.entries.length;
    }

    get hasPrevious() {
        return this.state.data.offset > 0;
    }

    get hasNext() {
        return this.pageEnd < this.state.data.entries_total;
    }

    async goToPage(direction) {
        const next = this.state.filters.offset + direction * this.state.data.page_size;
        this.state.filters.offset = Math.max(next, 0);
        await this.reload({ keepOffset: true });
    }

    /**
     * Reloads the current page after an entry changed, and steps back a page
     * when closing the last entry on it would otherwise leave the table empty.
     */
    async reloadAfterChange() {
        await this.reload({ keepOffset: true });
        if (!this.state.data.entries.length && this.state.filters.offset > 0) {
            this.state.filters.offset = Math.max(
                this.state.filters.offset - this.state.data.page_size,
                0
            );
            await this.load();
        }
    }

    /**
     * Opens Odoo's own activity dialog for the entry. stopPropagation keeps
     * the click off the row, which navigates to the task.
     */
    async editEntry(entry, ev) {
        ev.stopPropagation();
        const action = await this.orm.call("mail.activity", "action_mom_open_form", [
            [entry.id],
        ]);
        await this.action.doAction(action, {
            onClose: () => this.reloadAfterChange(),
        });
    }

    markDone(entry, ev) {
        ev.stopPropagation();
        this.dialog.add(MomDoneDialog, {
            entry,
            onConfirm: async (feedback) => {
                await this.orm.call("mail.activity", "action_mom_mark_done", [
                    [entry.id],
                    feedback,
                ]);
                await this.reloadAfterChange();
            },
        });
    }

    openTask(taskId) {
        if (!taskId) {
            return;
        }
        this.action.doAction({
            type: "ir.actions.act_window",
            res_model: "project.task",
            res_id: taskId,
            views: [[false, "form"]],
            target: "current",
        });
    }
}

registry.category("actions").add("mom_dashboard", MomDashboard);
