/** @odoo-module **/
// Glass Workspace — per-user preferences, delivered with session_info and kept reactive so
// the navbar, views, mobile shell and preferences panel all react the moment one changes.
// Runtime-only effects (chatter body class) are applied here.
import { registry } from "@web/core/registry";
import { session } from "@web/session";
import { user } from "@web/core/user";
import { proxy } from "@odoo/owl";
import { browser } from "@web/core/browser/browser";
import { cookie } from "@web/core/browser/cookie";

const DEFAULTS = { nav: "top", split: false, split_side: "right", split_chatter: "float", chatter: "right", m_tabbar: "keep" };
const LOCAL_KEY = "glass.workspace.local";


export const glassPrefsService = {
    dependencies: ["orm"],
    start(env, { orm }) {
        let local = {};
        try {
            local = JSON.parse(browser.localStorage.getItem(LOCAL_KEY) || "{}");
        } catch {
            local = {};
        }
        const prefs = proxy({ ...DEFAULTS, ...(session.glass_prefs || {}) });
        const state = proxy({ splitPct: 50, paneOpen: prefs.nav !== "top", ...local });

        function saveLocal() {
            try {
                browser.localStorage.setItem(
                    LOCAL_KEY,
                    JSON.stringify({ splitPct: state.splitPct, paneOpen: state.paneOpen })
                );
            } catch {
                // private mode / quota — the convenience just does not persist
            }
        }

        // --- runtime CSS effects ------------------------------------------------------
        function applyChatter() {
            document.body.classList.toggle("o_glass_chatter_bottom", prefs.chatter === "bottom");
        }
        applyChatter();
        // phones: the tab bar steps aside while a record is open (mobile_shell.scss reads the class)
        function applyTabbar() {
            document.body.classList.toggle("o_glass_m_notab", prefs.m_tabbar === "hide");
        }
        applyTabbar();

        const api = {
            prefs,
            state,
            async set(vals) {
                const map = {
                    nav: "glass_nav",
                    split: "glass_split",
                    split_side: "glass_split_side",
                    split_chatter: "glass_split_chatter",
                    chatter: "glass_chatter",
                    m_tabbar: "glass_m_tabbar",
                };
                const fieldVals = {};
                for (const [k, v] of Object.entries(vals)) {
                    if (k in map) {
                        fieldVals[map[k]] = v;
                    }
                }
                await orm.write("res.users", [user.userId], fieldVals);
                Object.assign(prefs, vals);
                if ("nav" in vals) {
                    state.paneOpen = vals.nav !== "top";
                    saveLocal();
                }
                if ("chatter" in vals) {
                    applyChatter();
                }
                if ("m_tabbar" in vals) {
                    applyTabbar();
                }
            },
            setLocal(vals) {
                Object.assign(state, vals);
                saveLocal();
            },
            // --- appearance mode (reuses Odoo's color_scheme cookie + user setting) ----
            // Community has no color_scheme service, no user setting and (natively) no dark
            // bundle: the theme serves its own (ir_http.py + community_dark.scss) from the same
            // cookie. The chosen mode (light / dark / system) is kept in localStorage there,
            // and "system" follows the OS preference on every load.
            get isCommunityScheme() {
                return !registry.category("services").contains("color_scheme");
            },
            get mode() {
                if (this.isCommunityScheme) {
                    let m = null;
                    try { m = browser.localStorage.getItem("glass_color_mode"); } catch { /* private mode */ }
                    return m === "dark" || m === "light" ? m : "system";
                }
                const c = cookie.get("color_scheme");
                if (user.settings && ["light", "dark"].includes(user.settings.color_scheme)) {
                    return user.settings.color_scheme;
                }
                return c === "dark" || c === "light" ? c : "system";
            },
            // the scheme a mode resolves to ("system" = the OS preference)
            effectiveScheme(mode) {
                if (mode === "dark" || mode === "light") {
                    return mode;
                }
                return browser.matchMedia && browser.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
            },
            // the scheme the page was served with (webclient.scss puts it on :root)
            get servedScheme() {
                const v = getComputedStyle(document.documentElement).getPropertyValue("--o-webclient-color-scheme").trim();
                return v === "dark" ? "dark" : "light";
            },
            async setMode(mode) {
                if (this.isCommunityScheme) {
                    try { browser.localStorage.setItem("glass_color_mode", mode); } catch { /* private mode */ }
                    cookie.set("color_scheme", this.effectiveScheme(mode));
                    browser.location.reload();
                    return;
                }
                const value = mode === "system" ? "" : mode;
                try {
                    if (user.settings && user.settings.id) {
                        await orm.call("res.users.settings", "set_res_users_settings", [
                            [user.settings.id],
                            { color_scheme: value },
                        ]);
                    }
                } catch {
                    // fall back to the cookie-only path below
                }
                if (value) {
                    cookie.set("color_scheme", value);
                } else {
                    cookie.delete("color_scheme");
                }
                browser.location.reload();
            },
            // Community, at start-up: make the cookie match the chosen mode (the OS preference
            // for "system") and reload once when the page was served with the other scheme
            syncCommunityScheme() {
                if (!this.isCommunityScheme) {
                    return;
                }
                const wanted = this.effectiveScheme(this.mode);
                if (cookie.get("color_scheme") !== wanted) {
                    cookie.set("color_scheme", wanted);
                }
                if (this.servedScheme !== wanted) {
                    let guard = null;
                    try { guard = browser.sessionStorage.getItem("glass_scheme_reload"); } catch { /* private mode */ }
                    if (guard !== wanted) {   // never loop if the server cannot serve the scheme
                        try { browser.sessionStorage.setItem("glass_scheme_reload", wanted); } catch { /* private mode */ }
                        browser.location.reload();
                    }
                }
            },
        };
        api.syncCommunityScheme();
        return api;
    },
};

registry.category("services").add("glass_prefs", glassPrefsService);
