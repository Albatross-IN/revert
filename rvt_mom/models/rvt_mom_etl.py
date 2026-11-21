"""The move of the earlier MOM entries (activities of the MOM type on tasks) into points and visits.

Run through tools/etl_mom.py. Dry run by default; nothing is written unless apply is asked.
Every entry, open or done, becomes one point that remembers the entry it came from, so a
second run creates nothing. The earlier records are not changed.
"""
import re
from collections import Counter, defaultdict

from odoo import api, models
from odoo.exceptions import UserError
import html as html_lib


def _key(name):
    return " ".join((name or "").lower().split())


def _plain(markup):
    """The words of a remark, without its formatting."""
    text = re.sub(r"(?i)<br\s*/?>|</p>|</div>|</li>|</h[1-6]>", "\n", str(markup or ""))
    text = html_lib.unescape(re.sub(r"<[^>]+>", "", text))
    lines = [" ".join(line.split()) for line in text.split("\n")]
    return "\n".join(line for line in lines if line)


class RvtMomEtl(models.AbstractModel):
    _name = "rvt.mom.etl"
    _description = "Move of earlier MOM entries"

    # ------------------------------------------------------------------
    @api.model
    def _source(self):
        Activity = self.env["mail.activity"].sudo().with_context(active_test=False)
        if "mom_partner_id" not in Activity._fields:
            raise UserError(self.env._("The earlier MOM is not installed on this database; there is nothing to move."))
        types = self.env["mail.activity.type"].sudo().with_context(active_test=False).search([("is_mom", "=", True)])
        return Activity.search([("activity_type_id", "in", types.ids)], order="id")

    @api.model
    def _text(self, activity):
        summary = (activity.summary or "").strip()
        note = _plain(activity.note)
        if summary and note and _key(note) != _key(summary):
            return "%s\n%s" % (summary, note)
        return summary or note or self.env._("(no text)")

    @api.model
    def _photos(self, activities):
        """{activity id: attachment} for the site photo of each entry."""
        Attachment = self.env["ir.attachment"].sudo()
        rows = Attachment.search([
            ("res_model", "=", "mail.activity"), ("res_field", "=", "mom_site_photo"), ("res_id", "in", activities.ids)])
        return {a.res_id: a for a in rows}

    @api.model
    def _stats_before(self, activities, photos):
        stats = defaultdict(lambda: {"entries": 0, "open": 0, "closed": 0, "photos": Counter(), "visits": {}, "no_project": 0})
        for a in activities:
            project = a.mom_project_id
            s = stats[project.id]
            s["name"] = project.name or self.env._("(no project)")
            s["entries"] += 1
            s["open" if a.active else "closed"] += 1
            if a.id in photos:
                s["photos"][photos[a.id].checksum] += 1
            if a.mom_visit_date:
                s["visits"][a.mom_visit_date] = a.mom_visit_no
        return stats

    @api.model
    def _stats_after(self, project_ids):
        Point = self.env["rvt.point"].sudo()
        Attachment = self.env["ir.attachment"].sudo()
        stats = {}
        for pid in project_ids:
            points = Point.search([("project_id", "=", pid), ("legacy_activity_id", ">", 0)])
            photos = Attachment.search([
                ("res_model", "=", "rvt.point"), ("res_field", "=", "photo"), ("res_id", "in", points.ids)])
            stats[pid] = {
                "entries": len(points),
                "open": len(points.filtered(lambda p: p.state == "open")),
                "closed": len(points.filtered(lambda p: p.state == "closed")),
                "photos": Counter(photos.mapped("checksum")),
                "visits": {v.date: v.number for v in points.visit_id},
            }
        return stats

    @api.model
    def _mapping(self, rows):
        """The sheet Revert fills in: one row per person named in the earlier entries.
        Columns: person, kind (agency / client / staff / vendor), agency, trade, phone, same_as.
        ``same_as`` merges a second spelling into the first. Nothing is merged by guessing."""
        out = {}
        for row in rows or []:
            person = _key(row.get("person"))
            if person:
                out[person] = {k: (v or "").strip() for k, v in row.items()}
        return out

    @api.model
    def _party(self, activity, mapping, cache, project):
        """Where a point goes: (for_kind, partner, user, trade, mapped?)."""
        partner = activity.mom_partner_id
        empty = (self.env["res.partner"], self.env["res.users"], self.env["rvt.trade"])
        if not partner:
            return ("vendor",) + empty + (False,)
        row = mapping.get(_key(partner.name))
        if row and row.get("same_as"):
            row = mapping.get(_key(row["same_as"])) or row
        if not row or not row.get("kind") or row["kind"] == "vendor":
            return ("vendor", partner, empty[1], empty[2], bool(row))
        kind = row["kind"].lower()
        if kind == "client":
            return ("client", project.rvt_client_id or partner, empty[1], empty[2], True)
        if kind == "staff":
            user = cache["users"].get(_key(row.get("agency") or partner.name))
            return ("staff", empty[0], user or empty[1], empty[2], bool(user)) if user else ("vendor", partner, empty[1], empty[2], False)
        if kind == "agency":
            name = row.get("agency") or partner.name
            agency = cache["agencies"].get(_key(name))
            if not agency:
                agency = self.env["res.partner"].sudo().create({"name": name, "rvt_is_agency": True})
                cache["agencies"][_key(name)] = agency
            trade = cache["trades"].get(_key(row.get("trade")))
            if trade and trade not in agency.rvt_trade_ids:
                agency.rvt_trade_ids = [(4, trade.id)]
            if partner != agency and not partner.parent_id and not partner.rvt_is_agency:
                partner.write({"parent_id": agency.id, **({"phone": row["phone"]} if row.get("phone") and not partner.phone else {})})
            return ("agency", agency, empty[1], trade or empty[2], True)
        return ("vendor", partner, empty[1], empty[2], False)

    # ------------------------------------------------------------------
    @api.model
    def run(self, apply=False, mapping_rows=None):
        """Returns the verification report: per project, the figures before and after.
        With ``apply`` false nothing is written (the "after" figures are what a move would give)."""
        if not self.env.su and not self.env.user.has_group("base.group_system"):
            raise UserError(self.env._("Only an administrator moves the earlier MOM."))
        env = self.env
        Point, Visit = env["rvt.point"].sudo(), env["rvt.visit"].sudo()
        activities = self._source()
        photos = self._photos(activities)
        before = self._stats_before(activities, photos)
        done = set(Point.search([("legacy_activity_id", "in", activities.ids)]).mapped("legacy_activity_id"))
        todo = activities.filtered(lambda a: a.id not in done and a.mom_project_id)
        mapping = self._mapping(mapping_rows)
        cache = {
            "agencies": {_key(p.name): p for p in env["res.partner"].sudo().search([("rvt_is_agency", "=", True)])},
            "trades": {},
            "users": {_key(u.name): u for u in env["res.users"].sudo().search([("share", "=", False)])},
        }
        for trade in env["rvt.trade"].sudo().search([]):
            cache["trades"][_key(trade.name)] = trade
            cache["trades"][_key(trade.code)] = trade
        people = Counter()
        unmapped = Counter()
        created = 0
        if apply:
            visits = {(v.project_id.id, v.date): v for v in Visit.search([("project_id", "in", todo.mom_project_id.ids)])}
            for a in todo:
                project = a.mom_project_id
                visit = False
                if a.mom_visit_date:
                    visit = visits.get((project.id, a.mom_visit_date))
                    if not visit:
                        visit = Visit.create({
                            "project_id": project.id, "date": a.mom_visit_date, "state": "finished",
                            "started_by_id": a.create_uid.id, "attendees": False})
                        visits[(project.id, a.mom_visit_date)] = visit
                kind, partner, user, trade, mapped = self._party(a, mapping, cache, project)
                photo = photos.get(a.id)
                point = Point.create({
                    "project_id": project.id, "visit_id": visit.id if visit else False,
                    "number": a.mom_sequence or 0, "text": self._text(a),
                    "for_kind": kind, "partner_id": partner.id or False, "user_id": user.id or False,
                    "trade_id": trade.id or False,
                    "due_date": a.mom_end_date or False,
                    "state": "open" if a.active else "closed",
                    "closed_on": a.date_done if not a.active else False,
                    "closed_by_id": a.write_uid.id if not a.active else False,
                    "close_note": (a.feedback or "").strip() or False if not a.active else False,
                    "client_confirmed": True, "sent_count": 0,
                    "raised_by_id": a.create_uid.id, "raised_on": a.create_date,
                    "legacy_activity_id": a.id, "legacy_task_id": a.mom_task_id.id or False,
                    "photo": photo.raw.to_base64() if photo and photo.raw else False,
                })
                if not point.number:
                    point.number = 0
                created += 1
        for a in activities:
            if a.mom_partner_id:
                people[a.mom_partner_id.name] += 1
                row = mapping.get(_key(a.mom_partner_id.name))
                if not row or not (row.get("kind") or row.get("same_as")):
                    unmapped[a.mom_partner_id.name] += 1
        after = self._stats_after([pid for pid in before if pid]) if apply or done else {}
        rows, all_equal = [], True
        for pid, b in sorted(before.items(), key=lambda kv: kv[1]["name"]):
            a = after.get(pid)
            row = {
                "project_id": pid, "project": b["name"],
                "entries": b["entries"], "open": b["open"], "closed": b["closed"],
                "photos": sum(b["photos"].values()), "visits": len(b["visits"]),
                "after": a and {"entries": a["entries"], "open": a["open"], "closed": a["closed"],
                                "photos": sum(a["photos"].values()), "visits": len(a["visits"])},
            }
            if a is None:
                row["equal"] = None
            else:
                row["equal"] = bool(
                    pid and a["entries"] == b["entries"] and a["open"] == b["open"] and a["closed"] == b["closed"]
                    and a["photos"] == b["photos"] and a["visits"] == b["visits"])
                all_equal = all_equal and row["equal"]
            rows.append(row)
        return {
            "applied": bool(apply), "source_entries": len(activities), "already_moved": len(done),
            "to_move": len(todo), "created": created,
            "without_project": len(activities.filtered(lambda a: not a.mom_project_id)),
            "without_person": len(activities.filtered(lambda a: not a.mom_partner_id)),
            "people": sorted(people.items(), key=lambda kv: -kv[1]),
            "unmapped": sorted(unmapped.items(), key=lambda kv: -kv[1]),
            "projects": rows, "all_equal": bool(after) and all_equal,
        }

    # ------------------------------------------------------------------
    @api.model
    def switch_off_earlier_screens(self):
        """After the owner's sign-off: the MOM type can no longer be scheduled, and the MOM button
        and dashboard links leave the task and project screens. The earlier records stay."""
        if not self.env.su and not self.env.user.has_group("base.group_system"):
            raise UserError(self.env._("Only an administrator switches the earlier MOM screens off."))
        done = []
        types = self.env["mail.activity.type"].sudo().search([("is_mom", "=", True)])
        if types:
            types.write({"active": False})
            done.append("activity type archived")
        View = self.env["ir.ui.view"].sudo()
        hide = [
            ("revert_customizations.view_task_form_inherit", "rvt_mom_hide_task_buttons", """<data>
                <xpath expr="//button[@name='action_create_mom']" position="attributes"><attribute name="invisible">1</attribute></xpath>
                <xpath expr="//button[@name='action_sync_mom_activities']" position="attributes"><attribute name="invisible">1</attribute></xpath>
            </data>"""),
        ]
        for xmlid, name, arch in hide:
            parent = self.env.ref(xmlid, raise_if_not_found=False)
            if parent and not View.search([("name", "=", name)]):
                View.create({"name": name, "model": parent.model, "inherit_id": parent.id, "arch": arch, "priority": 99})
                done.append("%s hidden" % xmlid)
        for xmlid in ("revert_customizations.view_project_card_inherit_mom", "revert_customizations.edit_project_inherit_mom"):
            view = self.env.ref(xmlid, raise_if_not_found=False)
            if view and view.active:
                view.active = False
                done.append("%s off" % xmlid)
        self.env["ir.config_parameter"].sudo().set_bool("rvt.mom_earlier_screens_off", True)
        return done
