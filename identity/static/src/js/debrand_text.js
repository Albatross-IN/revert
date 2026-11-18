/**
 * Identity — client-side brand replacement.
 *
 * In Odoo 20 every translatable string, whether it comes from `_t()` or from
 * the text nodes of an OWL template (`appTranslateFn`), is resolved through
 * `LazyTranslatedString.translate()`: eager strings call it directly, lazy
 * ones through `valueOf()` / `toString()`.  Patching that single method
 * rewrites the brand everywhere the client renders text, in the backend as
 * well as on the website / portal.  Markup values are re-wrapped so they stay
 * trusted HTML.
 */
import { markup } from "@odoo/owl";
import { LazyTranslatedString } from "@web/core/l10n/translation";
import { isMarkup } from "@web/core/utils/html";
import { patch } from "@web/core/utils/patch";
import { session } from "@web/session";

const identity = session.identity || {};
const brandName = identity.name || "";
const botName = identity.bot_name || "";
const enabled = Boolean(brandName) && identity.replace_text !== false;

export function debrandText(value) {
    if (!enabled || value == null) {
        return value;
    }
    const str = String(value);
    if (!str.includes("Odoo")) {
        return value;
    }
    const out = str.replace(/OdooBot/g, botName).replace(/Odoo/g, brandName);
    return isMarkup(value) ? markup(out) : out;
}

if (enabled) {
    patch(LazyTranslatedString.prototype, {
        translate() {
            return debrandText(super.translate());
        },
    });
}
