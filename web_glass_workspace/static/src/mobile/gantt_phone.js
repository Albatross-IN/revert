/** @odoo-module **/
// Glass Workspace — vertical gantt for phones.
//
// Odoo's gantt is a wide timeline (time on the horizontal axis, one line per row) that a phone
// can only scroll sideways. Below 768px the controller renders this component instead
// (gantt_phone.xml patches web_gantt.GanttController): time runs DOWN the left edge, every
// gantt row (assignee, work centre, project…) is a column and each record is a pill placed
// by its start / stop, so the whole plan reads with a vertical scroll. Nothing of the model
// is redone: the data, the range / scale / today controls (GanttRendererControls), the pill
// colours (o_gantt_color_N), the form dialog and "create from a slot" (model.getDialogContext)
// are Odoo's own. Desktop keeps Odoo's renderer untouched.
import { Component, onMounted, onPatched, proxy, signal, t, useListener, useProps } from "@odoo/owl";
import { browser } from "@web/core/browser/browser";
import { render } from "@web/owl2/utils";
import { _t } from "@web/core/l10n/translation";
import { useBus } from "@web/core/utils/hooks";
import { patch } from "@web/core/utils/patch";
import { useCallbackRecorder } from "@web/search/action_hook";
import { ActionHelper } from "@web/views/action_helper";
import { GanttController } from "@web_gantt/gantt_controller";
import { GanttRendererControls } from "@web_gantt/gantt_renderer_controls";
import { getColorIndex } from "@web_gantt/gantt_helpers";

const { DateTime } = luxon;

// height of one time slot per scale (hour / day / day / month)
const SLOT_HEIGHT = { day: 44, week: 56, month: 48, year: 72 };
const MIN_PILL = 24;

export class GlassGanttPhoneRenderer extends Component {
    static template = "web_glass_workspace.GanttPhoneRenderer";
    static components = { ActionHelper, GanttRendererControls };

    // the props Odoo's controller gives its renderer (gantt_controller.xml) + the phone's own two
    props = useProps({
        model: t.any(),
        arch: t.any().optional(),
        class: t.any().optional(),
        create: t.any().optional(),
        openDialog: t.any().optional(),
        noContentHelp: t.any().optional(),
        showNoContentHelp: t.any().optional(),
        scrollPosition: t.any().optional(),
        multiCreateValues: t.any().optional(),
        contentRef: t.any().optional(),
        context: t.any().optional(),
    });
    rootRef = signal.ref();
    gridRef = signal.ref();
    scrollerRef = signal.ref();

    setup() {
        this.model = this.props.model;
        this.state = proxy({ focusColumnId: null });
        // the gantt model is not reactive: it notifies on its bus (Odoo's renderer does the same)
        useBus(this.model.bus, "update", () => render(this));
        useCallbackRecorder(
            this.env.getCurrentFocusDateCallBackRecorder,
            this.getCurrentFocusDate.bind(this)
        );
        this._focusedRange = null;
        // the grid scrolls inside its own box (both ways) so the column heads and the time axis
        // can stay sticky; the box is sized to what is left of the screen under the controls
        onMounted(() => {
            this.sizeScroller();
            this.focusOnLoad();
        });
        onPatched(() => {
            this.sizeScroller();
            this.focusOnLoad();
        });
        useListener(window, "resize", () => this.sizeScroller());
    }

    sizeScroller() {
        const el = this.scrollerRef();
        if (!el) {
            return;
        }
        const top = el.getBoundingClientRect().top;
        const tabbar = document.querySelector(".o_glass_m_tabbar");
        const bottom = tabbar ? tabbar.getBoundingClientRect().top : browser.innerHeight;
        const h = Math.max(240, Math.floor(bottom - top - 8));
        if (el.style.height !== `${h}px`) {
            el.style.height = `${h}px`;
        }
    }

