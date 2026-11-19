import secrets
from datetime import timedelta

from odoo import api, fields, models
from odoo.exceptions import AccessError, UserError, ValidationError

DRAWING_STATES = [
    ("to_draw", "To draw"),
    ("in_progress", "In progress"),
    ("awaiting_approval", "Awaiting approval"),
    ("approved", "Approved · to release"),
    ("released", "Released"),
]
REVISION_STATES = [
    ("draft", "Draft"),
    ("awaiting_approval", "Awaiting approval"),
    ("approved", "Approved"),
    ("released", "Released"),
    ("superseded", "Superseded"),
]


class RvtDrawing(models.Model):
    _name = "rvt.drawing"
    _description = "Drawing"
    _inherit = ["mail.thread", "rvt.live.mixin"]
    _order = "project_id, due_date, id"

    project_id = fields.Many2one("project.project", required=True, ondelete="cascade", index=True)
    type_id = fields.Many2one("rvt.drawing.type", string="Standard drawing", ondelete="set null")
    code = fields.Char(required=True, help="The sheet number is this code plus a running number per project.")
    number = fields.Integer(readonly=True, copy=False)
    sheet_no = fields.Char(string="Sheet", compute="_compute_sheet_no", store=True)
    name = fields.Char(string="Title", required=True, tracking=True)
    trade_id = fields.Many2one("rvt.trade", string="Trade", ondelete="restrict", index=True, help="Empty for the general set.")
    entity_id = fields.Many2one(
        "project.task", string="Room or zone", ondelete="set null",
        domain="[('project_id', '=', project_id), ('rvt_kind', '=', 'entity')]")
    designer_id = fields.Many2one("res.users", string="Designer", tracking=True, index=True)
    due_date = fields.Date(string="Due", tracking=True)
    for_client = fields.Boolean(string="For the client", tracking=True)
    needs_client_approval = fields.Boolean(string="Client must approve", tracking=True)
    state = fields.Selection(DRAWING_STATES, default="to_draw", required=True, index=True, tracking=True, copy=False)
    revision_ids = fields.One2many("rvt.drawing.revision", "drawing_id", string="Revisions", copy=False)
    current_revision_id = fields.Many2one(
        "rvt.drawing.revision", string="Current revision", compute="_compute_current_revision", store=True)
    released_revision_id = fields.Many2one(
        "rvt.drawing.revision", string="Released revision", compute="_compute_current_revision", store=True,
        help="What receivers see: the one released revision that is not superseded.")
    question_ids = fields.One2many("rvt.drawing.question", "drawing_id", string="Questions", copy=False)
    receiver_ids = fields.Many2many(
        "res.partner", "rvt_drawing_receiver_rel", "drawing_id", "partner_id", string="Receivers",
        compute="_compute_receivers", store=True,
        help="Who received the released revision. This is what gives an agency or the client its access.")
    client_released = fields.Boolean(
        string="Released to the client", compute="_compute_receivers", store=True,
        help="The released revision was sent to the client.")

    _project_code_number_uniq = models.Constraint(
        "unique (project_id, code, number)", "This sheet number is already on the project.")

    @api.depends("code", "number")
    def _compute_sheet_no(self):
        for drawing in self:
            drawing.sheet_no = "%s-%02d" % (drawing.code or "", drawing.number or 0)

    @api.depends("sheet_no", "name")
    def _compute_display_name(self):
        for drawing in self:
            drawing.display_name = "%s %s" % (drawing.sheet_no or "", drawing.name or "")

    @api.depends("revision_ids.number", "revision_ids.state")
    def _compute_current_revision(self):
        for drawing in self:
            revisions = drawing.revision_ids.sorted("number")
            drawing.current_revision_id = revisions[-1:]
            drawing.released_revision_id = revisions.filtered(lambda r: r.state == "released")[-1:]

    @api.depends("released_revision_id", "released_revision_id.receipt_ids.partner_id", "released_revision_id.receipt_ids.kind")
    def _compute_receivers(self):
        for drawing in self:
            receipts = drawing.released_revision_id.receipt_ids
            drawing.receiver_ids = receipts.partner_id
            drawing.client_released = any(r.kind == "client" for r in receipts)

    @api.constrains("for_client", "needs_client_approval")
    def _check_client_approval(self):
        for drawing in self:
            if drawing.needs_client_approval and not drawing.for_client:
                raise ValidationError(self.env._("Only a drawing shown to the client can need the client's approval."))

    @api.model_create_multi
    def create(self, vals_list):
        taken = {}
        for vals in vals_list:
            vals["code"] = (vals.get("code") or "AD").strip().upper()
            key = (vals.get("project_id"), vals["code"])
            if key not in taken:
                last = self.sudo().with_context(active_test=False).search(
                    [("project_id", "=", key[0]), ("code", "=", key[1])], order="number desc", limit=1)
                taken[key] = last.number
            taken[key] += 1
            vals["number"] = taken[key]
        drawings = super().create(vals_list)
        self.env["rvt.drawing.revision"].sudo().create([{"drawing_id": d.id, "number": 1} for d in drawings])
        drawings._rvt_designer_joins_team()
        return drawings

    def write(self, vals):
        res = super().write(vals)
        if vals.get("designer_id"):
            self._rvt_designer_joins_team()
        return res

    def _rvt_designer_joins_team(self):
        """A designer with a drawing on a project must see that project: the team is where
        access comes from, so the designer joins it."""
        for drawing in self.sudo():
            project, designer = drawing.project_id, drawing.designer_id
            if designer and designer not in project._rvt_team_users():
                project.rvt_designer_ids = [(4, designer.id)]

    # ------------------------------------------------------------------
    # who may
    # ------------------------------------------------------------------
    def _rvt_staff(self):
        """The caller is staff and may work on this drawing's project."""
        self.env["project.project"]._rvt_check_staff()
        self.check_access("write")

    def _rvt_may_approve(self):
        user = self.env.user
        return self.env.su or user.has_group("rvt_base.group_rvt_principal")

    # ------------------------------------------------------------------
    # the flow
    # ------------------------------------------------------------------
    def action_start(self):
        for drawing in self:
            drawing._rvt_staff()
            if drawing.state == "to_draw":
                drawing.state = "in_progress"
        return True

    def action_send_for_approval(self, file=None, file_name=None, note=None):
        """The designer attaches the PDF and sends it on. With "release needs approval" off,
        it is approved at once and the designer chooses the receivers next."""
        self.ensure_one()
        self._rvt_staff()
        if self.state not in ("to_draw", "in_progress"):
            raise UserError(self.env._("This drawing is already sent. Start a new revision to send it again."))
        revision = self.current_revision_id.sudo()
        if file:
            revision.write({"file": file, "file_name": file_name or "%s_rev%s.pdf" % (self.sheet_no, revision.number)})
        if not revision.file:
            raise UserError(self.env._("Choose the PDF first."))
        now = fields.Datetime.now()
        vals = {"sent_by_id": self.env.uid, "sent_on": now, "back_note": False}
        if note and note.strip():
            vals["note"] = note.strip()
        if self.env["rvt.config"].get("release_needs_approval"):
            revision.write(dict(vals, state="awaiting_approval"))
            self.state = "awaiting_approval"
            principal = self.project_id.sudo().rvt_principal_id
            if principal:
                self.env["rvt.notify"].send("drawing_approval_needed", self, principal)
        else:
            revision.write(dict(vals, state="approved", approved_by_id=self.env.uid, approved_on=now))
            self.state = "approved"
        return True

    def action_approve(self):
        self.ensure_one()
        self._rvt_staff()
        if not self._rvt_may_approve():
            raise AccessError(self.env._("Only the principal approves a release."))
        if self.state != "awaiting_approval":
            raise UserError(self.env._("This drawing is not waiting for approval."))
        self.current_revision_id.sudo().write({
            "state": "approved", "approved_by_id": self.env.uid, "approved_on": fields.Datetime.now()})
        self.state = "approved"
        return True

    def action_send_back(self, note):
        self.ensure_one()
        self._rvt_staff()
        if not self._rvt_may_approve():
            raise AccessError(self.env._("Only the principal sends a drawing back."))
        if self.state != "awaiting_approval":
            raise UserError(self.env._("This drawing is not waiting for approval."))
        if not (note or "").strip():
            raise UserError(self.env._("Say why it goes back."))
        self.current_revision_id.sudo().write({"state": "draft", "back_note": note.strip()})
        self.state = "in_progress"
        return True

    def rvt_receivers(self):
        """Who can receive this drawing: every agency on the project (the drawing's own trade
        first and ticked), and the client when the drawing is marked for the client."""
        self.ensure_one()
        project = self.project_id.sudo()
        plans = project.rvt_trade_plan_ids.filtered("agency_id")
        own = plans.filtered(lambda p: p.trade_id == self.trade_id).agency_id
        rows = []
        for agency in plans.agency_id.sorted(lambda a: (a != own, a.name)):
            mine = plans.filtered(lambda p: p.agency_id == agency)
            rows.append({
                "partner_id": agency.id, "name": agency.name, "kind": "agency",
                "trades": ", ".join(mine.mapped("trade_id.name")),
                "people": ", ".join(mine.contact_ids.mapped("name")),
                "own": agency == own, "ticked": agency == own,
            })
        if self.for_client and project.rvt_client_id:
            rows.append({
                "partner_id": project.rvt_client_id.id, "name": project.rvt_client_id.name, "kind": "client",
                "trades": "", "people": ", ".join(project.rvt_client_contact_ids.mapped("name")),
                "own": False, "ticked": True,
            })
        return rows

    def action_release(self, agency_ids=None, client=False):
        """Send the approved revision to its receivers. The revision before it is superseded;
        work lines that waited for this drawing are free again. Returns {"freed": n}."""
        self.ensure_one()
        self._rvt_staff()
        if self.state != "approved":
            raise UserError(self.env._("A drawing is released after it is approved."))
        project = self.project_id.sudo()
        agencies = self.env["res.partner"].sudo().browse(agency_ids or []).exists() & project.rvt_agency_ids
        to_client = bool(client and self.for_client and project.rvt_client_id)
        if not agencies and not to_client:
            raise UserError(self.env._("Choose at least one receiver."))
        revision = self.current_revision_id.sudo()
        now = fields.Datetime.now()
        self.revision_ids.sudo().filtered(lambda r: r.state == "released").write({"state": "superseded"})
        receipts = [{"revision_id": revision.id, "partner_id": a.id, "kind": "agency", "sent_on": now} for a in agencies]
        if to_client:
            receipts.append({"revision_id": revision.id, "partner_id": project.rvt_client_id.id, "kind": "client", "sent_on": now})
        receipts = self.env["rvt.drawing.receipt"].sudo().create(receipts)
        revision.write({
            "state": "released", "released_by_id": self.env.uid, "released_on": now,
            "client_decision": "pending" if to_client and self.needs_client_approval else False,
        })
        self.state = "released"
        self.flush_recordset(["receiver_ids", "client_released", "released_revision_id"])
        freed = self._rvt_free_waiting_lines(("drawing",))
        Notify = self.env["rvt.notify"]
        for receipt in receipts:
            Notify.send("drawing_released" if receipt.kind == "agency" else "drawing_client", receipt, receipt._rvt_people())
        return {"freed": len(freed)}

    def _rvt_free_waiting_lines(self, causes):
        lines = self.env["project.task"].sudo().search([
            ("rvt_wait_drawing_id", "in", self.ids), ("rvt_work_state", "=", "waiting"), ("rvt_wait_cause", "in", causes)])
        lines.write({"rvt_work_state": "not_started"})
        return lines

    def action_new_revision(self, note=None):
        """Start the next revision. Receivers keep seeing the released one until the new one goes out."""
        self.ensure_one()
        self._rvt_staff()
        if self.state != "released":
            raise UserError(self.env._("A new revision starts from a released drawing."))
        return self._rvt_add_revision(note, days=5)

    def _rvt_add_revision(self, note, days):
        revision = self.env["rvt.drawing.revision"].sudo().create({
            "drawing_id": self.id, "number": self.current_revision_id.number + 1, "note": (note or "").strip() or False})
        today = self.env["rvt.config"].today()
        self.sudo().write({"state": "in_progress", "due_date": max(self.due_date or today, today + timedelta(days=days))})
        return revision.id

    # ------------------------------------------------------------------
    # receivers: opening, the client's decision, questions
    # ------------------------------------------------------------------
    def rvt_open(self, partner):
        """Record that a receiver opened the released revision. True when this is the first time."""
        self.ensure_one()
        firm = partner.sudo().commercial_partner_id
        receipt = self.sudo().released_revision_id.receipt_ids.filtered(
            lambda r: r.partner_id == firm or r.partner_id == partner)
        return receipt[:1]._rvt_mark_opened() if receipt else False

    def rvt_client_decide(self, decision, note=None, partner=None):
        """The client's tap is the record: name, date and time. No signature."""
        self.ensure_one()
        revision = self.sudo().released_revision_id
        if not revision or revision.client_decision != "pending":
            raise UserError(self.env._("Nothing is waiting for the client's decision on this drawing."))
        if decision not in ("approved", "change"):
            raise UserError(self.env._("Approve the drawing, or ask for a change."))
        note = (note or "").strip()
        if decision == "change" and not note:
            raise UserError(self.env._("Say what should change."))
        partner = partner or self.env.user.partner_id
        revision.write({
            "client_decision": decision, "client_partner_id": partner.id, "client_decided_by": partner.name,
            "client_decided_on": fields.Datetime.now(), "client_note": note or False,
        })
        drawing = self.sudo()
        if decision == "approved":
            drawing._rvt_free_waiting_lines(("client",))
        else:
            drawing._rvt_add_revision(self.env._("Change asked by the client: %s", note), days=3)
        return True

    def rvt_ask(self, partner, text, photo=None, via="app", person_name=None):
        """A question on the drawing, from an agency or the client, or logged by staff from a call."""
        self.ensure_one()
        text = (text or "").strip()
        if not text:
            raise UserError(self.env._("Type the question."))
        question = self.env["rvt.drawing.question"].sudo().create({
            "drawing_id": self.id, "partner_id": partner.sudo().commercial_partner_id.id,
            "asked_by_name": person_name or partner.name, "via": via, "text": text, "photo": photo or False,
        })
        # the designer answers; the coordinators and the principal of the project see it too
        # (read as the system: the asker is an agency person or a client, who cannot read staff records)
        project = self.sudo().project_id
        staff = (self.sudo().designer_id | project.rvt_coordinator_ids | project.rvt_principal_id).filtered(
            lambda user: user.active and not user.share)
        if via == "office":
            staff -= self.env.user
        if staff:
            self.env["rvt.notify"].send("drawing_question", question, staff)
        return question.id

    def rvt_say(self, partner, text):
        """A line from the office in the conversation with one party about this drawing, when no
        question of theirs is waiting: it sits in the same thread as their questions and the answers."""
        self.ensure_one()
        self._rvt_staff()
        text = (text or "").strip()
        if not text:
            raise UserError(self.env._("Type the message first."))
        partner = partner.sudo().commercial_partner_id
        if not partner:
            raise UserError(self.env._("Choose who the message is for."))
        now = fields.Datetime.now()
        return self.env["rvt.drawing.question"].sudo().create({
            "drawing_id": self.id, "partner_id": partner.id, "asked_by_name": self.env.user.name, "via": "revert",
            "text": text, "asked_on": now, "answered_by_id": self.env.uid, "answered_on": now,
        }).id


