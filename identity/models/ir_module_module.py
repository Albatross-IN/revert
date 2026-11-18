# -*- coding: utf-8 -*-
from odoo import api, models
from odoo.tools import BinaryBytes

from .identity_brand import custom_icon_path, custom_icon_url

TEXT_FIELDS = ('summary', 'shortdesc', 'description', 'description_html')


class IrModuleModule(models.Model):
    _inherit = 'ir.module.module'

    @api.depends('icon')
    def _get_icon_image(self):
        super()._get_icon_image()
        if not self.env['identity.brand']._params()['custom_icons']:
            return
        for module in self:
            if not module.id:
                continue
            custom = custom_icon_path(module.icon or module.name)
            if custom:
                with open(custom, 'rb') as icon_file:
                    module.icon_image = BinaryBytes(icon_file.read())

    def _read_format(self, fnames, load='_classic_read'):
        """The Apps kanban shows ``icon`` (a URL) and the module summary:
        point the URL at the Identity tile, debrand the texts and drop the
        odoo.com 'Learn More' links.  ``_read_format`` backs both ``read``
        and ``search_read``."""
        result = super()._read_format(fnames, load=load)
        Brand = self.env['identity.brand']
        brand = Brand.get()
        wanted = set(fnames or [])
        do_icon = brand['custom_icons'] and (not wanted or 'icon' in wanted)
        do_text = brand['replace_text'] and (not wanted or wanted & set(TEXT_FIELDS))
        do_links = brand['hide_external_links'] and (not wanted or 'website' in wanted)
        if not (do_icon or do_text or do_links):
            return result
        names = {r['id']: r for r in result}
        for module in self:
            vals = names.get(module.id)
            if not vals:
                continue
            if do_icon and 'icon' in vals:
                custom = custom_icon_url(vals['icon'] or module.name)
                if custom:
                    vals['icon'] = custom
            if do_text:
                for fname in TEXT_FIELDS:
                    if vals.get(fname) and 'Odoo' in vals[fname]:
                        vals[fname] = Brand.debrand(vals[fname], brand)
            if do_links and vals.get('website') and 'odoo.com' in vals['website']:
                vals['website'] = False
        return result
