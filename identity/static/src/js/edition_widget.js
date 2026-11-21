import { Component, useProps } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { session } from "@web/session";
import { Setting } from "@web/views/form/setting/setting";
import { standardWidgetProps } from "@web/views/widgets/standard_widget_props";

const { DateTime } = luxon;

/**
 * Replacement for the stock `res_config_edition` widget in Settings → About:
 * shows the brand and the platform version without Odoo S.A. links.
 */
export class IdentityEdition extends Component {
    static template = "identity.Edition";
    static components = { Setting };
    props = useProps({ ...standardWidgetProps });

    setup() {
        this.identity = session.identity || {};
        const info = session.server_version_info || [];
        this.serverVersion = info.length ? `${info[0]}.${info[1]}` : session.server_version || "";
        this.expirationDate = session.expiration_date
            ? DateTime.fromSQL(session.expiration_date).toLocaleString(DateTime.DATE_FULL)
            : false;
    }
}

registry.category("view_widgets").add("identity_edition", { component: IdentityEdition });
