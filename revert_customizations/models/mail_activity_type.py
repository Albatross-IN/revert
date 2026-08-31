from odoo import fields, models


class MailActivityType(models.Model):
    _inherit = 'mail.activity.type'

    is_mom = fields.Boolean(
        string='Minutes of Meeting',
        help="Activities of this type record a Minutes of Meeting point: they carry a "
             "Related To contact, a site photo and a serial number unique to the task."
    )
