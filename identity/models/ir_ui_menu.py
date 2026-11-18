# -*- coding: utf-8 -*-
import logging

from odoo import api, models
from odoo.tools import BinaryBytes

from .identity_brand import custom_icon_path

_logger = logging.getLogger(__name__)


class IrUiMenu(models.Model):
    _inherit = 'ir.ui.menu'

    def _read_image(self, path):
        """Serve the Identity tile instead of the module's icon.png when one
        exists and custom icons are enabled."""
        if (not self.env.context.get('identity_skip_icons')
                and self.env['identity.brand']._params()['custom_icons']):
            custom = custom_icon_path(path)
            if custom:
                with open(custom, 'rb') as icon_file:
                    return BinaryBytes(icon_file.read())
        return super()._read_image(path)

    @api.model
    def _identity_refresh_icons(self):
        """Recompute ``web_icon_data`` for every menu carrying an image icon."""
        menus = self.sudo().search([('web_icon', '!=', False)])
        count = 0
        for menu in menus:
            if menu.web_icon and len(menu.web_icon.split(',')) == 2:
                menu.write({'web_icon': menu.web_icon})
                count += 1
        self.env.transaction.invalidate_ormcache()
        _logger.info("Identity: refreshed %d application icons", count)
