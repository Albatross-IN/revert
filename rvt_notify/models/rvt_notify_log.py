from odoo import fields, models

STATES = [
    ("sent", "Sent"),
    ("held", "Held"),
    ("failed", "Failed"),
    ("no_number", "No number"),
    ("in_app", "In the app"),
]


class RvtNotifyLog(models.Model):
    _name = "rvt.notify.log"
    _description = "Message log"
    _order = "id desc"

    event = fields.Char(required=True, index=True)
    partner_id = fields.Many2one("res.partner", string="To", ondelete="set null", index=True)
    user_id = fields.Many2one("res.users", string="To (staff)", ondelete="set null")
    name = fields.Char(string="Name")
    phone = fields.Char()
    lang = fields.Char(string="Language")
    text = fields.Text()
    document = fields.Char(help="The name of the file sent with the message.")
    state = fields.Selection(STATES, required=True, index=True)
    reason = fields.Char(help="Why a message was held or failed.")
    project_id = fields.Many2one("project.project", ondelete="set null", index=True)
    res_model = fields.Char(string="About (model)")
    res_id = fields.Integer(string="About (id)")
    sent_by_id = fields.Many2one("res.users", string="Sent by", default=lambda self: self.env.user)
