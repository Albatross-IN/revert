# -*- coding: utf-8 -*-
from lxml import etree

from odoo import api, models

from .identity_brand import custom_icon_url


class Base(models.AbstractModel):
    _inherit = 'base'

    @api.model
    def get_view(self, view_id=None, view_type='form', **options):
        result = super().get_view(view_id, view_type, **options)
        arch = result.get('arch')
        if not arch:
            return result
        Brand = self.env['identity.brand']
        brand = Brand.get()
        # 1. Settings sidebar logos: the client builds them from
        #    /<module>/static/description/icon.png; point them at our tiles.
        if (self._name == 'res.config.settings' and view_type == 'form'
                and brand['custom_icons'] and '<app ' in arch):
            root = etree.fromstring(arch)
            touched = False
            for app in root.iter('app'):
                icon = custom_icon_url(app.get('logo') or app.get('name'))
                if icon:
                    app.set('logo', icon)
                    touched = True
            if touched:
                arch = etree.tostring(root, encoding='unicode')
        # 2. Brand word in labels, help texts and placeholders.
        arch = Brand.debrand(arch, brand)
        result['arch'] = arch
        return result

    @api.model
    def get_views(self, views, options=None):
        result = super().get_views(views, options)
        Brand = self.env['identity.brand']
        brand = Brand.get()
        if not brand['replace_text']:
            return result
        for model_info in result.get('models', {}).values():
            for field in model_info.get('fields', {}).values():
                for key in ('string', 'help'):
                    if field.get(key) and 'Odoo' in field[key]:
                        field[key] = Brand.debrand(field[key], brand)
        return result
