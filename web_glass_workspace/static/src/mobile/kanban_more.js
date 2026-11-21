/** @odoo-module **/
// Phone grouped kanban: stages are stacked top-to-bottom by the theme, so a busy stage would push
// the next ones far down. Each group shows its first cards and a "Show more" button reveals ten
// more per tap — the records are already loaded by Odoo (its own "Load more" stays for the
// server-side batches). Desktop untouched (everything gated on ui.isSmall). Presentation only.
import { KanbanRenderer } from "@web/views/kanban/kanban_renderer";
import { patch } from "@web/core/utils/patch";
import { proxy } from "@odoo/owl";

const FIRST = 4;
const STEP = 10;

patch(KanbanRenderer.prototype, {
    setup() {
        super.setup(...arguments);
        this.glassMore = proxy({ shown: {} }); // group id → cards currently shown
    },
    // number of cards to render for a group on a phone
    glassVisible(group) {
        if (!this.uiService.isSmall || !group) {
            return Infinity;
        }
        return this.glassMore.shown[group.id] || FIRST;
    },
    // how many loaded cards are still hidden behind the button
    glassHidden(group) {
        if (!this.uiService.isSmall || !group || !group.list) {
            return 0;
        }
        return Math.max(0, group.list.records.length - this.glassVisible(group));
    },
    glassShowMore(group) {
        this.glassMore.shown[group.id] = this.glassVisible(group) + STEP;
    },
});
