"""Bills in the desk and in the staff app: the screens' shapes, and one operation per button."""
from odoo import api, models
from odoo.exceptions import UserError

from odoo.addons.rvt_desk.models.rvt_desk import _num

from .rvt_bill import MODES

MODE_LABEL = dict(MODES)
MODE_KEY = {label: key for key, label in MODES}


class RvtDesk(models.AbstractModel):
    _inherit = "rvt.desk"

    @api.model
    def _features(self):
        return dict(super()._features(), bills=True)

    # ------------------------------------------------------------------
    # snapshot
    # ------------------------------------------------------------------
    def _bill_row(self, bill, off, money=True, payments=True):
        """A bill in the screens' shape. ``money`` and ``payments`` are the owner's: without them the
        amount is hidden (0 once uploaded, so the screen can still tell "uploaded" from "not yet")."""
        b = bill.sudo().with_context(bin_size=True)
        uploaded = bool(b.submitted_on)
        return {
            "id": "b%s" % b.id, "pid": b.project_id.id, "ag": "a%s" % b.agency_id.id, "t": b.trade_id.code,
            "askedBy": "s%s" % b.asked_by_id.id if b.asked_by_id else None, "askedOn": off(b.asked_on),
            "what": b.what, "upto": (b.up_to_amount or None) if money else None,
            "no": b.bill_number or "", "date": off(b.bill_date),
            "amount": ((b.amount or 0.0) if money else 0) if uploaded else None,
            "billedTo": b.billed_to, "st": b.state, "subOn": off(b.submitted_on), "reason": b.return_reason or "",
            "doc": ("pdf" if (b.document_name or "").lower().endswith(".pdf") else "image") if b.has_document else "",
            "pay": [{
                "id": p.id, "on": off(p.date), "amount": p.amount, "by": p.paid_by,
                "mode": MODE_LABEL.get(p.mode, p.mode), "proof": p.has_proof,
            } for p in b.payment_ids] if payments else [],
        }

    def _snapshot_extra(self, data, projects, off, today):
        super()._snapshot_extra(data, projects, off, today)
        owner = self.env["rvt.bill"]._rvt_is_owner()
        bills = self.env["rvt.bill"].search([("project_id", "in", projects.ids)], order="asked_on desc, id desc")
        data["bills"] = [self._bill_row(b, off, money=owner, payments=owner) for b in bills]

    # ------------------------------------------------------------------
    # operations
    # ------------------------------------------------------------------
    def _bill(self, ref):
        bill = self.env["rvt.bill"].browse(_num(ref)).exists()
        if not bill:
            raise UserError(self.env._("That bill is not there any more."))
        bill.check_access("read")
        return bill

    def _op_ask_bill(self, a):
        bill = self.env["rvt.bill"].rvt_ask(
            _num(a.get("project")), _num(a.get("agency")), a.get("what"),
            trade_code=a.get("trade"), up_to=a.get("upto"), billed_to=a.get("billedTo"))
        return {"id": "b%s" % bill.id}

    def _op_upload_bill(self, a):
        self._bill(a.get("bill")).rvt_upload(a.get("no"), a.get("amount"), a.get("file") or None, a.get("name") or None)

    def _op_review_bill(self, a):
        self._bill(a.get("bill")).rvt_review(bool(a.get("ok")), a.get("reason"))

    def _op_bill_to(self, a):
        self._bill(a.get("bill")).rvt_set_billed_to(a.get("to"))

    def _op_pay_bill(self, a):
        mode = a.get("mode")
        self._bill(a.get("bill")).rvt_pay(
            a.get("amount"), a.get("by"), MODE_KEY.get(mode, mode), a.get("file") or None, a.get("name") or None)
