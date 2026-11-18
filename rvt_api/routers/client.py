"""The client app (and the same screens behind a link): what Revert needs from the client, and the
client's drawings. Approve, ask for a change, mark an item done."""
from typing import Annotated

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from ..deps import Caller, client
from ..errors import forbidden, not_found

router = APIRouter(prefix="/client", tags=["client"])


class Decision(BaseModel):
    decision: str
    note: str = ""


def _mine(who, model, record_id):
    record = who.env[model].browse(record_id).exists()
    if not record:
        raise not_found()
    record.check_access("read")
    if who.project_id and record.sudo().project_id.id != who.project_id:
        raise forbidden("This link opens one project only.")
    return record


@router.get("/home", summary="Everything the client screens read")
def home(who: Annotated[Caller, Depends(client)]):
    return who.env["rvt.api"].client_home(who.project_id or None)


@router.get("/snapshot", summary="The client's slice in the shape of the app's screens")
def snapshot(who: Annotated[Caller, Depends(client)]):
    data = who.env["rvt.api"].client_snapshot(who.project_id or None)
    data["me_info"] = who.user.rvt_api_me()
    return data


@router.post("/drawings/{drawing_id}/open", summary="The client opened the drawing")
def open_drawing(drawing_id: int, who: Annotated[Caller, Depends(client)]):
    drawing = _mine(who, "rvt.drawing", drawing_id)
    first = drawing.rvt_open(who.partner)
    return {"first": bool(first), "rev_id": drawing.sudo().released_revision_id.id}


@router.post("/drawings/{drawing_id}/decide", summary="Approve, or ask for a change")
def decide(drawing_id: int, data: Decision, who: Annotated[Caller, Depends(client)]):
    drawing = _mine(who, "rvt.drawing", drawing_id)
    drawing.rvt_client_decide(data.decision, data.note, partner=who.partner)
    return {"ok": True}


@router.post("/points/{point_id}/done", summary="The client marks its own item as done")
def point_done(point_id: int, who: Annotated[Caller, Depends(client)]):
    point = _mine(who, "rvt.point", point_id)
    point.rvt_client_done(who.partner)
    return {"ok": True}
