from odoo import api, fields, models


class ProjectTask(models.Model):
    _inherit = "project.task"

    rvt_wait_point_id = fields.Many2one(
        "rvt.point", string="Waiting for point", ondelete="set null", copy=False, index=True,
        help="The item the client (or another party) must close before this work goes on.")

    @property
    def TASK_PORTAL_READABLE_FIELDS(self):
        return super().TASK_PORTAL_READABLE_FIELDS | {"rvt_wait_point_id"}

    @api.model
    def _rvt_state_side_effects(self, vals, line, today):
        out = super()._rvt_state_side_effects(vals, line, today)
        if vals.get("rvt_work_state") != "waiting":
            out["rvt_wait_point_id"] = False
        return out

    def _rvt_wait_links(self, cause, extra):
        links = super()._rvt_wait_links(cause, extra)
        links["rvt_wait_point_id"] = extra.get("point_id") or False
        return links

    def _rvt_can_remove(self):
        """A cell that carries a point is not removed by unticking it."""
        if not super()._rvt_can_remove():
            return False
        return not self.env["rvt.point"].sudo().search_count([
            ("entity_id", "=", self.parent_id.id), ("trade_id", "=", self.rvt_trade_id.id)])

    def rvt_cell(self):
        cell = super().rvt_cell()
        cell["wait_point_id"] = self.rvt_wait_point_id.id or False
        cell["open_points"] = self.env["rvt.point"].sudo().search_count([
            ("entity_id", "=", self.parent_id.id), ("trade_id", "=", self.rvt_trade_id.id), ("state", "=", "open")])
        return cell
