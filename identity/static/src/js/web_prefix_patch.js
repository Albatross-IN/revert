import { WEB_PREFIX } from "@web/core/browser/router";
import { registry } from "@web/core/registry";
import { patch } from "@web/core/utils/patch";
import { Many2One } from "@web/views/fields/many2one/many2one";
import { NavBar } from "@web/webclient/navbar/navbar";
import { WebClient } from "@web/webclient/webclient";

/**
 * Remaining places that build "/odoo/..." URLs outside the router.
 * (The router and menu helpers themselves are replaced, see __manifest__.py.)
 */
const STOCK_PREFIX_RE = /^\/odoo(?=$|[/?#])/;

export function toWebPrefix(href) {
    return typeof href === "string" ? href.replace(STOCK_PREFIX_RE, `/${WEB_PREFIX}`) : href;
}

if (WEB_PREFIX !== "odoo") {
    patch(NavBar.prototype, {
        getMenuItemHref(payload) {
            return toWebPrefix(super.getMenuItemHref(payload));
        },
    });

    patch(Many2One.prototype, {
        get linkHref() {
            return toWebPrefix(super.linkHref);
        },
    });

    patch(WebClient.prototype, {
        registerServiceWorker() {
            const container = navigator.serviceWorker;
            if (!container) {
                return super.registerServiceWorker();
            }
            // the stock implementation registers with { scope: "/odoo" }: shadow
            // `register` for the duration of the call to swap the scope
            const register = container.register.bind(container);
            container.register = (url, options) => register(url, { ...options, scope: `/${WEB_PREFIX}` });
            try {
                return super.registerServiceWorker();
            } finally {
                delete container.register;
            }
        },
    });

    // PWA service: start URL used for the "Install App" entry and install state
    const services = registry.category("services");
    if (services.contains("pwa")) {
        const pwa = services.get("pwa");
        const start = pwa.start;
        pwa.start = function (...args) {
            const state = start.apply(this, args);
            if (state && state.startUrl === "/odoo") {
                state.startUrl = `/${WEB_PREFIX}`;
            }
            return state;
        };
    }
}
