import { registry } from "@web/core/registry";
import { session } from "@web/session";

/**
 * User menu / systray clean-up.  Runs as a service so it executes after every
 * module (including enterprise ones) has registered its items, whatever the
 * asset order.
 */
const identityCleanupService = {
    start() {
        const identity = session.identity || {};
        const userMenu = registry.category("user_menuitems");
        const systray = registry.category("systray");

        if (identity.hide_external_links !== false) {
            // "My Odoo.com account" → accounts.odoo.com; "My Subscription" (module mysubscription,
            // auto-installed) → the vendor's subscription dashboard
            for (const key of ["odoo_account", "mysubscription_user_menu"]) {
                if (userMenu.contains(key)) {
                    userMenu.remove(key);
                }
            }
            // enterprise: "Odoo Studio – add new fields…" promo for admins
            for (const key of systray.getEntries().map(([k]) => k)) {
                if (/promote_?studio/i.test(key)) {
                    systray.remove(key);
                }
            }
        }
        // "Help" points to session.support_url, which the server sets to the
        // brand support URL or false.
        if (!session.support_url && userMenu.contains("support")) {
            userMenu.remove("support");
        }
    },
};

registry.category("services").add("identity_cleanup", identityCleanupService);
