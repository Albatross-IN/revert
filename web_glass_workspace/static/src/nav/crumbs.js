/** @odoo-module **/
// Navigation path (breadcrumbs) on the desktop and tablets: a separate Back key, the page name as
// a button that drops the whole navigation trail down (any level is one tap away), and a small line
// with the parent page and "n of total" for a record. Phones keep Odoo's own compact breadcrumb.
// Odoo's breadcrumbs keep their functions: every entry calls the same `onSelected` the native
// crumb calls, the back key is the native `o_back_button` (hotkey b).
import { patch } from "@web/core/utils/patch";
import { Breadcrumbs } from "@web/search/breadcrumbs/breadcrumbs";
import { _t } from "@web/core/l10n/translation";

patch(Breadcrumbs.prototype, {
    setup() {
        super.setup(...arguments);
        // the controller's pager state (usePager): a proxy, so "n of total" follows it
        this.glassPager = (this.env.config && this.env.config.pagerProps) || null;
    },
    get glassPrev() {
        const b = this.props.breadcrumbs;
        return b.length > 1 ? b[b.length - 2] : null;
    },
    get glassCurrent() {
        const b = this.props.breadcrumbs;
        return b[b.length - 1] || {};
    },
    // "Sales Orders · 63 of 69" — the parent page, then the record's position when the pager
    // walks single records (a form); a list shows its own counter in the pager
    get glassSub() {
        const parts = [];
        if (this.glassPrev && this.glassPrev.name) {
            parts.push(this.glassPrev.name);
        }
        const p = this.glassPager;
        if (p && p.total > 0 && p.limit === 1) {
            parts.push(_t("%s of %s", p.offset + 1, p.total));
        }
        return parts.join(" · ");
    },
    glassName(crumb) {
        return crumb.name || _t("Unnamed");
    },
});
