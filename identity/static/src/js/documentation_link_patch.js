import { DocumentationLink } from "@web/views/widgets/documentation_link/documentation_link";
import { patch } from "@web/core/utils/patch";
import { session } from "@web/session";

const ABSOLUTE_RE = /^https?:\/\//;
// vendor site, and the version prefix of its documentation
const VENDOR_RE = /^https?:\/\/(?:[\w-]+\.)*odoo\.com(?=[/?#]|$)/;
const VENDOR_DOC_RE = /^https?:\/\/(?:www\.)?odoo\.com\/documentation\/[^/?#]+/;

/**
 * Documentation links: point at the brand documentation when configured,
 * hide them otherwise (instead of sending users to odoo.com).  Links given
 * as absolute odoo.com documentation URLs are mapped the same way; links to
 * third-party documentation (Google, payment providers...) are left alone.
 */
patch(DocumentationLink.prototype, {
    get url() {
        const identity = session.identity || {};
        const keepVendorLinks = identity.hide_external_links === false;
        let path = this.props.path || "";
        if (ABSOLUTE_RE.test(path)) {
            if (!VENDOR_RE.test(path)) {
                return path;
            }
            if (!VENDOR_DOC_RE.test(path)) {
                return keepVendorLinks ? path : "";
            }
            path = path.replace(VENDOR_DOC_RE, "");
        }
        if (identity.documentation_url) {
            return identity.documentation_url.replace(/\/+$/, "") + path;
        }
        return keepVendorLinks ? super.url : "";
    },
});
