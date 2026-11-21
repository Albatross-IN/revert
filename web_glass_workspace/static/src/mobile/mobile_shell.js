/** @odoo-module **/
// Glass Workspace — app-like mobile shell: the bottom tab bar (Apps · Menu · Activity · Account),
// and the grouped-kanban stage picker.
//
// An overlay component (registered in main_components, exactly like the left pane) so it
// NEVER touches the navbar or webclient templates. It renders only while the `ui` service
// reports `isSmall` (< 768px), which is the same breakpoint web_theme_glass/scss/mobile.scss
// keys off — so the desktop (and a tablet) is provably untouched.
//
// The tabs open Odoo's OWN phone navigation, restyled by the theme — nothing is redrawn:
//   Apps     → the drawer's "All Apps" list (Enterprise: the home menu)   — navbar_toggle.js
//   Menu     → the drawer with the current app's sections                   — navbar_toggle.js
//   Activity → the activity menu of the top bar
//   Account  → the burger menu (user · companies · preferences · log out)   — burger_menu.js
import { Component, proxy, useEffect } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useBus, useService } from "@web/core/utils/hooks";
import { stageStore } from "./stage_store";
import "./kanban_stage_patch"; // installs the KanbanController patch that feeds stageStore

export class GlassMobileShell extends Component {
    static template = "web_glass_workspace.MobileShell";

    setup() {
        this.ui = useService("ui");
        // overlay: null | "stages"
        this.state = proxy({ overlay: null, onForm: false });
        // the grouped-kanban stage picker is driven by a reactive store the Kanban controller
        // feeds (real stages + server totals + a real domain filter) — see kanban_stage_patch.js
        this.stage = stageStore;
        // mail store (for closing Discuss chat windows on navigation); guarded — may be absent
        this.mailStore = this.env.services["mail.store"];

        // body classes: the shell is on screen / a sheet is open / a record's form is on screen
        useEffect(() => {
            const b = document.body;
            b.classList.toggle("o_glass_mobile", this.active);
            b.classList.toggle("o_glass_m_locked", this.active && !!this.state.overlay);
            b.classList.toggle("o_glass_m_form", this.active && this.state.onForm);
        });

        // On ANY navigation: (1) close any open sheet; (2) close any Discuss chat window — on
        // mobile it's a full-screen fixed overlay that otherwise stays on top of the newly-opened
        // app and makes it look "stuck"; (3) clear leftover stage state; (4) note whether the
        // screen is a record's form (the "tab bar on a record" preference reads it).
        useBus(this.env.bus, "ACTION_MANAGER:UI-UPDATED", () => {
            this.state.overlay = null;
            this.closeChatWindows();
            this.state.onForm = !!document.querySelector(".o_action_manager > .o_action.o_form_view");
            setTimeout(() => {
                const hasGroupedKanban = document.querySelector(".o_kanban_view .o_kanban_renderer.o_kanban_grouped");
                if (!hasGroupedKanban && stageStore.active) {
                    stageStore.reset();
                }
            }, 350);
        });

    }

    get active() {
        return this.ui.isSmall;
    }

    // -- overlays ------------------------------------------------------------
    openOverlay(name) {
        this.state.overlay = this.state.overlay === name ? null : name;
    }
    closeOverlay() {
        this.state.overlay = null;
    }

    // -- the tabs: Odoo's own navigation ---------------------------------------
    openApps() {
        this.closeOverlay();
        this.env.bus.trigger("GLASS:APP-DRAWER", "apps");
    }
    openMenu() {
        this.closeOverlay();
        this.env.bus.trigger("GLASS:APP-DRAWER", "menu");
    }
    openActivity() {
        this.closeOverlay();
        // Odoo's own activity menu (top bar), not a copy of it
        const icon = document.querySelector('.o_menu_systray .oi[data-icon="schedule"]');
        const btn = icon && icon.closest("button");
        if (btn) {
            btn.click();
        }
    }
    openAccount() {
        this.closeOverlay();
        this.env.bus.trigger("GLASS:BURGER");
    }

    // -- stage picker (grouped kanban) ---------------------------------------
    // All data + filtering comes from the reactive stageStore, fed by the Kanban controller
    // (kanban_stage_patch.js). Selecting a stage applies a real search domain server-side.
    get showStagePicker() {
        return this.active && this.stage.active && this.stage.groups.length > 0;
    }
    get stages() {
        return this.stage.groups;
    }
    isStageSelected(value) {
        return this.stage.selected === value;
    }
    selectStage(value) {
        if (this.stage.apply) {
            // undefined from the "All" button -> clear the filter
            this.stage.apply(value === undefined ? null : value);
        }
        this.closeOverlay();
    }
    get currentStageLabel() {
        if (this.stage.selected === null) {
            return "All stages";
        }
        const g = this.stage.groups.find((s) => s.value === this.stage.selected);
        return g ? g.label : "Stage";
    }
    get isStageFiltered() {
        return this.stage.selected !== null;
    }

    // -- navigation ----------------------------------------------------------
    closeChatWindows() {
        // close any open Discuss chat window so it can't cover the view we navigate to
        try {
            this.mailStore?.chatHub?.closeAll();
        } catch {
            // mail not loaded / API changed — ignore
        }
    }

}

registry.category("main_components").add("GlassMobileShell", { Component: GlassMobileShell });