class RvtDrawingRevision(models.Model):
    _name = "rvt.drawing.revision"
    _inherit = ["rvt.live.mixin"]
    _description = "Drawing revision"
    _order = "drawing_id, number"

    drawing_id = fields.Many2one("rvt.drawing", required=True, ondelete="cascade", index=True)
    project_id = fields.Many2one(related="drawing_id.project_id", store=True, index=True)
    number = fields.Integer(required=True, default=1)
    file = fields.Binary(string="PDF", attachment=True)
    file_name = fields.Char()
    note = fields.Char()
    back_note = fields.Char(string="Sent back because")
    state = fields.Selection(REVISION_STATES, default="draft", required=True, index=True)
    sent_by_id = fields.Many2one("res.users", string="Sent by")
    sent_on = fields.Datetime()
    approved_by_id = fields.Many2one("res.users", string="Approved by")
    approved_on = fields.Datetime()
    released_by_id = fields.Many2one("res.users", string="Released by")
    released_on = fields.Datetime(index=True)
    client_decision = fields.Selection(
        [("pending", "Pending"), ("approved", "Approved"), ("change", "Change asked")], string="Client's decision")
    client_partner_id = fields.Many2one("res.partner", string="Decided by (contact)")
    client_decided_by = fields.Char(string="Decided by")
    client_decided_on = fields.Datetime()
    client_note = fields.Char(string="Change asked")
    receipt_ids = fields.One2many("rvt.drawing.receipt", "revision_id", string="Sent to")

    _drawing_number_uniq = models.Constraint("unique (drawing_id, number)", "This revision number exists already.")

    @api.depends("drawing_id.sheet_no", "number")
    def _compute_display_name(self):
        for revision in self:
            revision.display_name = "%s rev %s" % (revision.drawing_id.sheet_no or "", revision.number)


