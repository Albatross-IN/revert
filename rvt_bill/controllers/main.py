from odoo import http
from odoo.http import request
from odoo.http.stream import content_disposition
from odoo.tools.mimetypes import guess_mimetype


def _is_staff(user):
    return user.has_group("rvt_base.group_rvt_staff") or user.has_group("base.group_system")


def _inline(content, name):
    return request.make_response(content, headers=[
        ("Content-Type", guess_mimetype(content, default="image/jpeg")),
        ("Content-Disposition", content_disposition(name, "inline")),
        ("Cache-Control", "private, max-age=300"),
    ])


class RvtBillFiles(http.Controller):
    """The desk shows a bill's document and a payment's proof; each is read with the person's own rights."""

    @http.route("/rvt/desk/bill/<int:bill_id>/document", type="http", auth="user")
    def bill_document(self, bill_id, **kw):
        if not _is_staff(request.env.user):
            return request.not_found()
        bill = request.env["rvt.bill"].browse(bill_id).exists()
        if not bill or not bill.has_access("read") or not bill.document:
            return request.not_found()
        return _inline(bill.document.content, bill.document_name or "bill")

    @http.route("/rvt/desk/payment/<int:payment_id>/proof", type="http", auth="user")
    def payment_proof(self, payment_id, **kw):
        # only the owner has any access to payments
        payment = request.env["rvt.bill.payment"].browse(payment_id).exists()
        if not _is_staff(request.env.user) or not payment or not payment.has_access("read") or not payment.proof:
            return request.not_found()
        return _inline(payment.proof.content, payment.proof_name or "proof")
