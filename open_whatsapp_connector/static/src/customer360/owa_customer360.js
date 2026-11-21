/** @odoo-module **/

import { Component, onMounted, proxy, usePlugin, useProps } from "@odoo/owl";
import { NotificationPlugin } from "@web/core/notifications/notification_plugin";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { _t } from "@web/core/l10n/translation";
import { ActionPlugin, standardActionServiceProps } from "@web/webclient/actions/action_plugin";

export class OwaCustomer360 extends Component {
    static template = "open_whatsapp_connector.OwaCustomer360";
    props = useProps({ ...standardActionServiceProps });

    setup() {
        this.orm = useService("orm");
        this.action = usePlugin(ActionPlugin);
        this.notification = usePlugin(NotificationPlugin);
        this.state = proxy({
            loading: true,
            partner: null,
            events: [],
            total: 0,
            error: null,
        });
        this.partnerId = this.props?.action?.context?.default_partner_id
            || this.props?.action?.context?.partner_id;
        onMounted(() => this.load());
    }

    async load() {
        if (!this.partnerId) {
            this.state.error = _t("No partner specified.");
            this.state.loading = false;
            return;
        }
        this.state.loading = true;
        try {
            const data = await this.orm.call(
                "owa.customer360", "get_timeline_data",
                [this.partnerId],
            );
            this.state.partner = data.partner;
            this.state.events = data.events || [];
            this.state.total = data.total || 0;
        } catch (e) {
            this.state.error = String(e.message || e);
        } finally {
            this.state.loading = false;
        }
    }

    open(ev) {
        if (!ev.model || !ev.res_id) {
            return;
        }
        this.action.doAction({
            type: "ir.actions.act_window",
            res_model: ev.model,
            res_id: ev.res_id,
            views: [[false, "form"]],
            target: "current",
        });
    }
}

registry.category("actions").add("owa_customer360", OwaCustomer360);