class RvtDrawingReceipt(models.Model):
    _name = "rvt.drawing.receipt"
    _inherit = ["rvt.live.mixin"]
    _description = "Drawing sent to a receiver"
    _order = "revision_id, id"

    revision_id = fields.Many2one("rvt.drawing.revision", required=True, ondelete="cascade", index=True)
    drawing_id = fields.Many2one(related="revision_id.drawing_id", store=True, index=True)
    project_id = fields.Many2one(related="revision_id.drawing_id.project_id", store=True, index=True)
    partner_id = fields.Many2one(
        "res.partner", string="Receiver", required=True, ondelete="restrict", index=True,
        help="The agency (the firm) or the client.")
    kind = fields.Selection([("agency", "Agency"), ("client", "Client")], required=True, default="agency")
    sent_on = fields.Datetime()
    opened_on = fields.Datetime()
    token = fields.Char(
        required=True, index=True, copy=False, default=lambda self: secrets.token_urlsafe(24),
        groups="rvt_base.group_rvt_staff,base.group_system")

    _token_uniq = models.Constraint("unique (token)", "This link exists already.")

    def _rvt_mark_opened(self):
        self.ensure_one()
        if self.opened_on:
            return False
        self.sudo().opened_on = fields.Datetime.now()
        return True

    def _rvt_people(self):
        """The people who get the message: the agency's contact people on this project's
        trade plan, or the project's client contacts."""
        self.ensure_one()
        project = self.project_id.sudo()
        if self.kind == "client":
            return project.rvt_client_contact_ids
        plans = project.rvt_trade_plan_ids.filtered(lambda p: p.agency_id == self.partner_id)
        return plans.contact_ids or self.env["res.partner"].sudo().search([("parent_id", "=", self.partner_id.id)], order="id", limit=1)

    def rvt_link(self):
        self.ensure_one()
        return "%s/rvt/d/%s" % (self.get_base_url(), self.sudo().token)


