"""The desk's data: one snapshot that feeds every screen, one entry point for every button.

The screens are those of the approved preview; the snapshot keeps the preview's
shapes (short keys, day offsets from today, ids with a letter in front:
s = staff, a = agency, e = entity, l = work line) so that the screen code is the
same code. Every write goes through a model method that the app uses too.
"""
import re
from datetime import timedelta

from odoo import api, fields, models
from odoo.exceptions import AccessError, UserError

from odoo.addons.rvt_project.models.rvt_picture import short_name

STATE_OUT = {"not_started": "ns", "waiting": "wait", "working": "work", "done": "done"}
STATE_IN = {v: k for k, v in STATE_OUT.items()}
LANG_OUT = {"gu_IN": "gu", "hi_IN": "hi"}
LANG_IN = {"gu": "gu_IN", "hi": "hi_IN", "en": "en_US"}
SITE_KIND_OUT = {"other": "any"}


def _num(ref):
    """'a12' -> 12; 12 -> 12; '' -> False."""
    if not ref:
        return False
    if isinstance(ref, int):
        return ref
    digits = re.sub(r"^\D+", "", str(ref))
    return int(digits) if digits.isdigit() else False


class RvtDesk(models.AbstractModel):
    _name = "rvt.desk"
    _description = "Revert Desk data"

    # ------------------------------------------------------------------
    # helpers
    # ------------------------------------------------------------------
    @api.model
    def _features(self):
        """Sections that have their back end. Later phases switch theirs on."""
        return {"drawings": False, "mom": False, "bills": False, "wa": False}

    @api.model
    def _web_prefix(self):
        """Where the standard back office lives: /odoo, or the prefix the identity module sets."""
        Module = self.env["ir.module.module"].sudo()
        if Module.search_count([("name", "=", "identity"), ("state", "=", "installed")]):
            try:
                from odoo.addons.identity.models.identity_brand import WEB_PREFIX
                return "/%s" % WEB_PREFIX
            except ImportError:
                pass
        return "/odoo"

    @api.model
    def _check_owner(self):
        user = self.env.user
        if not (user.has_group("rvt_base.group_rvt_owner") or user.has_group("base.group_system")):
            raise AccessError(self.env._("Only an owner can change this."))

    @api.model
    def _staff_users(self):
        users = self.env.ref("rvt_base.group_rvt_staff").sudo().all_user_ids
        return users.filtered(lambda u: u.active and not u.share).sorted(lambda u: (not u.has_group("rvt_base.group_rvt_owner"), u.id))

    def _staff_row(self, user):
        roles = [r for r in user.rvt_roles() if r in ("owner", "principal", "designer", "coordinator")]
        return {"id": "s%s" % user.id, "n": short_name(user.name), "full": user.name, "roles": roles, "login": user.login}

    def _agency_row(self, agency):
        people = self.env["res.partner"].sudo().search([("parent_id", "=", agency.id)], order="id")
        return {
            "id": "a%s" % agency.id, "n": agency.name,
            "tr": agency.rvt_trade_ids.mapped("code"),
            "lang": LANG_OUT.get(agency.lang, "en"),
            "people": [{"id": p.id, "n": p.name, "ph": p.phone or ""} for p in people],
        }

    # ------------------------------------------------------------------
    # masters
    # ------------------------------------------------------------------
    @api.model
    def _masters(self):
        env = self.env
        trades = env["rvt.trade"].sudo().search([])
        names = {lang: {t.id: t.with_context(lang=code).name for t in trades} for lang, code in (("gu", "gu_IN"), ("hi", "hi_IN"))}
        etypes = env["rvt.entity.type"].sudo().search([])
        return {
            "trades": [{"id": t.code, "n": t.name, "s": t.short_name, "gu": names["gu"][t.id], "hi": names["hi"][t.id]} for t in trades],
            "default_trades": trades.filtered("is_usual").mapped("code"),
            "etypes": [{
                "id": e.id, "n": e.name, "kind": SITE_KIND_OUT.get(e.site_kind, e.site_kind),
                "tr": e.trade_ids.mapped("code"), "whole": e.is_whole_site,
            } for e in etypes],
            "extras": etypes.filtered("is_extra").mapped("name"),
            "presets": [{
                "id": p.id, "n": p.name, "kind": p.site_kind,
                "e": [[l.entity_type_id.name, l.count, l.number_from] for l in p.line_ids],
            } for p in env["rvt.site.preset"].sudo().search([])],
            "dtypes": [{
                "id": d.id, "code": d.code, "n": d.name, "t": d.trade_id.code or "",
                "client": d.for_client, "appr": d.needs_client_approval, "off": d.due_offset,
            } for d in env["rvt.drawing.type"].sudo().search([])],
        }

    # ------------------------------------------------------------------
    # the picture, in the preview's shape
    # ------------------------------------------------------------------
    def _act(self, action):
        if not action:
            return None
        key, label = action["key"], action.get("label", "")
        if key == "assign":
            arg = "%s|%s" % (action["project_id"], action["trade"])
        elif key == "cell":
            arg = "%s|l%s" % (action["project_id"], action["line_id"])
        elif key == "remind":
            to = "client" if action.get("client") else "a%s" % action["agency_id"]
            arg = "%s|%s|%s" % (to, action["project_id"], action.get("text", ""))
        elif key in ("dwg", "approve", "release"):
            arg = "d%s" % action["drawing_id"]
        elif key in ("closept", "confirmpt"):
            arg = "pt%s" % action["point_id"]
        elif key == "bill":
            arg = "b%s" % action["bill_id"]
        else:
            arg = ""
        return [key, arg, label]

    def _next_row(self, item):
        return {
            "pid": item["project_id"], "sec": item["section"],
            "who": ["s%s" % uid for uid in item.get("who", [])], "whoN": item.get("who_name", ""),
            "text": item["text"], "sub": item.get("sub", ""), "warn": item.get("warn", ""),
            "late": bool(item.get("late")), "act": self._act(item.get("action")),
        }

    def _pic(self, picture):
        g = picture["progress"]
        return {
            "status": picture["status"],
            "progress": {"ag": g["agencies"], "dr": g["drawings"], "wk": g["work"], "pt": g["points"]},
            "week": {"rel": picture["week"]["released"], "started": picture["week"]["started"],
                     "done": picture["week"]["done"], "closed": picture["week"]["closed"]},
            "blockers": [{
                "k": b["rule"], "crit": b["critical"], "text": b["text"], "sub": b.get("sub", ""),
                "holds": b["holds"], "actor": b["actor"], "who": ["s%s" % uid for uid in b["who"]],
                "age": b["age"], "act": self._act(b.get("action")),
            } for b in picture["blockers"]],
            "next": {
                "revert": [self._next_row(n) for n in picture["next"]["revert"]],
                "agencies": [{
                    "ag": "a%s" % a["agency_id"], "name": a["name"], "trades": a["trades"],
                    "pts": a["points"], "od": a["overdue"], "lines": a["lines"], "done": a["done"],
                    "work": a["working"], "wait": a["waiting"], "sub": a["sub"],
                    "unopened": a["unopened"], "rem": a["remind"],
                } for a in picture["next"]["agencies"]],
                "client": [{
                    "text": c["text"], "sub": c.get("sub", ""), "late": bool(c.get("late")), "rem": c.get("remind", c["text"]),
                    "dwg": "d%s" % c["drawing_id"] if c.get("drawing_id") else None,
                    "pt": "pt%s" % c["point_id"] if c.get("point_id") else None,
                } for c in picture["next"]["client"]],
            },
            "noDwg": [{"id": "l%s" % lid} for lid in picture.get("working_without_drawing", [])],
        }

    # ------------------------------------------------------------------
    # projects
    # ------------------------------------------------------------------
    def _wait_ref(self, line):
        """What a waiting line points at: a trade code now; a drawing or a point later."""
        if line.rvt_wait_cause == "trade":
            return line.rvt_wait_trade_id.code or None
        return None

    def _line_row(self, line, plan_agency, off, today):
        override = line.rvt_agency_id if line.rvt_agency_id != plan_agency.get(line.rvt_trade_id.id) else False
        return {
            "id": "l%s" % line.id, "e": "e%s" % line.parent_id.id, "t": line.rvt_trade_id.code,
            "ag": "a%s" % override.id if override else None,
            "st": STATE_OUT.get(line.rvt_work_state, "ns"),
            "cause": line.rvt_wait_cause or None, "ref": self._wait_ref(line),
            "note": line.rvt_wait_note or "",
            "since": (today - line.rvt_wait_since).days if line.rvt_wait_since else None,
            "fin": off(line.rvt_expected_finish), "doneOn": off(line.rvt_done_on), "startOn": off(line.rvt_started_on),
        }

    def _project_row(self, project, tasks_of, off, today, agency_people):
        p = project.sudo()
        plan_agency = {pl.trade_id.id: pl.agency_id for pl in p.rvt_trade_plan_ids}
        lines = self.env["project.task"].sudo().search(
            [("project_id", "=", p.id), ("rvt_kind", "=", "work")], order="parent_id, sequence, id")
        entities = p.rvt_entity_ids.sorted(lambda t: (t.rvt_entity_type_id.is_whole_site, t.sequence, t.id))
        client = p.rvt_client_id or p.partner_id
        row = {
            "id": p.id, "name": p.name, "kind": p.rvt_site_kind or "home",
            "label": p.rvt_site_label or "", "area": p.rvt_site_area or "", "address": p.rvt_site_address or "",
            "client": {
                "id": client.id or False, "n": client.name or "",
                "contacts": [{"id": c.id, "n": c.name, "ph": c.phone or "", "inv": False} for c in p.rvt_client_contact_ids],
            },
            "billedTo": p.rvt_billed_to_default or "client",
            "principal": "s%s" % p.rvt_principal_id.id if p.rvt_principal_id else None,
            "designers": ["s%s" % u.id for u in p.rvt_designer_ids],
            "coords": ["s%s" % u.id for u in p.rvt_coordinator_ids],
            "onb": p.rvt_onboarded, "onbOn": off(p.rvt_onboarded_on), "visitNo": 0,
            "plan": [{
                "t": pl.trade_id.code, "ag": "a%s" % pl.agency_id.id if pl.agency_id else None,
                "people": [i for i, person in enumerate(agency_people.get(pl.agency_id.id, [])) if person in pl.contact_ids.ids],
                "by": off(pl.decide_by),
            } for pl in p.rvt_trade_plan_ids],
            "ents": [{"id": "e%s" % e.id, "n": e.name, "ty": e.rvt_entity_type_id.name or "Other room"} for e in entities],
            "lines": [self._line_row(l, plan_agency, off, today) for l in lines],
            "tasks": tasks_of.get(p.id, []),
        }
        if p.rvt_onboarded:
            row["pic"] = self._pic(project.rvt_picture())
        return row

    def _hand_made_tasks(self, projects):
        """Top-level tasks made by hand, per project, with their sub-task and MOM entry counts."""
        Task = self.env["project.task"].sudo()
        tasks = Task.search([
            ("project_id", "in", projects.ids), ("parent_id", "=", False), ("rvt_kind", "=", False)], order="project_id, sequence, id")
        if not tasks:
            return {}
        subs = {parent.id: count for parent, count in Task._read_group(
            [("parent_id", "in", tasks.ids), ("rvt_kind", "=", False)], ["parent_id"], ["__count"])}
        self.env.cr.execute("""
            SELECT COALESCE(t.parent_id, t.id), count(*)
              FROM mail_activity a
              JOIN mail_activity_type ty ON ty.id = a.activity_type_id
              JOIN project_task t ON t.id = a.res_id
             WHERE a.res_model = 'project.task' AND ty.name->>'en_US' ILIKE '%%MOM%%'
               AND COALESCE(t.parent_id, t.id) = ANY(%s)
             GROUP BY 1""", [tasks.ids])
        mom = dict(self.env.cr.fetchall())
        out = {}
        for task in tasks:
            out.setdefault(task.project_id.id, []).append({
                "id": task.id, "n": task.name, "stage": task.stage_id.name or "",
                "subs": subs.get(task.id, 0), "mom": mom.get(task.id, 0),
            })
        return out

    def _my_tasks(self):
        tasks = self.env["project.task"].search([
            ("user_ids", "in", self.env.uid), ("rvt_kind", "=", False), ("project_id", "!=", False),
            ("state", "not in", ("1_done", "1_canceled"))], order="priority desc, date_deadline, id desc", limit=6)
        return [{
            "id": t.id, "n": t.name, "p": t.project_id.name, "stage": t.stage_id.name or "",
            "subs": len(t.child_ids),
        } for t in tasks]

    # ------------------------------------------------------------------
    # snapshot
    # ------------------------------------------------------------------
    @api.model
    def snapshot(self):
        Project = self.env["project.project"]
        Project._rvt_check_staff()
        user = self.env.user
        today = self.env["rvt.config"].today()
        off = lambda date: (date - today).days if date else None
        config = self.env["rvt.config"].get()
        agencies = self.env["res.partner"].sudo().search([("rvt_is_agency", "=", True)], order="name")
        agency_rows = [self._agency_row(a) for a in agencies]
        agency_people = {_num(a["id"]): [p["id"] for p in a["people"]] for a in agency_rows}
        projects = Project.search([], order="rvt_onboarded desc, id")
        tasks_of = self._hand_made_tasks(projects)
        project_rows = [self._project_row(p, tasks_of, off, today, agency_people) for p in projects]
        pictures = {}
        for project in projects.filtered(lambda p: p.sudo().rvt_onboarded):
            pictures[project.id] = project.rvt_picture()
        data = {
            "today_date": fields.Date.to_string(today),
            "me": "s%s" % user.id,
            "admin": user.has_group("base.group_system"),
            "prefix": self._web_prefix(),
            "company": user.company_id.name,
            "features": self._features(),
            "set": {
                "approval": config["release_needs_approval"],
                "clientConfirm": config["client_points_need_confirmation"],
                "lim": {"open": config["limit_not_opened_days"], "q": config["limit_question_days"],
                        "bill": config["limit_bill_review_days"], "stuck": config["limit_stuck_days"]},
                "sending": False, "number": "",
                "live": self.env["rvt.live"].info(),
            },
            "masters": self._masters(),
            "staff": [self._staff_row(u) for u in self._staff_users() | user],
            "agencies": agency_rows,
            "projects": project_rows,
            "today": [dict(self._next_row(i), pname=i.get("project", "")) for i in Project.rvt_today(pictures)],
            "mytasks": self._my_tasks(),
            "drawings": [], "visits": [], "points": [], "bills": [], "wa": [], "notes": [],
        }
        self._snapshot_extra(data, projects, off, today)
        return data

    def _snapshot_extra(self, data, projects, off, today):
        """Hook: later phases add drawings, visits, points and bills."""
        return

    # ------------------------------------------------------------------
    # operations: one method per button, each a thin layer over a model method
    # ------------------------------------------------------------------
    @api.model
    def op(self, name, args=None):
        self.env["project.project"]._rvt_check_staff()
        method = getattr(self, "_op_%s" % name, None)
        if not method or not re.match(r"^[a-z_]+$", name or ""):
            raise UserError(self.env._("Unknown action."))
        result = method(args or {}) or {}
        # every button changes what some screen shows: the open screens read again
        self.env["rvt.live"].touch()
        return result

    def _line(self, ref):
        line = self.env["project.task"].browse(_num(ref)).exists()
        if not line or line.rvt_kind != "work":
            raise UserError(self.env._("That work line is not there any more. Reload the page."))
        return line

    def _op_set_line(self, a):
        line = self._line(a.get("line"))
        state = STATE_IN.get(a.get("state"))
        if not state:
            raise UserError(self.env._("Unknown work state."))
        if "agency" in a:
            agency_id = _num(a["agency"])
            plan = self.env["rvt.project.trade"].search([
                ("project_id", "=", line.project_id.id), ("trade_id", "=", line.rvt_trade_id.id)], limit=1)
            wanted = agency_id or plan.agency_id.id
            if wanted != line.rvt_agency_id.id:
                line.rvt_agency_id = wanted
        cause = a.get("cause") or None
        trade = self.env["rvt.trade"].search([("code", "=", a.get("ref"))], limit=1) if cause == "trade" else None
        extra = self._wait_extra(cause, a.get("ref"))
        line.rvt_set_state(
            state, cause=cause, wait_trade_id=trade.id if trade else None, note=a.get("note"),
            **({"expected_finish": a["fin"]} if "fin" in a else {}), **extra)
        return {"id": "l%s" % line.id}

    def _wait_extra(self, cause, ref):
        """Hook: the record a waiting line points at, from the desk's reference."""
        return {}

    def _op_assign(self, a):
        project = self.env["project.project"].browse(_num(a.get("project"))).exists()
        trade = self.env["rvt.trade"].search([("code", "=", a.get("trade"))], limit=1)
        if not project or not trade:
            raise UserError(self.env._("Choose the project and the trade."))
        project.check_access("read")
        agency_id = _num(a.get("agency"))
        today = self.env["rvt.config"].today()
        vals = {"agency_id": agency_id}
        if agency_id:
            first = self.env["res.partner"].sudo().search([("parent_id", "=", agency_id)], order="id", limit=1)
            vals["contact_ids"] = [(6, 0, first.ids)]
        else:
            vals["decide_by"] = today + timedelta(days=int(a.get("by") if a.get("by") is not None else 7))
        plan = self.env["rvt.project.trade"].search([("project_id", "=", project.id), ("trade_id", "=", trade.id)], limit=1)
        if plan:
            plan.write(vals)
        else:
            self.env["rvt.project.trade"].create(dict(vals, project_id=project.id, trade_id=trade.id))
        return {}

    def _onboard_vals(self, a):
        """The wizard's state in the shape rvt_onboard takes."""
        env = self.env
        etype = {e.name: e.id for e in env["rvt.entity.type"].sudo().search([])}
        trade = {t.code: t.id for t in env["rvt.trade"].sudo().search([])}
        today = self.env["rvt.config"].today()
        vals = {
            "project_id": _num(a.get("pid")) or False,
            "name": a.get("name", ""), "client_name": a.get("client", ""), "client_phone": a.get("cphone", ""),
            "site_address": a.get("address", ""), "site_area": a.get("area", ""),
            "site_kind": {"any": "other"}.get(a.get("kind"), a.get("kind") or "home"),
            "site_label": a.get("label", ""), "billed_to": a.get("billedTo") or "client",
            "principal_id": _num(a.get("principal")),
            "designer_ids": [_num(s) for s in a.get("designers", []) if _num(s)],
            "coordinator_ids": [_num(s) for s in a.get("coords", []) if _num(s)],
            "entities": [], "trades": [], "ticks": [],
        }
        for ent in a.get("ents", []):
            row = {"key": str(ent["u"]), "name": ent.get("n", ""), "entity_type_id": etype.get(ent.get("ty")) or etype.get("Other room")}
            if ent.get("id"):
                row["id"] = _num(ent["id"])
            if ent.get("taskId"):
                row["task_id"] = int(ent["taskId"])
            vals["entities"].append(row)
        for code, t in (a.get("tr") or {}).items():
            if not t.get("on") or code not in trade:
                continue
            agency_id = _num(t.get("ag"))
            vals["trades"].append({
                "trade_id": trade[code], "agency_id": agency_id,
                "decide_by": False if agency_id else fields.Date.to_string(today + timedelta(days=int(t.get("by") or 7))),
            })
        for key, code in a.get("ticks", []):
            if code in trade:
                vals["ticks"].append([str(key), trade[code]])
        vals.update(self._onboard_vals_extra(a))
        return vals

    def _onboard_vals_extra(self, a):
        """Hook: drawings (P4), invitations (P6)."""
        return {}

    def _op_onboard(self, a):
        result = self.env["project.project"].rvt_onboard(self._onboard_vals(a))
        return {"pid": result["project_id"], "new": result["new"],
                "nl": result["lines_created"], "nd": result.get("drawings_created", 0), "inv": result.get("invited", 0)}

    def _op_task_entity(self, a):
        task = self.env["project.task"].browse(int(a.get("task") or 0)).exists()
        if not task:
            raise UserError(self.env._("That task is not there any more. Reload the page."))
        task.action_rvt_mark_entity()
        etype = self.env["rvt.entity.type"].sudo().search([("name", "=", a.get("type"))], limit=1)
        if etype:
            task.sudo().rvt_entity_type_id = etype
        return {"id": "e%s" % task.id}

    # ---- setup ---------------------------------------------------------
    def _op_setting(self, a):
        self._check_owner()
        keys = {"approval": "rvt.release_needs_approval", "clientConfirm": "rvt.client_points_need_confirmation"}
        keys.update(self._setting_keys())
        if a.get("key") not in keys:
            raise UserError(self.env._("Unknown setting."))
        self.env["ir.config_parameter"].sudo().set_bool(keys[a["key"]], bool(a.get("value")))
        return {}

    def _setting_keys(self):
        return {}

    def _op_limit(self, a):
        self._check_owner()
        keys = {"open": "rvt.limit_not_opened_days", "q": "rvt.limit_question_days",
                "bill": "rvt.limit_bill_review_days", "stuck": "rvt.limit_stuck_days"}
        if a.get("key") not in keys:
            raise UserError(self.env._("Unknown setting."))
        self.env["ir.config_parameter"].sudo().set_int(keys[a["key"]], max(1, min(60, int(a.get("value") or 1))))
        return {}

    def _op_etype_trade(self, a):
        self._check_owner()
        etype = self.env["rvt.entity.type"].search([("name", "=", a.get("type"))], limit=1)
        trade = self.env["rvt.trade"].search([("code", "=", a.get("trade"))], limit=1)
        if etype and trade:
            etype.trade_ids = [(3 if trade in etype.trade_ids else 4, trade.id)]
        return {}

    def _op_dtype_flag(self, a):
        self._check_owner()
        dtype = self.env["rvt.drawing.type"].browse(int(a.get("id") or 0)).exists()
        if dtype and a.get("flag") in ("client", "appr"):
            if a["flag"] == "client":
                dtype.write({"for_client": not dtype.for_client,
                             "needs_client_approval": dtype.needs_client_approval and not dtype.for_client})
            elif dtype.for_client:
                dtype.needs_client_approval = not dtype.needs_client_approval
        return {}

    def _op_add_trade(self, a):
        self._check_owner()
        name = (a.get("name") or "").strip()
        if not name:
            raise UserError(self.env._("Type the trade's name."))
        Trade = self.env["rvt.trade"]
        code = re.sub(r"[^a-z0-9]", "", name.lower())[:8] or "trade"
        base, n = code, 1
        while Trade.with_context(active_test=False).search_count([("code", "=", code)]):
            n += 1
            code = "%s%s" % (base, n)
        trade = Trade.create({
            "name": name, "short_name": name[:5], "code": code,
            "sequence": (max(Trade.search([]).mapped("sequence") or [0]) + 10)})
        for lang, value in (("gu_IN", a.get("gu")), ("hi_IN", a.get("hi"))):
            if (value or "").strip():
                trade.with_context(lang=lang).write({"name": value.strip(), "short_name": value.strip()[:6]})
        return {"id": code}

    def _op_add_agency(self, a):
        name = (a.get("name") or "").strip()
        if not name:
            raise UserError(self.env._("Type the agency's name."))
        Partner = self.env["res.partner"].sudo()
        trades = self.env["rvt.trade"].search([("code", "in", a.get("trades") or [])])
        agency = Partner.create({
            "name": name, "rvt_is_agency": True, "rvt_trade_ids": [(6, 0, trades.ids)],
            "lang": LANG_IN.get(a.get("lang"), "en_US")})
        person = (a.get("person") or "").strip()
        if person:
            Partner.create({"name": person, "phone": (a.get("phone") or "").strip() or False,
                            "parent_id": agency.id, "lang": agency.lang})
        return {"id": "a%s" % agency.id}

    def _op_role(self, a):
        self._check_owner()
        user = self.env["res.users"].browse(_num(a.get("user"))).exists()
        role = a.get("role")
        if not user or role not in ("owner", "principal", "designer", "coordinator"):
            raise UserError(self.env._("Choose a person and a role."))
        roles = set(r for r in user.rvt_roles() if r in ("owner", "principal", "designer", "coordinator"))
        roles ^= {role}
        if role == "owner" and "owner" not in roles and user == self.env.user:
            raise UserError(self.env._("You cannot take the owner role away from yourself."))
        user.rvt_set_roles(sorted(roles))
        return {}
