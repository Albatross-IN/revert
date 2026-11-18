import { BusPlugin } from "@bus/services/bus_plugin";
import { Component, onWillUnmount, usePlugin, useProps } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { standardWidgetProps } from "@web/views/widgets/standard_widget_props";

export class OwaCampaignBusListener extends Component {
    props = useProps(standardWidgetProps);
    static template = "open_whatsapp_connector.OwaCampaignBusListener";

    setup() {
        const busService = usePlugin(BusPlugin);
        let active = true;
        const handler = ({ id }) => {
            if (!active) {
                return;
            }
            const record = this.props.record;
            if (record && record.resId === id) {
                record.load();
            }
        };
        busService.subscribe("owa.campaign/refresh", handler);
        busService.start();
        onWillUnmount(() => {
            active = false;
        });
    }
}

registry.category("view_widgets").add("owa_campaign_bus_listener", {
    component: OwaCampaignBusListener,
});
