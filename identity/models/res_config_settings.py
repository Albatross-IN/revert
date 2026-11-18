# -*- coding: utf-8 -*-
from odoo import api, fields, models

from .identity_brand import WEB_PREFIX


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    identity_name = fields.Char(related='company_id.identity_name', readonly=False)
    identity_logo = fields.Binary(related='company_id.identity_logo', readonly=False)
    identity_icon = fields.Binary(related='company_id.identity_icon', readonly=False)
    identity_url = fields.Char(related='company_id.identity_url', readonly=False)
    identity_support_url = fields.Char(related='company_id.identity_support_url', readonly=False)
    identity_documentation_url = fields.Char(related='company_id.identity_documentation_url', readonly=False)
    identity_theme_color = fields.Char(related='company_id.identity_theme_color', readonly=False)
    identity_bot_name = fields.Char(related='company_id.identity_bot_name', readonly=False)
    identity_powered_by = fields.Boolean(related='company_id.identity_powered_by', readonly=False)

    identity_replace_text = fields.Boolean(
        "Replace the platform name in texts", config_parameter='identity.replace_text', default=True,
        help="Rewrites the platform name in client texts, rendered pages, e-mails and view labels.")
    identity_custom_icons = fields.Boolean(
        "Use Identity app icons", config_parameter='identity.custom_icons', default=True,
        help="Replace the stock application icons with the Identity icon set.")
    identity_hide_external_links = fields.Boolean(
        "Hide vendor links", config_parameter='identity.hide_external_links', default=True,
        help="Removes the vendor account and subscription entries, upgrade prompts and documentation links "
             "unless your own URLs are configured.")

    identity_web_prefix = fields.Char("Web client URL prefix", compute='_compute_identity_web_prefix')

    @api.depends('company_id')
    def _compute_identity_web_prefix(self):
        for settings in self:
            settings.identity_web_prefix = '/' + WEB_PREFIX

    def set_values(self):
        icp = self.env['ir.config_parameter'].sudo()
        icons_before = icp.get_bool('identity.custom_icons', True)
        super().set_values()
        if icp.get_bool('identity.custom_icons', True) != icons_before:
            self.env['ir.ui.menu']._identity_refresh_icons()
        # menus & assets cache the brand name through session_info / icons
        self.env.transaction.invalidate_ormcache()

    def action_identity_refresh_icons(self):
        self.env['ir.ui.menu']._identity_refresh_icons()
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }
