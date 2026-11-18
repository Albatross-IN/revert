"""What the agency app and the client app show, read with the signed-in person's own rights.

An agency sees its slice: its points, the drawings released to it, its lines on each site.
A client sees two things: what Revert needs from them, and their drawings.
"""
from odoo import api, fields, models

STATE_OUT = {"not_started": "ns", "waiting": "wait", "working": "work", "done": "done"}


class RvtApi(models.AbstractModel):
    _name = "rvt.api"
    _description = "App data for agencies and clients"

    def _tools(self):
        config = self.env["rvt.config"]
        today = config.today()
        iso = lambda d: fields.Date.to_string(d) if d else None
        off = lambda d: (d - today).days if d else None
        return today, iso, off, config.to_date

    # ------------------------------------------------------------------
    @api.model
    def agency_home(self):
        env = self.env
        firm = env.user.partner_id.commercial_partner_id
        today, iso, off, local = self._tools()
        points = env["rvt.point"].search([("state", "=", "open")], order="due_date, number")
        drawings = env["rvt.drawing"].search([], order="id desc")
        projects = env["project.project"].search([], order="name")
        lines = env["project.task"].search([("rvt_kind", "=", "work")], order="project_id, parent_id, sequence")
        names = {p.id: p.sudo().name for p in (projects | points.project_id | drawings.project_id).sudo()}

        def point_row(p):
            return {
                "id": p.id, "n": p.number, "text": p.text, "pid": p.project_id.id, "project": names.get(p.project_id.id, ""),
                "area": p.sudo().entity_id.name or "", "due": iso(p.due_date), "due_off": off(p.due_date),
                "late": bool(p.due_date and p.due_date < today), "photo": p.has_photo,
                "visit": p.sudo().visit_id.number or 0, "st": p.state,
            }

        def drawing_row(d):
            rev = d.sudo().released_revision_id
            receipt = rev.receipt_ids.filtered(lambda r: r.partner_id == firm)[:1]
            return {
                "id": d.id, "pid": d.project_id.id, "project": names.get(d.project_id.id, ""),
                "sheet": d.sheet_no, "title": d.name, "t": d.sudo().trade_id.code or "",
                "rev": rev.number, "rev_id": rev.id, "released": iso(local(rev.released_on)), "rel_off": off(local(rev.released_on)),
                "opened": bool(receipt.opened_on), "in_revision": d.state != "released",
                "q": [{
                    "id": q.id, "text": q.text, "photo": bool(q.photo), "on_off": off(local(q.asked_on)),
                    "ans": q.answer or None, "ans_by": q.sudo().answered_by_id.name or "", "ans_off": off(local(q.answered_on)),
                } for q in env["rvt.drawing.question"].with_context(bin_size=True).search([("drawing_id", "=", d.id)], order="asked_on")],
            }

        sites = []
        for project in projects:
            p = project.sudo()
            mine = lines.filtered(lambda l: l.project_id == project)
            ctx = p._rvt_picture_ctx()
            count = lambda state: len(mine.filtered(lambda l: l.rvt_work_state == state))
            sites.append({
                "id": p.id, "name": p.name, "area": p.rvt_site_area or "", "label": p.rvt_site_label or "",
                "kind": p.rvt_site_kind or "home",
                "lines": [{
                    "id": l.id, "area": l.sudo().parent_id.name, "t": l.sudo().rvt_trade_id.code,
                    "st": STATE_OUT.get(l.rvt_work_state, "ns"),
                    "wait": p._rvt_wait_text(l.sudo(), ctx) if l.rvt_work_state == "waiting" else "",
                    "fin": iso(l.rvt_expected_finish),
                } for l in mine],
                "counts": {"done": count("done"), "work": count("working"), "wait": count("waiting"), "ns": count("not_started")},
                "points": len(points.filtered(lambda x: x.project_id == project)),
            })
        rows = [drawing_row(d) for d in drawings]
        data = {
            "today": iso(today),
            "agency": {"id": firm.id, "name": firm.name, "trades": firm.sudo().rvt_trade_ids.mapped("code")},
            "points": [point_row(p) for p in points],
            "new_drawings": [r for r in rows if not r["opened"]],
            "drawings": rows,
            "sites": sites,
            "asks": [], "bills": [],
        }
        self._agency_home_extra(data, firm)
        return data

    def _agency_home_extra(self, data, firm):
        """Hook: bills (P10)."""
        return

    # ------------------------------------------------------------------
    @api.model
    def client_home(self, project_id=None):
        env = self.env
        me = env.user.partner_id
        today, iso, off, local = self._tools()
        domain = [("id", "=", project_id)] if project_id else []
        out = []
        for project in env["project.project"].search(domain, order="id"):
            p = project.sudo()
            drawings = env["rvt.drawing"].search([("project_id", "=", project.id)], order="id desc")
            items = env["rvt.point"].search([("project_id", "=", project.id), ("state", "=", "open")], order="due_date, number")
            waiting, rows = [], []
            for d in drawings:
                rev = d.sudo().released_revision_id
                receipt = rev.receipt_ids.filtered(lambda r: r.kind == "client")[:1]
                row = {
                    "id": d.id, "sheet": d.sheet_no, "title": d.name, "rev": rev.number, "rev_id": rev.id,
                    "released": iso(local(rev.released_on)), "rel_off": off(local(rev.released_on)),
                    "new": not receipt.opened_on, "needs_approval": d.needs_client_approval,
                    "decision": rev.client_decision or None, "decided_by": rev.client_decided_by or "",
                    "decided_on": iso(local(rev.client_decided_on)), "note": rev.client_note or "",
                    "in_revision": d.state != "released",
                }
                rows.append(row)
                if rev.client_decision == "pending":
                    waiting.append({"kind": "drawing", "id": d.id, "text": env._("Approve the %s", d.name.lower() if d.name else ""),
                                    "sub": env._("revision %s", rev.number), "due": None, "due_off": None})
            for item in items:
                waiting.append({"kind": "point", "id": item.id, "text": item.text, "sub": item.sudo().entity_id.name or "",
                                "due": iso(item.due_date), "due_off": off(item.due_date)})
            lines = env["project.task"].sudo().search([("project_id", "=", p.id), ("rvt_kind", "=", "work")])
            done = len(lines.filtered(lambda l: l.rvt_work_state == "done"))
            out.append({
                "id": p.id, "name": p.name, "label": p.rvt_site_label or "", "area": p.rvt_site_area or "",
                "kind": p.rvt_site_kind or "home", "share": round(done / len(lines), 3) if lines else 0,
                "waiting": waiting, "drawings": rows,
            })
        return {"today": iso(today), "name": me.name, "projects": out}
