import { TitlePlugin } from "@web/core/browser/title_plugin";
import { patch } from "@web/core/utils/patch";
import { session } from "@web/session";

/**
 * Browser tab title: "<action> - <brand>" instead of the bare action name.
 * Title parts are joined in insertion order, so the brand part is moved
 * back to the end whenever the parts change.  Without any part the title
 * is the server-rendered <title>, i.e. the brand (see webclient_templates.xml).
 */
const brandName = session.identity && session.identity.name;

if (brandName) {
    patch(TitlePlugin.prototype, {
        setParts(parts) {
            super.setParts(parts);
            const titleParts = this.titleParts();
            if (Object.keys(titleParts).some((key) => key !== "identity")) {
                delete titleParts.identity;
                titleParts.identity = brandName;
            } else {
                delete titleParts.identity;
            }
        },
    });
}
