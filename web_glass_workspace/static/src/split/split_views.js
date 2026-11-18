/** @odoo-module **/
// Split Form View — list & kanban controllers open a clicked record in the side panel when
// the user preference is on (desktop only). With the preference off, `openRecord` is stock.
//
// The panel is injected through `Layout` (patched below), not through each view template,
// because many apps (CRM, Project, …) define their own list/kanban template via primary
// inheritance — extending `web.ListView` would miss them. Every view renders inside
// `Layout`, so patching Layout covers them all.
import { patch } from "@web/core/utils/patch";
import { useService } from "@web/core/utils/hooks";
import { proxy } from "@odoo/owl";
import { useSubEnv } from "@web/owl2/utils";
import { Layout } from "@web/search/layout";
import { ListController } from "@web/views/list/list_controller";
import { KanbanController } from "@web/views/kanban/kanban_controller";
import { ListRenderer } from "@web/views/list/list_renderer";
import { KanbanRecord } from "@web/views/kanban/kanban_record";
import { GlassSplitPanel } from "./split_panel";

// Shared controller wiring: expose an env descriptor Layout reads to decide whether/how to
// draw the panel. Getters read `this` (controller) + the reactive `state`, so Layout
// re-renders when the selected record or collapsed flag changes.
function setupSplit(ctrl) {
    ctrl.glassPrefs = useService("glass_prefs");
    ctrl.glassUi = useService("ui");
    ctrl.glassSplit = proxy({ resId: null, collapsed: false });
    const state = ctrl.glassSplit;
    const prefs = ctrl.glassPrefs;
    const ui = ctrl.glassUi;

    // ONE stable props object. Only `resId`/`collapsed` (reactive getters) change what the
    // panel sees; the object identity never changes, so Layout re-rendering does not remount
    // the panel, and rendering never reads the record collection (which would subscribe
    // Layout to every model tick and loop). prev/next reads the collection lazily on click.
    const panelProps = {
        get resModel() {
            return ctrl.props.resModel;
        },
        // Use the SAME form view the record would open in normally (the action's bound form
        // view), not the model's default. Without this, models whose default form differs
        // from the action's — e.g. res.users defaults to the cut-down `view_users_simple_form`
        // — render the wrong (stripped) form in the panel.
        get formViewId() {
            const views = (ctrl.env.config && ctrl.env.config.views) || [];
            const f = views.find((v) => v[1] === "form");
            return f ? f[0] : false;
        },
        get resId() {
            return state.resId;
        },
        get context() {
            return ctrl.props.context;
        },
        get side() {
            return prefs.prefs.split_side;
        },
        get collapsed() {
            return state.collapsed;
        },
        getResIds: () => ctrl.model.root.records.map((r) => r.resId).filter(Boolean),
        onClose: () => {
            state.resId = null;
            state.collapsed = false;
        },
        onSelect: (resId) => (state.resId = resId),
        onSaved: () => ctrl.model.root.load(),
        onToggleCollapse: () => (state.collapsed = !state.collapsed),
        onResize: (pct) => prefs.setLocal({ splitPct: pct }),
    };

    useSubEnv({
        glassSplit: {
            state,
            get active() {
                return !!prefs.prefs.split && !ui.isSmall && !ctrl.env.inDialog;
            },
            get open() {
                return this.active && !!state.resId;
            },
            get bottom() {
                return prefs.prefs.split_side === "bottom";
            },
            get collapsed() {
                return state.collapsed;
            },
            get style() {
                return `--glass-split: ${prefs.state.splitPct}%`;
            },
            props: panelProps,
        },
    });
}

function splitActive(ctrl) {
    return !!ctrl.glassPrefs.prefs.split && !ctrl.glassUi.isSmall && !ctrl.env.inDialog;
}

patch(ListController.prototype, {
    setup() {
        super.setup(...arguments);
        setupSplit(this);
    },
    async openRecord(record, options = {}) {
        const openAction = this.props.allowOpenAction && this.archInfo.openAction;
        if (splitActive(this) && !options.newWindow && !options.force && !openAction && record.resId) {
            if (await record.isDirty()) {
                await record.save();
            }
            this.glassSplit.resId = record.resId;
            return;
        }
        return super.openRecord(...arguments);
    },
});

patch(KanbanController.prototype, {
    setup() {
        super.setup(...arguments);
        setupSplit(this);
    },
    async openRecord(record, options = {}) {
        if (splitActive(this) && !options.newWindow && !this.props.archInfo.openAction && record.resId) {
            this.glassSplit.resId = record.resId;
            return;
        }
        return super.openRecord(...arguments);
    },
});

// Layout draws the panel as a sibling of the renderer inside `.o_content` (see split_views.xml).
// Layout resolves its own sub-components through `this.components` (Odoo 20), hence a getter
// and `t-component` rather than a static components entry.
patch(Layout.prototype, {
    get glassSplitPanel() {
        return GlassSplitPanel;
    },
});

// Highlight the record shown in the panel
patch(ListRenderer.prototype, {
    getRowClass(record) {
        const cls = super.getRowClass(record);
        if (this.env.glassSplit && this.env.glassSplit.state.resId === record.resId) {
            return cls + " o_glass_split_current";
        }
        return cls;
    },
});

patch(KanbanRecord.prototype, {
    getCardClasses() {
        const cls = super.getCardClasses();
        if (this.env.glassSplit && this.env.glassSplit.state.resId === this.props.record.resId) {
            return cls + " o_glass_split_current";
        }
        return cls;
    },
});
