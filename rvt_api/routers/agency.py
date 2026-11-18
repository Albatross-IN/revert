"""The agency app: its points, the drawings released to it, its lines on each site. Read-only in
Release 1, except opening a drawing and asking a question."""
from typing import Annotated

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from ..deps import Caller, agency
from ..errors import not_found

router = APIRouter(prefix="/agency", tags=["agency"])


class Ask(BaseModel):
    text: str
    media_id: int | None = None
    photo: str | None = None


def _drawing(who, drawing_id):
    drawing = who.env["rvt.drawing"].browse(drawing_id).exists()
    if not drawing:
        raise not_found()
    drawing.check_access("read")
    return drawing


@router.get("/home", summary="Everything the agency screens read")
def home(who: Annotated[Caller, Depends(agency)]):
    return who.env["rvt.api"].agency_home()


@router.post("/drawings/{drawing_id}/open", summary="The agency opened the drawing")
def open_drawing(drawing_id: int, who: Annotated[Caller, Depends(agency)]):
    drawing = _drawing(who, drawing_id)
    first = drawing.rvt_open(who.partner)
    return {"first": bool(first), "rev_id": drawing.sudo().released_revision_id.id}


@router.post("/drawings/{drawing_id}/questions", summary="Ask a question on a drawing")
def ask(drawing_id: int, data: Ask, who: Annotated[Caller, Depends(agency)]):
    drawing = _drawing(who, drawing_id)
    photo = who.env["rvt.api.media"]._take(who.user, data.media_id) if data.media_id else data.photo
    return {"id": drawing.rvt_ask(who.partner, data.text, photo=photo, via="app", person_name=who.partner.name)}
