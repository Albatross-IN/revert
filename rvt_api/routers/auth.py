"""Sign-in. Staff: login and password. Agencies and clients: mobile number, then a code on WhatsApp.
A client may also arrive from a signed link that opens one project without signing in."""
from typing import Annotated

from odoo.api import Environment
from odoo.exceptions import AccessDenied

from odoo.addons.fastapi.dependencies import odoo_env
from odoo.addons.rvt_notify.models.rvt_notify import e164

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from ..deps import Caller, caller
from ..errors import ApiError, forbidden, invalid, unauthorized
from ..tokens import TokenError, decode, encode, issue

router = APIRouter(prefix="/auth", tags=["auth"])


class Device(BaseModel):
    uid: str = ""
    name: str = ""
    platform: str = ""
    app_version: str = ""
    push_token: str = ""


class Login(BaseModel):
    login: str
    password: str
    device: Device = Device()


class OtpRequest(BaseModel):
    phone: str
    lang: str = ""


class OtpVerify(BaseModel):
    phone: str
    code: str
    lang: str = ""
    device: Device = Device()


class Refresh(BaseModel):
    refresh_token: str


class Link(BaseModel):
    token: str
    device: Device = Device()


def _session(env, user, device_info, project_id=None):
    device = env["rvt.api.device"]._rvt_register(user, device_info.model_dump())
    me = user.with_user(user).rvt_api_me()
    return dict(issue(env, user, device, project_id), me=me)


@router.post("/login", summary="Staff: login and password")
def login(data: Login, env: Annotated[Environment, Depends(odoo_env)]):
    try:
        info = env["res.users"].sudo().authenticate(
            credential={"type": "password", "login": data.login.strip(), "password": data.password},
            user_agent_env={"interactive": False})
    except AccessDenied as error:
        raise unauthorized("Wrong login or password.") from error
    user = env["res.users"].sudo().browse(info.get("uid"))
    if not user or user.rvt_api_role() != "staff":
        raise forbidden("This account is not Revert staff. Agencies and clients sign in with their mobile number.")
    return _session(env, user, data.device)


@router.post("/otp/request", summary="Agency or client: send the sign-in code on WhatsApp")
def otp_request(data: OtpRequest, env: Annotated[Environment, Depends(odoo_env)]):
    number = e164(data.phone)
    if not number:
        raise invalid("Type the ten-digit mobile number.")
    person, role = env["res.users"]._rvt_person_for_phone(number)
    if not person:
        raise ApiError(404, "UNKNOWN_NUMBER", "This number is not on a Revert project yet. Ask the Revert office to add it.")
    if data.lang in ("en", "gu", "hi"):
        person.sudo().rvt_lang = data.lang
    code = env["rvt.api.otp"]._rvt_issue(number, person)
    Notify = env["rvt.notify"]
    sent = Notify.send("otp", None, person, code=code)
    answer = {"sent": bool(sent), "expires_in": 600, "role": role}
    if Notify.is_test_copy():
        # a test copy never sends: show the code so the app can be tried on it. Never on the live database.
        answer["test_code"] = code
    elif not sent:
        raise ApiError(503, "NOT_SENT", "The code could not be sent on WhatsApp just now. Try again in a minute.", rollback=False)
    return answer


@router.post("/otp/verify", summary="Agency or client: sign in with the code")
def otp_verify(data: OtpVerify, env: Annotated[Environment, Depends(odoo_env)]):
    number = e164(data.phone)
    person = env["rvt.api.otp"]._rvt_verify(number, data.code) if number else env["res.partner"]
    if not person:
        raise ApiError(401, "WRONG_CODE", "That code is not right, or it has expired. Ask for a new one.", rollback=False)
    found, role = env["res.users"]._rvt_person_for_phone(number)
    if not role:
        raise forbidden("This number is no longer on a Revert project.")
    user = env["res.users"]._rvt_user_for_person(person, role)
    if data.lang in ("en", "gu", "hi"):
        person.sudo().rvt_lang = data.lang
    return _session(env, user, data.device)


@router.post("/refresh", summary="A new access token for a device that is still signed in")
def refresh(data: Refresh, env: Annotated[Environment, Depends(odoo_env)]):
    try:
        payload = decode(env, data.refresh_token, "refresh")
    except TokenError as error:
        raise unauthorized(str(error)) from error
    user = env["res.users"].sudo().browse(int(payload["sub"])).exists()
    device = env["rvt.api.device"].sudo().browse(payload.get("dev")).exists()
    if not user or not user.active or not device or not device.active or device.epoch != payload.get("ep") or device.user_id != user:
        raise unauthorized("This device was signed out.")
    return dict(issue(env, user, device, payload.get("prj")), me=user.with_user(user).rvt_api_me())


@router.post("/logout", summary="Sign this device out")
def logout(who: Annotated[Caller, Depends(caller)]):
    who.device._sign_out()
    return {"ok": True}


@router.post("/link", summary="A client opens one project from the link they were sent")
def link(data: Link, env: Annotated[Environment, Depends(odoo_env)]):
    try:
        payload = decode(env, data.token, "link")
    except TokenError as error:
        raise unauthorized("This link is no longer valid. Ask the Revert office for a new one.") from error
    project = env["project.project"].sudo().browse(int(payload.get("prj") or 0)).exists()
    person = env["res.partner"].sudo().browse(int(payload.get("sub") or 0)).exists()
    if not project or not person or person not in project.rvt_client_contact_ids:
        raise unauthorized("This link is no longer valid. Ask the Revert office for a new one.")
    user = env["res.users"]._rvt_user_for_person(person, "client")
    return _session(env, user, data.device, project.id)


def client_link(env, project, person):
    """The address a client contact opens without signing in (used by the desk and the staff app)."""
    token = encode(env, "link", sub=str(person.id), prj=project.id)
    return "%s/rvt/c/%s" % (project.get_base_url(), token)
