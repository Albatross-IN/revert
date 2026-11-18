# -*- coding: utf-8 -*-
from odoo import models
from odoo.http import request

# The phone gantt extends and imports Enterprise's web_gantt, which lives in the on-demand bundle
# web.assets_backend_lazy. Community has that bundle too (Chart.js for graph views) but no
# web_gantt, so a manifest entry made every Community graph screen log "Missing (extension)
# parent templates: web_gantt.GanttController" (BUG-0048). These records exist only where
# web_gantt is installed; init() runs at every install / update of this module. The template is
# prepended so it is applied before any primary copy of web_gantt.GanttController.
GANTT_ASSETS = [
    {"name": "web_glass_workspace: phone gantt templates", "bundle": "web.assets_backend_lazy", "directive": "prepend",
     "path": "web_glass_workspace/static/src/mobile/gantt_phone.xml", "sequence": 20},
    {"name": "web_glass_workspace: phone gantt controller", "bundle": "web.assets_backend_lazy", "directive": "append",
     "path": "web_glass_workspace/static/src/mobile/gantt_phone.js", "sequence": 20},
    {"name": "web_glass_workspace: phone gantt styles", "bundle": "web.assets_backend_lazy", "directive": "append",
     "path": "web_glass_workspace/static/src/mobile/gantt_phone.scss", "sequence": 20},
]


class IrHttp(models.AbstractModel):
    _inherit = "ir.http"

    def session_info(self):
        info = super().session_info()
        if request.session.uid and not self.env.user._is_public():
            info["glass_prefs"] = self.env.user._glass_prefs()
        return info

    def _glass_has_gantt(self):
        return bool(self.env["ir.module.module"].sudo().search_count(
            [("name", "=", "web_gantt"), ("state", "in", ("installed", "to upgrade", "to install"))]
        ))

    def init(self):
        super().init()
        Asset = self.env["ir.asset"].sudo()
        has_gantt = self._glass_has_gantt()
        for values in GANTT_ASSETS:
            record = Asset.search([("path", "=", values["path"])], limit=1)
            if has_gantt and not record:
                Asset.create(values)
            elif record and not has_gantt:
                record.unlink()
