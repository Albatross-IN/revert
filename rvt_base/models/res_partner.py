from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    rvt_is_agency = fields.Boolean(
        string="Agency",
        help="A firm that does a trade's work on site. Its people are its contacts, each with a mobile number.")
    rvt_trade_ids = fields.Many2many(
        "rvt.trade", "rvt_partner_trade_rel", "partner_id", "trade_id", string="Trades")
