/** @odoo-module **/

import { Component, onWillStart, onWillUnmount, useEffect, useRef, useState } from "@odoo/owl";
import { loadBundle } from "@web/core/assets";
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

const PALETTE = [
    "#0E6C7A", "#4B7BE5", "#C97A2B", "#5B8C5A", "#8B5CA8",
    "#B4544E", "#3F7F93", "#A9862F", "#6E7B8B", "#7C5CBF",
];

function emptyFilters() {
    return {
        status: "all",
        date_from: "",
        date_to: "",
        partner_ids: [],
        user_ids: [],
        task_ids: [],
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
        this.chart = new window.Chart(this.canvasRef.el, {
            type: this.props.type,
            data: this.props.chartData,
            options: Object.assign(
                {
                    responsive: true,
                    maintainAspectRatio: false,
                },
                this.props.options || {}
            ),
        });
    }
}

export class MomDashboard extends Component {
    static template = "revert_customizations.MomDashboard";
    static components = { MomChart };
    static props = ["*"];

    setup() {
        this.orm = useService("orm");
        this.action = useService("action");

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
        return this.state.data ? this.state.data.filter_options : { partners: [], users: [], tasks: [] };
    }

    get activeFilterCount() {
        const f = this.state.filters;
        let count = 0;
        if (f.status !== "all") count++;
        if (f.date_from || f.date_to) count++;
        count += f.partner_ids.length ? 1 : 0;
        count += f.user_ids.length ? 1 : 0;
        count += f.task_ids.length ? 1 : 0;
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

    get statusChartData() {
        const rows = this.state.data.by_status;
        return {
            labels: rows.map((row) => row.label),
            datasets: [
                {
                    data: rows.map((row) => row.value),
                    backgroundColor: rows.map((row) => STATUS_COLORS[row.key]),
                    borderWidth: 0,
                },
            ],
        };
    }

    get statusChartOptions() {
        return {
            cutout: "62%",
            plugins: { legend: { position: "right" } },
        };
    }

    get partnerChartData() {
        const rows = this.state.data.by_partner;
        return {
            labels: rows.map((row) => row.label),
            datasets: [
                {
                    label: "Entries",
                    data: rows.map((row) => row.value),
                    backgroundColor: rows.map((row, index) => PALETTE[index % PALETTE.length]),
                    borderWidth: 0,
                },
            ],
        };
    }

    get partnerChartOptions() {
        return {
            indexAxis: "y",
            plugins: { legend: { display: false } },
            scales: { x: { beginAtZero: true, ticks: { precision: 0 } } },
        };
    }

    get periodChartData() {
        const rows = this.state.data.by_period;
        return {
            labels: rows.map((row) => row.label),
            datasets: [
                {
                    label: "Open",
                    data: rows.map((row) => row.open),
                    backgroundColor: STATUS_COLORS.open,
                },
                {
                    label: "Closed",
                    data: rows.map((row) => row.done),
                    backgroundColor: STATUS_COLORS.done,
                },
            ],
        };
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
