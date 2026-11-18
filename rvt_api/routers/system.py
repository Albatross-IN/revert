from typing import Annotated

from odoo.api import Environment

from odoo.addons.fastapi.dependencies import odoo_env

from fastapi import APIRouter, Depends

router = APIRouter(tags=["system"])


@router.get("/health", summary="Is the API there")
def health(env: Annotated[Environment, Depends(odoo_env)]):
    module = env["ir.module.module"].sudo().search([("name", "=", "rvt_api")], limit=1)
    return {"status": "ok", "version": module.installed_version or "", "today": str(env["rvt.config"].today())}
