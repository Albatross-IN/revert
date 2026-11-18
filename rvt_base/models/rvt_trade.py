from odoo import api, fields, models


class RvtTrade(models.Model):
    _name = "rvt.trade"
    _description = "Trade"
    _order = "sequence, id"

    name = fields.Char(required=True, translate=True)
    short_name = fields.Char(
        string="Short name", required=True, translate=True,
        help="Shown as the column heading of the work grid.")
    code = fields.Char(required=True, help="Stable key used by the app and by imports.")
    covers = fields.Char(translate=True, help="What this trade usually does on a site.")
    is_usual = fields.Boolean(
        string="Usually on a project", help="Pre-ticked in the trades step of onboarding.")
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)

    _code_uniq = models.Constraint("unique (code)", "A trade with this code already exists.")

    @api.model
    def _rvt_init_usual(self, codes):
        """Mark the usual trades once; later changes in Setup are kept."""
        if not self.with_context(active_test=False).search_count([("is_usual", "=", True)]):
            self.search([("code", "in", codes)]).write({"is_usual": True})
