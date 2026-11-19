from odoo import api, fields, models

STATES = [
    ("sent", "Sent"),
    ("held", "Held"),
    ("failed", "Failed"),
    ("no_number", "No number"),
    ("in_app", "In the app"),
]


class RvtNotifyLog(models.Model):
    _name = "rvt.notify.log"
    _inherit = ["rvt.live.mixin"]
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
    seen = fields.Boolean(help="The person opened their list of notifications after this one arrived.")

    @api.model
    def rvt_mine(self, limit=40):
        """The signed-in person's notifications, newest first, in the shape of the screens:
        staff read what was meant for them in the app; an agency person or a client contact
        reads what was sent to them."""
        user = self.env.user
        if user.has_group("rvt_base.group_rvt_staff"):
            domain = [("user_id", "=", user.id)]
        else:
            domain = [("partner_id", "=", user.partner_id.id), ("event", "!=", "otp")]
        config = self.env["rvt.config"]
        today = config.today()
        rows = []
        for log in self.sudo().search(domain, limit=limit):
            when = config.to_local(log.create_date)
            rows.append({
                "id": log.id, "ev": log.event, "text": log.text or "", "pid": log.project_id.id or None,
                "on": (when.date() - today).days, "at": "%s:%02d %s" % ((when.hour % 12) or 12, when.minute, "am" if when.hour < 12 else "pm"),
                "ref": log._rvt_ref(), "seen": log.seen,
            })
        return rows

    def _rvt_ref(self):
        """Where a tap on the notification leads: [kind, id] in the ids of the screens."""
        self.ensure_one()
        model, rid = self.res_model, self.res_id
        if not model or not rid:
            return None
        if model == "rvt.drawing":
            return ["dwg", "d%s" % rid]
        if model in ("rvt.drawing.question", "rvt.drawing.receipt", "rvt.drawing.revision"):
            record = self.env[model].sudo().browse(rid).exists()
            return ["dwg", "d%s" % record.drawing_id.id] if record else None
        if model == "rvt.point":
            return ["point", "pt%s" % rid]
        if model == "rvt.bill":
            return ["bill", "b%s" % rid]
        if model == "rvt.visit":
            return ["visit", "v%s" % rid]
        if model == "project.project":
            return ["proj", rid]
        return None

    @api.model
    def rvt_seen(self):
        """The person opened the list: what is in it is no longer new."""
        user = self.env.user
        if user.has_group("rvt_base.group_rvt_staff"):
            domain = [("user_id", "=", user.id)]
        else:
            domain = [("partner_id", "=", user.partner_id.id)]
        # nobody else's screen shows this mark, so the open screens are not asked to read again
        self.sudo().with_context(rvt_quiet=True).search(domain + [("seen", "=", False)]).write({"seen": True})
        return True
