"""A bill of an agency, and the payments recorded against it."""
import base64

from odoo import api, fields, models
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.tools.mimetypes import guess_mimetype

STATES = [
    ("asked", "Asked"), ("submitted", "Submitted"), ("returned", "Returned"),
    ("accepted", "Accepted"), ("part_paid", "Part paid"), ("paid", "Paid"),
]
BILLED_TO = [("client", "The client"), ("revert", "Revert")]
MODES = [("bank", "Bank transfer"), ("upi", "UPI"), ("cheque", "Cheque"), ("cash", "Cash")]
# amounts are the owner's: no other group reads or writes these fields
MONEY = "rvt_base.group_rvt_acc_money,base.group_system"
DOCUMENTS = ("application/pdf", "image/jpeg", "image/png", "image/webp", "image/heic", "image/heif")
MAX_DOCUMENT = 15 * 1024 * 1024
CENT = 0.005


def rupees(amount):
    """1,85,000 as it is written in India."""
    digits = str(int(round(amount or 0)))
    head, tail = digits[:-3], digits[-3:]
    groups = []
    while len(head) > 2:
        groups.insert(0, head[-2:])
        head = head[:-2]
    if head:
        groups.insert(0, head)
    return "₹" + ",".join(groups + [tail])


class RvtBill(models.Model):
    _name = "rvt.bill"
    _inherit = ["rvt.live.mixin"]
    _description = "Bill of an agency"
    _order = "asked_on desc, id desc"

    project_id = fields.Many2one("project.project", required=True, ondelete="cascade", index=True)
    agency_id = fields.Many2one("res.partner", string="Agency", required=True, ondelete="restrict", index=True)
    trade_id = fields.Many2one("rvt.trade", required=True, ondelete="restrict")
    what = fields.Char(string="What the bill is for", required=True)
    asked_by_id = fields.Many2one("res.users", string="Asked by", default=lambda self: self.env.user, readonly=True)
    asked_on = fields.Date(default=lambda self: self.env["rvt.config"].today(), readonly=True)
    up_to_amount = fields.Float(string="Asked up to", digits=(16, 2), groups=MONEY)
    billed_to = fields.Selection(BILLED_TO, required=True, default="client")
    state = fields.Selection(STATES, required=True, default="asked", index=True, readonly=True)
    bill_number = fields.Char()
    bill_date = fields.Date()
    amount = fields.Float(digits=(16, 2), groups=MONEY)
    document = fields.Binary(attachment=True, help="A photo or a PDF of the bill.")
    document_name = fields.Char()
    has_document = fields.Boolean(compute="_compute_has_document")
    submitted_on = fields.Date(readonly=True)
    uploaded_by_id = fields.Many2one("res.users", readonly=True)
    return_reason = fields.Char()
    payment_ids = fields.One2many("rvt.bill.payment", "bill_id", groups=MONEY)
    paid_amount = fields.Float(digits=(16, 2), compute="_compute_paid", compute_sudo=True, groups=MONEY)
    balance = fields.Float(digits=(16, 2), compute="_compute_paid", compute_sudo=True, groups=MONEY)

    @api.depends("agency_id", "what")
    def _compute_display_name(self):
        for bill in self:
            bill.display_name = "%s · %s" % (bill.agency_id.name or "", bill.what or "")

    @api.depends("document")
    def _compute_has_document(self):
        for bill in self.with_context(bin_size=True):
            bill.has_document = bool(bill.document)

    @api.depends("payment_ids.amount", "amount")
    def _compute_paid(self):
        for bill in self:
            bill.paid_amount = sum(bill.payment_ids.mapped("amount"))
            bill.balance = (bill.amount or 0.0) - bill.paid_amount

    # ------------------------------------------------------------------
    # who may do what
    # ------------------------------------------------------------------
    def _rvt_is_owner(self):
        user = self.env.user
        return self.env.su or user.has_group("rvt_base.group_rvt_acc_money") or user.has_group("base.group_system")

    def _rvt_staff(self):
        """Staff act on a bill of a project they may see."""
        self.env["project.project"]._rvt_check_staff()
        self.check_access("write")

    def _rvt_tell(self, event, **values):
        """A message to the agency's people on this project."""
        for bill in self:
            project = bill.project_id
            people = project._rvt_people_of(bill.sudo().agency_id)
            self.env["rvt.notify"].send(event, bill, people, what=bill.what, **values)

    def _rvt_tell_office(self, event, **values):
        """A line in the app of the project's coordinators (and whoever asked)."""
        for bill in self:
            users = bill.project_id.sudo().rvt_coordinator_ids | bill.sudo().asked_by_id
            users = users.filtered(lambda u: u.active and u != self.env.user)
            self.env["rvt.notify"].send(event, bill, users, what=bill.what, agency=bill.sudo().agency_id.name, **values)

    @api.model
    def _rvt_document(self, data, name=None):
        """A bill's photo or PDF as it arrives (base64): checked for size and kind."""
        if not data:
            return {}
        try:
            raw = base64.b64decode(data, validate=False)
        except Exception as error:  # noqa: BLE001
            raise UserError(self.env._("That file could not be read.")) from error
        if len(raw) > MAX_DOCUMENT:
            raise UserError(self.env._("That file is larger than 15 MB."))
        kind = guess_mimetype(raw, default="")
        if kind not in DOCUMENTS:
            raise UserError(self.env._("A bill is a photo or a PDF."))
        extension = {"application/pdf": "pdf", "image/png": "png", "image/webp": "webp"}.get(kind, "jpg")
        return {"document": data, "document_name": name or "bill.%s" % extension}

    # ------------------------------------------------------------------
    # the four acts
    # ------------------------------------------------------------------
    @api.model
    def rvt_ask(self, project_id, agency_id, what, trade_code=None, up_to=None, billed_to=None):
        """The office asks an agency of the project for a bill. Nothing else starts one."""
        Project = self.env["project.project"]
        Project._rvt_check_staff()
        project = Project.browse(int(project_id or 0)).exists()
        if not project:
            raise UserError(self.env._("Choose the project."))
        project.check_access("read")
        what = (what or "").strip()
        plans = project.sudo().rvt_trade_plan_ids.filtered(lambda p: p.agency_id.id == int(agency_id or 0))
        if not plans or not what:
            raise UserError(self.env._("Choose an agency of this project, and say what the bill is for."))
        plan = plans.filtered(lambda p: p.trade_id.code == trade_code)[:1] or plans[:1]
        if billed_to not in dict(BILLED_TO):
            billed_to = project.rvt_billed_to_default or "client"
        bill = self.create({
            "project_id": project.id, "agency_id": plan.agency_id.id, "trade_id": plan.trade_id.id,
            "what": what, "billed_to": billed_to,
        })
        ceiling = float(up_to or 0)
        if ceiling > 0:
            bill.sudo().up_to_amount = ceiling
        bill._rvt_tell("bill_asked")
        return bill

    def rvt_upload(self, number, amount, document=None, document_name=None, bill_date=None):
        """The agency uploads its bill against the request; the office may do it on its behalf."""
        self.ensure_one()
        user = self.env.user
        bill = self.sudo()
        is_staff = user.has_group("rvt_base.group_rvt_staff") or user.has_group("base.group_system") or self.env.su
        if is_staff:
            self._rvt_staff()
        elif not (user.has_group("rvt_base.group_rvt_agency") and bill.agency_id == user.partner_id.commercial_partner_id):
            raise AccessError(self.env._("This bill is not yours."))
        if bill.state not in ("asked", "returned"):
            raise UserError(self.env._("This bill is already with the office."))
        try:
            amount = float(amount or 0)
        except (TypeError, ValueError):
            amount = 0.0
        if amount <= 0:
            raise UserError(self.env._("Enter the bill amount."))
        today = self.env["rvt.config"].today()
        vals = {
            "bill_number": (number or "").strip() or False, "amount": amount,
            "bill_date": bill_date or today, "state": "submitted", "submitted_on": today,
            "uploaded_by_id": user.id, "return_reason": False,
        }
        vals.update(self._rvt_document(document, document_name))
        bill.write(vals)
        if not is_staff:
            self._rvt_tell_office("bill_submitted")
        return True

    def rvt_review(self, accept, reason=None):
        """The office accepts a submitted bill, or returns it with the reason."""
        self.ensure_one()
        self._rvt_staff()
        if self.state != "submitted":
            raise UserError(self.env._("Only a submitted bill is reviewed."))
        if accept:
            self.write({"state": "accepted", "return_reason": False})
            self._rvt_tell("bill_accepted")
        else:
            reason = (reason or "").strip()
            if not reason:
                raise UserError(self.env._("Say why it is returned."))
            self.write({"state": "returned", "return_reason": reason})
            self._rvt_tell("bill_returned", reason=reason)
        return True

    def rvt_set_billed_to(self, billed_to):
        self.ensure_one()
        self._rvt_staff()
        if billed_to not in dict(BILLED_TO):
            raise UserError(self.env._("Billed to the client, or to Revert."))
        if self.state == "paid":
            raise UserError(self.env._("A paid bill is not changed."))
        self.billed_to = billed_to
        return True

    def rvt_pay(self, amount, paid_by, mode="bank", proof=None, proof_name=None, date=None):
        """The owner records a payment against an accepted bill. Part payments add up to the bill."""
        self.ensure_one()
        self.env["project.project"]._rvt_check_staff()
        if not self._rvt_is_owner():
            raise AccessError(self.env._("Payments are recorded by the owner."))
        self.check_access("write")
        try:
            amount = float(amount or 0)
        except (TypeError, ValueError):
            amount = 0.0
        payment = self.env["rvt.bill.payment"].create(dict({
            "bill_id": self.id, "amount": amount, "paid_by": paid_by if paid_by in dict(BILLED_TO) else self.billed_to,
            "mode": mode if mode in dict(MODES) else "bank", "date": date or self.env["rvt.config"].today(),
        }, **self.env["rvt.bill.payment"]._rvt_proof(proof, proof_name)))
        self._rvt_tell("bill_paid", state=dict(STATES)[self.state])
        return payment

    def _rvt_settle(self):
        """The state follows the payments: part paid until they add up to the bill."""
        for bill in self.sudo():
            if bill.state not in ("accepted", "part_paid", "paid"):
                continue
            paid = sum(bill.payment_ids.mapped("amount"))
            state = "accepted" if paid < CENT else "paid" if paid >= (bill.amount or 0) - CENT else "part_paid"
            if bill.state != state:
                bill.state = state


