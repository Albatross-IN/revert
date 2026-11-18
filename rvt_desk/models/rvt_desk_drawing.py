"""Drawings in the desk: the register in the screens' shape, and one operation per button."""
from datetime import timedelta

from odoo import api, models
from odoo.exceptions import UserError

from .rvt_desk import _num

STATE_OUT = {"awaiting_approval": "awaiting"}


class RvtDesk(models.AbstractModel):
    _inherit = "rvt.desk"

    @api.model
    def _features(self):
        return dict(super()._features(), drawings=True)

    # ------------------------------------------------------------------
    # snapshot
    # ------------------------------------------------------------------
    def _clock(self, moment):
        local = self.env["rvt.config"].to_local(moment)
        return local.strftime("%-I:%M %p").lower() if local else ""

    def _drawing_row(self, drawing, off, client_partners):
        local = self.env["rvt.config"].to_date
        s = lambda user: "s%s" % user.id if user else None
        revisions = []
        for r in drawing.revision_ids.sorted("number"):
            client = None
            if r.client_decision:
                client = {"dec": r.client_decision, "by": r.client_decided_by or "", "on": off(local(r.client_decided_on)),
                          "at": self._clock(r.client_decided_on), "note": r.client_note or ""}
            revisions.append({
                "id": r.id, "n": r.number, "st": STATE_OUT.get(r.state, r.state), "note": r.note or "",
                "back": r.back_note or None, "file": bool(r.file_name), "fname": r.file_name or "",
                "sentBy": s(r.sent_by_id), "sentOn": off(local(r.sent_on)),
                "apprBy": s(r.approved_by_id), "apprOn": off(local(r.approved_on)),
                "relBy": s(r.released_by_id), "relOn": off(local(r.released_on)),
                "rc": [{
                    "to": "client" if x.kind == "client" else "a%s" % x.partner_id.id,
                    "sent": off(local(x.sent_on)), "opened": off(local(x.opened_on)) if x.opened_on else None,
                    "at": self._clock(x.opened_on),
                } for x in r.receipt_ids],
                "client": client,
            })
        return {
            "id": "d%s" % drawing.id, "pid": drawing.project_id.id, "code": drawing.code, "no": drawing.number,
            "title": drawing.name, "t": drawing.trade_id.code or None,
            "e": "e%s" % drawing.entity_id.id if drawing.entity_id else None,
            "ds": s(drawing.designer_id), "due": off(drawing.due_date) or 0,
            "forClient": drawing.for_client, "needsApproval": drawing.needs_client_approval,
            "st": STATE_OUT.get(drawing.state, drawing.state),
            "revs": revisions,
            "q": [{
                "id": "q%s" % q.id,
                "by": "client" if q.partner_id in client_partners else "a%s" % q.partner_id.id,
                "byName": q.asked_by_name or q.partner_id.name, "via": q.via, "text": q.text,
                "photo": bool(q.photo), "on": off(local(q.asked_on)),
                "ans": q.answer or None, "ansBy": s(q.answered_by_id), "ansOn": off(local(q.answered_on)),
            } for q in drawing.question_ids.sorted("asked_on")],
        }

    def _snapshot_extra(self, data, projects, off, today):
        super()._snapshot_extra(data, projects, off, today)
        drawings = self.env["rvt.drawing"].sudo().with_context(bin_size=True).search(
            [("project_id", "in", projects.ids)], order="project_id, due_date, id")
        clients = {}
        for project in projects.sudo():
            clients[project.id] = project.rvt_client_id | project.rvt_client_contact_ids
        data["drawings"] = [self._drawing_row(d, off, clients.get(d.project_id.id, self.env["res.partner"])) for d in drawings]

    def _wait_ref(self, line):
        if line.rvt_wait_cause in ("drawing", "client") and line.rvt_wait_drawing_id:
            return "d%s" % line.rvt_wait_drawing_id.id
        return super()._wait_ref(line)

    def _wait_extra(self, cause, ref):
        extra = super()._wait_extra(cause, ref)
        if cause in ("drawing", "client") and str(ref or "").startswith("d"):
            extra["drawing_id"] = _num(ref)
        return extra

    # ------------------------------------------------------------------
    # onboarding step 5
    # ------------------------------------------------------------------
    def _onboard_vals_extra(self, a):
        vals = super()._onboard_vals_extra(a)
        trade = {t.code: t.id for t in self.env["rvt.trade"].sudo().search([])}
        today = self.env["rvt.config"].today()
        rows = []
        for row in a.get("dr") or []:
            title = (row.get("n") or "").strip()
            if not title:
                continue
            rows.append({
                "code": row.get("code") or "AD", "title": title,
                "trade_id": trade.get(row.get("t")) or False,
                "designer_id": _num(row.get("ds")),
                "due_date": today + timedelta(days=int(row.get("due") or 0)),
                "for_client": bool(row.get("client")),
                "needs_client_approval": bool(row.get("client") and row.get("appr")),
            })
        if rows:
            vals["drawings"] = rows
        return vals

    # ------------------------------------------------------------------
    # operations
    # ------------------------------------------------------------------
    def _drawing(self, ref):
        drawing = self.env["rvt.drawing"].browse(_num(ref)).exists()
        if not drawing:
            raise UserError(self.env._("That drawing is not there any more. Reload the page."))
        return drawing

    def _op_dstart(self, a):
        self._drawing(a.get("drawing")).action_start()

    def _op_send_for_approval(self, a):
        self._drawing(a.get("drawing")).action_send_for_approval(a.get("file") or None, a.get("name") or None, a.get("note"))

    def _op_approve(self, a):
        self._drawing(a.get("drawing")).action_approve()

    def _op_send_back(self, a):
        self._drawing(a.get("drawing")).action_send_back(a.get("note"))

    def _op_release(self, a):
        receivers = a.get("to") or []
        agencies = [_num(x) for x in receivers if x != "client" and _num(x)]
        return self._drawing(a.get("drawing")).action_release(agencies, client="client" in receivers)

    def _op_new_revision(self, a):
        self._drawing(a.get("drawing")).action_new_revision(a.get("note"))

    def _op_answer(self, a):
        question = self.env["rvt.drawing.question"].browse(_num(a.get("question"))).exists()
        if not question:
            raise UserError(self.env._("That question is not there any more. Reload the page."))
        question.action_answer(a.get("text"))

    def _op_ask(self, a):
        """A question logged by staff from a phone call."""
        drawing = self._drawing(a.get("drawing"))
        drawing._rvt_staff()
        project = drawing.project_id.sudo()
        if a.get("by") == "client":
            partner = project.rvt_client_id
            person = a.get("name") or project.rvt_client_contact_ids[:1].name
        else:
            partner = self.env["res.partner"].sudo().browse(_num(a.get("by"))).exists()
            person = a.get("name")
        if not partner:
            raise UserError(self.env._("Choose who asked."))
        qid = drawing.rvt_ask(partner, a.get("text"), via="office", person_name=person)
        return {"id": "q%s" % qid}
