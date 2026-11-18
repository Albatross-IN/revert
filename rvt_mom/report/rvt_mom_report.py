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
            "photo": _photo_uri(p.photo) if p.has_photo else False,
        } for p in points]


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
                points = points.filtered(lambda p: p.for_kind == kind)
                if party.get("partner_id"):
                    points = points.filtered(lambda p: p.partner_id.id == party["partner_id"])
                elif party.get("user_id"):
                    points = points.filtered(lambda p: p.user_id.id == party["user_id"])
                elif party.get("name"):
                    points = points.filtered(lambda p: not p.partner_id and (p.party_name or "") == party["name"])
                points = points.filtered(lambda p: p.state == "open") if kind != "staff" else points
                label = points[:1]._rvt_party_label() if points else (party.get("name") or "")
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
