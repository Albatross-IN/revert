import {
    MENU_TABS,
    MessagingMenu,
} from "@mail/core/public_web/messaging_menu/messaging_menu_model";
import { fields } from "@mail/model/export";

import { _t } from "@web/core/l10n/translation";
import { patch } from "@web/core/utils/patch";

// Odoo 20 port: the sidebar/messaging-menu is organized by MENU_TABS records
// (DiscussAppCategory is gone). The v19 per-kind sidebar sections map to tab
// FILTERS; the server-side counterpart domains live in
// controllers/messaging_menu.py. (#wa-sidebar-sections)
MENU_TABS.WHATSAPP = "whatsapp";

patch(MessagingMenu.prototype, {
    setup() {
        super.setup(...arguments);
        this.whatsappTab = fields.One("MessagingMenuTab", {
            compute() {
                if (this.store.self_user?.share !== false) {
                    return null;
                }
                return {
                    id: MENU_TABS.WHATSAPP,
                    icon: "oi_whatsapp",
                    sequence: 80,
                    label: _t("WhatsApp"),
                    emptyState: {
                        title: _t("No WhatsApp conversations yet."),
                    },
                    filters: [
                        {
                            id: "whatsapp_unread",
                            text: _t("Unread"),
                            includesChannel: (c) =>
                                Boolean(c.importantCounter ?? c.needactionCounter),
                        },
                        {
                            id: "whatsapp_dm",
                            text: _t("Chats"),
                            includesChannel: (c) => !c.whatsapp_kind || c.whatsapp_kind === "dm",
                        },
                        {
                            id: "whatsapp_group",
                            text: _t("Groups"),
                            includesChannel: (c) => c.whatsapp_kind === "group",
                        },
                        {
                            id: "whatsapp_community",
                            text: _t("Communities"),
                            includesChannel: (c) => c.whatsapp_kind === "community",
                        },
                        {
                            id: "whatsapp_channel",
                            text: _t("Channels"),
                            includesChannel: (c) => c.whatsapp_kind === "channel",
                        },
                    ],
                    includesChannel: (c) =>
                        c.channel_type === "whatsapp" &&
                        (c.self_member_id?.is_pinned || c.isLocallyPinned),
                    recordType: "discuss.channel",
                };
            },
            eager: true,
        });
    },
});