    // ------------------------------------------------------------------ data
    get metaData() {
        return this.model.metaData;
    }
    get scaleId() {
        return this.metaData.scale.id;
    }
    get interval() {
        return this.metaData.scale.interval; // hour | day | month
    }
    get slotHeight() {
        return SLOT_HEIGHT[this.scaleId] || 48;
    }
    /** time slots of the whole range (3 periods around the focus date, like the desktop) */
    get slots() {
        const { startDate, stopDate } = this.metaData;
        const unit = this.interval;
        const slots = [];
        let d = startDate.startOf(unit);
        const end = stopDate.endOf("day");
        const now = DateTime.local();
        let guard = 0;
        while (d <= end && guard++ < 2000) {
            const next = d.plus({ [unit]: 1 });
            slots.push({
                start: d,
                stop: next,
                label: this.slotLabel(d),
                sub: this.slotSub(d),
                isToday: now >= d && now < next,
                isPeriodStart: unit === "hour" ? d.hour === 0 : unit === "day" ? d.day === 1 : d.month === 1,
            });
            d = next;
        }
        return slots;
    }
    slotLabel(d) {
        switch (this.interval) {
            case "hour":
                return d.toFormat("HH:mm");
            case "month":
                return d.toFormat("MMM");
            default:
                return d.toFormat("d");
        }
    }
    slotSub(d) {
        switch (this.interval) {
            case "hour":
                return d.hour === 0 ? d.toFormat("ccc d MMM") : "";
            case "month":
                return d.month === 1 ? d.toFormat("yyyy") : "";
            default:
                return d.toFormat("ccc");
        }
    }
    /** the gantt rows as columns, sub-rows flattened ("Parent · Child") */
    get columns() {
        const all = this.allColumns;
        if (this.state.focusColumnId) {
            const one = all.find((c) => c.id === this.state.focusColumnId);
            if (one) {
                return [one];
            }
        }
        return all;
    }
    get allColumns() {
        const out = [];
        const walk = (rows, prefix) => {
            for (const row of rows || []) {
                const name = row.name ? (prefix ? `${prefix} · ${row.name}` : row.name) : prefix;
                if (row.rows && row.rows.length) {
                    walk(row.rows, name);
                } else {
                    out.push({ id: row.id, name: name || this.metaData.string || _t("All"), row });
                }
            }
        };
        walk(this.model.data.rows, "");
        if (!out.length) {
            out.push({ id: "__all__", name: this.metaData.string || _t("All"), row: null });
        }
        return out;
    }
    get recordsById() {
        const map = new Map();
        for (const record of this.model.data.records || []) {
            map.set(record.id, record);
        }
        return map;
    }
    /** pills of one column, laid out in lanes so overlapping records sit side by side */
    pillsOf(column, slots) {
        const { dateStartField, dateStopField, colorField } = this.metaData;
        const byId = this.recordsById;
        const ids = column.row ? column.row.recordIds : [...byId.keys()];
        const rangeStart = slots[0] ? slots[0].start : null;
        const rangeStop = slots.length ? slots[slots.length - 1].stop : null;
        if (!rangeStart) {
            return [];
        }
        const slotMs = slots[0].stop.diff(slots[0].start).as("milliseconds");
        const pills = [];
        for (const id of ids) {
            const record = byId.get(id);
            if (!record) {
                continue;
            }
            let start = record[dateStartField];
            let stop = record[dateStopField] || start;
            if (!start || stop < rangeStart || start > rangeStop) {
                continue;
            }
            if (this.model.dateStartFieldIsDate()) {
                // a date range is inclusive: the stop day counts
                stop = stop.plus({ days: 1 });
            }
            const s = start < rangeStart ? rangeStart : start;
            const e = stop > rangeStop ? rangeStop : stop;
            const top = (s.diff(rangeStart).as("milliseconds") / slotMs) * this.slotHeight;
            const height = Math.max(MIN_PILL, (e.diff(s).as("milliseconds") / slotMs) * this.slotHeight - 2);
            pills.push({
                id,
                record,
                start,
                stop,
                top: Math.round(top),
                height: Math.round(height),
                name: record.display_name || "",
                time: this.pillTime(record[dateStartField], record[dateStopField]),
                color: colorField ? getColorIndex(record[colorField]) : null,
            });
        }
        pills.sort((a, b) => a.top - b.top || b.height - a.height);
        // lanes: greedy — first lane whose last pill ended before this one starts
        const lanesEnd = [];
        for (const pill of pills) {
            let lane = lanesEnd.findIndex((end) => end <= pill.top);
            if (lane === -1) {
                lane = lanesEnd.length;
                lanesEnd.push(0);
            }
            lanesEnd[lane] = pill.top + pill.height + 2;
            pill.lane = lane;
        }
        const laneCount = Math.max(1, lanesEnd.length);
        for (const pill of pills) {
            pill.style = `top:${pill.top}px;height:${pill.height}px;left:calc(${(pill.lane / laneCount) * 100}% + 2px);width:calc(${100 / laneCount}% - 4px)`;
        }
        return pills;
    }
    pillTime(start, stop) {
        if (!start) {
            return "";
        }
        if (this.model.dateStartFieldIsDate()) {
            return stop && !stop.equals(start) ? `${start.toFormat("d MMM")} – ${stop.toFormat("d MMM")}` : start.toFormat("d MMM");
        }
        const sameDay = stop && start.hasSame(stop, "day");
        const fmt = this.interval === "hour" ? "HH:mm" : "d MMM HH:mm";
        return stop ? `${start.toFormat(fmt)} – ${stop.toFormat(sameDay ? "HH:mm" : fmt)}` : start.toFormat(fmt);
    }
    pillClass(pill) {
        return pill.color !== null && pill.color !== undefined ? `o_gantt_color_${pill.color}` : "";
    }
    /** columns get wider when their records overlap (up to 3 lanes side by side) */
    columnWidth(column, slots) {
        const lanes = Math.max(1, ...this.pillsOf(column, slots).map((p) => p.lane + 1));
        const base = this.columns.length === 1 ? 240 : 140;
        return Math.max(base, Math.min(lanes, 3) * 100);
    }
    gridStyle(columns, slots) {
        const cols = columns.map((c) => `minmax(${this.columnWidth(c, slots)}px, 1fr)`).join(" ");
        return `grid-template-columns: 62px ${cols}; --glass-gantt-slot: ${this.slotHeight}px;`;
    }

