/** @odoo-module **/
// Shared reactive bridge between a grouped Kanban's controller (which owns the search model)
// and the mobile shell overlay (which draws the stage picker). The controller publishes the
// real stage list + totals here and exposes an apply() that adds a real search domain; the
// overlay only reads this store and calls apply(). Nothing hides DOM — the server returns only
// the chosen stage's leads, so it scales to 100k+ records and respects default + custom filters.
import { proxy } from "@odoo/owl";

export const stageStore = proxy({
    active: false, // a single-groupby grouped kanban is on screen (mobile)
    groups: [], // [{ label, value (serverValue), count (real total) }]
    field: null, // group-by field name, e.g. "stage_id"
    selected: null, // null = all stages; otherwise a group's serverValue (may be false = "None")
    owner: null, // token of the KanbanController currently publishing (kanban_stage_patch.js)
    apply: null, // async (value|null) => void  — set by the controller

    reset() {
        this.active = false;
        this.groups = [];
        this.field = null;
        this.selected = null;
        this.owner = null;
        this.apply = null;
    },
});
