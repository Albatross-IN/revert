from datetime import timedelta

from odoo import api, fields, models
from odoo.exceptions import UserError


class ProjectProject(models.Model):
    _inherit = "project.project"

    rvt_drawing_ids = fields.One2many("rvt.drawing", "project_id", string="Drawings")

    @api.model
    def rvt_drawing_proposal(self, trade_ids, designer_ids=None, project_id=None):
        """The standard set for the trades ticked: the general set and each trade's own
        drawings, with the designer and the due date pre-filled so that most rows need only
        the tick. Drawings the project has already are marked."""
        self._rvt_check_staff()
        today = self.env["rvt.config"].today()
        types = self.env["rvt.drawing.type"].search(["|", ("trade_id", "=", False), ("trade_id", "in", list(trade_ids or []))])
        designers = self.env["res.users"].browse(designer_ids or []).exists()
        have = set()
        if project_id:
            have = set(self.browse(project_id).sudo().rvt_drawing_ids.mapped("code"))
        services = {"elec", "plmb", "ac", "av"}
        first_of_trade = {}
        rows = []
        for dtype in types:
            first = dtype.trade_id.id not in first_of_trade
            first_of_trade.setdefault(dtype.trade_id.id, dtype.id)
            second = designers[1:2] if dtype.trade_id.code in services else designers.browse()
            designer = second or designers[:1]
            rows.append({
                "type_id": dtype.id, "code": dtype.code, "title": dtype.name,
                "trade_id": dtype.trade_id.id or False,
                # a first proposal: what the client sees, and the first drawing of each trade
                "ticked": dtype.code not in have and (dtype.for_client or first),
                "exists": dtype.code in have,
                "designer_id": designer.id or False,
                "due_date": fields.Date.to_string(today + timedelta(days=dtype.due_offset)),
                "for_client": dtype.for_client, "needs_client_approval": dtype.needs_client_approval,
            })
        return rows

    def _rvt_onboard_extra(self, vals, result):
        """Onboarding step 5: one drawing per ticked row, on its designer's list."""
        super()._rvt_onboard_extra(vals, result)
        rows = vals.get("drawings") or []
        result["drawings_created"] = 0
        if not rows:
            return
        Type = self.env["rvt.drawing.type"].sudo()
        staff = self.env.ref("rvt_base.group_rvt_staff").sudo().all_user_ids
        today = self.env["rvt.config"].today()
        to_create = []
        for row in rows:
            dtype = Type.browse(row.get("type_id")).exists() if row.get("type_id") else Type
            if not dtype and row.get("code"):
                dtype = Type.search([("code", "=", row["code"])], limit=1)
            title = (row.get("title") or dtype.name or "").strip()
            if not title:
                raise UserError(self.env._("Every drawing needs a title."))
            designer = row.get("designer_id")
            for_client = bool(row.get("for_client", dtype.for_client))
            to_create.append({
                "project_id": self.id, "type_id": dtype.id or False,
                "code": row.get("code") or dtype.code or "AD", "name": title,
                "trade_id": row["trade_id"] if "trade_id" in row else (dtype.trade_id.id or False),
                "entity_id": row.get("entity_id") or False,
                "designer_id": designer if designer in staff.ids else (self.rvt_designer_ids[:1].id or False),
                "due_date": row.get("due_date") or today + timedelta(days=dtype.due_offset or 7),
                "for_client": for_client,
                "needs_client_approval": for_client and bool(row.get("needs_client_approval", dtype.needs_client_approval)),
            })
        self.env["rvt.drawing"].sudo().create(to_create)
        result["drawings_created"] = len(to_create)