    // ---------------------------------------------------------- focus / scroll
    getCurrentFocusDate() {
        return this.metaData.focusDate;
    }
    focusOnLoad() {
        // once per range: bring the focus date (today) to the top of the screen
        const { startDate, stopDate, focusDate } = this.metaData;
        const key = `${startDate.toISODate()}|${stopDate.toISODate()}|${this.scaleId}`;
        if (this._focusedRange === key) {
            return;
        }
        this._focusedRange = key;
        this.scrollToDate(focusDate || DateTime.local());
    }
    focusToday() {
        return this.scrollToDate(DateTime.local());
    }
    scrollToDate(date) {
        const el = this.gridRef();
        if (!el || !date) {
            return false;
        }
        const { startDate, stopDate } = this.metaData;
        if (date < startDate.startOf("day") || date > stopDate.endOf("day")) {
            return false;
        }
        const idx = this.slots.findIndex((s) => date >= s.start && date < s.stop);
        const target = el.querySelector(`[data-slot="${idx}"]`);
        const scroller = this.scrollerRef();
        if (!target || !scroller) {
            return false;
        }
        // the slot sits right under the sticky column heads (44px)
        scroller.scrollTop = Math.max(0, target.offsetTop - 44);
        return true;
    }

    // a tap on a column head shows that column alone, full width; a second tap brings all back
    toggleColumnFocus(column) {
        this.state.focusColumnId = this.state.focusColumnId === column.id ? null : column.id;
    }

    // ------------------------------------------------------------ interaction
    onPillClick(pill) {
        if (this.model.useSampleModel) {
            return;
        }
        this.props.openDialog({ resId: pill.id });
    }
    onSlotClick(column, slot) {
        if (this.model.useSampleModel || !this.metaData.canCreate) {
            return;
        }
        const context = this.model.getDialogContext({
            rowId: column.row ? column.row.id : undefined,
            start: slot.start,
            stop: slot.stop,
            withDefault: true,
        });
        this.props.create(context);
    }
}

// the controller picks this renderer below 768px (see gantt_phone.xml)
patch(GanttController.prototype, {
    get glassGanttRenderer() {
        return GlassGanttPhoneRenderer;
    },
    // props only the phone renderer takes (Odoo's renderer must not receive unknown props).
    // showNoContentHelp is the controller's own decision (an app controller may override it):
    // Odoo's controller places its "no content" helper by measuring elements of its own renderer
    // (.o_gantt_header_groups / .o_gantt_header_columns) in a useEffect — those did not exist in
    // the phone renderer, so a gantt with no record in the period (sample data) crashed on phones
    // (BUG-0041). The phone renderer now carries hidden placeholders for that effect and shows
    // the help text itself (the controller's copy is hidden by CSS on phones).
    get glassRendererProps() {
        return this.uiService.isSmall
            ? { noContentHelp: this.props.info?.noContentHelp, showNoContentHelp: !!this.showNoContentHelp }
            : {};
    },
});
