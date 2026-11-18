/** @odoo-module **/
// Split Form View — the panel beside a list / kanban. It embeds Odoo's own form view
// (the same `View` component FormViewDialog uses) with a fresh env config, so the form
// behaves exactly as when opened on its own: header buttons, statusbar, sheet, chatter,
// save / discard indicator and cog menu all work; only breadcrumbs are dropped.
import { Component, onWillUnmount, onWillUpdateProps, proxy, signal, t, useEffect, useOnChange, useProps } from "@odoo/owl";
import { useSubEnv } from "@web/owl2/utils";
import { useService } from "@web/core/utils/hooks";
import { CallbackRecorder } from "@web/search/action_hook";
import { View, getDefaultConfig } from "@web/views/view";
import {
    chatterStore,
    chatterCaps,
    ensureChatterCapability,
    showChatter,
    hideChatter,
} from "../chatter/chatter_store";

// Pane width buckets (right split). Module kanban cards are laid out for a window-wide renderer;
// below these widths split_panel.scss adapts them (BUG-0047):
//   mid    < 1500px — no capped card heights, lg/xl grid columns wrap (the row cards still
//                     collide at 1300px: Time Off ribbon over its buttons, Work Orders two per line)
//   narrow <  768px — Odoo's md breakpoint: what the modules themselves do on a phone
const PANE_MID = 1500;
const PANE_NARROW = 768;

export class GlassSplitPanel extends Component {
    static template = "web_glass_workspace.SplitPanel";
    static components = { View };

    props = useProps({
        resModel: t.string(),
        resId: t.number(),
        formViewId: t.or([t.number(), t.boolean()]).optional(),
        getResIds: t.function().optional(),
        context: t.object().optional(),
        side: t.string().optional(), // "right" | "bottom"
        collapsed: t.boolean().optional(),
        onClose: t.function(),
        onSelect: t.function(), // (resId) => void — prev / next
        onSaved: t.function().optional(),
        onToggleCollapse: t.function(),
        onResize: t.function(), // (pct) => void
    });
    panelRef = signal.ref();

    setup() {
        this.actionService = useService("action");
        this.orm = useService("orm");
        this.prefs = useService("glass_prefs");
        this.state = proxy({ displayName: "", paneBucket: "wide" });
        // The list pane's width = the content box of `.o_content` (its padding is the strip
        // reserved for this panel; the divider drag changes it). Only the bucket is stored, so a
        // drag re-renders this component only when a threshold is crossed.
        useEffect(() => {
            const el = this.panelRef();
            const content = el && el.closest(".o_content");
            if (!content || typeof ResizeObserver === "undefined") {
                return;
            }
            const measure = () => {
                const cs = getComputedStyle(content);
                const w = content.clientWidth - parseFloat(cs.paddingLeft) - parseFloat(cs.paddingRight);
                const bucket = w < PANE_NARROW ? "narrow" : w < PANE_MID ? "mid" : "wide";
                if (bucket !== this.state.paneBucket) {
                    this.state.paneBucket = bucket;
                }
            };
            const observer = new ResizeObserver(measure);
            observer.observe(content);
            return () => observer.disconnect();
        });
        // floating chatter: the window follows the record shown here (see chatter_window.js)
        this.chatter = chatterStore;
        this.chatterCaps = chatterCaps;
        useOnChange(
            () => [this.props.resModel, this.props.resId],
            (resModel, resId) => {
                this.refreshTitle(resModel, resId);
                this.onRecordShown(resModel, resId);
            }
        );
        onWillUnmount(() => {
            // split closed / full form opened / navigated away: the window goes with it
            chatterStore.split = null;
            chatterStore.dockedByUser = false;
            if (chatterStore.source === "split") {
                hideChatter();
            }
        });
        // Fresh, isolated env.config so the embedded form's `Object.assign(env.config, …)`
        // (in View.setup) cannot mutate the list action's config and re-render it.
        // The embedded form renders its own Layout, which our patch also sees. Clear
        // glassSplit for this subtree so that Layout does not inject another panel
        // (which would embed another form → another Layout → infinite recursion).
        useSubEnv({
            glassSplit: false,
            config: {
                ...getDefaultConfig(),
                // Odoo 20 loads `display_name` only for a form WITH a control panel (the panel
                // has none), so the form reports an empty name: the title is read by the panel
                // itself (refreshTitle) and a form's empty report never blanks it
                setDisplayName: (name) => {
                    if (name && name !== this.state.displayName) {
                        this.state.displayName = name;
                    }
                },
            },
        });
        this.buildViewProps(this.props);
        onWillUpdateProps((next) => {
            if (next.resId !== this.props.resId || next.resModel !== this.props.resModel) {
                this.buildViewProps(next);
            }
        });
    }

    buildViewProps(props) {
        this.viewProps = {
            type: "form",
            viewId: props.formViewId || false,
            resModel: props.resModel,
            resId: props.resId,
            resIds: [props.resId],
            context: props.context || {},
            display: { controlPanel: false },
            __beforeLeave__: new CallbackRecorder(),
            saveRecord: async (record, params) => {
                const saved = await record.save();
                if (saved) {
                    this.refreshTitle(record.resModel, record.resId);
                    if (this.props.onSaved) {
                        await this.props.onSaved(record);
                    }
                }
                return saved;
            },
        };
    }

