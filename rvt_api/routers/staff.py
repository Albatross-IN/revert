"""Staff. The app reads one snapshot and sends one operation per button, exactly as the desk does;
the same model methods are also offered one by one."""
from typing import Annotated, Any

from fastapi import APIRouter, Depends, Header, Response
from pydantic import BaseModel
from starlette.responses import JSONResponse

from ..deps import Caller, staff
from ..errors import invalid, not_found
from ..snapshots import snapshot_response
from .auth import client_link

router = APIRouter(tags=["staff"])


class Op(BaseModel):
    name: str
    args: dict[str, Any] = {}


class LineState(BaseModel):
    state: str
    cause: str | None = None
    wait_trade_id: int | None = None
    note: str | None = None
    drawing_id: int | None = None
    point_id: int | None = None
    expected_finish: str | None = None


class SendForApproval(BaseModel):
    media_id: int | None = None
    file: str | None = None
    file_name: str | None = None
    note: str | None = None


class Note(BaseModel):
    note: str = ""


class Release(BaseModel):
    agency_ids: list[int] = []
    client: bool = False


class Question(BaseModel):
    partner_id: int
    text: str
    person: str = ""


class Answer(BaseModel):
    text: str


class VisitStart(BaseModel):
    project_id: int


class Party(BaseModel):
    partner_id: int


class Points(BaseModel):
    points: list[dict[str, Any]]


class Close(BaseModel):
    note: str = ""
    media_id: int | None = None
    photo: str | None = None


class Remind(BaseModel):
    text: str
    agency_id: int | None = None
    client: bool = False


class Invite(BaseModel):
    agency_ids: list[int] = []
    client_contact_ids: list[int] = []


def _one(who, model, record_id):
    record = who.env[model].browse(record_id).exists()
    if not record:
        raise not_found()
    record.check_access("read")
    return record


def _media(who, args, key, media_key):
    """A file sent ahead with POST /media is put where the operation expects it."""
    if args.get(media_key):
        args[key] = who.env["rvt.api.media"]._take(who.user, args.pop(media_key))
    return args


# ---- the app's two calls ------------------------------------------------------
@router.get("/staff/snapshot", summary="Everything the staff screens read, in one answer")
def snapshot(who: Annotated[Caller, Depends(staff)], if_none_match: Annotated[str | None, Header()] = None,
             accept_encoding: Annotated[str | None, Header()] = None):
    data = who.env["rvt.desk"].with_context(rvt_app=True).snapshot()
    data["me_info"] = who.user.rvt_api_me()
    return snapshot_response(data, if_none_match, accept_encoding)


@router.post("/staff/op", summary="One operation, as a button of the desk does it")
def op(data: Op, who: Annotated[Caller, Depends(staff)]):
    args = dict(data.args)
    _media(who, args, "photo", "photo_media_id")
    _media(who, args, "file", "file_media_id")
    return who.env["rvt.desk"].op(data.name, args)


# ---- the same, one method at a time ---------------------------------------------
@router.get("/masters", summary="Trades, room types, presets, standard drawings")
def masters(who: Annotated[Caller, Depends(staff)]):
    return who.env["rvt.desk"]._masters()


@router.get("/me/today", summary="What do I do now")
def today(who: Annotated[Caller, Depends(staff)]):
    return who.env["project.project"].rvt_today()


@router.get("/projects", summary="The projects I may see, one row each")
def projects(who: Annotated[Caller, Depends(staff)]):
    return who.env["project.project"].search([], order="rvt_onboarded desc, id").rvt_picture_summary()


@router.get("/projects/{project_id}/picture", summary="Progress, blockers, next actions, status")
def picture(project_id: int, who: Annotated[Caller, Depends(staff)]):
    return _one(who, "project.project", project_id).rvt_picture()


