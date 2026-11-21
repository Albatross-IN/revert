/** @odoo-module **/
/*
 * Identity — glyph icons.
 *
 * Every application icon ships as two files: the tile (`apps/<key>.svg`, what the menu's
 * `web_icon_data` holds) and the glyph alone (`apps/glyph/<key>.svg`). Where a template can
 * render a `<div class="o_identity_icon">` instead of the `<img>`, the two files are handed to
 * CSS as custom properties: the default stylesheet paints the tile file; a theme can paint the
 * tile itself and the glyph through `mask-image`, in any colour, with plain colour transitions.
 * The server publishes the available keys in the session (`identity_glyphs`).
 */
import { session } from "@web/session";

const TILE_DIR = "/identity/static/src/img/apps/";
const GLYPH_DIR = "/identity/static/src/img/apps/glyph/";
let keySet = null;

/**
 * @param {string} webIcon an ir.ui.menu `web_icon` value ("module,static/description/icon.png")
 * @returns {string|null} the icon key ("<module>__<basename>" or "<module>")
 */
export function identityIconKey(webIcon) {
    if (!webIcon || typeof webIcon !== "string") {
        return null;
    }
    if (!keySet) {
        keySet = new Set(session.identity_glyphs || []);
    }
    if (!keySet.size) {
        return null;
    }
    let module;
    let res;
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
    for (const key of [`${module}__${base}`, module]) {
        if (keySet.has(key)) {
            return key;
        }
    }
    return null;
}

/** The inline style carrying both files for a `.o_identity_icon` element, or null. */
export function identityIconStyle(webIcon) {
    const key = identityIconKey(webIcon);
    if (!key) {
        return null;
    }
    return `--identity-tile:url('${TILE_DIR}${key}.svg');--identity-glyph:url('${GLYPH_DIR}${key}.svg')`;
}
