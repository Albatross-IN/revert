# Part of open_whatsapp_connector. Odoo 20 messaging-menu tab domains.

from odoo.fields import Domain

from odoo.addons.mail.controllers.discuss.messaging_menu import (
    DiscussMessagingMenuController,
)


class OwaMessagingMenuController(DiscussMessagingMenuController):
    def _get_menu_tab_domain(self, tab_id):
        if tab_id == "whatsapp":
            return Domain([
                ("channel_type", "=", "whatsapp"),
                ("self_member_id.is_pinned", "=", True),
            ])
        return super()._get_menu_tab_domain(tab_id)

    def _get_menu_tab_filter_domain(self, tab_id, filter_id):
        if tab_id == "whatsapp":
            if filter_id == "whatsapp_unread":
                return Domain("self_member_id.is_unread", "=", True)
            if filter_id == "whatsapp_dm":
                return Domain("whatsapp_kind", "in", ["dm", False])
            if filter_id == "whatsapp_group":
                return Domain("whatsapp_kind", "=", "group")
            if filter_id == "whatsapp_community":
                return Domain("whatsapp_kind", "=", "community")
            if filter_id == "whatsapp_channel":
                return Domain("whatsapp_kind", "=", "channel")
        return super()._get_menu_tab_filter_domain(tab_id, filter_id)