@router.get("/projects/{project_id}/grid", summary="Rooms down, trades across")
def grid(project_id: int, who: Annotated[Caller, Depends(staff)]):
    return _one(who, "project.project", project_id).rvt_grid()


@router.get("/onboarding/proposal", summary="What a site preset proposes")
def proposal(who: Annotated[Caller, Depends(staff)], preset_id: int | None = None):
    return who.env["project.project"].rvt_onboard_proposal(preset_id)


@router.get("/projects/{project_id}/onboarding", summary="A project's present configuration")
def onboarding_state(project_id: int, who: Annotated[Caller, Depends(staff)]):
    return _one(who, "project.project", project_id).rvt_onboard_state()


@router.post("/onboarding", summary="Set a project up, or complete it")
def onboard(vals: dict[str, Any], who: Annotated[Caller, Depends(staff)]):
    return who.env["project.project"].rvt_onboard(vals)


@router.post("/work-lines/{line_id}/state", summary="Change a cell of the grid")
def line_state(line_id: int, data: LineState, who: Annotated[Caller, Depends(staff)]):
    line = _one(who, "project.task", line_id)
    extra = {k: v for k, v in (("drawing_id", data.drawing_id), ("point_id", data.point_id)) if v}
    kwargs = {"expected_finish": data.expected_finish} if data.expected_finish is not None else {}
    return line.rvt_set_state(data.state, cause=data.cause, wait_trade_id=data.wait_trade_id, note=data.note, **kwargs, **extra)


@router.get("/drawings", summary="The register, for one project or all of mine")
def drawings(who: Annotated[Caller, Depends(staff)], project_id: int | None = None):
    Desk = who.env["rvt.desk"]
    config = who.env["rvt.config"]
    today_ = config.today()
    off = lambda d: (d - today_).days if d else None
    domain = [("project_id", "=", project_id)] if project_id else []
    rows = who.env["rvt.drawing"].with_context(bin_size=True).search(domain, order="project_id, due_date, id")
    clients = {p.id: p.rvt_client_id | p.rvt_client_contact_ids for p in rows.project_id.sudo()}
    return [Desk._drawing_row(d.sudo(), off, clients.get(d.project_id.id)) for d in rows]


@router.post("/drawings/{drawing_id}/start")
def drawing_start(drawing_id: int, who: Annotated[Caller, Depends(staff)]):
    return {"ok": _one(who, "rvt.drawing", drawing_id).action_start()}


@router.post("/drawings/{drawing_id}/send-for-approval")
def drawing_send(drawing_id: int, data: SendForApproval, who: Annotated[Caller, Depends(staff)]):
    file = who.env["rvt.api.media"]._take(who.user, data.media_id) if data.media_id else data.file
    return {"ok": _one(who, "rvt.drawing", drawing_id).action_send_for_approval(file, data.file_name, data.note)}


@router.post("/drawings/{drawing_id}/approve")
def drawing_approve(drawing_id: int, who: Annotated[Caller, Depends(staff)]):
    return {"ok": _one(who, "rvt.drawing", drawing_id).action_approve()}


@router.post("/drawings/{drawing_id}/send-back")
def drawing_send_back(drawing_id: int, data: Note, who: Annotated[Caller, Depends(staff)]):
    return {"ok": _one(who, "rvt.drawing", drawing_id).action_send_back(data.note)}


@router.get("/drawings/{drawing_id}/receivers")
def drawing_receivers(drawing_id: int, who: Annotated[Caller, Depends(staff)]):
    return _one(who, "rvt.drawing", drawing_id).rvt_receivers()


@router.post("/drawings/{drawing_id}/release")
def drawing_release(drawing_id: int, data: Release, who: Annotated[Caller, Depends(staff)]):
    return _one(who, "rvt.drawing", drawing_id).action_release(data.agency_ids, client=data.client)


@router.post("/drawings/{drawing_id}/new-revision")
def drawing_new_revision(drawing_id: int, data: Note, who: Annotated[Caller, Depends(staff)]):
    return {"revision_id": _one(who, "rvt.drawing", drawing_id).action_new_revision(data.note)}


