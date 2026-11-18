from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

WORK_STATES = [
    ("not_started", "Not started"),
    ("waiting", "Waiting"),
    ("working", "Working"),
    ("done", "Done"),
]
WAIT_CAUSES = [
    ("drawing", "A drawing"),
    ("client", "The client"),
    ("trade", "Another trade"),
    ("material", "Material"),
    ("other", "Another cause"),
]
WAIT_FIELDS = ("rvt_wait_cause", "rvt_wait_trade_id", "rvt_wait_note", "rvt_wait_since")
# what an agency person may read on its own work lines and their rooms
RVT_OUTSIDE_READABLE = {
    "rvt_kind", "rvt_entity_type_id", "rvt_trade_id", "rvt_agency_id", "rvt_work_state",
    "rvt_wait_cause", "rvt_wait_trade_id", "rvt_wait_note", "rvt_wait_since", "rvt_expected_finish",
    "rvt_started_on", "rvt_done_on", "rvt_entity_state", "rvt_line_count", "rvt_line_done_count",
    "rvt_entity_agency_ids",
}


class ProjectTask(models.Model):
    _inherit = "project.task"

    rvt_kind = fields.Selection(
        [("entity", "Room or zone"), ("work", "Work line")], string="Revert kind", index=True, tracking=True,
        help="A room or zone of the site, or one trade's work in it. Empty for tasks made by hand.")
    rvt_entity_type_id = fields.Many2one("rvt.entity.type", string="Entity type", ondelete="restrict")

    # ---- work line ----------------------------------------------------
    rvt_trade_id = fields.Many2one("rvt.trade", string="Trade", ondelete="restrict", index=True)
    rvt_agency_id = fields.Many2one(
        "res.partner", string="Agency", ondelete="restrict", index=True,
        domain="[('rvt_is_agency', '=', True)]", tracking=True,
        help="Taken from the project's trade plan; change it here for a second agency on this line only.")
    rvt_work_state = fields.Selection(WORK_STATES, string="Work state", index=True, copy=False, tracking=True)
    rvt_wait_cause = fields.Selection(WAIT_CAUSES, string="Waiting for", copy=False, tracking=True)
    rvt_wait_trade_id = fields.Many2one("rvt.trade", string="Waiting for trade", ondelete="restrict", copy=False)
    rvt_wait_note = fields.Char(string="Waiting note", copy=False)
    rvt_wait_since = fields.Date(string="Waiting since", copy=False)
    rvt_expected_finish = fields.Date(string="Expected finish", copy=False, tracking=True)
    rvt_started_on = fields.Date(string="Started on", copy=False)
    rvt_done_on = fields.Date(string="Done on", copy=False)

    # ---- entity -------------------------------------------------------
    rvt_line_ids = fields.One2many(
        "project.task", "parent_id", string="Work lines", domain=[("rvt_kind", "=", "work")])
    rvt_entity_state = fields.Selection(
        [("not_started", "Not started"), ("in_progress", "In progress"), ("done", "Done")],
        string="Entity state", compute="_compute_rvt_entity_state", store=True)
    rvt_line_count = fields.Integer(string="Lines", compute="_compute_rvt_entity_state", store=True)
    rvt_line_done_count = fields.Integer(string="Lines done", compute="_compute_rvt_entity_state", store=True)

    rvt_entity_agency_ids = fields.Many2many(
        "res.partner", "rvt_entity_agency_rel", "task_id", "partner_id", string="Agencies in this room",
        compute="_compute_rvt_entity_agency_ids", store=True)

    _rvt_entity_trade_uniq = models.UniqueIndex(
        "(parent_id, rvt_trade_id) WHERE rvt_kind = 'work'",
        "This trade already has a work line in this room.")

    @property
    def TASK_PORTAL_READABLE_FIELDS(self):
        return super().TASK_PORTAL_READABLE_FIELDS | RVT_OUTSIDE_READABLE

    # ------------------------------------------------------------------
    @api.depends("child_ids.rvt_work_state", "child_ids.rvt_kind", "rvt_kind")
    def _compute_rvt_entity_state(self):
        for task in self:
            if task.rvt_kind != "entity":
                task.rvt_entity_state = False
                task.rvt_line_count = task.rvt_line_done_count = 0
                continue
            lines = task.child_ids.filtered(lambda t: t.rvt_kind == "work")
            done = lines.filtered(lambda t: t.rvt_work_state == "done")
            task.rvt_line_count = len(lines)
            task.rvt_line_done_count = len(done)
            if lines and len(done) == len(lines):
                task.rvt_entity_state = "done"
            elif any(l.rvt_work_state != "not_started" for l in lines):
                task.rvt_entity_state = "in_progress"
            else:
                task.rvt_entity_state = "not_started"

    @api.depends("child_ids.rvt_agency_id", "child_ids.rvt_kind", "rvt_kind")
    def _compute_rvt_entity_agency_ids(self):
        for task in self:
            task.rvt_entity_agency_ids = task.child_ids.filtered(
                lambda t: t.rvt_kind == "work").rvt_agency_id if task.rvt_kind == "entity" else False

    @api.constrains("rvt_kind", "parent_id")
    def _check_rvt_parent(self):
        for task in self:
            if task.rvt_kind == "work" and task.parent_id.rvt_kind != "entity":
                raise ValidationError(self.env._("A work line belongs to a room or zone."))
            if task.rvt_kind == "entity" and task.parent_id:
                raise ValidationError(self.env._("A room or zone is a top-level task; it cannot sit under another task."))

    @api.constrains("rvt_kind", "rvt_trade_id")
    def _check_rvt_trade(self):
        for task in self:
            if task.rvt_kind == "work" and not task.rvt_trade_id:
                raise ValidationError(self.env._("A work line needs its trade."))

    @api.constrains("rvt_work_state", "rvt_wait_cause", "rvt_wait_trade_id")
    def _check_rvt_wait(self):
        for task in self:
            if task.rvt_kind != "work":
                continue
            if task.rvt_work_state == "waiting":
                if not task.rvt_wait_cause:
                    raise ValidationError(self.env._("Say what the work is waiting for."))
                if task.rvt_wait_cause == "trade" and not task.rvt_wait_trade_id:
                    raise ValidationError(self.env._("Choose the trade this work is waiting for."))
                if task.rvt_wait_cause == "trade" and task.rvt_wait_trade_id == task.rvt_trade_id:
                    raise ValidationError(self.env._("A trade cannot wait for itself."))

    # ------------------------------------------------------------------
    def _rvt_plan_agency(self, project_id, trade_id):
        plan = self.env["rvt.project.trade"].sudo().search(
            [("project_id", "=", project_id), ("trade_id", "=", trade_id)], limit=1)
        return plan.agency_id.id

    @api.model_create_multi
    def create(self, vals_list):
        today = fields.Date.context_today(self)
        for vals in vals_list:
            if vals.get("rvt_kind") != "work":
                continue
            vals.setdefault("rvt_work_state", "not_started")
            parent = self.browse(vals.get("parent_id"))
            if parent and not vals.get("project_id"):
                vals["project_id"] = parent.project_id.id
            if not vals.get("name") and vals.get("rvt_trade_id"):
                vals["name"] = self.env["rvt.trade"].browse(vals["rvt_trade_id"]).name
            if "rvt_agency_id" not in vals and vals.get("project_id") and vals.get("rvt_trade_id"):
                vals["rvt_agency_id"] = self._rvt_plan_agency(vals["project_id"], vals["rvt_trade_id"])
            vals.update(self._rvt_state_side_effects(vals, False, today))
        tasks = super().create(vals_list)
        tasks.filtered(lambda t: t.rvt_kind == "work")._rvt_flush_agency_access()
        return tasks

    def _rvt_flush_agency_access(self):
        """The agency access rules read two stored helpers (the agencies of a project and
        of a room). Bring them up to date at once: a search under those rules, later in
        the same transaction, does not recompute them by itself."""
        self.project_id.flush_recordset(["rvt_agency_ids"])
        self.parent_id.flush_recordset(["rvt_entity_agency_ids"])

    def write(self, vals):
        if "rvt_work_state" not in vals:
            res = super().write(vals)
            if "rvt_agency_id" in vals or "rvt_kind" in vals:
                self._rvt_flush_agency_access()
            return res
        today = fields.Date.context_today(self)
        lines = self.filtered(lambda t: t.rvt_kind == "work" or vals.get("rvt_kind") == "work")
        res = True
        if self - lines:
            res = super(ProjectTask, self - lines).write(vals)
        for line in lines:
            line_vals = dict(vals)
            line_vals.update(self._rvt_state_side_effects(vals, line, today))
            res = super(ProjectTask, line).write(line_vals)
        if "rvt_agency_id" in vals:
            lines._rvt_flush_agency_access()
        return res

    def unlink(self):
        projects, rooms = self.project_id, self.parent_id - self
        res = super().unlink()
        projects.exists().flush_recordset(["rvt_agency_ids"])
        rooms.exists().flush_recordset(["rvt_entity_agency_ids"])
        return res

    @api.model
    def _rvt_state_side_effects(self, vals, line, today):
        """What follows from a work state: dates, the cleared waiting cause, and
        the task's own state so that the earlier task views agree."""
        new = vals.get("rvt_work_state")
        old = line.rvt_work_state if line else False
        out = {}
        if new != "waiting":
            out.update({f: False for f in WAIT_FIELDS})
        elif old != "waiting" or ("rvt_wait_cause" in vals and vals["rvt_wait_cause"] != line.rvt_wait_cause):
            out["rvt_wait_since"] = vals.get("rvt_wait_since") or today
        if new == "working" and old != "working" and not vals.get("rvt_started_on"):
            out["rvt_started_on"] = today
        if new == "done":
            if not vals.get("rvt_done_on"):
                out["rvt_done_on"] = today
            if line and not line.rvt_started_on and not vals.get("rvt_started_on"):
                out["rvt_started_on"] = today
            out["state"] = "1_done"
        else:
            out["rvt_done_on"] = False
            if not line or line.state == "1_done":
                out["state"] = "01_in_progress"
        if new == "not_started":
            out["rvt_started_on"] = False
        return out

    def rvt_set_state(self, state, cause=None, wait_trade_id=None, note=None, expected_finish=None, **extra):
        """One tap on a grid cell. ``extra`` carries the links later phases add
        (the drawing or the point the line waits for)."""
        self.ensure_one()
        if self.rvt_kind != "work":
            raise UserError(self.env._("Only a work line has a work state."))
        if state not in dict(WORK_STATES):
            raise UserError(self.env._("Unknown work state."))
        vals = {"rvt_work_state": state}
        if state == "waiting":
            vals.update({
                "rvt_wait_cause": cause or False,
                "rvt_wait_trade_id": wait_trade_id if cause == "trade" else False,
                "rvt_wait_note": (note or "").strip() or False,
            })
            vals.update(self._rvt_wait_links(cause, extra))
        if expected_finish is not None:
            vals["rvt_expected_finish"] = expected_finish or False
        self.write(vals)
        return self.rvt_cell()

    def _rvt_wait_links(self, cause, extra):
        """Hook: field values for the record a line waits for."""
        return {}

    def rvt_cell(self):
        """One grid cell as the desk and the app read it."""
        self.ensure_one()
        return {
            "id": self.id,
            "entity_id": self.parent_id.id,
            "trade_id": self.rvt_trade_id.id,
            "agency_id": self.rvt_agency_id.id or False,
            "agency": self.rvt_agency_id.name or False,
            "state": self.rvt_work_state,
            "cause": self.rvt_wait_cause or False,
            "wait_trade_id": self.rvt_wait_trade_id.id or False,
            "note": self.rvt_wait_note or "",
            "since": fields.Date.to_string(self.rvt_wait_since) if self.rvt_wait_since else False,
            "expected_finish": fields.Date.to_string(self.rvt_expected_finish) if self.rvt_expected_finish else False,
            "started_on": fields.Date.to_string(self.rvt_started_on) if self.rvt_started_on else False,
            "done_on": fields.Date.to_string(self.rvt_done_on) if self.rvt_done_on else False,
        }

    def _rvt_can_remove(self):
        """A cell may be unticked only while its work has not started.
        Later phases also keep a line that carries points."""
        self.ensure_one()
        return self.rvt_kind == "work" and self.rvt_work_state == "not_started"

    def action_rvt_mark_entity(self):
        """Use a room task made by hand as an entity instead of creating a second one."""
        for task in self:
            if task.parent_id:
                raise UserError(self.env._("Only a top-level task can become a room or zone."))
            if task.rvt_kind == "work":
                raise UserError(self.env._("A work line cannot become a room or zone."))
            task.rvt_kind = "entity"
        return True