class RvtDrawingQuestion(models.Model):
    _name = "rvt.drawing.question"
    _inherit = ["rvt.live.mixin"]
    _description = "Question on a drawing"
    _order = "asked_on desc, id desc"

    drawing_id = fields.Many2one("rvt.drawing", required=True, ondelete="cascade", index=True)
    project_id = fields.Many2one(related="drawing_id.project_id", store=True, index=True)
    partner_id = fields.Many2one("res.partner", string="Asked by", required=True, ondelete="restrict", index=True)
    asked_by_name = fields.Char(string="Person")
    via = fields.Selection(
        [("app", "The app"), ("office", "Logged from a call"), ("revert", "A message from the office")],
        default="app", required=True,
        help="A message from the office is a line Revert wrote to the party in the same conversation: "
             "it asks nothing, so it never waits for an answer.")
    text = fields.Text(required=True)
    photo = fields.Binary(attachment=True)
    asked_on = fields.Datetime(default=fields.Datetime.now, required=True)
    answer = fields.Text()
    answered_by_id = fields.Many2one("res.users", string="Answered by")
    answered_on = fields.Datetime()
    state = fields.Selection([("open", "Open"), ("answered", "Answered")], compute="_compute_state", store=True, index=True)

    @api.depends("answer", "via")
    def _compute_state(self):
        for question in self:
            question.state = "answered" if question.answer or question.via == "revert" else "open"

    def action_answer(self, text):
        self.ensure_one()
        self.drawing_id._rvt_staff()
        text = (text or "").strip()
        if not text:
            raise UserError(self.env._("Type the answer first."))
        if self.via == "revert":
            raise UserError(self.env._("That is a message from the office, not a question."))
        self.sudo().write({"answer": text, "answered_by_id": self.env.uid, "answered_on": fields.Datetime.now()})
        return True
