from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    rvt_invited_on = fields.Datetime(
        string="Invited to the app", copy=False,
        help="When this person was last sent the invitation to open the app with their number.")
