from odoo import fields, models

SITE_KINDS = [
    ("home", "Home"),
    ("office", "Office"),
    ("clinic", "Clinic / hospital"),
    ("other", "Any site"),
]


class RvtEntityType(models.Model):
    _name = "rvt.entity.type"
    _description = "Entity type"
    _order = "sequence, id"

    name = fields.Char(required=True, translate=True)
    site_kind = fields.Selection(SITE_KINDS, string="Kind of site", required=True, default="other")
    trade_ids = fields.Many2many(
        "rvt.trade", "rvt_entity_type_trade_rel", "entity_type_id", "trade_id",
        string="Usual trades",
        help="Pre-ticked for an entity of this type at onboarding; the user unticks what does not apply.")
    is_whole_site = fields.Boolean(
        string="Whole site",
        help="Added to every project for work that belongs to no single room.")
    is_extra = fields.Boolean(
        string="Offered as an extra",
        help="Shown as a one-tap addition in the site configuration step.")
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)