    /** The panel's title: the record's display name (see setDisplayName). */
    async refreshTitle(resModel, resId) {
        try {
            const [rec] = await this.orm.read(resModel, [resId], ["display_name"]);
            if (rec && this.props.resModel === resModel && this.props.resId === resId) {
                this.state.displayName = (rec.display_name || "").split("\n")[0];
            }
        } catch {
            // no read access / deleted record: the panel keeps its last title
        }
    }

    // --- floating chatter ----------------------------------------------------------------
    /** A record is shown in the panel: float its chatter (preference), or follow it. */
    async onRecordShown(resModel, resId) {
        const s = chatterStore;
        s.split = { resModel, resId };
        // shared, cached request: the global ORM (see chatter_button.js)
        const cap = await ensureChatterCapability(this.env.services.orm, resModel);
        if (!s.split || s.split.resModel !== resModel || s.split.resId !== resId) {
            return; // the panel moved on while we were asking
        }
        if (!cap.thread) {
            if (s.source === "split") {
                hideChatter();
            }
            return;
        }
        if (s.open && s.source === "split") {
            if (s.follow) {
                showChatter(resModel, resId, { source: "split", hasActivities: cap.activities });
            }
            return;
        }
        if (!s.dockedByUser && this.prefs.prefs.split_chatter !== "docked") {
            showChatter(resModel, resId, { source: "split", hasActivities: cap.activities });
        }
    }
    get chatterAvailable() {
        const cap = this.chatterCaps[this.props.resModel];
        return !!(cap && cap.thread);
    }
    /** true while the window shows THIS record (then the docked chatter in the form is hidden) */
    get chatterFloating() {
        const s = this.chatter;
        return (
            s.open &&
            s.source === "split" &&
            s.resModel === this.props.resModel &&
            s.resId === this.props.resId
        );
    }
    toggleChatterFloat() {
        const s = chatterStore;
        if (this.chatterFloating) {
            s.dockedByUser = true;
            hideChatter();
            return;
        }
        s.dockedByUser = false;
        s.follow = true;
        const cap = this.chatterCaps[this.props.resModel];
        showChatter(this.props.resModel, this.props.resId, {
            source: "split",
            hasActivities: !!(cap && cap.activities),
        });
    }

    // the list pane is narrower than 1500px / 768px (right split only — a bottom split keeps the
    // list at full width); split_panel.scss reads these classes through :has()
    get paneMid() {
        return (this.props.side || "right") !== "bottom" && this.state.paneBucket !== "wide";
    }
    get paneNarrow() {
        return (this.props.side || "right") !== "bottom" && this.state.paneBucket === "narrow";
    }

    /** Save (or refuse to leave) a dirty record before switching / closing. */
    async beforeLeave() {
        const callbacks = this.viewProps.__beforeLeave__.callbacks;
        const res = await Promise.all(callbacks.map((cb) => cb()));
        return !res.includes(false);
    }

    get resIds() {
        return this.props.getResIds ? this.props.getResIds() : [];
    }
    get index() {
        return this.resIds.indexOf(this.props.resId);
    }
    get total() {
        return this.resIds.length;
    }

    async step(delta) {
        const ids = this.resIds;
        if (ids.length < 2) {
            return;
        }
        if (!(await this.beforeLeave())) {
            return;
        }
        const i = (this.index + delta + ids.length) % ids.length;
        this.props.onSelect(ids[i]);
    }

    async close() {
        if (await this.beforeLeave()) {
            this.props.onClose();
        }
    }

    async expand() {
        if (!(await this.beforeLeave())) {
            return;
        }
        this.actionService.doAction({
            type: "ir.actions.act_window",
            res_model: this.props.resModel,
            res_id: this.props.resId,
            // Use the action's form view (not false → model default) so expanding to the full
            // page shows the SAME form as the split panel — e.g. res.users' full Access Rights
            // form, not the cut-down default.
            views: [[this.props.formViewId || false, "form"]],
            context: this.props.context || {},
        });
    }

    // --- divider drag (pointer events; works with mouse and touch) -------------------
    onDividerDown(ev) {
        const panel = this.panelRef();
        const content = panel && panel.closest(".o_content");
        if (!content) {
            return;
        }
        const rect = content.getBoundingClientRect();
        const vertical = this.props.side === "bottom";
        const divider = ev.currentTarget;
        divider.setPointerCapture(ev.pointerId);
        divider.classList.add("o_glass_split_dragging");
        const onMove = (e) => {
            const raw = vertical
                ? (e.clientY - rect.top) / rect.height
                : (e.clientX - rect.left) / rect.width;
            const pct = Math.round(Math.min(78, Math.max(22, raw * 100)));
            content.style.setProperty("--glass-split", pct + "%");
            divider._pct = pct;
        };
        const onUp = () => {
            divider.removeEventListener("pointermove", onMove);
            divider.removeEventListener("pointerup", onUp);
            divider.classList.remove("o_glass_split_dragging");
            if (divider._pct) {
                this.props.onResize(divider._pct);
            }
        };
        divider.addEventListener("pointermove", onMove);
        divider.addEventListener("pointerup", onUp);
    }
}
