"""The signed-in person: who they are, what they prefer (the profile page), their devices."""
from typing import Annotated

from odoo.exceptions import AccessDenied

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from ..deps import Caller, caller, staff
from ..errors import invalid

router = APIRouter(tags=["me"])


class Prefs(BaseModel):
    lang: str | None = None
    push: dict[str, bool] | None = None


class Password(BaseModel):
    old: str
    new: str


class PushToken(BaseModel):
    push_token: str = ""
    name: str = ""
    platform: str = ""
    app_version: str = ""


@router.get("/me", summary="Who is signed in, with their preferences")
def me(who: Annotated[Caller, Depends(caller)]):
    data = who.user.rvt_api_me()
    data["link_project_id"] = who.project_id or None
    data["devices"] = [{
        "id": d.id, "name": d.name or d.platform or "Phone", "platform": d.platform or "", "this": d == who.device,
        "last_seen": str(d.last_seen or ""),
    } for d in who.env["rvt.api.device"].sudo().search([("user_id", "=", who.user.id)])]
    return data


@router.put("/me/preferences", summary="Language and which notifications a person wants")
def preferences(data: Prefs, who: Annotated[Caller, Depends(caller)]):
    return who.partner.rvt_set_prefs(lang=data.lang, push=data.push)


@router.put("/me/password", summary="Staff: change the password")
def password(data: Password, who: Annotated[Caller, Depends(staff)]):
    if len(data.new or "") < 8:
        raise invalid("The new password needs at least 8 characters.")
    try:
        who.env["res.users"].sudo().authenticate(
            credential={"type": "password", "login": who.user.login, "password": data.old},
            user_agent_env={"interactive": False})
    except AccessDenied as error:
        raise invalid("The present password is not right.") from error
    who.user.sudo().password = data.new
    # every other device signs in again; this one keeps its session
    others = who.env["rvt.api.device"].sudo().search([("user_id", "=", who.user.id), ("id", "!=", who.device.id)])
    for device in others:
        device._sign_out()
    return {"ok": True}


@router.post("/me/device", summary="Where this device's notifications go")
def device(data: PushToken, who: Annotated[Caller, Depends(caller)]):
    vals = {"push_token": data.push_token or False}
    for key in ("name", "platform", "app_version"):
        if getattr(data, key):
            vals[key] = getattr(data, key)
    who.device.sudo().write(vals)
    return {"ok": True}


@router.delete("/me/devices/{device_id}", summary="Sign another of one's devices out")
def sign_out_device(device_id: int, who: Annotated[Caller, Depends(caller)]):
    target = who.env["rvt.api.device"].sudo().browse(device_id).exists()
    if target and target.user_id == who.user:
        target._sign_out()
    return {"ok": True}
