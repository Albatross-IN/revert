from odoo import api, fields, models
from odoo.exceptions import ValidationError


class RvtProjectTrade(models.Model):
    """The trade plan: which trades a project needs and the agency chosen for each."""
    _name = "rvt.project.trade"
    _inherit = ["rvt.live.mixin"]
    _description = "Trade on a project"
    _order = "project_id, sequence, id"

    project_id = fields.Many2one("project.project", required=True, ondelete="cascade", index=True)
    trade_id = fields.Many2one("rvt.trade", required=True, ondelete="restrict", index=True)
    sequence = fields.Integer(related="trade_id.sequence", store=True)
    agency_id = fields.Many2one(
        "res.partner", string="Agency", ondelete="restrict", index=True,
        domain="[('rvt_is_agency', '=', True)]", tracking=True,
        help="Empty while the agency is undecided.")
    contact_ids = fields.Many2many(
        "res.partner", "rvt_project_trade_contact_rel", "plan_id", "partner_id", string="Contact people",
        domain="[('parent_id', '=', agency_id)]",
        help="The agency's people who receive this project's drawings and MOM points.")
    decide_by = fields.Date(string="Decide by", help="By when the agency must be chosen.")
    note = fields.Char()
    is_undecided_late = fields.Boolean(
        string="Undecided past its date", compute="_compute_is_undecided_late", search="_search_is_undecided_late")
    line_count = fields.Integer(string="Work lines", compute="_compute_line_count")

    _project_trade_uniq = models.Constraint(
        "unique (project_id, trade_id)", "This trade is already on the project.")

    @api.depends("trade_id", "agency_id")
    def _compute_display_name(self):
        for plan in self:
            trade = plan.trade_id.name or ""
            plan.display_name = f"{trade} · {plan.agency_id.name}" if plan.agency_id else trade

    @api.depends("agency_id", "decide_by")
    def _compute_is_undecided_late(self):
        today = self.env["rvt.config"].today()
        for plan in self:
            plan.is_undecided_late = bool(not plan.agency_id and plan.decide_by and plan.decide_by < today)

    def _search_is_undecided_late(self, operator, value):
        if operator not in ("=", "!=", "in", "not in"):
            return NotImplemented
        today = self.env["rvt.config"].today()
        late = [("agency_id", "=", False), ("decide_by", "<", today)]
        positive = (operator in ("=", "in")) == bool(value if operator in ("=", "!=") else True in value)
        return late if positive else ["!"] + ["&"] + late

    def _compute_line_count(self):
        Task = self.env["project.task"]
        for plan in self:
            plan.line_count = Task.search_count([
                ("project_id", "=", plan.project_id.id), ("rvt_kind", "=", "work"),
                ("rvt_trade_id", "=", plan.trade_id.id)])

    @api.constrains("agency_id", "contact_ids")
    def _check_contacts(self):
        for plan in self:
            strangers = plan.contact_ids.filtered(lambda c: c.commercial_partner_id != plan.agency_id.commercial_partner_id)
            if strangers:
                raise ValidationError(self.env._(
                    "%(people)s do not belong to %(agency)s.",
                    people=", ".join(strangers.mapped("name")), agency=plan.agency_id.name or self.env._("the agency")))

    def _lines(self):
        return self.env["project.task"].search([
            ("project_id", "in", self.project_id.ids), ("rvt_kind", "=", "work"),
            ("rvt_trade_id", "in", self.trade_id.ids)])

    @api.model_create_multi
    def create(self, vals_list):
        plans = super().create(vals_list)
        for plan in plans.filtered("agency_id"):
            # lines created before the plan line (or left without an agency) take the plan's agency
            plan._lines().filtered(
                lambda l: l.rvt_trade_id == plan.trade_id and l.project_id == plan.project_id and not l.rvt_agency_id
            ).write({"rvt_agency_id": plan.agency_id.id})
        plans.project_id.flush_recordset(["rvt_agency_ids"])
        return plans

    def unlink(self):
        projects = self.project_id
        res = super().unlink()
        projects.exists().flush_recordset(["rvt_agency_ids"])
        return res

    def write(self, vals):
        if "agency_id" not in vals:
            return super().write(vals)
        Task = self.env["project.task"]
        for plan in self:
            old = plan.agency_id
            plan_vals = dict(vals)
            if (vals["agency_id"] or False) != old.id:
                if not vals["agency_id"]:
                    plan_vals["contact_ids"] = [(5, 0, 0)]
                else:
                    plan_vals.setdefault("decide_by", False)
                    # people of the old agency do not carry over to the new one
                    plan_vals.setdefault("contact_ids", [(5, 0, 0)])
            super(RvtProjectTrade, plan).write(plan_vals)
            if old != plan.agency_id:
                # work lines that still carry the old default follow the plan; overridden lines stay
                Task.sudo().search([
                    ("project_id", "=", plan.project_id.id), ("rvt_kind", "=", "work"),
                    ("rvt_trade_id", "=", plan.trade_id.id), ("rvt_agency_id", "=", old.id or False),
                ]).write({"rvt_agency_id": plan.agency_id.id})
        self.project_id.flush_recordset(["rvt_agency_ids"])
        return True
