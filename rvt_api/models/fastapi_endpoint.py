from odoo import fields, models

from starlette.middleware import Middleware

from fastapi import APIRouter

from ..errors import RvtErrorMiddleware
from ..routers import agency, auth, client, files, me, staff, system


class FastapiEndpoint(models.Model):
    _inherit = "fastapi.endpoint"

    app: str = fields.Selection(selection_add=[("rvt", "Revert app API")], ondelete={"rvt": "cascade"})

    def _get_fastapi_routers(self) -> list[APIRouter]:
        if self.app == "rvt":
            return [system.router, auth.router, me.router, staff.router, files.router, agency.router, client.router]
        return super()._get_fastapi_routers()

    def _get_fastapi_app_middlewares(self) -> list[Middleware]:
        middlewares = super()._get_fastapi_app_middlewares()
        if self.app == "rvt":
            middlewares = middlewares + [Middleware(RvtErrorMiddleware)]
        return middlewares
