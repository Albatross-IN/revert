from odoo import api, fields, models
from odoo.exceptions import ValidationError


class ProjectTask(models.Model):
    _inherit = "project.task"

    rvt_wait_drawing_id = fields.Many2one(
        "rvt.drawing", string="Waiting for drawing", ondelete="set null", copy=False, index=True,
        help="The drawing this work waits for, or the drawing the client must approve first.")

    @property
    def TASK_PORTAL_READABLE_FIELDS(self):
        return super().TASK_PORTAL_READABLE_FIELDS | {"rvt_wait_drawing_id"}

    @api.constrains("rvt_work_state", "rvt_wait_cause", "rvt_wait_drawing_id")
    def _check_rvt_wait_drawing(self):
        for task in self:
            if task.rvt_kind == "work" and task.rvt_work_state == "waiting" and task.rvt_wait_cause == "drawing":
                if not task.rvt_wait_drawing_id:
                    raise ValidationError(self.env._("Choose the drawing this work waits for."))
                if task.rvt_wait_drawing_id.project_id != task.project_id:
                    raise ValidationError(self.env._("That drawing belongs to another project."))

    @api.model
    def _rvt_state_side_effects(self, vals, line, today):
        out = super()._rvt_state_side_effects(vals, line, today)
        if vals.get("rvt_work_state") != "waiting" or vals.get("rvt_wait_cause") not in ("drawing", "client"):
            out["rvt_wait_drawing_id"] = False
        return out

    def _rvt_wait_links(self, cause, extra):
        links = super()._rvt_wait_links(cause, extra)
        if cause in ("drawing", "client"):
            links["rvt_wait_drawing_id"] = extra.get("drawing_id") or False
        return links

    def rvt_cell(self):
        cell = super().rvt_cell()
        cell["wait_drawing_id"] = self.rvt_wait_drawing_id.id or False
        return cell
