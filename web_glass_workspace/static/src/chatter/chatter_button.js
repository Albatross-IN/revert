/** @odoo-module **/
// Glass Workspace — the "open the chatter" button, and the generic hooks that put it in every
// kanban card and every list row (phones and desktop) and in every form control panel (phones)
// of a model that has a chatter (mail.thread) — stock apps and customer modules alike, because
// the hooks live in the base templates (web.FormView / web.KanbanRecord / web.ListRenderer)
// which every module's views inherit, and the model capability is asked from the server.
//
// The button is reached through a prototype getter + `t-component` (not `static components`)
// so subclassed controllers / renderers in other modules — which copy `components` when they
// are defined — can never miss it.
import { Component, t, useOnChange, useProps } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { patch } from "@web/core/utils/patch";
import { FormController } from "@web/views/form/form_controller";
import { KanbanRecord } from "@web/views/kanban/kanban_record";
import { ListRenderer } from "@web/views/list/list_renderer";
import {
    chatterStore,
    chatterCaps,
    chatterCounts,
    chatterCapability,
    requestCount,
    showChatter,
    hideChatter,
    isChatterShown,
} from "./chatter_store";

export class GlassChatterButton extends Component {
    static template = "web_glass_workspace.ChatterButton";

    props = useProps({
        resModel: t.string(),
        resId: t.number(),
        variant: t.string(), // "cp" (form control panel) | "card" (kanban) | "row" (list)
        openRecord: t.function().optional(),
    });

    setup() {
        // The capability and count requests are SHARED (one per model, cached in the store) and
        // outlive the button that starts them: the global ORM, not `useService("orm")` — Odoo 20
        // leaves a destroyed component's calls pending forever, and a grouped kanban renders its
        // cards twice while it loads, so every later button waited on an orphaned request.
        this.orm = this.env.services.orm;
        this.ui = useService("ui");
        // proxies: the template follows them
        this.store = chatterStore;
        this.caps = chatterCaps;
        this.counts = chatterCounts;

        // does this model have a chatter? (cached per model) — and the badge count
        useOnChange(
            () => [this.props.resModel, this.props.resId, !!this.cap?.thread],
            (model, id, thread) => {
                chatterCapability(this.orm, model);
                if (thread) {
                    requestCount(this.orm, model, id);
                }
            }
        );

        // phone form: a window opened from this form follows the record the form shows
        if (this.props.variant === "cp") {
            useOnChange(
                () => [this.props.resModel, this.props.resId],
                (model, id) => {
                    const s = this.store;
                    if (s.open && s.source === "form" && (s.resModel !== model || s.resId !== id)) {
                        showChatter(model, id, {
                            source: "form",
                            hasActivities: !!this.cap?.activities,
                            keepMode: true,
                        });
                    }
                }
            );
        }
    }

    get cap() {
        return this.caps[this.props.resModel];
    }
    get visible() {
        // cards and rows everywhere; the control-panel key only on phones (a desktop form
        // shows its own chatter)
        if (this.props.variant === "cp" && !this.ui.isSmall) {
            return false;
        }
        return !!(this.cap && this.cap.thread) && !!this.props.resId;
    }
    get isOpen() {
        return isChatterShown(this.props.resModel, this.props.resId);
    }
    get count() {
        const byId = this.counts[this.props.resModel];
        return byId ? byId[this.props.resId] || 0 : 0;
    }
    get title() {
        return this.isOpen ? "Close the chatter" : "Open the chatter";
    }

    onClick(ev) {
        ev.stopPropagation();
        ev.preventDefault();
        if (this.isOpen) {
            hideChatter();
            return;
        }
        const fromForm = this.props.variant === "cp";
        showChatter(this.props.resModel, this.props.resId, {
            source: fromForm ? "form" : "card",
            hasActivities: !!this.cap?.activities,
            onOpenRecord: fromForm ? null : this.props.openRecord || null,
        });
    }
}

// --- generic hooks -------------------------------------------------------------------
const buttonGetter = {
    get glassChatterButton() {
        return GlassChatterButton;
    },
};
patch(FormController.prototype, buttonGetter);
patch(KanbanRecord.prototype, buttonGetter);
patch(ListRenderer.prototype, {
    ...buttonGetter,
    setup() {
        super.setup(...arguments);
        this.glassOrm = this.env.services.orm; // shared request (see GlassChatterButton.setup)
        this.glassCaps = chatterCaps;
        useOnChange(
            () => [this.props.list.resModel],
            (resModel) => chatterCapability(this.glassOrm, resModel)
        );
    },
    // the list gets a trailing chatter column (header, rows, footer) once the model is known to
    // have a chatter — never on sample data, never inside a record-picker dialog
    get glassChatterCol() {
        const cap = this.glassCaps[this.props.list.resModel];
        return !!(cap && cap.thread) && !this.props.list.model.useSampleModel && !this.env.inDialog;
    },
});
