"""Signed tokens: an access token for a day and a refresh token for ninety, per device."""
from datetime import datetime, timedelta, timezone

import jwt

ALGORITHM = "HS256"
ISSUER = "revert"
PARAM_SECRET = "rvt_api.jwt_secret"


class TokenError(Exception):
    pass


def _secret(env):
    secret = env["ir.config_parameter"].sudo().get_str(PARAM_SECRET)
    if not secret:
        raise TokenError("The API is not set up on this database.")
    return secret


def _ttl(env, kind):
    params = env["ir.config_parameter"].sudo()
    if kind == "access":
        return timedelta(minutes=params.get_int("rvt_api.access_token_ttl_minutes", 1440))
    if kind == "refresh":
        return timedelta(days=params.get_int("rvt_api.refresh_token_ttl_days", 90))
    return timedelta(days=60)   # a link


def encode(env, kind, **claims):
    now = datetime.now(timezone.utc)
    payload = dict(claims, iss=ISSUER, typ=kind, iat=int(now.timestamp()), exp=int((now + _ttl(env, kind)).timestamp()))
    return jwt.encode(payload, _secret(env), algorithm=ALGORITHM)


def decode(env, token, kind):
    try:
        payload = jwt.decode(token, _secret(env), algorithms=[ALGORITHM], issuer=ISSUER)
    except jwt.ExpiredSignatureError as error:
        raise TokenError("The session has expired.") from error
    except jwt.InvalidTokenError as error:
        raise TokenError("The session is not valid.") from error
    if payload.get("typ") != kind:
        raise TokenError("The session is not valid.")
    return payload


def issue(env, user, device, project_id=None):
    claims = {"sub": str(user.id), "dev": device.id, "ep": device.epoch}
    if project_id:
        claims["prj"] = project_id
    return {
        "access_token": encode(env, "access", **claims),
        "refresh_token": encode(env, "refresh", **claims),
        "expires_in": int(_ttl(env, "access").total_seconds()),
    }
