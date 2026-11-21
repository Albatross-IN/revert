"""One shape for every refusal: {"error": {"code": ..., "message": ...}}.

A middleware and not an exception handler, because the fastapi module clears
the handlers of the mounted app. A refusal rolls the transaction back before
it answers, so half an action is never kept.
"""
import logging

from odoo.exceptions import AccessDenied, AccessError, MissingError, UserError, ValidationError

from odoo.addons.fastapi.context import odoo_env_ctx

from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

_logger = logging.getLogger(__name__)


class ApiError(Exception):
    def __init__(self, status, code, message, rollback=True, **extra):
        super().__init__(message)
        self.status, self.code, self.message, self.rollback, self.extra = status, code, message, rollback, extra

    @property
    def body(self):
        return {"error": dict(self.extra, code=self.code, message=self.message)}


def unauthorized(message="Sign in again."):
    return ApiError(401, "AUTH", message)


def forbidden(message="You are not allowed to do this."):
    return ApiError(403, "FORBIDDEN", message)


def not_found(message="Not found."):
    return ApiError(404, "NOT_FOUND", message)


def invalid(message, **extra):
    return ApiError(422, "VALIDATION", message, **extra)


def _rollback(error):
    if not getattr(error, "rollback", True):
        return
    env = odoo_env_ctx.get(None)
    if env is None:
        return
    try:
        env.cr.rollback()
    except Exception:  # noqa: BLE001
        _logger.exception("rvt_api: could not roll back a refused request")


def _plain_refusal(error):
    """Our own refusals are one short line and go out as written. The framework's
    access messages (several lines, record names, user ids) stay in the server log."""
    text = str(error.args[0] if error.args else error)
    if "\n" not in text and len(text) <= 160:
        return text
    _logger.warning("rvt_api: access refused\n%s", text, exc_info=error)
    return "You are not allowed to do this."


def _answer(error, status, code, message, **extra):
    _rollback(error)
    return JSONResponse(status_code=status, content={"error": dict(extra, code=code, message=message)})


class RvtErrorMiddleware(BaseHTTPMiddleware):

    async def dispatch(self, request, call_next):
        try:
            return await call_next(request)
        except ApiError as error:
            _rollback(error)
            return JSONResponse(status_code=error.status, content=error.body)
        except RequestValidationError as error:
            fields = [".".join(str(p) for p in e.get("loc", [])[1:]) for e in error.errors()]
            return _answer(error, 422, "VALIDATION", "The request is not complete.", fields=fields)
        except (UserError, ValidationError) as error:
            if isinstance(error, AccessDenied):
                return _answer(error, 401, "AUTH", "Sign in again.")
            if isinstance(error, AccessError):
                return _answer(error, 403, "FORBIDDEN", _plain_refusal(error))
            if isinstance(error, MissingError):
                return _answer(error, 404, "NOT_FOUND", "That record is not there any more.")
            return _answer(error, 422, "VALIDATION", str(error.args[0] if error.args else error))
        except StarletteHTTPException as error:
            return _answer(error, error.status_code, "HTTP", str(error.detail))
