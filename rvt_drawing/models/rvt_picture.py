"""What the project picture learns from drawings: their progress, rules B2, B3, B4, B8, B9,
the next actions for designers, the principal and coordinators, and "working without a drawing"."""
from datetime import timedelta

from odoo import api, models

from odoo.addons.rvt_project.models.rvt_picture import day_month, plural, short_name


def working_days(start, end):
    """Days from start to end without Sundays (the office works six days)."""
    days, day = 0, start
    while day < end:
        day += timedelta(days=1)
        if day.weekday() != 6:
            days += 1
    return days


class ProjectProject(models.Model):
    _inherit = "project.project"

    # ------------------------------------------------------------------
    def _rvt_picture_ctx(self):
        ctx = super()._rvt_picture_ctx()
        drawings = self.env["rvt.drawing"].sudo().search([("project_id", "=", self.id)], order="due_date, id")
        waiting = {}
        for line in ctx["lines"]:
            if line.rvt_work_state == "waiting" and line.rvt_wait_drawing_id:
                waiting.setdefault((line.rvt_wait_cause, line.rvt_wait_drawing_id.id), self.env["project.task"])
                waiting[(line.rvt_wait_cause, line.rvt_wait_drawing_id.id)] |= line
        ctx.update({
            "drawings": drawings,
            "released": drawings.filtered(lambda d: d.state == "released"),
            "waiting_drawing": waiting,
            "principal": ctx["project"].rvt_principal_id,
            "local": self.env["rvt.config"].to_date,
        })
        return ctx

    def _rvt_wait_text(self, line, ctx):
        drawing = line.rvt_wait_drawing_id
        if line.rvt_wait_cause == "drawing" and drawing:
            return "%s %s" % (drawing.sheet_no, drawing.name)
        if line.rvt_wait_cause == "client" and drawing:
            return self.env._("client: approve %s", drawing.name)
        return super()._rvt_wait_text(line, ctx)

    def _rvt_waiting_since(self, lines, today):
        return max([(today - l.rvt_wait_since).days for l in lines if l.rvt_wait_since] or [0])

    def _rvt_drawing_action(self, drawing):
        if drawing.state == "awaiting_approval":
            return {"key": "approve", "label": self.env._("Approve"), "drawing_id": drawing.id}
        if drawing.state == "approved":
            return {"key": "release", "label": self.env._("Release"), "drawing_id": drawing.id}
        return {"key": "dwg", "label": self.env._("Open"), "drawing_id": drawing.id}

    def _rvt_unopened(self, ctx):
        """(drawing, receipt, days) for every agency that has not opened a released drawing in time."""
        limit = ctx["limits"]["limit_not_opened_days"]
        out = []
        for drawing in ctx["released"]:
            for receipt in drawing.released_revision_id.receipt_ids:
                if receipt.kind != "agency" or receipt.opened_on or not receipt.sent_on:
                    continue
                days = (ctx["today"] - ctx["local"](receipt.sent_on)).days
                if days >= limit:
                    out.append((drawing, receipt, days))
        return out

    # ------------------------------------------------------------------
    # blockers
    # ------------------------------------------------------------------
    @api.model
    def _rvt_blocker_rules(self):
        rules = super()._rvt_blocker_rules()
        at = rules.index("_rvt_b1_trade_undecided") + 1
        rules[at:at] = ["_rvt_b2_b3_drawing_not_released", "_rvt_b4_client_approval"]
        return rules + ["_rvt_b8_drawing_not_opened", "_rvt_b9_question_unanswered"]

    def _rvt_b2_b3_drawing_not_released(self, ctx):
        """B2: a work line waits for a drawing. B3: a required drawing is past its due date and not released."""
        out = []
        today = ctx["today"]
        for drawing in ctx["drawings"]:
            if drawing.state == "released":
                continue
            waiting = ctx["waiting_drawing"].get(("drawing", drawing.id), self.env["project.task"])
            late = drawing.due_date and drawing.due_date < today
            if not waiting and not late:
                continue
            awaiting = drawing.state == "awaiting_approval"
            actor = ctx["principal"] if awaiting else drawing.designer_id
            plan = ctx["plan"].get(drawing.trade_id.id)
            agency = plan.agency_id if plan else self.env["res.partner"]
            if waiting:
                holds = self.env._("%s waiting", plural(len(waiting), self.env._("work line")))
                if agency:
                    holds += " · %s" % agency.name
            else:
                holds = self.env._("lines of %s", drawing.trade_id.name or self.env._("all trades"))
            out.append({
                "rule": "B2" if waiting else "B3", "critical": False,
                "text": self.env._("%(sheet)s %(title)s not released", sheet=drawing.sheet_no, title=drawing.name),
                "holds": holds,
                "actor": (self.env._("%s (approve)", short_name(actor.name)) if awaiting else short_name(actor.name)) or self.env._("Designer"),
                "who": actor.ids,
                "age": max((today - drawing.due_date).days if drawing.due_date else 0, self._rvt_waiting_since(waiting, today), 0),
                "action": self._rvt_drawing_action(drawing),
            })
        return out

    def _rvt_b4_client_approval(self, ctx):
        """B4 (drawings): the client has not approved a released drawing after two days."""
        out = []
        client = ctx["project"].rvt_client_id.name or self.env._("The client")
        for drawing in ctx["released"]:
            revision = drawing.released_revision_id
            if revision.client_decision != "pending" or not revision.released_on:
                continue
            days = (ctx["today"] - ctx["local"](revision.released_on)).days
            if days < 2:
                continue
            waiting = ctx["waiting_drawing"].get(("client", drawing.id), self.env["project.task"])
            out.append({
                "rule": "B4", "critical": False,
                "text": self.env._("Client: approve %(title)s rev %(rev)s", title=drawing.name, rev=revision.number),
                "holds": ", ".join(self._rvt_line_label(l) for l in waiting) or self.env._("the drawings that follow it"),
                "actor": client, "who": ctx["coords"].ids, "age": days,
                "action": {"key": "remind", "label": self.env._("Remind"), "project_id": self.id, "client": True,
                           "text": self.env._("Please have a look at %s and give your go-ahead.", drawing.name)},
            })
        return out

    def _rvt_b8_drawing_not_opened(self, ctx):
        """B8: a released drawing is not opened by an agency after N days."""
        out = []
        for drawing, receipt, days in self._rvt_unopened(ctx):
            out.append({
                "rule": "B8", "critical": False,
                "text": self.env._("%(agency)s has not opened %(sheet)s %(title)s",
                                   agency=receipt.partner_id.name, sheet=drawing.sheet_no, title=drawing.name),
                "holds": self.env._("its %s lines", drawing.trade_id.name) if drawing.trade_id else self.env._("its lines"),
                "actor": self.env._("%s (chase)", ctx["first_coord"]), "who": ctx["coords"].ids, "age": days,
                "action": {"key": "remind", "label": self.env._("Remind"), "project_id": self.id, "agency_id": receipt.partner_id.id,
                           "text": self.env._("Please open %(sheet)s %(title)s.", sheet=drawing.sheet_no, title=drawing.name)},
            })
        return out

    def _rvt_b9_question_unanswered(self, ctx):
        """B9: a question on a drawing is unanswered after N working days."""
        out = []
        limit = ctx["limits"]["limit_question_days"]
        client = ctx["project"].rvt_client_id
        for drawing in ctx["drawings"]:
            for question in drawing.question_ids.filtered(lambda q: q.state == "open"):
                if working_days(ctx["local"](question.asked_on), ctx["today"]) < limit:
                    continue
                by_client = question.partner_id == client or question.partner_id in ctx["project"].rvt_client_contact_ids
                out.append({
                    "rule": "B9", "critical": False,
                    "text": self.env._("Question on %s unanswered", drawing.sheet_no),
                    "sub": "“%s” · %s" % (question.text, question.asked_by_name or question.partner_id.name),
                    "holds": self.env._("the client") if by_client else self.env._("%s’s lines", question.partner_id.name),
                    "actor": short_name(drawing.designer_id.name) or self.env._("Designer"), "who": drawing.designer_id.ids,
                    "age": (ctx["today"] - ctx["local"](question.asked_on)).days,
                    "action": {"key": "dwg", "label": self.env._("Answer"), "drawing_id": drawing.id},
                })
        return out

    # ------------------------------------------------------------------
    # next actions
    # ------------------------------------------------------------------
    @api.model
    def _rvt_next_builders(self):
        builders = super()._rvt_next_builders()
        at = builders.index("_rvt_next_agencies")
        builders[at:at] = ["_rvt_next_chase"]
        return ["_rvt_next_drawings"] + builders + ["_rvt_next_client_approvals"]

    def _rvt_next_drawings(self, ctx, nxt):
        today, principal = ctx["today"], ctx["principal"]
        limit = ctx["limits"]["limit_question_days"]
        for drawing in ctx["drawings"]:
            waiting = ctx["waiting_drawing"].get(("drawing", drawing.id), self.env["project.task"])
            warn = ""
            if waiting:
                plan = ctx["plan"].get(drawing.trade_id.id)
                who = plan.agency_id.name if plan and plan.agency_id else plural(len(waiting), self.env._("line"))
                warn = self.env._("%(who)s waiting · %(days)s", who=who, days=self._rvt_days(self._rvt_waiting_since(waiting, today)))
            revision = drawing.current_revision_id
            designer = drawing.designer_id
            sheet = "%s %s" % (drawing.sheet_no, drawing.name)
            if drawing.state in ("to_draw", "in_progress"):
                revised = revision.number > 1
                previous = drawing.revision_ids.filtered(lambda r: r.number == revision.number - 1)
                changed = revised and previous.client_decision == "change"
                sub = self.env._("due %s", self._rvt_due_word(drawing.due_date, today)) if drawing.due_date else ""
                if changed:
                    sub += self.env._(" · client asked for a change")
                elif revision.back_note:
                    sub += self.env._(" · sent back: %s", revision.back_note)
                nxt["revert"].append({
                    "section": "change" if changed else "draw", "who": designer.ids, "who_name": short_name(designer.name),
                    "text": (self.env._("Revise %s", sheet) if revised else self.env._("Draw and send %s", sheet)),
                    "sub": sub, "warn": warn, "late": bool(drawing.due_date and drawing.due_date < today),
                    "action": {"key": "dwg", "label": self.env._("Open"), "drawing_id": drawing.id},
                })
            elif drawing.state == "awaiting_approval":
                sent = ctx["local"](revision.sent_on) if revision.sent_on else today
                nxt["revert"].append({
                    "section": "approve", "who": principal.ids, "who_name": short_name(principal.name),
                    "text": self.env._("Approve %(sheet)s rev %(rev)s", sheet=sheet, rev=revision.number),
                    "sub": self.env._("sent by %(who)s · %(when)s", who=short_name(revision.sent_by_id.name),
                                      when=self.env._("today") if sent == today else day_month(sent)),
                    "warn": warn, "late": False,
                    "action": {"key": "approve", "label": self.env._("Approve"), "drawing_id": drawing.id},
                })
            elif drawing.state == "approved":
                nxt["revert"].append({
                    "section": "release", "who": (designer | principal).ids, "who_name": short_name(designer.name or principal.name),
                    "text": self.env._("Release %(sheet)s rev %(rev)s", sheet=sheet, rev=revision.number),
                    "sub": self.env._("approved by %s", short_name(revision.approved_by_id.name)), "warn": warn, "late": False,
                    "action": {"key": "release", "label": self.env._("Release"), "drawing_id": drawing.id},
                })
            for question in drawing.question_ids.filtered(lambda q: q.state == "open"):
                nxt["revert"].append({
                    "section": "question", "who": designer.ids, "who_name": short_name(designer.name),
                    "text": self.env._("Answer on %s", sheet),
                    "sub": "“%s” · %s%s" % (question.text, question.asked_by_name or question.partner_id.name,
                                            self.env._(" · photo") if question.photo else ""),
                    "warn": "", "late": working_days(ctx["local"](question.asked_on), today) >= limit,
                    "action": {"key": "dwg", "label": self.env._("Answer"), "drawing_id": drawing.id},
                })

    def _rvt_next_chase(self, ctx, nxt):
        for drawing, receipt, days in self._rvt_unopened(ctx):
            nxt["revert"].append({
                "section": "chase", "who": ctx["coords"].ids, "who_name": ctx["first_coord"],
                "text": self.env._("Chase %(agency)s to open %(sheet)s", agency=receipt.partner_id.name, sheet=drawing.sheet_no),
                "sub": self.env._("released %s ago, not opened", self._rvt_days(days)), "warn": "", "late": True,
                "action": {"key": "remind", "label": self.env._("Remind"), "project_id": self.id, "agency_id": receipt.partner_id.id,
                           "text": self.env._("Please open %(sheet)s %(title)s.", sheet=drawing.sheet_no, title=drawing.name)},
            })

    def _rvt_agency_summary(self, agency, ctx):
        row = super()._rvt_agency_summary(agency, ctx)
        unopened = ctx["released"].filtered(lambda d: any(
            r.partner_id == agency and not r.opened_on for r in d.released_revision_id.receipt_ids))
        if unopened:
            row["unopened"] = len(unopened)
            row["sub"] = self.env._("has not opened %s", ", ".join(unopened.mapped("sheet_no")))
            row["remind"] = self.env._("Please open %s.", ", ".join("%s %s" % (d.sheet_no, d.name) for d in unopened))
        return row

    def _rvt_next_client_approvals(self, ctx, nxt):
        for drawing in ctx["released"]:
            revision = drawing.released_revision_id
            if revision.client_decision != "pending":
                continue
            days = (ctx["today"] - ctx["local"](revision.released_on)).days if revision.released_on else 0
            nxt["client"].append({
                "text": self.env._("Approve %(title)s rev %(rev)s", title=drawing.name, rev=revision.number),
                "sub": self.env._("sent %s ago", self._rvt_days(days)) if days else self.env._("sent today"),
                "late": days >= 2,
                "remind": self.env._("Please have a look at %s and give your go-ahead.", drawing.name),
                "drawing_id": drawing.id,
            })

    # ------------------------------------------------------------------
    # progress
    # ------------------------------------------------------------------
    def _rvt_progress(self, ctx):
        picture = super()._rvt_progress(ctx)
        drawings, released = ctx["drawings"], ctx["released"]
        week_ago = ctx["today"] - timedelta(days=7)
        picture["progress"]["drawings"] = [len(released), len(drawings)]
        picture["week"]["released"] = len(released.filtered(
            lambda d: d.released_revision_id.released_on and ctx["local"](d.released_revision_id.released_on) > week_ago))
        # a line marked Working whose trade has drawings on the list but none released yet
        with_drawings = drawings.trade_id
        with_released = released.trade_id
        picture["working_without_drawing"] = ctx["lines"].filtered(
            lambda l: l.rvt_work_state == "working" and l.rvt_trade_id in with_drawings and l.rvt_trade_id not in with_released).ids
        return picture
