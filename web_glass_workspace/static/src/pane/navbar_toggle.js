/** @odoo-module **/
// The top bar (web.NavBar, both editions — Enterprise's navbar extends it):
//   * a ☰ toggle at the very start to show / hide the desktop left pane — the only change to the
//     navbar's markup: nothing is removed or moved, the button simply prepends;
//   * on a phone, the Glass tab bar opens Odoo's OWN app drawer through the bus
//     ("GLASS:APP-DRAWER", detail "apps" | "menu") — the drawer, its sections and its "All Apps"
//     list (Enterprise: the home menu) are Odoo's, the theme only restyles them.
import { patch } from "@web/core/utils/patch";
import { NavBar } from "@web/webclient/navbar/navbar";
import { useBus, useService } from "@web/core/utils/hooks";

patch(NavBar.prototype, {
    setup() {
        super.setup(...arguments);
        this.glassPrefs = useService("glass_prefs");
        this.glassUi = useService("ui");
        useBus(this.env.bus, "GLASS:APP-DRAWER", ({ detail }) => this.glassOpenDrawer(detail));
    },
    get glassPaneAvailable() {
        // only meaningful on desktop with a pane layout chosen
        return !this.glassUi.isSmall && this.glassPrefs.prefs.nav !== "top";
    },
    toggleGlassPane() {
        this.glassPrefs.setLocal({ paneOpen: !this.glassPrefs.state.paneOpen });
    },
    async glassOpenDrawer(what) {
        if (what === "apps") {
            // Community: the drawer's "All Apps" list; Enterprise: its home menu (the app grid)
            this.state.isAllAppsMenuOpened = false;
            this.state.isAppMenuSidebarOpened = true;
            this.onAllAppsBtnClick();
            return;
        }
        // "menu": the current app's sections. Enterprise draws the drawer only inside an app,
        // so leave its home menu first.
        if (this.hm && this.hm.hasHomeMenu) {
            await this.hm.toggle(false);
        }
        this.state.isAllAppsMenuOpened = false;
        this.state.isAppMenuSidebarOpened = true;
    },
});
