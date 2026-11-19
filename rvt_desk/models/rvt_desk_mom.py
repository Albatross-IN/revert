"""Visits and points in the desk: the screens' shapes, and one operation per button."""
from datetime import timedelta

from odoo import api, models
from odoo.exceptions import AccessError, UserError

from .rvt_desk import _num


class RvtDesk(models.AbstractModel):
    _inherit = "rvt.desk"

    @api.model
    def _features(self):
        return dict(super()._features(), mom=True)

    # ------------------------------------------------------------------
    # snapshot
    # ------------------------------------------------------------------
    def _point_party(self, point):
        if point.for_kind == "agency":
            return "a%s" % point.partner_id.id
        if point.for_kind == "client":
            return "client"
        if point.for_kind == "staff":
            return "s%s" % point.user_id.id
        return point.partner_id.name or point.party_name or self.env._("Not named")

    def _point_row(self, point, off):
        return {
            "id": "pt%s" % point.id, "pid": point.project_id.id,
            "vid": "v%s" % point.visit_id.id if point.visit_id else None,
            "n": point.number, "kind": point.for_kind, "party": self._point_party(point), "text": point.text,
            "e": "e%s" % point.entity_id.id if point.entity_id else None,
            "t": point.trade_id.code or None,
            "dwg": "d%s" % point.drawing_id.id if point.drawing_id else None,
            "photo": point.has_photo, "due": off(point.due_date),
            "st": point.state, "closedBy": "s%s" % point.closed_by_id.id if point.closed_by_id else None,
            "doneBy": point.closed_by_partner_id.name or None,
            "on": off(self.env["rvt.config"].to_date(point.raised_on)) if point.raised_on else None,
            "closedOn": off(point.closed_on), "note": point.close_note or "", "cphoto": point.has_close_photo,
            # the check of a point the agency marked done: "check" waits for the office, "change" is back with the agency
            "rev": {"to_check": "check", "change": "change"}.get(point.review_state) if point.state == "open" else None,
            "doneOn": off(point.done_on), "chg": point.change_note or "", "chgOn": off(point.change_on),
            "chgBy": "s%s" % point.change_by_id.id if point.change_by_id else None, "chgN": point.change_count,
            "confirmed": point.client_confirmed, "sent": point.sent_count,
            "fresh": point.state == "open" and not point.sent_count and not point.legacy_activity_id,
            "by": "s%s" % point.raised_by_id.id if point.raised_by_id else None,
            "pending": False, "legacy": bool(point.legacy_activity_id),
        }

    def _snapshot_extra(self, data, projects, off, today):
        super()._snapshot_extra(data, projects, off, today)
        env = self.env
        visits = env["rvt.visit"].sudo().search([("project_id", "in", projects.ids)], order="project_id, date, id")
        data["visits"] = [{
            "id": "v%s" % v.id, "pid": v.project_id.id, "no": v.number, "date": off(v.date),
            "by": "s%s" % v.started_by_id.id if v.started_by_id else None,
            "att": [n.strip() for n in (v.attendees or "").split(",") if n.strip()], "st": v.state,
        } for v in visits]
        last = {}
        for visit in visits:
            last[visit.project_id.id] = max(last.get(visit.project_id.id, 0), visit.number)
        domain = [("project_id", "in", projects.ids)]
        if self.env.context.get("rvt_app"):
            # the phone keeps what is open and what was closed in the last six weeks
            domain += ["|", ("state", "=", "open"), ("closed_on", ">", today - timedelta(days=42))]
        points = env["rvt.point"].sudo().search(domain, order="project_id, number, id")
        data["points"] = [self._point_row(p, off) for p in points]
        moved = {task.id: count for task, count in env["rvt.point"].sudo()._read_group(
            [("project_id", "in", projects.ids), ("legacy_task_id", "!=", False)], ["legacy_task_id"], ["__count"])}
        for row in data["projects"]:
            row["visitNo"] = last.get(row["id"], 0)
            for task in row["tasks"]:
                task["moved"] = bool(task["mom"]) and moved.get(task["id"], 0) > 0

    def _wait_ref(self, line):
        if line.rvt_wait_cause == "client" and line.rvt_wait_point_id:
            return "pt%s" % line.rvt_wait_point_id.id
        return super()._wait_ref(line)

    def _wait_extra(self, cause, ref):
        extra = super()._wait_extra(cause, ref)
        if cause == "client" and str(ref or "").startswith("pt"):
            extra["point_id"] = _num(ref)
        return extra

    # ------------------------------------------------------------------
    # operations
    # ------------------------------------------------------------------
    def _visit(self, ref):
        visit = self.env["rvt.visit"].browse(_num(ref)).exists()
        if not visit:
            raise UserError(self.env._("That visit is not there any more. Reload the page."))
        return visit

    def _point(self, ref):
        point = self.env["rvt.point"].browse(_num(ref)).exists()
        if not point:
            raise UserError(self.env._("That point is not there any more. Reload the page."))
        return point

    def _op_start_visit(self, a):
        return {"id": "v%s" % self.env["rvt.visit"].rvt_start(_num(a.get("project")))}

    def _op_finish_visit(self, a):
        self._visit(a.get("visit")).action_finish()

    def _op_add_point(self, a):
        kind = a.get("kind") or "agency"
        party = a.get("party")
        today = self.env["rvt.config"].today()
        vals = {
            "project_id": _num(a.get("pid")), "visit_id": _num(a.get("vid")), "text": a.get("text") or "",
            "for_kind": kind, "entity_id": _num(a.get("e")), "drawing_id": _num(a.get("dwg")),
            "due_date": today + timedelta(days=int(a["due"])) if a.get("due") not in (None, "") else False,
            "photo": a.get("photo") or False,
            # given by a phone that wrote the point without network: the same point sent twice is created once
            "client_uid": a.get("client_uid") or False,
        }
        if a.get("t"):
            vals["trade_id"] = self.env["rvt.trade"].search([("code", "=", a["t"])], limit=1).id
        if kind == "agency":
            vals["partner_id"] = _num(party)
        elif kind == "staff":
            vals["user_id"] = _num(party)
        elif kind == "vendor":
            vals["party_name"] = (party or "").strip() or False
        point = self.env["rvt.point"].browse(self.env["rvt.point"].rvt_add([vals]))
        if kind == "client" and point.client_confirmed:
            point.sudo()._rvt_tell_client()
        return {"id": "pt%s" % point.id}

    def _op_close_point(self, a):
        self._point(a.get("point")).action_close(a.get("note"), a.get("photo") or None)

    def _op_confirm_point(self, a):
        self._point(a.get("point")).action_confirm()

    def _op_reopen_point(self, a):
        self._point(a.get("point")).action_reopen()

    def _op_solve_point(self, a):
        """The office looked at the agency's photo: the point is solved."""
        self._point(a.get("point")).action_solved()

    def _op_change_point(self, a):
        """The office looked and asks for a change, with a note: the point goes back to the agency."""
        self._point(a.get("point")).action_ask_change(a.get("note"))

    def _op_send_party(self, a):
        visit = self._visit(a.get("visit"))
        key = a.get("key") or ""
        if not key.startswith("a"):
            return {"points": 0, "new": 0, "sent": 0}
        return visit.rvt_send_party(_num(key))

    def _op_etl_report(self, a):
        """The verification report of the move of earlier MOM entries, for Setup."""
        self._check_owner()
        report = self.env["rvt.mom.etl"].sudo().run(apply=False)
        return {
            "source": report["source_entries"], "moved": report["already_moved"], "left": report["to_move"],
            "people": len(report["people"]), "unmapped": len(report["unmapped"]), "noperson": report["without_person"],
            "all_equal": report["all_equal"],
            "rows": [{
                "p": r["project"], "b": [r["entries"], r["open"], r["closed"], r["photos"], r["visits"]],
                "a": [r["after"][k] for k in ("entries", "open", "closed", "photos", "visits")] if r["after"] else None,
                "eq": r["equal"],
            } for r in report["projects"]],
        }
