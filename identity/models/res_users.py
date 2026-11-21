# -*- coding: utf-8 -*-
from markupsafe import Markup

from odoo import models


class ResUsers(models.Model):
    _inherit = 'res.users'

    def _init_odoobot(self):
        """The bot's welcome message is posted once per user (at first
        web-client load): debrand it right after it is created."""
        channel = super()._init_odoobot()
        Brand = self.env['identity.brand']
        if channel and Brand.get()['replace_text']:
            root_id = self.env['ir.model.data']._xmlid_to_res_id('base.partner_root')
            message = self.env['mail.message'].sudo().search([
                ('model', '=', 'discuss.channel'), ('res_id', '=', channel.id),
                ('author_id', '=', root_id)], order='id desc', limit=1)
            if message and 'Odoo' in (message.body or ''):
                message.body = Markup(Brand.debrand(str(message.body)))
        return channel
