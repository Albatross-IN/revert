import { Composer } from "@mail/core/common/composer";
import { usePlugin } from "@odoo/owl";
import { patch } from "@web/core/utils/patch";
import { ActionPlugin } from "@web/webclient/actions/action_plugin";

patch(Composer.prototype, {
    setup() {
        super.setup();
        this.action = usePlugin(ActionPlugin);
    },
    get isRevivingWhatsapp() {
        return this.action.id === "owa-revive-whatsapp-conversation";
    },
});
