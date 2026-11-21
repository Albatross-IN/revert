# -*- coding: utf-8 -*-
from urllib.parse import urlparse

from odoo import api, fields, models
from odoo.exceptions import ValidationError


class ResCompany(models.Model):
    _inherit = 'res.company'

    identity_name = fields.Char(
        'Brand Name',
        help="Replaces the platform name everywhere (titles, texts, footers). Defaults to the company name.")
    identity_logo = fields.Binary(
        'Brand Logo',
        help="Wordmark used in 'Powered by' footers, e-mails and as the login logo "
             "when the company has no logo of its own.")
    identity_icon = fields.Binary(
        'Brand Icon',
        help="Square icon (PNG, at least 512x512) used for the favicon, the mobile "
             "home-screen icon and the progressive web app.")
    identity_url = fields.Char('Brand Website', help="Target of the 'Powered by' links.")
    identity_support_url = fields.Char(
        'Support URL', help="Shown as 'Help' in the user menu. Leave empty to hide the entry.")
    identity_documentation_url = fields.Char(
        'Documentation URL',
        help="Base URL for the documentation links in Settings. Leave empty to hide them.")
    identity_theme_color = fields.Char(
        'Theme Color', default='#141A2C', help="Browser / PWA chrome colour (hex).")
    identity_bot_name = fields.Char('Bot Name', default='Assistant', help="Name of the built-in chat bot.")
    identity_powered_by = fields.Boolean(
        "Show 'Powered by'", default=True,
        help="Keep a 'Powered by <brand>' mention in footers. Untick to remove it entirely.")

    @api.constrains('identity_url', 'identity_support_url', 'identity_documentation_url')
    def _check_identity_urls(self):
        for company in self:
            for value in (company.identity_url, company.identity_support_url, company.identity_documentation_url):
                if value:
                    parsed = urlparse(value)
                    if parsed.scheme not in ('http', 'https') or not parsed.netloc:
                        raise ValidationError(self.env._("'%s' is not a valid URL. Use the form https://www.example.com", value))

    @api.constrains('identity_theme_color')
    def _check_identity_theme_color(self):
        for company in self:
            color = company.identity_theme_color
            if color and not (len(color) in (4, 7) and color.startswith('#')
                              and all(c in '0123456789abcdefABCDEF' for c in color[1:])):
                raise ValidationError(self.env._("Theme color must be a hex colour such as #141A2C."))

    def identity_brand(self):
        """Brand dictionary for this company (used by QWeb e-mail layouts)."""
        self.ensure_one()
        return self.env['identity.brand']._get(self)

    def write(self, vals):
        res = super().write(vals)
        if 'identity_bot_name' in vals or 'identity_icon' in vals:
            self.env['identity.brand'].with_context(identity_force_avatar='identity_icon' in vals)._sync_bot()
        return res
