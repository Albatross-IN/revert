/** @odoo-module **/
// Glass Workspace — optional left application pane. It is an overlay component (registered
// in main_components) so it never touches the navbar or webclient templates: the stock
// Odoo top bar stays exactly as it is. The pane sits under the top bar and shifts only the
// action area. A ☰ button (added to the navbar) shows / hides it.
import { Component, onMounted, onPatched, onWillUnmount, proxy, signal, useEffect, useListener } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { session } from "@web/session";

// Identity's glyph icons (optional): when the `identity` module publishes its glyph keys in the
// session, an app whose icon has a glyph file is drawn as a `.o_identity_icon` element (tile +
// glyph as CSS custom properties) instead of the <img>, so the theme colours it without filters.
// Same key rule as identity/static/src/js/icons.js; no import, identity may be absent.
let identityKeys = null;
function identityIconStyle(webIcon) {
    if (!webIcon || typeof webIcon !== "string") {
        return null;
    }
    if (!identityKeys) {
        identityKeys = new Set(session.identity_glyphs || []);
    }
    if (!identityKeys.size) {
        return null;
    }
    let module, res;
    if (webIcon.includes(",")) {
        const i = webIcon.indexOf(",");
        module = webIcon.slice(0, i).trim();
        res = webIcon.slice(i + 1);
    } else if (webIcon.includes("/static/")) {
        const path = webIcon.replace(/^\/+/, "");
        module = path.split("/")[0];
        res = path.slice(module.length + 1);
    } else {
        module = webIcon;
        res = "static/description/icon.png";
    }
    if (!/^[A-Za-z0-9_]+$/.test(module)) {
        return null;
    }
    const base = res.split("/").pop().replace(/\.[^.]+$/, "");
    const key = [`${module}__${base}`, module].find((k) => identityKeys.has(k));
    return key ? `--identity-tile:url('/identity/static/src/img/apps/${key}.svg');--identity-glyph:url('/identity/static/src/img/apps/glyph/${key}.svg')` : null;
}

// a Material Symbols glyph per kind of top-level menu (the hover menu's cards)
const FLY_GLYPHS = [
    [/overview|dashboard|home/, "speed"],
    [/operation|transfer|order|sale|purchase|quotation/, "local_shipping"],
    [/product|catalog|item|article/, "sell"],
    [/report|analysis|statistic/, "bar_chart"],
    [/config|setting|technical/, "settings"],
    [/customer|contact|partner|vendor|supplier|employee|people|member|attendee/, "group"],
    [/invoice|bill|account|payment|expense|payroll/, "description"],
    [/calendar|schedule|planning|appointment|time/, "calendar_today"],
    [/project|task|activity|to-do|todo/, "task_alt"],
    [/mail|message|discuss|chat|channel/, "forum"],
    [/website|site|page|blog|shop/, "public"],
    [/lead|opportunit|pipeline/, "star"],
    [/manufactur|work|production|repair|maintenance|quality/, "build"],
    [/stock|inventory|warehouse|lot/, "inventory_2"],
    [/document|file|knowledge|note/, "folder"],
];

export class GlassLeftPane extends Component {
    static template = "web_glass_workspace.LeftPane";

    flyRef = signal.ref();

    setup() {
        this.prefsSvc = useService("glass_prefs");
        this.prefs = this.prefsSvc.prefs; // proxy: nav
        this.paneState = this.prefsSvc.state; // proxy: paneOpen
        this.menu = useService("menu"); // reactive in Odoo 20: the pane follows the current app
        this.ui = useService("ui");
        // hover: mini-pane expand on hover; expanded: which menu nodes are open in the tree
        this.state = proxy({ hover: false, expanded: {} });
        // the hover menu: app (menu id) it shows, its top (px, the hovered app row), folded cards
        this.fly = proxy({ app: null, top: 0, folded: {} });
        this._flyTimer = null;
        onPatched(() => this.placeFly());
        useListener(window, "keydown", (ev) => {
            if (ev.key === "Escape" && this.fly.app) {
                this.closeFly();
            }
        }, { capture: true });

        // body classes the stylesheet shifts the action area with
        useEffect(() => {
            const active = this.active;
            document.body.classList.toggle("o_glass_pane_open", active);
            document.body.classList.toggle("o_glass_pane_mini", active && this.prefs.nav === "mini");
        });
        onMounted(() => {
            this.measureNavbar();
            this._obs = new ResizeObserver(() => this.measureNavbar());
            const nav = document.querySelector(".o_navbar");
            if (nav) {
                this._obs.observe(nav);
            }
        });
        onWillUnmount(() => {
            this._obs?.disconnect();
            clearTimeout(this._flyTimer);
            document.body.classList.remove("o_glass_pane_open", "o_glass_pane_mini");
        });
        useListener(window, "resize", () => this.measureNavbar());
    }

    measureNavbar() {
        const nav = document.querySelector(".o_navbar");
        if (nav) {
            document.body.style.setProperty("--glass-navbar-h", `${nav.offsetHeight}px`);
        }
    }

    get active() {
        return !this.ui.isSmall && this.prefs.nav !== "top" && this.paneState.paneOpen;
    }

    // -- the hover menu -------------------------------------------------------------------------
    get flyApp() {
        return this.fly.app ? this.apps.find((a) => a.id === this.fly.app) || null : null;
    }
    // one card per top-level node of the app's menu: its own sub-menus become headings, the
    // pages under them bulleted links (deeper levels indent); a top-level page is a card of its own
    get flyCards() {
        const app = this.flyApp;
        if (!app) {
            return [];
        }
        return this.sectionsOf(app.id).map((node) => {
            const rows = [];
            const walk = (nodes, depth) => {
                for (const child of nodes || []) {
                    if (this.hasChildren(child)) {
                        rows.push({ node: child, depth, header: true });
                        walk(child.childrenTree, depth + 1);
                    } else {
                        rows.push({ node: child, depth, header: false });
                    }
                }
            };
            walk(node.childrenTree, 0);
            if (!rows.length) {
                // a top-level page (Inventory › Overview): a card of its own with the one link
                rows.push({ node, depth: 0, header: false });
            }
            return { node, rows, glyph: this.flyGlyph(node.name) };
        });
    }
    flyGlyph(name) {
        const n = String(name || "").toLowerCase();
        for (const [re, glyph] of FLY_GLYPHS) {
            if (re.test(n)) {
                return glyph;
            }
        }
        return "radio_button_unchecked";
    }
    onAppHover(app, ev) {
        clearTimeout(this._flyTimer);
        if (!this.sectionsOf(app.id).length) {
            // an app that is one page (Discuss, Calendar…): nothing to unfold
            this.fly.app = null;
            return;
        }
        const top = ev.currentTarget.getBoundingClientRect().top;
        const open = () => {
            this.fly.top = Math.round(top);
            this.fly.app = app.id;
        };
        // a short hover intent the first time; an open menu follows the pointer at once
        if (this.fly.app) {
            open();
        } else {
            this._flyTimer = setTimeout(open, 140);
        }
    }
    onPaneLeave() {
        this.state.hover = false;
        clearTimeout(this._flyTimer);
        this._flyTimer = setTimeout(() => this.closeFly(), 220);
    }
    onPaneEnter() {
        this.state.hover = true;
        clearTimeout(this._flyTimer);
    }
    closeFly() {
        clearTimeout(this._flyTimer);
        this.fly.app = null;
    }
    // keep the menu inside the window: it starts at the hovered app's row and moves up when it
    // would run past the bottom
    placeFly() {
        const el = this.flyRef();
        if (!el || !this.fly.app) {
            return;
        }
        const navH = parseFloat(getComputedStyle(document.body).getPropertyValue("--glass-navbar-h")) || 46;
        const max = window.innerHeight - el.offsetHeight - 10;
        const top = Math.max(navH + 6, Math.min(this.fly.top, max));
        if (Math.abs(top - this.fly.top) > 1) {
            this.fly.top = Math.round(top);
        }
    }
    isFolded(node) {
        return !!this.fly.folded[node && node.id];
    }
    toggleFold(node) {
        this.fly.folded[node.id] = !this.fly.folded[node.id];
    }
    onFlyClick(node) {
        this.closeFly();
        const target = node.actionID ? node : this._firstWithAction(node);
        if (target) {
            this.menu.selectMenu(target);
        }
    }
    identityIconStyle(app) {
        return identityIconStyle(app && app.webIcon);
    }

    get mini() {
        return this.prefs.nav === "mini" && !this.state.hover;
    }

    get apps() {
        return this.menu.getApps().filter((a) => a.id !== "root");
    }
    get currentApp() {
        return this.menu.getCurrentApp();
    }
    sectionsOf(appId) {
        return this.menu.getMenuAsTree(appId).childrenTree || [];
    }
    // Flatten the current app's menu tree into a [{node, depth}] list, including the children of
    // any expanded node. Rendered with a single loop (no recursive template) so it's robust.
    visibleMenuNodes(appId) {
        const out = [];
        const walk = (nodes, depth) => {
            for (const node of nodes || []) {
                out.push({ node, depth });
                if (this.hasChildren(node) && this.isExpanded(node)) {
                    walk(node.childrenTree, depth + 1);
                }
            }
        };
        walk(this.sectionsOf(appId), 0);
        return out;
    }
    isCurrentApp(app) {
        return this.currentApp && this.currentApp.id === app.id;
    }

    onAppClick(app) {
        this.closeFly();
        // apps carry their own action, but fall back to the first actionable child just in case
        this.menu.selectMenu(this._firstWithAction(app) || app);
    }
    // The pane renders the FULL menu tree like the native top-menu dropdown: a node with
    // children expands/collapses to reveal them (Orders -> Quotations/Orders/Customers,
    // Configuration -> Settings/Sales Teams/Stages/…), and a leaf (which carries the actionID)
    // navigates.
    onMenuClick(node) {
        if (this.hasChildren(node)) {
            this.state.expanded[node.id] = !this.state.expanded[node.id];
        } else if (node.actionID) {
            this.menu.selectMenu(node);
        } else {
            // childless node with no action (rare) — drill to something actionable
            const target = this._firstWithAction(node);
            if (target) {
                this.menu.selectMenu(target);
            }
        }
    }
    hasChildren(node) {
        return !!(node && node.childrenTree && node.childrenTree.length);
    }
    isExpanded(node) {
        return !!this.state.expanded[node && node.id];
    }
    isCurrentMenu(node) {
        const cur = this.menu.getCurrentMenu ? this.menu.getCurrentMenu() : null;
        return !!(cur && node && cur.id === node.id);
    }
    _firstWithAction(menu) {
        if (menu && menu.actionID) {
            return menu;
        }
        for (const child of (menu && menu.childrenTree) || []) {
            const found = this._firstWithAction(child);
            if (found) {
                return found;
            }
        }
        return null;
    }
    toggleLock() {
        this.prefsSvc.set({ nav: this.prefs.nav === "mini" ? "side" : "mini" });
    }
}

registry.category("main_components").add("GlassLeftPane", { Component: GlassLeftPane });
