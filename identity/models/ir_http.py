# -*- coding: utf-8 -*-
from odoo import models

from .identity_brand import glyph_keys


class IrHttp(models.AbstractModel):
    _inherit = 'ir.http'

    def _identity_session_values(self):
        brand = self.env['identity.brand'].get()
        return {
            'identity': brand,
            # glyph-only icon files available for the CSS-mask rendering (see static/src/js/icons.js)
            'identity_glyphs': list(glyph_keys()) if brand['custom_icons'] else [],
            # the stock "Help" user-menu item reads this key
            'support_url': brand['support_url'] or False,
        }

    def session_info(self):
        result = super().session_info()
        result.update(self._identity_session_values())
        return result

    def get_frontend_session_info(self):
        result = super().get_frontend_session_info()
        result['identity'] = self.env['identity.brand'].get()
        return result
