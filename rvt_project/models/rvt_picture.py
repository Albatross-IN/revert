"""The project picture: progress, blockers, next actions and a status word.

Computed on reading from the live records; nothing here is stored
(docs/phase1_adoption.md §5.10 and §7.1). The desk, the app, Today and Review
all read this one method, so they cannot disagree.

Each blocker rule is one small method. Later modules append theirs to
``_rvt_blocker_rules`` and their next actions to ``_rvt_next_builders``.
"""
from datetime import timedelta

from odoo import api, fields, models

MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
WEEKDAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
TITLES = ("mr", "mrs", "ms", "miss", "dr", "shri", "smt", "ar")


def short_name(name):
    """How a person is called in a line of text: "Ar. Pranav Vora" -> "Pranav"."""
    parts = [p for p in (name or "").split() if p.strip(".").lower() not in TITLES]
    return parts[0] if parts else (name or "")


def day_month(date):
    return "%s %s" % (date.day, MONTHS[date.month - 1])


def plural(n, word, many=None):
    return "%s %s" % (n, word if n == 1 else (many or word + "s"))


class ProjectProject(models.Model):
    _inherit = "project.project"

    # ------------------------------------------------------------------
    # words
    # ------------------------------------------------------------------
    def _rvt_due_word(self, date, today):
        """A date as people say it: today, tomorrow, Fri, 12 Nov."""
        n = (date - today).days
        if n == 0:
            return self.env._("today")
        if n == 1:
            return self.env._("tomorrow")
        if n == -1:
            return self.env._("yesterday")
        if 1 < n < 7:
            return WEEKDAYS[date.weekday()]
        return day_month(date)

    def _rvt_days(self, n):
        return self.env._("today") if n <= 0 else (self.env._("1 day") if n == 1 else self.env._("%s days", n))

    def _rvt_wait_text(self, line, ctx):
        """What a waiting line waits for, in words."""
        cause = line.rvt_wait_cause
        if cause == "trade":
            trade = line.rvt_wait_trade_id
            agency = ctx["plan"].get(trade.id) and ctx["plan"][trade.id].agency_id
            return "%s%s" % (trade.name or self.env._("another trade"), " (%s)" % agency.name if agency else "")
        if cause == "drawing":
            return self.env._("a drawing")
        if cause == "client":
            return self.env._("client: a decision")
        word = self.env._("material") if cause == "material" else self.env._("other")
        return "%s%s" % (word, ": %s" % line.rvt_wait_note if line.rvt_wait_note else "")

    # ------------------------------------------------------------------
    # context: every record the rules read, fetched once
    # ------------------------------------------------------------------
    def _rvt_picture_ctx(self):
        self.ensure_one()
        project = self.sudo()
        lines = self.env["project.task"].sudo().search(
            [("project_id", "=", self.id), ("rvt_kind", "=", "work")], order="parent_id, sequence, id")
        plans = project.rvt_trade_plan_ids
        coords = project.rvt_coordinator_ids
        return {
            "today": self.env["rvt.config"].today(),
            "limits": self.env["rvt.config"].get(),
            "project": project,
            "lines": lines,
            "plans": plans,
            "plan": {p.trade_id.id: p for p in plans},
            "coords": coords,
            "coord_names": ", ".join(short_name(u.name) for u in coords) or self.env._("Coordinator"),
            "first_coord": short_name(coords[:1].name) if coords else self.env._("Coordinator"),
        }

    def _rvt_line_label(self, line):
        return "%s · %s" % (line.parent_id.name, line.rvt_trade_id.name)

    # ------------------------------------------------------------------
    # blockers
    # ------------------------------------------------------------------
    @api.model
    def _rvt_blocker_rules(self):
        """Method names, in the order of the rule numbers. Each returns a list of blockers:
        {rule, critical, text, sub, holds, actor, who (user ids), age (days), action}."""
        return ["_rvt_b1_trade_undecided", "_rvt_b5_b6_line_waits"]

    def _rvt_b1_trade_undecided(self, ctx):
        """B1: a trade is undecided past its decide-by date."""
        out = []
        for plan in ctx["plans"]:
            if plan.agency_id or not plan.decide_by or plan.decide_by >= ctx["today"]:
                continue
            held = ctx["lines"].filtered(lambda l: l.rvt_trade_id == plan.trade_id)
            out.append({
                "rule": "B1", "critical": True,
                "text": self.env._("%s agency undecided", plan.trade_id.name),
                "holds": plural(len(held), self.env._("work line")),
                "actor": ctx["coord_names"], "who": ctx["coords"].ids,
                "age": (ctx["today"] - plan.decide_by).days,
                "action": {"key": "assign", "label": self.env._("Assign"), "project_id": self.id, "trade": plan.trade_id.code},
            })
        return out

    def _rvt_b5_b6_line_waits(self, ctx):
        """B5: a work line waits for another trade. B6: it waits for material or another cause."""
        out = []
        for line in ctx["lines"]:
            if line.rvt_work_state != "waiting" or line.rvt_wait_cause not in ("trade", "material", "other"):
                continue
            by_trade = line.rvt_wait_cause == "trade"
            other = ctx["plan"].get(line.rvt_wait_trade_id.id) if by_trade else None
            agency = other.agency_id if other else self.env["res.partner"]
            if by_trade and agency:
                action = {
                    "key": "remind", "label": self.env._("Remind"), "project_id": self.id, "agency_id": agency.id,
                    "text": self.env._("%(room)s: %(trade)s is waiting for your work.",
                                       room=line.parent_id.name, trade=line.rvt_trade_id.name)}
            else:
                action = {"key": "cell", "label": self.env._("Open"), "project_id": self.id, "line_id": line.id}
            out.append({
                "rule": "B5" if by_trade else "B6", "critical": False,
                "text": self.env._("%(line)s waits for %(what)s", line=self._rvt_line_label(line), what=self._rvt_wait_text(line, ctx)),
                "holds": self.env._("this line"),
                "actor": (agency.name or line.rvt_wait_trade_id.name) if by_trade else ctx["first_coord"],
                "who": ctx["coords"].ids,
                "age": (ctx["today"] - line.rvt_wait_since).days if line.rvt_wait_since else 0,
                "action": action,
            })
        return out

    # ------------------------------------------------------------------
    # next actions
    # ------------------------------------------------------------------
    @api.model
    def _rvt_next_builders(self):
        """Method names; each fills ``nxt`` = {"revert": [], "agencies": [], "client": []}."""
        return ["_rvt_next_decide", "_rvt_next_agencies"]

    def _rvt_next_decide(self, ctx, nxt):
        for plan in ctx["plans"]:
            if plan.agency_id:
                continue
            held = ctx["lines"].filtered(lambda l: l.rvt_trade_id == plan.trade_id)
            nxt["revert"].append({
                "section": "decide", "who": ctx["coords"].ids, "who_name": ctx["first_coord"],
                "text": self.env._("Decide the %s agency", (plan.trade_id.name or "").lower()),
                "sub": self.env._("decide by %(date)s · holds %(lines)s", date=day_month(plan.decide_by),
                                  lines=plural(len(held), self.env._("line"))) if plan.decide_by else "",
                "warn": "", "late": bool(plan.decide_by and plan.decide_by < ctx["today"]),
                "action": {"key": "assign", "label": self.env._("Assign"), "project_id": self.id, "trade": plan.trade_id.code},
            })

    def _rvt_agency_summary(self, agency, ctx):
        """One agency's slice; later modules add its points and unopened drawings."""
        lines = ctx["lines"].filtered(lambda l: l.rvt_agency_id == agency)
        count = lambda state: len(lines.filtered(lambda l: l.rvt_work_state == state))
        waiting = lines.filtered(lambda l: l.rvt_work_state == "waiting")[:1]
        working = count("working")
        return {
            "agency_id": agency.id, "name": agency.name,
            "trades": ", ".join(ctx["plans"].filtered(lambda p: p.agency_id == agency).mapped("trade_id.name")),
            "points": 0, "overdue": 0, "unopened": 0,
            "lines": len(lines), "done": count("done"), "working": working, "waiting": count("waiting"),
            "sub": (self.env._("waiting for %s", self._rvt_wait_text(waiting, ctx)) if waiting
                    else self.env._("%s in hand", plural(working, self.env._("line"))) if working else ""),
            "remind": self.env._("Please share where the work stands at %s.", self.name),
        }

    def _rvt_next_agencies(self, ctx, nxt):
        seen = self.env["res.partner"]
        for plan in ctx["plans"]:
            if plan.agency_id and plan.agency_id not in seen:
                seen |= plan.agency_id
                nxt["agencies"].append(self._rvt_agency_summary(plan.agency_id, ctx))

    # ------------------------------------------------------------------
    # progress
    # ------------------------------------------------------------------
    def _rvt_progress(self, ctx):
        """Four counts, never an estimated percentage. Later modules fill drawings and points."""
        lines = ctx["lines"]
        count = lambda state: len(lines.filtered(lambda l: l.rvt_work_state == state))
        week_ago = ctx["today"] - timedelta(days=7)
        return {
            "progress": {
                "agencies": [len(ctx["plans"].filtered("agency_id")), len(ctx["plans"])],
                "drawings": [0, 0],
                "work": [count("done"), len(lines), count("working"), count("waiting")],
                "points": [0, 0, 0, 0],
            },
            "week": {
                "released": 0,
                "started": len(lines.filtered(lambda l: l.rvt_started_on and l.rvt_started_on > week_ago)),
                "done": len(lines.filtered(lambda l: l.rvt_done_on and l.rvt_done_on > week_ago)),
                "closed": 0,
            },
            "working_without_drawing": [],
        }

    # ------------------------------------------------------------------
    # the picture
    # ------------------------------------------------------------------
    def rvt_picture(self):
        """Progress, blockers, next actions and status of one project, for staff."""
        self.ensure_one()
        self._rvt_check_staff()
        self.check_access("read")
        ctx = self._rvt_picture_ctx()
        blockers = []
        for rule in self._rvt_blocker_rules():
            blockers += getattr(self, rule)(ctx)
        for blocker in blockers:
            blocker.setdefault("sub", "")
            blocker["age"] = max(blocker["age"], 0)
        blockers.sort(key=lambda b: -(999 if b["critical"] else b["age"]))
        nxt = {"revert": [], "agencies": [], "client": []}
        for builder in self._rvt_next_builders():
            getattr(self, builder)(ctx, nxt)
        for item in nxt["revert"]:
            item["project_id"] = self.id
        picture = self._rvt_progress(ctx)
        stuck_after = ctx["limits"]["limit_stuck_days"]
        if not ctx["project"].rvt_onboarded:
            status = "ok"
        elif any(b["critical"] or b["age"] >= stuck_after for b in blockers):
            status = "stuck"
        else:
            status = "attention" if blockers else "ok"
        picture.update({"project_id": self.id, "status": status, "blockers": blockers, "next": nxt})
        return picture

    def rvt_picture_summary(self):
        """One row per project for the weekly review: status, the four counts and the oldest blocker."""
        rows = []
        for project in self:
            if not project.sudo().rvt_onboarded:
                rows.append({"project_id": project.id, "name": project.name, "onboarded": False})
                continue
            picture = project.rvt_picture()
            oldest = picture["blockers"][:1]
            rows.append({
                "project_id": project.id, "name": project.name, "onboarded": True,
                "status": picture["status"], "progress": picture["progress"],
                "blockers": len(picture["blockers"]),
                "oldest": {"text": oldest[0]["text"], "age": oldest[0]["age"]} if oldest else False,
            })
        return rows

    @api.model
    def rvt_today(self, pictures=None):
        """The items where the signed-in person must act, across their projects.
        ``pictures`` = {project id: picture} when the caller has them already."""
        self._rvt_check_staff()
        user = self.env.user
        is_owner = user.has_group("rvt_base.group_rvt_owner")
        out = []
        from odoo.addons.rvt_base.models.res_users import SECTION_ACCESS
        access = user.rvt_access()
        allowed = lambda item: SECTION_ACCESS.get(item.get("section")) in (None, *access)
        projects = self.search([("rvt_onboarded", "=", True)], order="id")
        for project in projects:
            picture = (pictures or {}).get(project.id) or project.rvt_picture()
            for item in picture["next"]["revert"]:
                if (user.id in item["who"] or (item.get("office") and is_owner)) and allowed(item):
                    out.append(dict(item, project_id=project.id, project=project.name))
            p = project.sudo()
            if user in p.rvt_coordinator_ids and "mom" in access:
                client = p.rvt_client_id.name or self.env._("the client")
                for item in picture["next"]["client"]:
                    if item.get("late"):
                        out.append({
                            "section": "client", "who": [user.id], "who_name": short_name(user.name),
                            "text": self.env._("Chase %(client)s: %(what)s", client=client, what=item["text"]),
                            "sub": item.get("sub", ""), "warn": "", "late": True,
                            "project_id": project.id, "project": project.name,
                            "action": {"key": "remind", "label": self.env._("Remind"), "project_id": project.id,
                                       "client": True, "text": item.get("remind", item["text"])},
                        })
        return out
