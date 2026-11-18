import re
from datetime import timedelta

from odoo import api, fields, models
from odoo.exceptions import AccessError, UserError

from odoo.addons.rvt_base.models.rvt_entity_type import SITE_KINDS

HONORIFIC = re.compile(r"^\s*(mr|mrs|ms|miss|dr|shri|smt|ar)\.?\s+", re.I)
# hand-made tasks that only exist to hang MOM entries on are not offered as rooms
NOT_A_ROOM = re.compile(r"^\s*\d|mom", re.I)


def _norm(text):
    return " ".join((text or "").lower().split())


class ProjectProject(models.Model):
    _inherit = "project.project"

    # ---- client and site ----------------------------------------------
    rvt_client_id = fields.Many2one("res.partner", string="Client", ondelete="restrict", tracking=True)
    rvt_client_contact_ids = fields.Many2many(
        "res.partner", "rvt_project_client_contact_rel", "project_id", "partner_id", string="Client contacts",
        help="The people of the client who may see this project's drawings and pending items.")
    rvt_site_address = fields.Char(string="Site address")
    rvt_site_area = fields.Char(string="Area", help="The locality, as people say it: Bopal, Satellite.")
    rvt_site_kind = fields.Selection(SITE_KINDS, string="Type of site")
    rvt_site_label = fields.Char(string="Site in a few words", help="For example: 3 BHK + garden.")
    rvt_billed_to_default = fields.Selection(
        [("client", "The client"), ("revert", "Revert")], string="Bills normally addressed to", default="client",
        help="A default for this project. It can be changed bill by bill.")

    # ---- team ----------------------------------------------------------
    rvt_principal_id = fields.Many2one(
        "res.users", string="Principal consultant", tracking=True,
        domain=lambda self: [("all_group_ids", "in", self.env.ref("rvt_base.group_rvt_principal").ids)])
    rvt_designer_ids = fields.Many2many(
        "res.users", "rvt_project_designer_rel", "project_id", "user_id", string="Designers",
        domain=lambda self: [("all_group_ids", "in", self.env.ref("rvt_base.group_rvt_staff").ids)])
    rvt_coordinator_ids = fields.Many2many(
        "res.users", "rvt_project_coordinator_rel", "project_id", "user_id", string="Coordinators",
        domain=lambda self: [("all_group_ids", "in", self.env.ref("rvt_base.group_rvt_staff").ids)])

    # ---- onboarding ----------------------------------------------------
    rvt_onboarded = fields.Boolean(string="Onboarded", copy=False, tracking=True, index=True)
    rvt_onboarded_on = fields.Date(string="Onboarded on", copy=False)
    rvt_trade_plan_ids = fields.One2many("rvt.project.trade", "project_id", string="Trade plan")
    rvt_entity_ids = fields.One2many(
        "project.task", "project_id", string="Rooms and zones", domain=[("rvt_kind", "=", "entity")])
    rvt_agency_ids = fields.Many2many(
        "res.partner", "rvt_project_agency_rel", "project_id", "partner_id", string="Agencies on the project",
        compute="_compute_rvt_agency_ids", store=True,
        help="Every agency on the trade plan or on a work line. This is what gives an agency its access.")

    @api.depends("rvt_trade_plan_ids.agency_id", "task_ids.rvt_agency_id")
    def _compute_rvt_agency_ids(self):
        Task = self.env["project.task"].sudo()
        for project in self:
            agencies = project.rvt_trade_plan_ids.agency_id
            if project.id:
                agencies |= Task.search([
                    ("project_id", "=", project.id), ("rvt_kind", "=", "work"), ("rvt_agency_id", "!=", False),
                ]).rvt_agency_id
            project.rvt_agency_ids = agencies

    # ------------------------------------------------------------------
    # access helpers
    # ------------------------------------------------------------------
    def _rvt_team_users(self):
        self.ensure_one()
        return self.rvt_principal_id | self.rvt_designer_ids | self.rvt_coordinator_ids

    @api.model
    def _rvt_check_staff(self):
        user = self.env.user
        if not (self.env.su or user.has_group("rvt_base.group_rvt_staff") or user.has_group("base.group_system")):
            raise AccessError(self.env._("Only Revert staff can do this."))

    # ------------------------------------------------------------------
    # onboarding: proposal, present state, apply
    # ------------------------------------------------------------------
    @api.model
    def rvt_onboard_proposal(self, preset_id=None):
        """What a preset proposes: its entities with the trades usually working in each,
        and the trades usually on a project."""
        self._rvt_check_staff()
        preset = self.env["rvt.site.preset"].browse(preset_id).exists() if preset_id else self.env["rvt.site.preset"]
        if preset:
            entities = preset.rvt_entities()
        else:
            whole = self.env["rvt.entity.type"].search([("is_whole_site", "=", True)], limit=1)
            entities = [{"name": whole.name, "entity_type_id": whole.id, "trade_ids": whole.trade_ids.ids}] if whole else []
        return {
            "preset_id": preset.id or False,
            "site_kind": preset.site_kind if preset else False,
            "site_label": preset.name if preset else False,
            "entities": entities,
            "usual_trade_ids": self.env["rvt.trade"].search([("is_usual", "=", True)]).ids,
        }

    def rvt_onboard_state(self):
        """The present configuration of a project, in the shape ``rvt_onboard`` takes,
        so that "Project configuration" opens on what is there."""
        self.ensure_one()
        self._rvt_check_staff()
        self.check_access("read")
        project = self.sudo()
        entities = project.rvt_entity_ids.sorted(lambda t: (t.sequence, t.id))
        lines = self.env["project.task"].sudo().search([("project_id", "=", self.id), ("rvt_kind", "=", "work")])
        contact = project.rvt_client_contact_ids[:1]
        hand_made = self.env["project.task"].sudo().search([
            ("project_id", "=", self.id), ("parent_id", "=", False), ("rvt_kind", "=", False)], order="sequence, id")
        return {
            "project_id": self.id,
            "onboarded": project.rvt_onboarded,
            "name": project.name,
            "client_id": project.rvt_client_id.id or project.partner_id.id or False,
            "client_name": project.rvt_client_id.name or project.partner_id.name or "",
            "client_phone": contact.phone or project.rvt_client_id.phone or "",
            "client_contacts": [{"id": c.id, "name": c.name, "phone": c.phone or ""} for c in project.rvt_client_contact_ids],
            "site_address": project.rvt_site_address or "",
            "site_area": project.rvt_site_area or "",
            "site_kind": project.rvt_site_kind or "home",
            "site_label": project.rvt_site_label or "",
            "billed_to": project.rvt_billed_to_default or "client",
            "principal_id": project.rvt_principal_id.id or False,
            "designer_ids": project.rvt_designer_ids.ids,
            "coordinator_ids": project.rvt_coordinator_ids.ids,
            "entities": [{
                "key": "id:%s" % e.id, "id": e.id, "name": e.name,
                "entity_type_id": e.rvt_entity_type_id.id or False,
            } for e in entities],
            "trades": [{
                "trade_id": p.trade_id.id, "agency_id": p.agency_id.id or False,
                "contact_ids": p.contact_ids.ids,
                "decide_by": fields.Date.to_string(p.decide_by) if p.decide_by else False,
                "lines": p.line_count,
            } for p in project.rvt_trade_plan_ids],
            "ticks": [["id:%s" % l.parent_id.id, l.rvt_trade_id.id] for l in lines],
            "earlier_tasks": [{"id": t.id, "name": t.name} for t in hand_made if not NOT_A_ROOM.search(t.name or "")],
        }

    @api.model
    def rvt_onboard(self, vals):
        """Set a project up, or complete it later, in one transaction.

        ``vals`` (every key optional except ``name`` for a new project)::

            project_id        an existing project; empty = create one
            name, client_id | client_name, client_phone, client_contacts [{id | name, phone}]
            site_address, site_area, site_kind, site_label, billed_to
            principal_id, designer_ids, coordinator_ids
            entities   [{key, id | task_id, name, entity_type_id}]
                       id = an entity that exists; task_id = a hand-made room task to use as an entity
            trades     [{trade_id, agency_id, contact_ids, decide_by, note}]
            ticks      [[entity key, trade_id], …]  the complete set of ticked cells for the
                       entities and trades listed. Without it, a new entity takes the usual
                       trades of its type.

        Calling it again adds what is new and never duplicates. A cell that is no longer
        ticked is removed only while its work has not started.
        """
        self._rvt_check_staff()
        vals = dict(vals or {})
        project = self.browse(vals.get("project_id")).exists() if vals.get("project_id") else self.browse()
        if project:
            project.check_access("read")
        elif not (vals.get("name") or "").strip():
            raise UserError(self.env._("Give the project a name first."))
        result = {"new": not project, "entities_created": 0, "lines_created": 0, "lines_removed": 0, "plan_removed": 0}
        # the caller is staff and may see the project; from here the set-up is the system's work
        self_sudo = self.sudo()
        project = project.sudo()
        pvals = self_sudo._rvt_onboard_project_vals(vals, project)
        if project:
            project.write(pvals)
        else:
            project = self_sudo.create(pvals)
        result["project_id"] = project.id

        key_to_entity = project._rvt_onboard_entities(vals.get("entities") or [], result)
        if "trades" in vals:
            project._rvt_onboard_trades(vals.get("trades") or [], result)
        project._rvt_onboard_ticks(vals, key_to_entity, result)
        if "trades" in vals:
            # a trade taken off the project goes when no work line needs it any more
            listed = {t["trade_id"] for t in vals.get("trades") or []}
            stale = project.rvt_trade_plan_ids.filtered(lambda p: p.trade_id.id not in listed and not p.line_count)
            result["plan_removed"] = len(stale)
            stale.unlink()
        project._rvt_onboard_extra(vals, result)
        if not project.rvt_onboarded:
            project.write({"rvt_onboarded": True, "rvt_onboarded_on": fields.Date.context_today(self)})
        return result

    @api.model
    def _rvt_onboard_project_vals(self, vals, project):
        out = {}
        simple = {
            "name": "name", "site_address": "rvt_site_address", "site_area": "rvt_site_area",
            "site_kind": "rvt_site_kind", "site_label": "rvt_site_label", "billed_to": "rvt_billed_to_default",
            "principal_id": "rvt_principal_id",
        }
        for key, field in simple.items():
            if key in vals:
                value = vals[key]
                out[field] = value.strip() if isinstance(value, str) else (value or False)
        for key, field in (("designer_ids", "rvt_designer_ids"), ("coordinator_ids", "rvt_coordinator_ids")):
            if key in vals:
                out[field] = [(6, 0, list(vals[key] or []))]
        if not project and "rvt_principal_id" not in out:
            principal = self.env.ref("rvt_base.group_rvt_principal").sudo().user_ids.filtered(
                lambda u: "principal" in u.rvt_roles())[:1]
            out["rvt_principal_id"] = principal.id
        if not project:
            out.setdefault("rvt_site_kind", "home")
        out.update(self._rvt_onboard_client_vals(vals, project))
        return out

    @api.model
    def _rvt_onboard_client_vals(self, vals, project):
        Partner = self.env["res.partner"].sudo()
        out = {}
        client = project.rvt_client_id
        if vals.get("client_id"):
            client = Partner.browse(vals["client_id"]).exists()
        elif (vals.get("client_name") or "").strip():
            name = vals["client_name"].strip()
            if not client and project.partner_id and _norm(project.partner_id.name) == _norm(name):
                client = project.partner_id
            if not client or _norm(client.name) != _norm(name):
                client = Partner.create({"name": name})
        if client and client != project.rvt_client_id:
            out["rvt_client_id"] = client.id
            if not project or not project.partner_id:
                out["partner_id"] = client.id
        contacts = project.rvt_client_contact_ids
        if client and project.rvt_client_id and client != project.rvt_client_id:
            contacts = Partner
        if "client_contacts" in vals:
            contacts = Partner
            for row in vals["client_contacts"] or []:
                if row.get("id"):
                    person = Partner.browse(row["id"]).exists()
                    if person and row.get("phone") and row["phone"] != person.phone:
                        person.phone = row["phone"]
                elif (row.get("name") or "").strip():
                    person = Partner.create({
                        "name": row["name"].strip(), "phone": row.get("phone") or False,
                        "parent_id": client.id if client else False, "type": "contact"})
                else:
                    continue
                contacts |= person
        phone = (vals.get("client_phone") or "").strip()
        if client and not contacts:
            # the first contact is the client in person: the name without "Mr." and the number given
            person = Partner.create({
                "name": HONORIFIC.sub("", client.name) or client.name, "phone": phone or client.phone or False,
                "parent_id": client.id, "type": "contact"})
            contacts = person
        elif phone and contacts and "client_contacts" not in vals and contacts[0].phone != phone:
            contacts[0].phone = phone
        if contacts != project.rvt_client_contact_ids:
            out["rvt_client_contact_ids"] = [(6, 0, contacts.ids)]
        return out

    def _rvt_onboard_entities(self, rows, result):
        """Create or update the entity tasks; return {payload key: task}."""
        self.ensure_one()
        Task = self.env["project.task"].sudo()
        existing = {e.id: e for e in self.rvt_entity_ids}
        by_name = {_norm(e.name): e for e in self.rvt_entity_ids}
        other = self.env["rvt.entity.type"].sudo().search([("is_whole_site", "=", False)], order="sequence desc", limit=1)
        sequence = max(self.rvt_entity_ids.mapped("sequence") or [0])
        out = {}
        for index, row in enumerate(rows):
            name = (row.get("name") or "").strip()
            etype = row.get("entity_type_id") or False
            entity = existing.get(row.get("id")) if row.get("id") else None
            if entity is None and row.get("task_id"):
                task = Task.browse(row["task_id"]).exists()
                if not task or task.project_id != self or task.parent_id or task.rvt_kind == "work":
                    raise UserError(self.env._("That task cannot be used as a room of this project."))
                task.write({"rvt_kind": "entity", "rvt_entity_type_id": etype or task.rvt_entity_type_id.id})
                entity = task
                by_name[_norm(task.name)] = task
            if entity is None and name and _norm(name) in by_name:
                entity = by_name[_norm(name)]
            if entity is None:
                if not name:
                    raise UserError(self.env._("Every room or zone needs a name."))
                sequence += 1
                entity = Task.create({
                    "name": name, "project_id": self.id, "rvt_kind": "entity",
                    "rvt_entity_type_id": etype or other.id, "sequence": sequence,
                    "user_ids": False,  # a room is nobody's personal task
                })
                by_name[_norm(name)] = entity
                result["entities_created"] += 1
                out.setdefault("_new", []).append(entity.id)
            else:
                changes = {}
                if name and name != entity.name:
                    changes["name"] = name
                if etype and etype != entity.rvt_entity_type_id.id:
                    changes["rvt_entity_type_id"] = etype
                if changes:
                    entity.write(changes)
            out[row.get("key") or "id:%s" % entity.id] = entity
            out["id:%s" % entity.id] = entity
        return out

    def _rvt_onboard_trades(self, rows, result):
        self.ensure_one()
        Plan = self.env["rvt.project.trade"].sudo()
        Partner = self.env["res.partner"].sudo()
        plans = {p.trade_id.id: p for p in self.rvt_trade_plan_ids}
        today = fields.Date.context_today(self)
        for row in rows:
            trade_id = row.get("trade_id")
            if not trade_id:
                continue
            agency = Partner.browse(row.get("agency_id")).exists() if row.get("agency_id") else Partner
            plan = plans.get(trade_id)
            values = {"agency_id": agency.id or False}
            if "note" in row:
                values["note"] = row["note"] or False
            if agency:
                values["decide_by"] = False
                if "contact_ids" in row:
                    values["contact_ids"] = [(6, 0, list(row["contact_ids"] or []))]
                elif not plan or plan.agency_id != agency:
                    first = Partner.search([("parent_id", "=", agency.id)], order="id", limit=1)
                    values["contact_ids"] = [(6, 0, first.ids)]
            else:
                values["decide_by"] = row.get("decide_by") or (plan.decide_by if plan and plan.decide_by else today + timedelta(days=7))
            if plan:
                changed = {k: v for k, v in values.items() if k == "contact_ids" or plan[k] != (v if k != "agency_id" else agency)}
                if plan.agency_id == agency:
                    changed.pop("agency_id", None)
                if changed:
                    plan.write(changed)
            else:
                plans[trade_id] = Plan.create(dict(values, project_id=self.id, trade_id=trade_id))

    def _rvt_onboard_ticks(self, vals, key_to_entity, result):
        """Create the work lines for the ticked cells and drop unticked ones that have not started."""
        self.ensure_one()
        Task = self.env["project.task"].sudo()
        new_ids = set(key_to_entity.pop("_new", []))
        entities = {e.id: e for e in key_to_entity.values()}
        if not entities:
            return
        plan_trades = self.rvt_trade_plan_ids.trade_id
        listed = self.env["rvt.trade"].browse([t["trade_id"] for t in vals.get("trades") or [] if t.get("trade_id")]) \
            if "trades" in vals else plan_trades
        lines = Task.search([("project_id", "=", self.id), ("rvt_kind", "=", "work"), ("parent_id", "in", list(entities))])
        have = {(l.parent_id.id, l.rvt_trade_id.id): l for l in lines}
        if vals.get("ticks") is not None:
            wanted = set()
            for key, trade_id in vals["ticks"]:
                entity = key_to_entity.get(key) or key_to_entity.get("id:%s" % key)
                if entity:
                    wanted.add((entity.id, trade_id))
        else:
            # no grid sent: a new entity takes the usual trades of its type; what exists stays
            wanted = set(have)
            for entity in entities.values():
                if entity.id in new_ids:
                    wanted |= {(entity.id, t.id) for t in entity.rvt_entity_type_id.trade_ids & listed}
        to_create = []
        for entity in entities.values():
            for trade in listed:
                cell = (entity.id, trade.id)
                line = have.get(cell)
                if cell in wanted and not line:
                    to_create.append({
                        "name": trade.name, "project_id": self.id, "parent_id": entity.id,
                        "rvt_kind": "work", "rvt_trade_id": trade.id, "sequence": trade.sequence,
                        "user_ids": False,
                    })
                elif cell not in wanted and line and line._rvt_can_remove():
                    line.unlink()
                    result["lines_removed"] += 1
        if to_create:
            Task.create(to_create)
            result["lines_created"] += len(to_create)

    def _rvt_onboard_extra(self, vals, result):
        """Hook for later phases: drawings (P4), invitations (P6)."""
        return

    # ------------------------------------------------------------------
    # the grid
    # ------------------------------------------------------------------
    def rvt_grid(self):
        """Entities down, trades across, one cell per work line."""
        self.ensure_one()
        self.check_access("read")
        project = self.sudo()
        entities = project.rvt_entity_ids.sorted(lambda t: (t.rvt_entity_type_id.is_whole_site, t.sequence, t.id))
        lines = self.env["project.task"].sudo().search([("project_id", "=", self.id), ("rvt_kind", "=", "work")])
        plans = project.rvt_trade_plan_ids
        trades = (plans.trade_id | lines.rvt_trade_id).sorted("sequence")
        plan_by_trade = {p.trade_id.id: p for p in plans}
        return {
            "project_id": self.id,
            "entities": [{
                "id": e.id, "name": e.name,
                "type_id": e.rvt_entity_type_id.id or False, "type": e.rvt_entity_type_id.name or "",
                "state": e.rvt_entity_state or "not_started",
                "lines": e.rvt_line_count, "done": e.rvt_line_done_count,
            } for e in entities],
            "trades": [project._rvt_grid_trade(t, plan_by_trade.get(t.id)) for t in trades],
            "cells": [project._rvt_grid_cell(l) for l in lines],
        }

    def _rvt_grid_trade(self, trade, plan):
        return {
            "id": trade.id, "code": trade.code, "name": trade.name, "short": trade.short_name,
            "plan_id": plan.id if plan else False,
            "agency_id": plan.agency_id.id if plan and plan.agency_id else False,
            "agency": plan.agency_id.name if plan and plan.agency_id else False,
            "undecided": bool(plan and not plan.agency_id),
            "decide_by": fields.Date.to_string(plan.decide_by) if plan and plan.decide_by else False,
            "late": bool(plan and plan.is_undecided_late),
        }

    def _rvt_grid_cell(self, line):
        """Hook: later phases add the open point count and the record a line waits for."""
        return line.rvt_cell()

    # ------------------------------------------------------------------
    # back-end helpers
    # ------------------------------------------------------------------
    def action_rvt_onboard_default(self):
        """Server action for administrators: set the project up from the preset that
        matches its type of site, with the usual trades. For testing the grid without the desk."""
        Preset = self.env["rvt.site.preset"]
        for project in self:
            preset = Preset.search([("site_kind", "=", project.rvt_site_kind or "home")], limit=1) or Preset.search([], limit=1)
            proposal = self.rvt_onboard_proposal(preset.id)
            trades = project.rvt_trade_plan_ids.trade_id.ids or proposal["usual_trade_ids"]
            agency_of = {p.trade_id.id: p.agency_id.id for p in project.rvt_trade_plan_ids}
            self.rvt_onboard({
                "project_id": project.id,
                "site_kind": project.rvt_site_kind or preset.site_kind,
                "site_label": project.rvt_site_label or preset.name,
                "entities": [dict(e, key="n%s" % i) for i, e in enumerate(proposal["entities"])],
                "trades": [{"trade_id": t, "agency_id": agency_of.get(t) or False} for t in trades],
            })
        return True
