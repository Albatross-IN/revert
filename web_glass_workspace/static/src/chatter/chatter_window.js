/** @odoo-module **/
// Glass Workspace — the floating chatter window.
//
// A `main_components` overlay (like the left pane and the mobile shell) that renders Odoo's
// OWN `Chatter` component for the record in `chatterStore` — messages, notes, activities,
// followers, attachments all behave exactly as in a form. Nothing native is modified.
//
//   desktop  : movable / resizable window; opened automatically by the split panel (pref) or
//              by its "Float chatter" button; follows the selected record; pin / minimise / dock
//   phone    : small movable window ("mini"), full-screen sheet ("full") or a draggable
//              bubble; opened ONLY from a button (form control panel, kanban card, list row)
import { Component, onWillUnmount, proxy, signal, toRaw, useEffect, useListener, useOnChange } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useBus, useService } from "@web/core/utils/hooks";
import { browser } from "@web/core/browser/browser";
import { Chatter } from "@mail/chatter/web_portal_project/chatter";
import { chatterStore, hideChatter, saveGeom } from "./chatter_store";

const MARGIN = 8;
const SNAP = 18;
const DESKTOP_MIN = { w: 340, h: 260 };
const PHONE_MIN = { w: 220, h: 190 };

export class GlassChatterWindow extends Component {
    static template = "web_glass_workspace.ChatterWindow";
    static components = { Chatter };

    setup() {
        this.ui = useService("ui");
        this.orm = useService("orm");
        this.action = useService("action");
        this.store = chatterStore; // proxy: the template follows it
        this.local = proxy({ dragging: false });
        // Geometry is computed and clamped while rendering (the screen may have changed), so it
        // lives in the RAW store object — writing a proxy during a render would re-trigger it;
        // `redraw` is the signal a drag / a window resize bumps to draw the new position.
        this.redraw = signal(0);

        // record title
        useOnChange(
            () => [this.store.resModel, this.store.resId, this.store.open],
            (model, id, open) => {
                if (open && model && id) {
                    this.fetchTitle(model, id);
                }
            }
        );

        // Any navigation closes a window that was opened from a button (phone / form / card);
        // the split panel manages its own (it unmounts). Opening the record from the window
        // itself is the one navigation that keeps it.
        this._onNav = () => {
            if (this._keepOnNextNav) {
                this._keepOnNextNav = false;
                return;
            }
            if (this.store.open && this.store.source !== "split") {
                hideChatter();
            }
        };
        useBus(this.env.bus, "ACTION_MANAGER:UI-UPDATED", this._onNav);
        onWillUnmount(() => document.body.classList.remove("o_glass_chatter_open"));
        useEffect(() => {
            document.body.classList.toggle("o_glass_chatter_open", this.active);
        });
        useListener(window, "resize", () => this.bump());
    }

    bump() {
        this.redraw.set(this.redraw() + 1);
    }
    // the remembered geometry, outside the reactive system (see setup)
    get geom() {
        return toRaw(this.store.geom);
    }

    async fetchTitle(model, id) {
        try {
            const [rec] = await this.orm.read(model, [id], ["display_name"]);
            if (rec && this.store.resModel === model && this.store.resId === id) {
                this.store.displayName = rec.display_name || "";
            }
        } catch {
            // no read access / deleted record: the window keeps a bare title
        }
    }

    // -- state ---------------------------------------------------------------
    get active() {
        return !!(this.store.open && this.store.resModel && this.store.resId);
    }
    get isPhone() {
        return this.ui.isSmall;
    }
    get fromSplit() {
        return this.store.source === "split";
    }
    get title() {
        return this.store.displayName || "";
    }
    get chatterProps() {
        return {
            threadModel: this.store.resModel,
            threadId: this.store.resId,
            isChatterAside: true,
            isInFormSheetBg: false,
            has_activities: !!this.store.hasActivities,
        };
    }
    get chatterKey() {
        return `${this.store.resModel}/${this.store.resId}`;
    }

