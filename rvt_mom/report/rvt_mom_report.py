from odoo import api, models
from odoo.tools.mimetypes import guess_mimetype

from odoo.addons.rvt_project.models.rvt_picture import MONTHS, WEEKDAYS


def _day(date):
    return "%s %s %s" % (WEEKDAYS[date.weekday()], date.day, MONTHS[date.month - 1]) if date else ""


def _photo_uri(value):
    """A data address for a stored photo (the PDF engine cannot fetch protected files)."""
    if not value:
        return False
    content = value.content
    return "data:%s;base64,%s" % (guess_mimetype(content, default="image/jpeg"), value.to_base64())


class RvtPointRows(models.AbstractModel):
    _name = "rvt.mom.report.mixin"
    _description = "Rows of a MOM PDF"

    def _rows(self, points):
        today = self.env["rvt.config"].today()
        return [{
            "number": p.number, "text": p.text, "party": p._rvt_party_label(),
            "area": p.entity_id.name or "", "due": "%s %s" % (p.due_date.day, MONTHS[p.due_date.month - 1]) if p.due_date else "",
            "late": bool(p.state == "open" and p.due_date and p.due_date < today),
            "new": p.state == "open" and not p.sent_count and p.for_kind != "staff" and not p.legacy_activity_id,
            "closed": p.state == "closed", "close_note": p.close_note or "",
            # sent back by the office: the party reads what has to change
            "change": p.change_note or "" if p.state == "open" and p.review_state == "change" else "",
            "to_check": p.state == "open" and p.review_state == "to_check",
            "photo": _photo_uri(p.photo) if p.has_photo else False,
            # a closed point shows what it looked like before and after
            "after": _photo_uri(p.close_photo) if p.state == "closed" and p.has_close_photo else False,
            "visit": p.visit_id.number or "",
        } for p in points]

    def _party_points(self, points, party):
        """One party's points out of a set, and the party's name. ``party`` is
        {"kind": "agency" | "client" | "vendor" | "staff", "partner_id" | "user_id" | "name": ...}."""
        kind = party.get("kind")
        points = points.filtered(lambda p: p.for_kind == kind)
        if party.get("partner_id"):
            points = points.filtered(lambda p: p.partner_id.id == party["partner_id"])
        elif party.get("user_id"):
            points = points.filtered(lambda p: p.user_id.id == party["user_id"])
        elif party.get("name"):
            points = points.filtered(lambda p: not p.partner_id and (p.party_name or "") == party["name"])
        label = points[:1]._rvt_party_label() if points else (party.get("name") or "")
        if not label and party.get("partner_id"):
            label = self.env["res.partner"].sudo().browse(party["partner_id"]).name or ""
        if not label and party.get("user_id"):
            label = self.env["res.users"].sudo().browse(party["user_id"]).name or ""
        if not label and kind == "client":
            label = self.env._("Client")
        return points, label


class ReportVisit(models.AbstractModel):
    _name = "report.rvt_mom.report_visit"
    _inherit = "rvt.mom.report.mixin"
    _description = "MOM of a visit"

    @api.model
    def _get_report_values(self, docids, data=None):
        party = (data or {}).get("party") or False
        docs = []
        for visit in self.env["rvt.visit"].sudo().browse(docids):
            points = visit.point_ids.sorted("number")
            label = self.env._("All parties")
            if party:
                kind = party.get("kind")
                points, label = self._party_points(points, party)
                points = points.filtered(lambda p: p.state == "open") if kind != "staff" else points
            docs.append({
                "visit": visit, "title": self.env._("Minutes of meeting"),
                "meta": [
                    (self.env._("Project"), visit.project_id.name),
                    (self.env._("Visit"), "%s · %s" % (visit.number, _day(visit.date))),
                    (self.env._("For"), label),
                    (self.env._("Present"), visit.attendees or "—"),
                ],
                "rows": self._rows(points),
            })
        company = self.env.company
        return {"docs": docs, "company": company, "place": company.city or ""}


class ReportPoints(models.AbstractModel):
    """The points of a project as one PDF, cut the way it is asked for: every visit or one visit,
    every party or one agency, open points or all of them."""
    _name = "report.rvt_mom.report_points"
    _inherit = "rvt.mom.report.mixin"
    _description = "Points of a project"

    @api.model
    def _get_report_values(self, docids, data=None):
        data = data or {}
        party, state = data.get("party") or False, data.get("state") or "open"
        visit = self.env["rvt.visit"].sudo().browse(data.get("visit_id") or 0).exists()
        today = self.env["rvt.config"].today()
        docs = []
        for project in self.env["project.project"].sudo().browse(docids):
            domain = [("project_id", "=", project.id)]
            if visit:
                domain.append(("visit_id", "=", visit.id))
            if state in ("open", "closed"):
                domain.append(("state", "=", state))
            points = self.env["rvt.point"].sudo().search(domain, order="number, id")
            label = self.env._("All parties")
            if party:
                points, label = self._party_points(points, party)
            counts = "%s · %s" % (
                self.env._("%s open", len(points.filtered(lambda p: p.state == "open"))),
                self.env._("%s closed", len(points.filtered(lambda p: p.state == "closed")))) if state == "all" else str(len(points))
            docs.append({
                "visit": visit or False,
                "title": self.env._("Minutes of meeting") if visit else self.env._("Points"),
                "meta": [
                    (self.env._("Project"), project.name),
                    (self.env._("Visit"), "%s · %s" % (visit.number, _day(visit.date)) if visit else self.env._("All visits · as on %s", _day(today))),
                    (self.env._("For"), label),
                    ({"open": self.env._("Open"), "closed": self.env._("Closed")}.get(state, self.env._("Points")), counts),
                ],
                "rows": self._rows(points), "show_visit": not visit,
            })
        company = self.env.company
        return {"docs": docs, "company": company, "place": company.city or ""}


class ReportOpenPoints(models.AbstractModel):
    _name = "report.rvt_mom.report_open_points"
    _inherit = "rvt.mom.report.mixin"
    _description = "Open points of a project"

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = []
        today = self.env["rvt.config"].today()
        for project in self.env["project.project"].sudo().browse(docids):
            points = self.env["rvt.point"].sudo().search(
                [("project_id", "=", project.id), ("state", "=", "open")], order="for_kind, partner_id, number")
            docs.append({
                "visit": False, "title": self.env._("Open points"),
                "meta": [
                    (self.env._("Project"), project.name),
                    (self.env._("As on"), _day(today)),
                    (self.env._("Open"), str(len(points))),
                    (self.env._("Site"), project.rvt_site_area or "—"),
                ],
                "rows": self._rows(points),
            })
        company = self.env.company
        return {"docs": docs, "company": company, "place": company.city or ""}
