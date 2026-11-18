/** @odoo-module **/
// User menu (avatar, top-right; the burger menu on a phone): "Theme preferences" opens the Glass
// panel; Community gets a "Dark mode" switch; phones and installed apps a "Developer mode" switch.
import { registry } from "@web/core/registry";
import { _t } from "@web/core/l10n/translation";
import { session } from "@web/session";
import { router } from "@web/core/browser/router";
import { isDisplayStandalone } from "@web/core/browser/feature_detection";
import { glassPanelState } from "./prefs_panel";

function themePreferencesItem() {
    return {
        type: "item",
        id: "glass_theme_prefs",
        description: _t("Theme preferences"),
        callback: () => {
            glassPanelState.open = true;
        },
        sequence: 45,
    };
}

registry.category("user_menuitems").add("glass_theme_prefs", themePreferencesItem, { sequence: 45 });

// Community has no "Dark Mode" entry (web_enterprise adds one): the same switch, driven by the
// theme's own dark scheme (glass_prefs.setMode). Not registered when Enterprise's color_scheme
// service exists, so the Enterprise menu is untouched.
function darkModeItem(env) {
    const prefs = env.services.glass_prefs;
    const dark = prefs.effectiveScheme(prefs.mode) === "dark";
    return {
        type: "switch",
        id: "glass_dark_mode",
        description: _t("Dark mode"),
        isChecked: dark,
        callback: () => prefs.setMode(dark ? "light" : "dark"),
        sequence: 44,
    };
}
if (!registry.category("services").contains("color_scheme")) {
    registry.category("user_menuitems").add("glass_dark_mode", darkModeItem, { sequence: 44 });
}

// Developer mode where there is no address bar to type `?debug=1` in — a phone, or Odoo installed
// as an app (PWA) on a tablet or a desktop: Odoo hides its technical menus (Settings › Groups /
// Technical, ~200 Configuration items) unless the SESSION is in developer mode. The state is the
// server session's (session_info.bundle_params.debug: `odoo.debug` is blanked whenever the URL has
// no `?debug=`); the switch does what Odoo's own "Activate the developer mode" link does.
function developerModeItem(env) {
    const on = !!(session.bundle_params && session.bundle_params.debug);
    return {
        type: "switch",
        id: "glass_dev_mode",
        description: _t("Developer mode"),
        isChecked: on,
        hide: !(env.services.ui.isSmall || isDisplayStandalone()),
        callback: () => router.pushState({ debug: on ? 0 : 1 }, { reload: true }),
        sequence: 46,
    };
}
registry.category("user_menuitems").add("glass_dev_mode", developerModeItem, { sequence: 46 });
