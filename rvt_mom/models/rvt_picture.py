"""What the project picture learns from points: their progress, rule B7, the points half of B4,
and the next actions for the office, each staff member, each agency and the client."""
from datetime import timedelta

from odoo import api, fields, models

from odoo.addons.rvt_project.models.rvt_picture import plural, short_name


class ProjectProject(models.Model):
    _inherit = "project.project"

    rvt_point_ids = fields.One2many("rvt.point", "project_id", string="Points")
    rvt_visit_ids = fields.One2many("rvt.visit", "project_id", string="Visits")

    @api.model
    def _rvt_party_of(self, key):
        """A party as the screens name it ("a12", "client", "s7", "v:Name") in the shape the PDFs take."""
        key = str(key or "")
        number = lambda ref: int("".join(ch for ch in ref if ch.isdigit()) or 0)
        if key in ("", "all"):
            return False
        if key.startswith("v:"):
            return {"kind": "vendor", "name": key[2:]}
        if key == "client":
            return {"kind": "client"}
        if key.startswith("a"):
            return {"kind": "agency", "partner_id": number(key)}
        if key.startswith("s"):
            return {"kind": "staff", "user_id": number(key)}
        return False

    def rvt_points_pdf(self, visit_id=None, party=None, state="open"):
        """The points of this project as a PDF: one visit or all of them, one party or all, open or all.
        Returns (file name, bytes)."""
        self.ensure_one()
        self._rvt_check_staff()
        self.check_access("read")
        project = self.sudo()
        visit = self.env["rvt.visit"].sudo().browse(visit_id or 0).exists()
        if visit and visit.project_id != project:
            visit = visit.browse()
        state = state if state in ("open", "closed", "all") else "open"
        pdf = self.env["ir.actions.report"].sudo()._render_qweb_pdf(
            "rvt_mom.action_report_points", project.ids,
            data={"visit_id": visit.id or False, "party": party or False, "state": state})[0]
        name = "%s - %s" % ("MOM" if visit else "Points", project.name)
        if visit:
            name += " - visit %s" % visit.number
        if party:
            who = party.get("name") or self.env["res.partner"].sudo().browse(party.get("partner_id") or 0).name \
                or self.env["res.users"].sudo().browse(party.get("user_id") or 0).name or party.get("kind")
            name += " - %s" % who
        return "%s.pdf" % name.replace("/", "-"), pdf

    def _rvt_picture_ctx(self):
        ctx = super()._rvt_picture_ctx()
        points = self.env["rvt.point"].sudo().search([("project_id", "=", self.id)], order="due_date, number")
        ctx["points"] = points
        ctx["open_points"] = points.filtered(lambda p: p.state == "open")
        return ctx

    def _rvt_wait_text(self, line, ctx):
        point = line.rvt_wait_point_id
        if line.rvt_wait_cause == "client" and point:
            return self.env._("client: %s", point.text)
        return super()._rvt_wait_text(line, ctx)

    def _rvt_by(self, date, today):
        return self.env._("by %s", self._rvt_due_word(date, today)) if date else self.env._("no date")

    # ------------------------------------------------------------------
    @api.model
    def _rvt_blocker_rules(self):
        rules = super()._rvt_blocker_rules()
        at = rules.index("_rvt_b4_client_approval") + 1
        rules[at:at] = ["_rvt_b4_client_point"]
        at = rules.index("_rvt_b5_b6_line_waits") + 1
        rules[at:at] = ["_rvt_b7_point_past_due"]
        return rules

    def _rvt_b4_client_point(self, ctx):
        """B4 (points): a client item is open past its date."""
        out = []
        client = ctx["project"].rvt_client_id.name or self.env._("The client")
        for point in ctx["open_points"]:
            if point.for_kind != "client" or not point.client_confirmed or not point.due_date or point.due_date >= ctx["today"]:
                continue
            out.append({
                "rule": "B4", "critical": False,
                "text": self.env._("Client: %s", point.text),
                "holds": point.entity_id.name or self.env._("the site"),
                "actor": client, "who": ctx["coords"].ids, "age": (ctx["today"] - point.due_date).days,
                "action": {"key": "remind", "label": self.env._("Remind"), "project_id": self.id, "client": True, "text": point.text},
            })
        return out

    def _rvt_b7_point_past_due(self, ctx):
        """B7: a MOM point is past its due date."""
        out = []
        for point in ctx["open_points"]:
            if point.for_kind == "client" or not point.due_date or point.due_date >= ctx["today"]:
                continue
            party = point._rvt_party_label()
            text = self.env._("%(party)s: point %(no)s past its date", party=party, no=point.number)
            actor = party
            if point.review_state == "to_check":
                # the agency has done its part: the point now waits for the office to look at the photo
                action = {"key": "ptview", "label": self.env._("Check"), "point_id": point.id}
                text = self.env._("%(party)s: point %(no)s done, to be checked", party=party, no=point.number)
                actor = self.env._("Office")
            elif point.for_kind == "agency" and point.partner_id:
                action = {"key": "remind", "label": self.env._("Remind"), "project_id": self.id, "agency_id": point.partner_id.id,
                          "text": self.env._("Point %(no)s: %(text)s", no=point.number, text=point.text)}
            else:
                action = {"key": "closept", "label": self.env._("Close"), "point_id": point.id}
            holds = point.entity_id.name or self.env._("the site")
            if point.trade_id:
                holds += " · %s" % point.trade_id.name
            out.append({
                "rule": "B7", "critical": False,
                "text": text,
                "sub": point.text, "holds": holds, "actor": actor, "who": ctx["coords"].ids,
                "age": (ctx["today"] - point.due_date).days, "action": action,
            })
        return out

    # ------------------------------------------------------------------
    @api.model
    def _rvt_next_builders(self):
        builders = super()._rvt_next_builders()
        at = builders.index("_rvt_next_chase") if "_rvt_next_chase" in builders else len(builders)
        builders[at:at] = ["_rvt_next_points"]
        return builders + ["_rvt_next_client_points"]

    def _rvt_next_points(self, ctx, nxt):
        today = ctx["today"]
        for point in ctx["open_points"]:
            if point.review_state == "to_check":
                # the agency marked it done with a photo: whoever raised it, and the coordinators, look and decide
                who = (point.raised_by_id | ctx["coords"]).filtered(lambda u: u.active and not u.share)
                nxt["revert"].append({
                    "section": "check", "who": who.ids, "who_name": self.env._("Office"), "office": True,
                    "text": self.env._("Check point %(no)s: %(agency)s marked it done",
                                       no=point.number, agency=point.partner_id.name or point._rvt_party_label()),
                    "sub": point.text, "warn": "", "late": False,
                    "action": {"key": "ptview", "label": self.env._("Check"), "point_id": point.id},
                })
            elif point.for_kind == "client" and not point.client_confirmed:
                nxt["revert"].append({
                    "section": "confirm", "who": ctx["coords"].ids, "who_name": self.env._("Office"), "office": True,
                    "text": self.env._("Confirm client point %s before the client sees it", point.number),
                    "sub": point.text, "warn": "", "late": False,
                    "action": {"key": "confirmpt", "label": self.env._("Confirm"), "point_id": point.id},
                })
            elif point.for_kind == "staff" and point.user_id:
                nxt["revert"].append({
                    "section": "point", "who": point.user_id.ids, "who_name": short_name(point.user_id.name),
                    "text": point.text,
                    "sub": self.env._("point %(no)s · %(by)s", no=point.number, by=self._rvt_by(point.due_date, today)),
                    "warn": "", "late": bool(point.due_date and point.due_date < today),
                    "action": {"key": "closept", "label": self.env._("Close"), "point_id": point.id},
                })

    def _rvt_agency_summary(self, agency, ctx):
        row = super()._rvt_agency_summary(agency, ctx)
        today = ctx["today"]
        # what the agency still has to do: a point it marked done waits for the office, not for the agency
        mine = ctx["open_points"].filtered(
            lambda p: p.for_kind == "agency" and p.partner_id == agency and p.review_state != "to_check")
        row["points"] = len(mine)
        row["overdue"] = len(mine.filtered(lambda p: p.due_date and p.due_date < today))
        nxt = mine.sorted(lambda p: (not p.due_date, p.due_date or today, p.number))[:1]
        if nxt and not row["unopened"]:
            if not row["waiting"]:
                row["sub"] = self.env._("next: %(text)s, %(by)s", text=nxt.text, by=self._rvt_by(nxt.due_date, today))
            row["remind"] = self.env._("Point %(no)s: %(text)s (%(by)s)", no=nxt.number, text=nxt.text, by=self._rvt_by(nxt.due_date, today))
        return row

    def _rvt_next_client_points(self, ctx, nxt):
        today = ctx["today"]
        for point in ctx["open_points"]:
            if point.for_kind == "client" and point.client_confirmed:
                nxt["client"].append({
                    "text": point.text, "sub": self._rvt_by(point.due_date, today),
                    "late": bool(point.due_date and point.due_date < today), "remind": point.text, "point_id": point.id,
                })

    # ------------------------------------------------------------------
    def _rvt_progress(self, ctx):
        picture = super()._rvt_progress(ctx)
        points, open_points, today = ctx["points"], ctx["open_points"], ctx["today"]
        week_ago = today - timedelta(days=7)
        picture["progress"]["points"] = [
            len(points) - len(open_points), len(points), len(open_points),
            len(open_points.filtered(lambda p: p.due_date and p.due_date < today))]
        picture["week"]["closed"] = len(points.filtered(lambda p: p.state == "closed" and p.closed_on and p.closed_on > week_ago))
        return picture
