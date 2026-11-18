"""Files: a drawing's PDF, a point's photo, a visit's MOM, and uploads sent ahead of an action.
Everything is read with the signed-in person's own rights."""
import base64
from typing import Annotated

from odoo.http.stream import content_disposition
from odoo.tools.mimetypes import guess_mimetype

from fastapi import APIRouter, Depends, File, Form, Response, UploadFile

from ..deps import Caller, caller, staff
from ..errors import invalid, not_found

router = APIRouter(tags=["files"])
MAX_UPLOAD = 25 * 1024 * 1024


def _readable(who, model, record_id):
    record = who.env[model].browse(record_id).exists()
    if not record:
        raise not_found()
    record.check_access("read")
    return record


@router.get("/files/revision/{revision_id}", summary="A revision's PDF")
def revision_pdf(revision_id: int, who: Annotated[Caller, Depends(caller)], open: int = 0):
    revision = _readable(who, "rvt.drawing.revision", revision_id)
    data = revision.sudo().file
    if not data:
        raise not_found("This revision has no PDF yet.")
    if open and who.role != "staff":
        # the first opening by a receiver is recorded
        revision.sudo().drawing_id.rvt_open(who.partner)
    name = revision.sudo().file_name or "%s.pdf" % revision.sudo().display_name
    return Response(content=data.content, media_type="application/pdf",
                    headers={"Content-Disposition": content_disposition(name, "inline"), "Cache-Control": "private, max-age=300"})


@router.get("/files/point/{point_id}/photo", summary="A point's photo, or its closing photo")
def point_photo(point_id: int, who: Annotated[Caller, Depends(caller)], close: int = 0):
    point = _readable(who, "rvt.point", point_id).sudo()
    value = point.close_photo if close else point.photo
    if not value:
        raise not_found("No photo.")
    content = value.content
    return Response(content=content, media_type=guess_mimetype(content, default="image/jpeg"),
                    headers={"Cache-Control": "private, max-age=3600"})


@router.get("/files/question/{question_id}/photo", summary="The photo sent with a question")
def question_photo(question_id: int, who: Annotated[Caller, Depends(caller)]):
    question = _readable(who, "rvt.drawing.question", question_id).sudo()
    if not question.photo:
        raise not_found("No photo.")
    content = question.photo.content
    return Response(content=content, media_type=guess_mimetype(content, default="image/jpeg"),
                    headers={"Cache-Control": "private, max-age=3600"})


@router.get("/files/visit/{visit_id}/pdf", summary="The MOM of a visit: whole, or one agency's points")
def visit_pdf(visit_id: int, who: Annotated[Caller, Depends(staff)], partner_id: int | None = None):
    visit = _readable(who, "rvt.visit", visit_id)
    party = None
    if partner_id:
        partner = who.env["res.partner"].sudo().browse(partner_id)
        party = {"kind": "agency" if partner.rvt_is_agency else "vendor", "partner_id": partner_id}
    pdf = visit.rvt_pdf(party)
    name = "MOM - %s - visit %s.pdf" % (visit.sudo().project_id.name, visit.number)
    return Response(content=pdf, media_type="application/pdf",
                    headers={"Content-Disposition": content_disposition(name, "inline"), "Cache-Control": "private, no-store"})


@router.get("/files/project/{project_id}/open-points", summary="The open points of a project as a PDF")
def open_points_pdf(project_id: int, who: Annotated[Caller, Depends(staff)]):
    project = _readable(who, "project.project", project_id)
    pdf = who.env["ir.actions.report"].sudo()._render_qweb_pdf("rvt_mom.action_report_open_points", project.ids)[0]
    return Response(content=pdf, media_type="application/pdf",
                    headers={"Content-Disposition": content_disposition("Open points - %s.pdf" % project.sudo().name, "inline")})


@router.post("/media", summary="Send a photo or a PDF ahead of the action that uses it")
async def upload(who: Annotated[Caller, Depends(caller)], file: Annotated[UploadFile, File()],
                 client_uid: Annotated[str, Form()] = ""):
    Media = who.env["rvt.api.media"].sudo()
    if client_uid:
        known = Media.search([("client_uid", "=", client_uid), ("user_id", "=", who.user.id)], limit=1)
        if known:
            return {"id": known.id}
    content = await file.read()
    if not content:
        raise invalid("The file is empty.")
    if len(content) > MAX_UPLOAD:
        raise invalid("That file is larger than 25 MB.")
    media = Media.create({
        "user_id": who.user.id, "name": file.filename or "file", "client_uid": client_uid or False,
        "mimetype": file.content_type or guess_mimetype(content), "data": base64.b64encode(content).decode(),
    })
    return {"id": media.id}
