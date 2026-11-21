"""Bills through the API. Staff ask, upload on an agency's behalf and review; the owner records
payments; an agency uploads against a request and reads its own bills. Each call runs with the
signed-in person's own rights and is a thin layer over the methods of rvt.bill."""
from typing import Annotated

from odoo.http.stream import content_disposition
from odoo.tools.mimetypes import guess_mimetype

from fastapi import APIRouter, Depends, Response
from pydantic import BaseModel

from odoo.addons.rvt_api.deps import Caller, agency, caller, owner, staff
from odoo.addons.rvt_api.errors import not_found

router = APIRouter(tags=["bills"])


class Ask(BaseModel):
    project_id: int
    agency_id: int
    what: str
    trade: str | None = None
    up_to: float | None = None
    billed_to: str | None = None


class Upload(BaseModel):
    no: str = ""
    amount: float
    photo: str | None = None          # base64, as the other photos of the app
    file: str | None = None
    name: str | None = None
    media_id: int | None = None       # or a file sent ahead with POST /media


class Review(BaseModel):
    ok: bool
    reason: str = ""


class BilledTo(BaseModel):
    to: str


class Payment(BaseModel):
    amount: float
    by: str = ""
    mode: str = "bank"
    file: str | None = None
    name: str | None = None
    media_id: int | None = None


def _bill(who, bill_id):
    bill = who.env["rvt.bill"].browse(bill_id).exists()
    if not bill:
        raise not_found()
    bill.check_access("read")
    return bill


def _offsets(who):
    today = who.env["rvt.config"].today()
    return lambda date: (date - today).days if date else None


def _file(who, data):
    """The document as base64, from the body or from a file sent ahead."""
    if data.media_id:
        return who.env["rvt.api.media"]._take(who.user, data.media_id)
    return getattr(data, "photo", None) or data.file or None


def _row(who, bill):
    is_owner = who.env["rvt.bill"]._rvt_is_owner()
    return who.env["rvt.desk"]._bill_row(bill, _offsets(who), money=is_owner, payments=is_owner)


# ---- staff ---------------------------------------------------------------------------------
@router.get("/bills", summary="The bills of the projects the caller may see")
def bills(who: Annotated[Caller, Depends(staff)], project_id: int | None = None, state: str | None = None):
    domain = []
    if project_id:
        domain.append(("project_id", "=", project_id))
    if state:
        domain.append(("state", "=", state))
    return [_row(who, b) for b in who.env["rvt.bill"].search(domain, order="asked_on desc, id desc")]


@router.post("/bills", summary="Ask an agency of the project for a bill")
def ask(data: Ask, who: Annotated[Caller, Depends(staff)]):
    bill = who.env["rvt.bill"].rvt_ask(
        data.project_id, data.agency_id, data.what, trade_code=data.trade, up_to=data.up_to, billed_to=data.billed_to)
    return _row(who, bill)


@router.post("/bills/{bill_id}/upload", summary="Upload the bill on the agency's behalf")
def upload(bill_id: int, data: Upload, who: Annotated[Caller, Depends(staff)]):
    bill = _bill(who, bill_id)
    bill.rvt_upload(data.no, data.amount, _file(who, data), data.name)
    return _row(who, bill)


@router.post("/bills/{bill_id}/review", summary="Accept a submitted bill, or return it with the reason")
def review(bill_id: int, data: Review, who: Annotated[Caller, Depends(staff)]):
    bill = _bill(who, bill_id)
    bill.rvt_review(data.ok, data.reason)
    return _row(who, bill)


@router.put("/bills/{bill_id}/billed-to", summary="Billed to the client, or to Revert")
def billed_to(bill_id: int, data: BilledTo, who: Annotated[Caller, Depends(staff)]):
    bill = _bill(who, bill_id)
    bill.rvt_set_billed_to(data.to)
    return _row(who, bill)


@router.post("/bills/{bill_id}/payments", summary="Record a payment against an accepted bill (owner)")
def pay(bill_id: int, data: Payment, who: Annotated[Caller, Depends(owner)]):
    bill = _bill(who, bill_id)
    bill.rvt_pay(data.amount, data.by, data.mode, _file(who, data), data.name)
    return _row(who, bill)


# ---- agency --------------------------------------------------------------------------------
@router.get("/agency/bills", summary="The agency's own bills and their states")
def agency_bills(who: Annotated[Caller, Depends(agency)]):
    data = {}
    who.env["rvt.api"]._agency_screen_extra(data, who.firm, _offsets(who))
    return data["bills"]


@router.post("/agency/bills/{bill_id}/upload", summary="The agency uploads its bill against the request")
def agency_upload(bill_id: int, data: Upload, who: Annotated[Caller, Depends(agency)]):
    bill = _bill(who, bill_id)
    bill.rvt_upload(data.no, data.amount, _file(who, data), data.name)
    return {"ok": True, "st": bill.sudo().state}


# ---- files ---------------------------------------------------------------------------------
@router.get("/files/bill/{bill_id}/document", summary="The photo or PDF of a bill")
def bill_document(bill_id: int, who: Annotated[Caller, Depends(caller)]):
    if who.role == "client":
        raise not_found()
    bill = _bill(who, bill_id).sudo()
    if not bill.document:
        raise not_found("No document on this bill.")
    content = bill.document.content
    return Response(content=content, media_type=guess_mimetype(content, default="image/jpeg"), headers={
        "Content-Disposition": content_disposition(bill.document_name or "bill", "inline"), "Cache-Control": "private, max-age=300"})


@router.get("/files/payment/{payment_id}/proof", summary="The proof attached to a payment (owner)")
def payment_proof(payment_id: int, who: Annotated[Caller, Depends(owner)]):
    payment = who.env["rvt.bill.payment"].browse(payment_id).exists()
    if not payment:
        raise not_found()
    payment.check_access("read")
    if not payment.proof:
        raise not_found("No proof on this payment.")
    content = payment.proof.content
    return Response(content=content, media_type=guess_mimetype(content, default="image/jpeg"), headers={
        "Content-Disposition": content_disposition(payment.proof_name or "proof", "inline"), "Cache-Control": "private, max-age=300"})
