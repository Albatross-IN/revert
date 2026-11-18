# -*- coding: utf-8 -*-
from markupsafe import Markup

from odoo import models

from .identity_brand import ASSET_REWRITES, rewrite_prefix_in_html


class IrQWeb(models.AbstractModel):
    _inherit = 'ir.qweb'

    def _render(self, template, values=None, **options):
        """Post-process every server-rendered page / e-mail / report:
        rewrite stock Odoo image assets and the brand word."""
        result = super()._render(template, values, **options)
        if (self.env.context.get('identity_skip_text')
                # website / mass-mailing editors: never rewrite what the user
                # is about to save back
                or options.get('inherit_branding') or options.get('inherit_branding_auto')
                or self.env.context.get('inherit_branding')):
            return result
        text = str(result)
        changed = False
        if '/web/static/img/' in text:
            for old, new in ASSET_REWRITES:
                if old in text:
                    text = text.replace(old, new)
                    changed = True
        if '/odoo' in text:
            new_text = rewrite_prefix_in_html(text)
            if new_text != text:
                text = new_text
                changed = True
        if 'Odoo' in text:
            brand_model = self.env['identity.brand']
            new_text = brand_model.debrand(text)
            if new_text is not text:
                text = new_text
                changed = True
        return Markup(text) if changed else result
