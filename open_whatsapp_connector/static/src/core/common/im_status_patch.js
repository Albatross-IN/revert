import { imStatusDataRegistry } from "@mail/core/common/im_status";

import { _t } from "@web/core/l10n/translation";

// Odoo 20 port: mail.ImStatus renders one <i> driven by the
// mail.im_status_data registry (the old template xpath on title='Bot' is
// gone). Show the WhatsApp brand icon for the channel's WhatsApp contact.
imStatusDataRegistry.add(
    "open_whatsapp_connector",
    {
        condition: ({ member }) =>
            Boolean(member && member.channel_id?.owaWhatsappMember?.eq(member)),
        icon: "oi_whatsapp",
        iconClass: "text-success",
        title: _t("WhatsApp User"),
    },
    { sequence: 80 }
);