@router.post("/drawings/{drawing_id}/questions", summary="Log a question from a call")
def drawing_question(drawing_id: int, data: Question, who: Annotated[Caller, Depends(staff)]):
    drawing = _one(who, "rvt.drawing", drawing_id)
    drawing._rvt_staff()
    partner = who.env["res.partner"].sudo().browse(data.partner_id).exists()
    if not partner:
        raise invalid("Choose who asked.")
    return {"id": drawing.rvt_ask(partner, data.text, via="office", person_name=data.person or None)}


@router.post("/questions/{question_id}/answer")
def question_answer(question_id: int, data: Answer, who: Annotated[Caller, Depends(staff)]):
    return {"ok": _one(who, "rvt.drawing.question", question_id).action_answer(data.text)}


@router.post("/visits", summary="Start the MOM of a site visit")
def visit_start(data: VisitStart, who: Annotated[Caller, Depends(staff)]):
    return {"id": who.env["rvt.visit"].rvt_start(data.project_id)}


@router.post("/visits/{visit_id}/finish")
def visit_finish(visit_id: int, who: Annotated[Caller, Depends(staff)]):
    return {"ok": _one(who, "rvt.visit", visit_id).action_finish()}


@router.post("/visits/{visit_id}/send-party", summary="Send one party its points of the visit as a PDF")
def visit_send(visit_id: int, data: Party, who: Annotated[Caller, Depends(staff)]):
    return _one(who, "rvt.visit", visit_id).rvt_send_party(data.partner_id)


@router.post("/points", summary="Write points; a batch sent twice is created once")
def points(data: Points, who: Annotated[Caller, Depends(staff)]):
    rows = []
    for row in data.points:
        row = dict(row)
        if row.get("photo_media_id"):
            row["photo"] = who.env["rvt.api.media"]._take(who.user, row.pop("photo_media_id"))
        rows.append(row)
    ids = who.env["rvt.point"].rvt_add(rows)
    out = who.env["rvt.point"].browse(ids)
    return [{"id": p.id, "number": p.number, "client_uid": p.client_uid or None} for p in out]


@router.post("/points/{point_id}/close")
def point_close(point_id: int, data: Close, who: Annotated[Caller, Depends(staff)]):
    photo = who.env["rvt.api.media"]._take(who.user, data.media_id) if data.media_id else data.photo
    point = _one(who, "rvt.point", point_id)
    point.action_close(data.note, photo)
    return {"ok": True, "offer_done_line_id": point.rvt_cell_line() or None}


@router.post("/points/{point_id}/confirm")
def point_confirm(point_id: int, who: Annotated[Caller, Depends(staff)]):
    return {"ok": _one(who, "rvt.point", point_id).action_confirm()}


@router.post("/projects/{project_id}/remind")
def remind(project_id: int, data: Remind, who: Annotated[Caller, Depends(staff)]):
    return {"sent": _one(who, "project.project", project_id).rvt_remind(data.text, agency_id=data.agency_id, client=data.client)}


@router.post("/projects/{project_id}/invite")
def invite(project_id: int, data: Invite, who: Annotated[Caller, Depends(staff)]):
    return {"invited": _one(who, "project.project", project_id).rvt_invite(data.agency_ids, data.client_contact_ids)}


@router.get("/projects/{project_id}/client-link", summary="The address a client contact opens without signing in")
def project_client_link(project_id: int, contact_id: int, who: Annotated[Caller, Depends(staff)]):
    project = _one(who, "project.project", project_id)
    person = who.env["res.partner"].sudo().browse(contact_id).exists()
    if not person or person not in project.sudo().rvt_client_contact_ids:
        raise invalid("That person is not a client contact of this project.")
    return {"url": client_link(who.env, project, person)}
