from odoo import api, fields, models
from odoo.exceptions import UserError


class RvtVisit(models.Model):
    _name = "rvt.visit"
    _inherit = ["rvt.live.mixin"]
    _description = "Site visit"
    _order = "project_id, date desc, id desc"

    project_id = fields.Many2one("project.project", required=True, ondelete="cascade", index=True)
    date = fields.Date(required=True, index=True, default=lambda self: self.env["rvt.config"].today())
    number = fields.Integer(
        string="Visit No", readonly=True, copy=False,
        help="The rank of this visit's date among the dates visited in the project: the first is visit 1.")
    started_by_id = fields.Many2one("res.users", string="Started by", default=lambda self: self.env.user)
    attendees = fields.Char(string="Present", help="Who was on site, as names.")
    state = fields.Selection([("open", "Open"), ("finished", "Finished")], default="open", required=True, index=True)
    point_ids = fields.One2many("rvt.point", "visit_id", string="Points")

    _project_date_uniq = models.Constraint("unique (project_id, date)", "This project already has a visit on that date.")

    @api.depends("project_id.name", "number", "date")
    def _compute_display_name(self):
        for visit in self:
            visit.display_name = "%s · visit %s" % (visit.project_id.name or "", visit.number or "?")

    @api.model
    def _rvt_renumber(self, project_ids):
        """Visit numbers are the rank of the date within the project, as they always were."""
        for project_id in set(project_ids):
            visits = self.sudo().search([("project_id", "=", project_id)], order="date, id")
            for rank, visit in enumerate(visits, start=1):
                if visit.number != rank:
                    visit.number = rank

    @api.model_create_multi
    def create(self, vals_list):
        visits = super().create(vals_list)
        self._rvt_renumber(visits.project_id.ids)
        return visits

    def write(self, vals):
        res = super().write(vals)
        if "date" in vals or "project_id" in vals:
            self._rvt_renumber(self.project_id.ids)
        return res

    def unlink(self):
        projects = self.project_id.ids
        res = super().unlink()
        self._rvt_renumber(projects)
        return res

    @api.model
    def rvt_start(self, project_id):
        """Start the MOM of today's visit: the open visit of the project if there is one,
        today's visit reopened if it was finished, otherwise a new one."""
        Project = self.env["project.project"]
        Project._rvt_check_staff()
        project = Project.browse(project_id).exists()
        if not project:
            raise UserError(self.env._("Choose the project."))
        project.check_access("read")
        today = self.env["rvt.config"].today()
        Visit = self.sudo()
        visit = Visit.search([("project_id", "=", project.id), ("state", "=", "open")], order="date desc", limit=1)
        if not visit:
            visit = Visit.search([("project_id", "=", project.id), ("date", "=", today)], limit=1)
            if visit:
                visit.state = "open"
            else:
                visit = Visit.create({
                    "project_id": project.id, "date": today, "started_by_id": self.env.uid,
                    "attendees": self.env.user.name.split(" ")[0] if self.env.user.name else False,
                })
        return visit.id

    def _rvt_staff(self):
        self.env["project.project"]._rvt_check_staff()
        self.project_id.check_access("read")

    def action_finish(self):
        for visit in self:
            visit._rvt_staff()
            visit.sudo().state = "finished"
        return True

    # ------------------------------------------------------------------
    # parties and sending
    # ------------------------------------------------------------------
    def _rvt_party_points(self, kind, partner=None, only_open=True):
        """This visit's points for one party."""
        self.ensure_one()
        points = self.point_ids.filtered(lambda p: p.for_kind == kind and (not only_open or p.state == "open"))
        if partner is not None:
            points = points.filtered(lambda p: p.partner_id == partner)
        return points.sorted("number")

    def rvt_send_party(self, partner_id):
        """Send one agency (or vendor) its points of this visit as a PDF. Points added since
        the last send are marked "new" in it. Returns {"points": n, "new": n, "sent": n}."""
        self.ensure_one()
        self._rvt_staff()
        partner = self.env["res.partner"].sudo().browse(partner_id).exists()
        visit = self.sudo()
        points = visit.point_ids.filtered(
            lambda p: p.partner_id == partner and p.for_kind in ("agency", "vendor") and p.state == "open").sorted("number")
        if not partner or not points:
            return {"points": 0, "new": 0, "sent": 0}
        fresh = points.filtered(lambda p: not p.sent_count)
        people = visit._rvt_party_people(partner)
        sent = self.env["rvt.notify"].send(
            "mom_party_pdf", visit, people, partner=partner, points=points, new=len(fresh))
        if sent:
            now = fields.Datetime.now()
            for point in points:
                point.write({"sent_count": point.sent_count + 1, "last_sent_on": now})
        return {"points": len(points), "new": len(fresh), "sent": sent}

    def _rvt_party_people(self, partner):
        """Who receives an agency's PDF: its contact people on the project's trade plan;
        for a vendor, the contact itself."""
        self.ensure_one()
        plans = self.project_id.sudo().rvt_trade_plan_ids.filtered(lambda p: p.agency_id == partner)
        return plans.contact_ids or partner

    def rvt_pdf(self, party=None):
        """The MOM as a PDF: the whole visit, or one party's points.
        ``party`` = {"kind": ..., "partner_id": ..., "user_id": ..., "name": ...}."""
        self.ensure_one()
        self._rvt_staff()
        return self.env["ir.actions.report"].sudo()._render_qweb_pdf(
            "rvt_mom.action_report_visit", self.ids, data={"party": party or False})[0]
