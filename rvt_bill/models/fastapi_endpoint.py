from odoo import models

from fastapi import APIRouter

from ..routers import bills


class FastapiEndpoint(models.Model):
    _inherit = "fastapi.endpoint"

    def _get_fastapi_routers(self) -> list[APIRouter]:
        routers = super()._get_fastapi_routers()
        if self.app == "rvt":
            routers = routers + [bills.router]
        return routers
