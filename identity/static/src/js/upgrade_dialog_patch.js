import { UpgradeDialog } from "@web/webclient/settings_form_view/fields/upgrade_dialog";
import { patch } from "@web/core/utils/patch";
import { session } from "@web/session";
import { browser } from "@web/core/browser/browser";

/**
 * Community "upgrade to Enterprise" dialog: open the brand website instead
 * of odoo.com/odoo-enterprise/upgrade.
 */
patch(UpgradeDialog.prototype, {
    async _confirmUpgrade() {
        const identity = session.identity || {};
        if (identity.hide_external_links === false) {
            return super._confirmUpgrade(...arguments);
        }
        if (identity.url) {
            browser.open(identity.url, "_blank");
        }
        this.props.close();
    },
});