    // -- geometry ------------------------------------------------------------
    get bounds() {
        // the screen area the window may use: below the navbar, above the phone tab bar
        const nav = document.querySelector(".o_main_navbar");
        const top = nav ? nav.getBoundingClientRect().bottom : 0;
        const tab = this.isPhone ? document.querySelector(".o_glass_m_tabbar") : null;
        const bottom = tab ? tab.getBoundingClientRect().top : browser.innerHeight;
        return { top: Math.max(0, top), bottom, left: 0, right: browser.innerWidth };
    }
    defaultDesktop() {
        const b = this.bounds;
        const w = 460;
        const h = Math.min(540, b.bottom - b.top - MARGIN * 2);
        return { x: b.right - w - MARGIN, y: b.bottom - h - MARGIN, w, h };
    }
    defaultPhone() {
        const b = this.bounds;
        const w = Math.round(b.right * 0.8);
        const h = Math.round((b.bottom - b.top) * 0.42);
        return { x: b.right - w - MARGIN, y: b.bottom - h - MARGIN, w, h };
    }
    defaultBubble() {
        const b = this.bounds;
        return { x: b.right - 56 - 12, y: b.bottom - 56 - 84 };
    }
    get win() {
        const g = this.geom;
        if (this.isPhone) {
            if (!g.mwin) {
                g.mwin = this.defaultPhone();
            }
            return this.clamp(g.mwin, PHONE_MIN);
        }
        if (!g.win) {
            g.win = this.defaultDesktop();
        }
        return this.clamp(g.win, DESKTOP_MIN);
    }
    get bubble() {
        const g = this.geom;
        if (!g.bubble) {
            g.bubble = this.defaultBubble();
        }
        const b = this.bounds;
        g.bubble.x = Math.min(Math.max(g.bubble.x, MARGIN), b.right - 56 - MARGIN);
        g.bubble.y = Math.min(Math.max(g.bubble.y, b.top + MARGIN), b.bottom - 56 - MARGIN);
        return g.bubble;
    }
    clamp(w, min) {
        const b = this.bounds;
        const maxW = b.right - b.left - MARGIN * 2;
        const maxH = b.bottom - b.top - MARGIN * 2;
        w.w = Math.round(Math.min(Math.max(w.w, min.w), Math.max(min.w, maxW)));
        w.h = Math.round(Math.min(Math.max(w.h, min.h), Math.max(min.h, maxH)));
        w.x = Math.round(Math.min(Math.max(w.x, b.left + MARGIN), b.right - w.w - MARGIN));
        w.y = Math.round(Math.min(Math.max(w.y, b.top + MARGIN), b.bottom - w.h - MARGIN));
        return w;
    }
    get winStyle() {
        this.redraw(); // a drag / resize bumps it
        if (this.isPhone && this.store.mode === "full") {
            const b = this.bounds;
            return `left:0;right:0;top:${b.top}px;bottom:${browser.innerHeight - b.bottom}px`;
        }
        if (this.isPhone && this.store.mode === "bubble") {
            const p = this.bubble;
            return `left:${p.x}px;top:${p.y}px`;
        }
        const w = this.win;
        if (!this.isPhone && this.store.minimized) {
            return `left:${w.x}px;top:${w.y + w.h - 48}px;width:${w.w}px`;
        }
        return `left:${w.x}px;top:${w.y}px;width:${w.w}px;height:${w.h}px`;
    }

    // -- drag (header) --------------------------------------------------------
    onHeaderPointerDown(ev) {
        if (ev.target.closest("button") || (this.isPhone && this.store.mode === "full")) {
            return;
        }
        ev.preventDefault();
        const el = ev.currentTarget;
        const w = this.win;
        const sx = ev.clientX - w.x;
        const sy = ev.clientY - w.y;
        el.setPointerCapture(ev.pointerId);
        this.local.dragging = true;
        const move = (e) => {
            const b = this.bounds;
            let x = e.clientX - sx;
            let y = e.clientY - sy;
            const hh = !this.isPhone && this.store.minimized ? 48 : w.h;
            if (Math.abs(x - MARGIN) < SNAP) {
                x = MARGIN;
            }
            if (Math.abs(b.right - (x + w.w) - MARGIN) < SNAP) {
                x = b.right - w.w - MARGIN;
            }
            if (Math.abs(y - (b.top + MARGIN)) < SNAP) {
                y = b.top + MARGIN;
            }
            if (Math.abs(b.bottom - (y + hh) - MARGIN) < SNAP) {
                y = b.bottom - hh - MARGIN;
            }
            w.x = x;
            w.y = y;
            this.clamp(w, this.isPhone ? PHONE_MIN : DESKTOP_MIN);
            this.bump();
        };
        const up = () => {
            el.removeEventListener("pointermove", move);
            el.removeEventListener("pointerup", up);
            el.removeEventListener("pointercancel", up);
            this.local.dragging = false;
            saveGeom();
        };
        el.addEventListener("pointermove", move);
        el.addEventListener("pointerup", up);
        el.addEventListener("pointercancel", up);
    }