class RvtBillPayment(models.Model):
    _name = "rvt.bill.payment"
    _inherit = ["rvt.live.mixin"]
    _description = "Payment against a bill"
    _order = "date, id"

    # required: a payment exists only against a bill, so there are no advances
    bill_id = fields.Many2one("rvt.bill", required=True, ondelete="cascade", index=True)
    project_id = fields.Many2one(related="bill_id.project_id", store=True, index=True)
    date = fields.Date(required=True, default=lambda self: self.env["rvt.config"].today())
    amount = fields.Float(digits=(16, 2), required=True)
    paid_by = fields.Selection(BILLED_TO, string="Paid by", required=True, default="client")
    mode = fields.Selection(MODES, required=True, default="bank")
    proof = fields.Binary(attachment=True)
    proof_name = fields.Char()
    has_proof = fields.Boolean(compute="_compute_has_proof")

    @api.depends("proof")
    def _compute_has_proof(self):
        for payment in self.with_context(bin_size=True):
            payment.has_proof = bool(payment.proof)

    @api.model
    def _rvt_proof(self, data, name=None):
        if not data:
            return {}
        checked = self.env["rvt.bill"]._rvt_document(data, name)
        return {"proof": checked["document"], "proof_name": name or checked["document_name"].replace("bill.", "proof.")}

    @api.constrains("amount", "bill_id")
    def _check_against_the_bill(self):
        for payment in self:
            bill = payment.bill_id.sudo()
            if payment.amount <= 0:
                raise ValidationError(self.env._("Enter the amount paid."))
            if bill.state not in ("accepted", "part_paid", "paid"):
                raise ValidationError(self.env._("A payment is recorded against an accepted bill."))
            paid = sum(bill.payment_ids.mapped("amount"))
            if paid > (bill.amount or 0) + CENT:
                balance = (bill.amount or 0) - (paid - payment.amount)
                raise ValidationError(self.env._("That is more than the balance of %s.", rupees(balance)))

    @api.model_create_multi
    def create(self, vals_list):
        payments = super().create(vals_list)
        payments.bill_id._rvt_settle()
        return payments

    def write(self, vals):
        bills = self.bill_id
        res = super().write(vals)
        (bills | self.bill_id)._rvt_settle()
        return res

    def unlink(self):
        bills = self.bill_id
        res = super().unlink()
        bills.exists()._rvt_settle()
        return res
