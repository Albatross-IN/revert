from odoo import api, fields, models


class RvtDrawingType(models.Model):
    _name = "rvt.drawing.type"
    _description = "Standard drawing"
    _order = "sequence, id"

    name = fields.Char(required=True, translate=True)
    code = fields.Char(required=True, help="Sheet numbers are this code plus a running number per project (EL-01).")
    trade_id = fields.Many2one(
        "rvt.trade", string="Trade", ondelete="restrict", index=True,
        help="Empty for the general set that every project gets.")
    for_client = fields.Boolean(string="Shown to the client")
    needs_client_approval = fields.Boolean(string="Client must approve")
    due_offset = fields.Integer(
        string="Due after (days)", default=7,
        help="Proposed due date, counted from the day the project is onboarded.")
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)

    _code_uniq = models.Constraint("unique (code)", "A standard drawing with this code already exists.")

    @api.depends("code", "name")
    def _compute_display_name(self):
        for rec in self:
            rec.display_name = f"{rec.code} · {rec.name}" if rec.code else rec.name