    // -- resize (8 handles) ---------------------------------------------------
    onResizePointerDown(ev) {
        ev.preventDefault();
        ev.stopPropagation();
        const el = ev.currentTarget;
        const dir = el.dataset.dir;
        const start = { ...this.win };
        const sx = ev.clientX;
        const sy = ev.clientY;
        const min = this.isPhone ? PHONE_MIN : DESKTOP_MIN;
        const w = this.win;
        el.setPointerCapture(ev.pointerId);
        this.local.dragging = true;
        const move = (e) => {
            const dx = e.clientX - sx;
            const dy = e.clientY - sy;
            let { x, y, w: ww, h } = start;
            if (dir.includes("e")) {
                ww = start.w + dx;
            }
            if (dir.includes("s")) {
                h = start.h + dy;
            }
            if (dir.includes("w")) {
                ww = start.w - dx;
                x = start.x + dx;
                if (ww < min.w) {
                    x = start.x + start.w - min.w;
                    ww = min.w;
                }
            }
            if (dir.includes("n")) {
                h = start.h - dy;
                y = start.y + dy;
                if (h < min.h) {
                    y = start.y + start.h - min.h;
                    h = min.h;
                }
            }
            Object.assign(w, { x, y, w: ww, h });
            this.clamp(w, min);
            this.bump();
        };
        const up = () => {
            el.removeEventListener("pointermove", move);
            el.removeEventListener("pointerup", up);
            el.removeEventListener("pointercancel", up);
            this.local.dragging = false;
            saveGeom();
        };
        el.addEventListener("pointermove", move);
        el.addEventListener("pointerup", up);
        el.addEventListener("pointercancel", up);
    }

    // -- phone bubble: drag anywhere, snap to a side; a tap re-opens the window -------
    onBubblePointerDown(ev) {
        ev.preventDefault();
        const el = ev.currentTarget;
        const p = this.bubble;
        const sx = ev.clientX - p.x;
        const sy = ev.clientY - p.y;
        let moved = false;
        el.setPointerCapture(ev.pointerId);
        const move = (e) => {
            const x = e.clientX - sx;
            const y = e.clientY - sy;
            if (Math.abs(x - p.x) > 4 || Math.abs(y - p.y) > 4) {
                moved = true;
            }
            p.x = x;
            p.y = y;
            this.bump();
        };
        const up = () => {
            el.removeEventListener("pointermove", move);
            el.removeEventListener("pointerup", up);
            el.removeEventListener("pointercancel", up);
            if (!moved) {
                this.store.mode = "mini";
                return;
            }
            const b = this.bounds;
            p.x = p.x + 28 < b.right / 2 ? MARGIN + 4 : b.right - 56 - MARGIN - 4;
            p.y = Math.min(Math.max(p.y, b.top + MARGIN), b.bottom - 56 - MARGIN);
            saveGeom();
            this.bump();
        };
        el.addEventListener("pointermove", move);
        el.addEventListener("pointerup", up);
        el.addEventListener("pointercancel", up);
    }

    // -- header actions -------------------------------------------------------
    toggleFollow() {
        this.store.follow = !this.store.follow;
        if (this.store.follow && this.store.split) {
            // catch up with the record the split panel shows now
            const { resModel, resId } = this.store.split;
            this.store.resModel = resModel;
            this.store.resId = resId;
        }
    }
    toggleMinimize() {
        this.store.minimized = !this.store.minimized;
    }
    dock() {
        // desktop split: back to the chatter inside the form panel, and stay docked until the
        // user floats it again (or another split opens)
        this.store.dockedByUser = true;
        hideChatter();
    }
    close() {
        hideChatter();
    }
    setMode(mode) {
        this.store.mode = mode;
    }
    async openRecord() {
        // phone, from a kanban card / list row: open the record; keep the window on it
        const { resModel, resId, onOpenRecord } = this.store;
        this._keepOnNextNav = true;
        this.store.source = "form";
        this.store.onOpenRecord = null;
        if (onOpenRecord) {
            await onOpenRecord();
            return;
        }
        this.action.doAction({
            type: "ir.actions.act_window",
            res_model: resModel,
            res_id: resId,
            views: [[false, "form"]],
        });
    }
}

registry.category("main_components").add("GlassChatterWindow", { Component: GlassChatterWindow });
