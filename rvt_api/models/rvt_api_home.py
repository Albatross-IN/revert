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
                # a message the office wrote without a question waiting is a line with an answer and no question
                "q": [{
                    "id": q.id, "text": "" if q.via == "revert" else q.text, "photo": bool(q.photo) and q.via != "revert",
                    "on_off": off(local(q.asked_on)), "ans": (q.text if q.via == "revert" else q.answer) or None,
                    "ans_by": q.sudo().answered_by_id.name or "", "ans_off": off(local(q.answered_on)),
                } for q in env["rvt.drawing.question"].with_context(bin_size=True).search([("drawing_id", "=", d.id)], order="asked_on, id")],
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

    # ------------------------------------------------------------------
    # the same slices in the shape of the screens (the app runs the approved screens as they are)
    # ------------------------------------------------------------------
    def _screen_base(self, role):
        Desk = self.env["rvt.desk"]
        config = self.env["rvt.config"].get()
        today = self.env["rvt.config"].today()
        masters = Desk._masters()
        return {
            "role": role, "today_date": fields.Date.to_string(today),
            "features": dict(Desk._features(), bills=False),
            "masters": {"trades": masters["trades"], "default_trades": [], "etypes": [], "extras": [], "presets": [], "dtypes": []},
            "set": {"approval": config["release_needs_approval"], "clientConfirm": config["client_points_need_confirmation"],
                    "lim": {"open": 2, "q": 1, "bill": 3, "stuck": 7}, "sending": self.env["rvt.notify"].sending_on(), "number": "",
                    "testcopy": self.env["rvt.notify"].is_test_copy(), "testsend": bool(self.env["rvt.notify"].test_numbers()),
                    "live": self.env["rvt.live"].info()},
            "staff": [], "agencies": [], "projects": [], "drawings": [], "visits": [], "points": [], "bills": [], "wa": [],
            "notes": self.env["rvt.notify.log"].rvt_mine(),
            "today": [], "mytasks": [], "company": self.env.company.name, "prefix": "", "admin": False,
        }

    def _screen_drawing(self, drawing, off, key, partners):
        """A drawing as a receiver may see it: the released revision only, its own receipt only,
        its own questions only, and none of the office's notes."""
        Desk = self.env["rvt.desk"]
        row = Desk._drawing_row(drawing.sudo().with_context(bin_size=True), off, partners if key == "client" else self.env["res.partner"])
        released = [r for r in row["revs"] if r["st"] == "released"][-1:]
        for rev in released:
            rev.update({"note": "", "back": None, "sentBy": None, "apprBy": None, "relBy": None, "sentOn": None, "apprOn": None})
            rev["rc"] = [r for r in rev["rc"] if r["to"] == key]
        row.update({"revs": released, "st": "released", "ds": None, "q": [q for q in row["q"] if q["by"] == key]})
        # the receiver's own link to the sheet: the same one sent on WhatsApp, which also records the opening.
        # The page behind the client's link opens the drawing with it, since a browser has no PDF viewer of ours.
        mine = self._screen_receipt(drawing, partners)
        row["url"] = "/rvt/d/%s" % mine.token if mine else ""
        return row

    def _screen_receipt(self, drawing, partners):
        receipts = drawing.sudo().released_revision_id.receipt_ids
        me = self.env.user.partner_id
        firm = partners or me.commercial_partner_id      # an agency's receipt is its firm's
        own = receipts.filtered(lambda r: r.partner_id == me)
        return (own or receipts.filtered(lambda r: r.partner_id in firm or r.partner_id.commercial_partner_id in firm))[:1]

    def _screen_staff(self, rows):
        """The names behind answers, nothing more."""
        ids = {int(q["ansBy"][1:]) for d in rows for q in d["q"] if q.get("ansBy")}
        users = self.env["res.users"].sudo().browse(list(ids)).exists()
        from odoo.addons.rvt_project.models.rvt_picture import short_name
        return [{"id": "s%s" % u.id, "n": short_name(u.name), "full": u.name, "roles": [], "login": ""} for u in users]

    @api.model
    def agency_snapshot(self):
        env = self.env
        Desk = env["rvt.desk"]
        me = env.user.partner_id
        firm = me.commercial_partner_id
        key = "a%s" % firm.id
        today = env["rvt.config"].today()
        off = lambda date: (date - today).days if date else None
        data = self._screen_base("agency")
        people = env["res.partner"].sudo().search([("parent_id", "=", firm.id)], order="id")
        people = (me if me != firm else people[:1]) | people
        data["me"] = key
        data["lang"] = me.rvt_prefs()["lang"]
        data["agencies"] = [{
            "id": key, "n": firm.name, "tr": firm.sudo().rvt_trade_ids.mapped("code"), "lang": data["lang"],
            "people": [{"id": p.id, "n": p.name, "ph": p.phone or ""} for p in people],
        }]
        lines = env["project.task"].search([("rvt_kind", "=", "work")], order="project_id, parent_id, sequence")
        drawings = env["rvt.drawing"].search([], order="id")
        seen = set(drawings.ids)
        for project in env["project.project"].search([], order="name"):
            p = project.sudo()
            mine = lines.filtered(lambda l: l.project_id == project).sudo()
            rooms = mine.parent_id.sorted(lambda t: (t.rvt_entity_type_id.is_whole_site, t.sequence, t.id))
            data["projects"].append({
                "id": p.id, "name": p.name, "kind": p.rvt_site_kind or "home", "label": p.rvt_site_label or "",
                "area": p.rvt_site_area or "", "address": p.rvt_site_address or "",
                "client": {"id": False, "n": "", "contacts": []}, "billedTo": "client",
                "principal": None, "designers": [], "coords": [], "onb": False, "onbOn": None, "visitNo": 0,
                "plan": [{"t": plan.trade_id.code, "ag": key, "people": [], "by": None}
                         for plan in p.rvt_trade_plan_ids if plan.agency_id == firm],
                "ents": [{"id": "e%s" % e.id, "n": e.name, "ty": e.rvt_entity_type_id.name or "Other room"} for e in rooms],
                "lines": [{
                    "id": "l%s" % l.id, "e": "e%s" % l.parent_id.id, "t": l.rvt_trade_id.code, "ag": key,
                    "st": STATE_OUT.get(l.rvt_work_state, "ns"), "cause": l.rvt_wait_cause or None,
                    "ref": "d%s" % l.rvt_wait_drawing_id.id if l.rvt_wait_cause == "drawing" and l.rvt_wait_drawing_id.id in seen else None,
                    "note": "", "since": None, "fin": off(l.rvt_expected_finish), "doneOn": None, "startOn": None,
                } for l in mine],
                "tasks": [],
            })
        data["drawings"] = [self._screen_drawing(d, off, key, None) for d in drawings]
        points = env["rvt.point"].search(["|", ("state", "=", "open"), ("closed_on", ">", fields.Date.subtract(today, days=30))], order="number")
        data["points"] = [Desk._point_row(p.sudo(), off) for p in points]
        data["staff"] = self._screen_staff(data["drawings"])
        self._agency_screen_extra(data, firm, off)
        return data

    def _agency_screen_extra(self, data, firm, off):
        """Hook: bills (P10)."""
        return

    @api.model
    def client_snapshot(self, project_id=None):
        env = self.env
        Desk = env["rvt.desk"]
        me = env.user.partner_id
        today = env["rvt.config"].today()
        off = lambda date: (date - today).days if date else None
        data = self._screen_base("client")
        data["me"] = "client"
        data["lang"] = me.rvt_prefs()["lang"]
        projects = env["project.project"].search([("id", "=", project_id)] if project_id else [], order="id")
        for project in projects:
            p = project.sudo()
            others = p.rvt_client_contact_ids - me
            data["projects"].append({
                "id": p.id, "name": p.name, "kind": p.rvt_site_kind or "home", "label": p.rvt_site_label or "",
                "area": p.rvt_site_area or "", "address": p.rvt_site_address or "",
                "client": {"id": p.rvt_client_id.id, "n": p.rvt_client_id.name or me.name,
                           "contacts": [{"id": c.id, "n": c.name, "ph": c.phone or "", "inv": True} for c in (me | others)]},
                "billedTo": p.rvt_billed_to_default or "client", "principal": None, "designers": [], "coords": [],
                "onb": True, "onbOn": None, "visitNo": 0, "plan": [], "ents": [], "lines": [], "tasks": [],
            })
        drawings = env["rvt.drawing"].search([("project_id", "in", projects.ids)], order="id")
        partners = {p.id: p.rvt_client_id | p.rvt_client_contact_ids for p in projects.sudo()}
        data["drawings"] = [self._screen_drawing(d, off, "client", partners.get(d.project_id.id)) for d in drawings]
        points = env["rvt.point"].search([("project_id", "in", projects.ids), ("state", "=", "open")], order="due_date, number")
        data["points"] = [Desk._point_row(p.sudo(), off) for p in points]
        data["staff"] = self._screen_staff(data["drawings"])
        data["clientPid"] = projects[:1].id or False
        return data
