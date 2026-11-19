from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

FOR_KINDS = [("agency", "An agency"), ("client", "The client"), ("vendor", "A vendor"), ("staff", "Revert staff")]
POINT_LOCK = 7482001    # the first key of the advisory lock that serialises numbering within a project


class RvtPoint(models.Model):
    _name = "rvt.point"
    _inherit = ["rvt.live.mixin"]
    _description = "Point"
    _order = "project_id, number desc, id desc"

    project_id = fields.Many2one("project.project", required=True, ondelete="cascade", index=True)
    visit_id = fields.Many2one(
        "rvt.visit", string="Visit", ondelete="set null", index=True,
        help="Empty for a point raised from the office.")
    number = fields.Integer(string="No", copy=False, help="Serial number of the point.")
    text = fields.Text(string="Point", required=True)
    for_kind = fields.Selection(FOR_KINDS, string="For", required=True, default="agency", index=True)
    partner_id = fields.Many2one(
        "res.partner", string="Party", ondelete="restrict", index=True,
        help="The agency (the firm), the client, or the vendor.")
    person_id = fields.Many2one("res.partner", string="Person", ondelete="set null", help="One of the agency's people.")
    user_id = fields.Many2one("res.users", string="Staff member", index=True)
    party_name = fields.Char(string="Named", help="A vendor known only by name.")
    trade_id = fields.Many2one("rvt.trade", string="Trade", ondelete="restrict", index=True)
    entity_id = fields.Many2one(
        "project.task", string="Room or zone", ondelete="set null", index=True,
        domain="[('project_id', '=', project_id), ('rvt_kind', '=', 'entity')]")
    drawing_id = fields.Many2one("rvt.drawing", string="Drawing", ondelete="set null")
    photo = fields.Binary(attachment=True, help="Kept as it was taken; nothing is resized.")
    has_photo = fields.Boolean(compute="_compute_has_photo", store=True)
    due_date = fields.Date(string="By", index=True)
    state = fields.Selection([("open", "Open"), ("closed", "Closed")], default="open", required=True, index=True)
    closed_by_id = fields.Many2one("res.users", string="Closed by")
    closed_by_partner_id = fields.Many2one(
        "res.partner", string="Marked done by", ondelete="set null",
        help="The agency's person who marked the point done from the app.")
    closed_on = fields.Date()
    close_note = fields.Text(string="Closing note")
    close_photo = fields.Binary(attachment=True)
    has_close_photo = fields.Boolean(compute="_compute_has_photo", store=True)
    client_confirmed = fields.Boolean(
        string="Confirmed for the client", default=True,
        help="A point for the client is shown to the client only once the office confirms it.")
    sent_count = fields.Integer(string="Times sent", copy=False)
    last_sent_on = fields.Datetime(copy=False)
    raised_by_id = fields.Many2one("res.users", string="Raised by", default=lambda self: self.env.user)
    raised_on = fields.Datetime(default=fields.Datetime.now)
    client_uid = fields.Char(
        string="Device id", copy=False, index=True,
        help="Given by the phone that wrote the point without network, so that sending it twice creates it once.")
    legacy_activity_id = fields.Integer(string="Earlier MOM entry", copy=False, index=True)
    legacy_task_id = fields.Many2one("project.task", string="Earlier task", ondelete="set null", copy=False)
    party_label = fields.Char(string="For whom", compute="_compute_party_label")

    _client_uid_uniq = models.UniqueIndex("(client_uid) WHERE client_uid IS NOT NULL", "This point was received already.")
    _legacy_uniq = models.UniqueIndex(
        "(legacy_activity_id) WHERE legacy_activity_id IS NOT NULL AND legacy_activity_id > 0",
        "This earlier MOM entry was moved already.")

    @api.depends("photo", "close_photo")
    def _compute_has_photo(self):
        for point in self.with_context(bin_size=True):
            point.has_photo = bool(point.photo)
            point.has_close_photo = bool(point.close_photo)

    @api.depends("for_kind", "partner_id", "user_id", "party_name")
    def _compute_party_label(self):
        for point in self:
            point.party_label = point._rvt_party_label()

    def _rvt_party_label(self):
        self.ensure_one()
        if self.for_kind == "staff":
            return self.user_id.name or self.env._("Office")
        if self.for_kind == "client":
            return self.partner_id.name or self.project_id.sudo().rvt_client_id.name or self.env._("Client")
        return self.partner_id.name or self.party_name or self.env._("Not named")

    @api.depends("number", "text")
    def _compute_display_name(self):
        for point in self:
            text = (point.text or "").strip().split("\n")[0]
            point.display_name = "%s · %s" % (point.number, text[:60]) if point.number else text[:60]

    @api.constrains("for_kind", "partner_id", "user_id")
    def _check_party(self):
        for point in self:
            if point.legacy_activity_id:
                continue
            if point.for_kind == "agency" and not point.partner_id:
                raise ValidationError(self.env._("Choose the agency this point is for."))
            if point.for_kind == "staff" and not point.user_id:
                raise ValidationError(self.env._("Choose the staff member this point is for."))

    @api.constrains("visit_id", "project_id")
    def _check_visit_project(self):
        for point in self:
            if point.visit_id and point.visit_id.project_id != point.project_id:
                raise ValidationError(self.env._("That visit belongs to another project."))

    # ------------------------------------------------------------------
    @api.model
    def _rvt_prepare(self, vals):
        """Defaults that follow from the project: the client, the agency's trade,
        the confirmation setting, the serial number."""
        vals = dict(vals)
        project = self.env["project.project"].sudo().browse(vals.get("project_id"))
        kind = vals.get("for_kind") or "agency"
        if kind == "client":
            if not vals.get("partner_id"):
                vals["partner_id"] = project.rvt_client_id.id
            if "client_confirmed" not in vals:
                vals["client_confirmed"] = not self.env["rvt.config"].get("client_points_need_confirmation")
        else:
            vals.setdefault("client_confirmed", True)
        if kind == "agency" and vals.get("partner_id") and not vals.get("trade_id"):
            plan = project.rvt_trade_plan_ids.filtered(lambda p: p.agency_id.id == vals["partner_id"])[:1]
            vals["trade_id"] = plan.trade_id.id
        if vals.get("entity_id") and not vals.get("trade_id") and kind == "agency":
            vals["trade_id"] = False
        return vals

    @api.model_create_multi
    def create(self, vals_list):
        vals_list = [self._rvt_prepare(v) if not v.get("legacy_activity_id") else dict(v) for v in vals_list]
        last = {}
        for vals in vals_list:
            if vals.get("number"):
                continue
            pid = vals.get("project_id")
            if pid not in last:
                # every project counts its own points from 1; two people writing at the same
                # moment wait for each other instead of taking the same number
                self.env.cr.execute("SELECT pg_advisory_xact_lock(%s, %s)", (POINT_LOCK, int(pid or 0)))
                top = self.sudo().search([("project_id", "=", pid)], order="number desc", limit=1)
                last[pid] = top.number
            last[pid] += 1
            vals["number"] = last[pid]
        return super().create(vals_list)

    # ------------------------------------------------------------------
    def _rvt_staff(self):
        self.env["project.project"]._rvt_check_staff()
        for project in self.project_id:
            project.check_access("read")

    @api.model
    def rvt_add(self, vals_list):
        """Write points, one or many. A point that carries a ``client_uid`` already
        received is returned as it is, so a phone can send the same batch twice."""
        self.env["project.project"]._rvt_check_staff()
        out = self.browse()
        allowed = {
            "project_id", "visit_id", "text", "for_kind", "partner_id", "person_id", "user_id", "party_name",
            "trade_id", "entity_id", "drawing_id", "photo", "due_date", "client_uid",
        }
        for vals in vals_list:
            uid = vals.get("client_uid")
            if uid:
                known = self.sudo().search([("client_uid", "=", uid)], limit=1)
                if known:
                    out |= known
                    continue
            project = self.env["project.project"].browse(vals.get("project_id")).exists()
            if not project:
                raise UserError(self.env._("Choose the project."))
            project.check_access("read")
            if not (vals.get("text") or "").strip():
                raise UserError(self.env._("Say what is needed."))
            clean = {k: v for k, v in vals.items() if k in allowed}
            clean["text"] = clean["text"].strip()
            out |= self.sudo().create(dict(clean, raised_by_id=self.env.uid))
        return out.ids

    def action_close(self, note=None, photo=None):
        """A point stays open until it is closed with a note or a photo."""
        self._rvt_staff()
        today = self.env["rvt.config"].today()
        for point in self.sudo().filtered(lambda p: p.state == "open"):
            point.write({
                "state": "closed", "closed_by_id": self.env.uid, "closed_on": today,
                "close_note": (note or "").strip() or False, "close_photo": photo or False,
            })
            point._rvt_after_close()
        return True

    def _rvt_after_close(self):
        """A line that waited for this point is free again."""
        lines = self.env["project.task"].sudo().search([
            ("rvt_wait_point_id", "=", self.id), ("rvt_work_state", "=", "waiting")])
        lines.write({"rvt_work_state": "not_started"})

    def action_reopen(self):
        """Not right yet: the point is open again, and the closing note and photo make room for the next ones."""
        self._rvt_staff()
        self.sudo().filtered(lambda p: p.state == "closed").write({
            "state": "open", "closed_by_id": False, "closed_by_partner_id": False, "closed_on": False,
            "close_note": False, "close_photo": False})
        return True

    def rvt_agency_done(self, note=None, photo=None, person=None):
        """The agency marks its own point done from the app, with a photo of the finished work.
        The point closes; the office is told and can open it again if the work is not right."""
        self.ensure_one()
        self.check_access("read")
        point = self.sudo()
        person = person or self.env.user.partner_id
        if point.for_kind != "agency" or point.partner_id != person.commercial_partner_id:
            raise UserError(self.env._("This point is not yours."))
        if point.state != "open":
            return True
        if not photo:
            raise UserError(self.env._("Add a photo of the finished work."))
        point.write({
            "state": "closed", "closed_on": self.env["rvt.config"].today(), "closed_by_partner_id": person.id,
            "close_note": (note or "").strip() or False, "close_photo": photo})
        point._rvt_after_close()
        project = point.project_id
        staff = point.raised_by_id | project.rvt_coordinator_ids
        staff = staff.filtered(lambda u: u.active and not u.share)
        if staff:
            self.env["rvt.notify"].send("point_done", point, staff, agency=point.partner_id.name, person=person.name)
        return True

    def action_confirm(self):
        """The office confirms a client point: the client sees it from now on and is told."""
        self._rvt_staff()
        for point in self.sudo().filtered(lambda p: p.for_kind == "client" and not p.client_confirmed):
            point.client_confirmed = True
            point._rvt_tell_client()
        return True

    def _rvt_tell_client(self):
        self.ensure_one()
        contacts = self.project_id.sudo().rvt_client_contact_ids
        if contacts and self.state == "open":
            sent = self.env["rvt.notify"].send("client_item", self, contacts)
            if sent:
                self.write({"sent_count": self.sent_count + 1, "last_sent_on": fields.Datetime.now()})

    def rvt_client_done(self, partner=None):
        """The client marks its own item as done."""
        self.ensure_one()
        point = self.sudo()
        if point.for_kind != "client" or not point.client_confirmed or point.state != "open":
            raise UserError(self.env._("This item is not open for you."))
        partner = partner or self.env.user.partner_id
        point.write({
            "state": "closed", "closed_on": self.env["rvt.config"].today(),
            "close_note": self.env._("Marked done by %s", partner.name)})
        point._rvt_after_close()
        return True

    def rvt_cell_line(self):
        """The work line of this point's room and trade, when it is the last open point there:
        the screen then offers "mark done"."""
        self.ensure_one()
        point = self.sudo()
        if not (point.entity_id and point.trade_id):
            return False
        line = self.env["project.task"].sudo().search([
            ("parent_id", "=", point.entity_id.id), ("rvt_kind", "=", "work"), ("rvt_trade_id", "=", point.trade_id.id)], limit=1)
        if not line or line.rvt_work_state == "done":
            return False
        others = self.sudo().search_count([
            ("project_id", "=", point.project_id.id), ("state", "=", "open"), ("id", "!=", point.id),
            ("entity_id", "=", point.entity_id.id), ("trade_id", "=", point.trade_id.id)])
        return False if others else line.id
