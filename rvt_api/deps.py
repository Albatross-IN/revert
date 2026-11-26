"""From "Authorization: Bearer …" to the signed-in person and an environment with that person's own rights."""
import dataclasses
from typing import Annotated

from odoo.api import Environment

from odoo.addons.fastapi.dependencies import odoo_env

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from .errors import forbidden, unauthorized
from .tokens import TokenError, decode

bearer = HTTPBearer(scheme_name="RevertToken", description="The access token returned at sign-in.", auto_error=False)


@dataclasses.dataclass
class Caller:
    user: object            # res.users, with the person's own rights
    env: Environment        # not elevated: the access rules apply
    device: object
    role: str               # staff | agency | client
    roles: list
    project_id: int = 0     # set when the session came from a client link: that project only

    @property
    def partner(self):
        return self.user.partner_id

    @property
    def firm(self):
        return self.user.partner_id.commercial_partner_id


def caller(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer)],
    env: Annotated[Environment, Depends(odoo_env)],
) -> Caller:
    if credentials is None:
        raise unauthorized("Sign in first.")
    try:
        payload = decode(env, credentials.credentials, "access")
        uid = int(payload["sub"])
    except (TokenError, KeyError, TypeError, ValueError) as error:
        raise unauthorized(str(error) if isinstance(error, TokenError) else "The session is not valid.") from error
    user = env["res.users"].sudo().browse(uid).exists()
    if not user or not user.active:
        raise unauthorized("This account is no longer active.")
    device = env["rvt.api.device"].sudo().browse(payload.get("dev")).exists()
    if not device or not device.active or device.user_id != user or device.epoch != payload.get("ep"):
        raise unauthorized("This device was signed out.")
    device._touch()
    bound = user.env(user=user.id, su=False, context=dict(user.env.context, lang=user.lang or "en_US", tz=user.tz or "Asia/Kolkata"))
    # The request began as the public user. From here on the transaction belongs to the caller,
    # as it does after a web sign-in: the framework checks links to contacts and users against
    # the transaction's own user, whoever the environment at hand says it is.
    bound.transaction.default_env = bound
    me = bound["res.users"].browse(user.id)
    role = me.rvt_api_role()
    if not role:
        raise forbidden("This account has no role in the Revert app.")
    return Caller(user=me, env=bound, device=device, role=role, roles=me.rvt_roles(), project_id=int(payload.get("prj") or 0))


def staff(who: Annotated[Caller, Depends(caller)]) -> Caller:
    if who.role != "staff":
        raise forbidden("This is for Revert staff.")
    return who


def agency(who: Annotated[Caller, Depends(caller)]) -> Caller:
    if who.role != "agency":
        raise forbidden("This is for agencies.")
    return who


def client(who: Annotated[Caller, Depends(caller)]) -> Caller:
    if who.role != "client":
        raise forbidden("This is for clients.")
    return who


def owner(who: Annotated[Caller, Depends(staff)]) -> Caller:
    """Bill amounts and payments: the access tick "Bill amounts and payments" (owners have it)."""
    if not who.user.has_group("rvt_base.group_rvt_acc_money") and not who.user.has_group("base.group_system"):
        raise forbidden("This is for those who see bill amounts and payments.")
    return who


def needs(key):
    """A staff route that needs one access tick (Settings > Users > Revert access)."""
    def check(who: Annotated[Caller, Depends(staff)]) -> Caller:
        if not (key in who.user.rvt_access() or who.user.has_group("base.group_system")):
            raise forbidden("You do not have this access. Ask an owner to tick it in your Revert access.")
        return who
    return check
