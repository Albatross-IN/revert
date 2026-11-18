/** @odoo-module **/
// Glass Workspace — phone calendar: jump straight to a month (see calendar_nav.xml).
// The period title carries an invisible <input type="month">; the phone shows its native
// month wheel and the chosen month is loaded through the controller's own model.load,
// exactly what Odoo's previous / next / today buttons do. (Odoo 20 shortens the month names of
// the week title on mobile devices itself.)
import { patch } from "@web/core/utils/patch";
import { CalendarController } from "@web/views/calendar/calendar_controller";

patch(CalendarController.prototype, {
    get glassMonthValue() {
        const d = this.model && this.model.date;
        return d ? d.toFormat("yyyy-LL") : "";
    },
    async glassJumpToMonth(ev) {
        const [year, month] = String(ev.target.value || "")
            .split("-")
            .map((x) => parseInt(x, 10));
        if (!year || !month) {
            return;
        }
        const date = luxon.DateTime.local(year, month, 1);
        if (!date.isValid) {
            return;
        }
        await this.model.load({ date });
    },
});
