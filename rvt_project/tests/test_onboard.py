from odoo import fields
from odoo.exceptions import AccessError, UserError
from odoo.tests import tagged

from .common import RvtCommon


@tagged("post_install", "-at_install")
class TestOnboard(RvtCommon):

    def test_preset_proposal(self):
        proposal = self.Project.with_user(self.coordinator).rvt_onboard_proposal(self.preset_3bhk.id)
        names = [e["name"] for e in proposal["entities"]]
        self.assertEqual(len(names), 13)
        self.assertEqual(names[-1], "Whole site")
        usual = self.env["rvt.trade"].browse(proposal["usual_trade_ids"]).mapped("code")
        self.assertEqual(set(usual), {"civ", "tile", "elec", "plmb", "pop", "carp", "col"})
        kitchen = next(e for e in proposal["entities"] if e["name"] == "Kitchen")
        self.assertIn(self.trade["stone"].id, kitchen["trade_ids"])
        empty = self.Project.with_user(self.coordinator).rvt_onboard_proposal()
        self.assertEqual([e["name"] for e in empty["entities"]], ["Whole site"])

    def test_onboard_new_3bhk(self):
        project, result = self.onboard()
        self.assertTrue(result["new"])
        self.assertTrue(project.rvt_onboarded)
        self.assertEqual(project.rvt_onboarded_on, self.today)
        self.assertEqual(project.name, "Shah Residence")
        self.assertEqual(project.rvt_site_label, "3 BHK + garden")
        self.assertEqual(project.rvt_principal_id, self.principal)
        self.assertEqual(project.rvt_designer_ids, self.designer | self.designer2)
        self.assertEqual(project.rvt_coordinator_ids, self.coordinator)
        # client: the firm or person, and the first contact in person
        self.assertEqual(project.rvt_client_id.name, "Mr. Nirav Shah")
        self.assertEqual(project.partner_id, project.rvt_client_id)
        self.assertEqual(project.rvt_client_contact_ids.name, "Nirav Shah")
        self.assertEqual(project.rvt_client_contact_ids.phone, "+91 98250 70011")
        self.assertEqual(project.rvt_client_contact_ids.parent_id, project.rvt_client_id)
        # one task per entity
        self.assertEqual(result["entities_created"], 13)
        self.assertEqual(len(project.rvt_entity_ids), 13)
        self.assertFalse(project.rvt_entity_ids.filtered("parent_id"))
        # trade plan
        plan = {p.trade_id.code: p for p in project.rvt_trade_plan_ids}
        self.assertEqual(set(plan), {"civ", "elec", "plmb", "pop", "carp", "col"})
        self.assertEqual(plan["carp"].agency_id, self.ag_carp)
        self.assertEqual(plan["carp"].contact_ids.name, "Bherubhai Suthar", "first contact person by default")
        self.assertFalse(plan["carp"].decide_by)
        self.assertFalse(plan["plmb"].agency_id)
        self.assertEqual(plan["col"].decide_by, self.days(7), "undecided without a date: a week from now")
        # work lines: usual trades of each entity type, limited to the project's trades
        kitchen = project.rvt_entity_ids.filtered(lambda e: e.name == "Kitchen")
        self.assertEqual(
            set(kitchen.rvt_line_ids.mapped("rvt_trade_id.code")), {"civ", "elec", "plmb", "pop", "carp", "col"},
            "kitchen: its usual trades without tiles and stone, which are not on this project")
        toilet = project.rvt_entity_ids.filtered(lambda e: e.name == "Toilet 1")
        self.assertEqual(set(toilet.rvt_line_ids.mapped("rvt_trade_id.code")), {"civ", "elec", "plmb", "pop"})
        lines = self.env["project.task"].search([("project_id", "=", project.id), ("rvt_kind", "=", "work")])
        self.assertEqual(result["lines_created"], len(lines))
        self.assertEqual(set(lines.mapped("rvt_work_state")), {"not_started"})
        self.assertFalse((lines | project.rvt_entity_ids).mapped("user_ids"), "rooms and lines land on nobody's My tasks")
        carp_line = self.line(project, "Kitchen", "carp")
        self.assertEqual(carp_line.rvt_agency_id, self.ag_carp, "the line carries the plan's agency")
        self.assertEqual(carp_line.name, "Carpenter")
        self.assertFalse(self.line(project, "Kitchen", "plmb").rvt_agency_id)
        self.assertEqual(project.rvt_agency_ids, self.ag_civil | self.ag_elec | self.ag_pop | self.ag_carp)

    def test_second_call_adds_without_duplicates(self):
        project, first = self.onboard()
        n_entities, n_plan = len(project.rvt_entity_ids), len(project.rvt_trade_plan_ids)
        n_lines = self.env["project.task"].search_count([("project_id", "=", project.id), ("rvt_kind", "=", "work")])
        # the same payload again: nothing new
        again = self.Project.with_user(self.coordinator).rvt_onboard(self.onboard_vals(project_id=project.id))
        self.assertFalse(again["new"])
        self.assertEqual((again["entities_created"], again["lines_created"], again["lines_removed"]), (0, 0, 0))
        self.assertEqual(len(project.rvt_entity_ids), n_entities)
        self.assertEqual(len(project.rvt_trade_plan_ids), n_plan)
        # add one room and one trade
        study = self.env.ref("rvt_base.entity_type_study")
        added = self.Project.with_user(self.coordinator).rvt_onboard({
            "project_id": project.id,
            "entities": [{"key": "s", "name": "Study", "entity_type_id": study.id}],
        })
        self.assertEqual(added["entities_created"], 1)
        study_task = project.rvt_entity_ids.filtered(lambda e: e.name == "Study")
        self.assertEqual(set(study_task.rvt_line_ids.mapped("rvt_trade_id.code")), {"elec", "pop", "carp", "col"})
        self.assertEqual(
            self.env["project.task"].search_count([("project_id", "=", project.id), ("rvt_kind", "=", "work")]),
            n_lines + 4)
        self.assertEqual(len(project.rvt_trade_plan_ids), n_plan, "the trade plan is left alone when no trades are sent")

    def test_ticks_and_untick(self):
        project, _ = self.onboard()
        state = project.with_user(self.coordinator).rvt_onboard_state()
        self.assertTrue(state["onboarded"])
        self.assertEqual(len(state["entities"]), 13)
        living = next(e for e in state["entities"] if e["name"] == "Living room")
        carp, civ = self.trade["carp"].id, self.trade["civ"].id
        self.assertIn([living["key"], carp], state["ticks"])
        living_civil = self.line(project, "Living room", "civ")
        living_carp = self.line(project, "Living room", "carp")
        living_civil.rvt_set_state("working")
        # untick both; only the one that has not started goes
        ticks = [t for t in state["ticks"] if t not in ([living["key"], carp], [living["key"], civ])]
        result = self.Project.with_user(self.coordinator).rvt_onboard({
            "project_id": project.id, "entities": state["entities"],
            "trades": [{"trade_id": t["trade_id"], "agency_id": t["agency_id"]} for t in state["trades"]],
            "ticks": ticks,
        })
        self.assertEqual(result["lines_removed"], 1)
        self.assertFalse(living_carp.exists())
        self.assertTrue(living_civil.exists(), "work that has started is never removed by unticking")
        # tick a cell that was not there
        garden_type = self.env.ref("rvt_base.entity_type_garden")
        result = self.Project.with_user(self.coordinator).rvt_onboard({
            "project_id": project.id,
            "entities": state["entities"] + [{"key": "g", "name": "Garden", "entity_type_id": garden_type.id}],
            "trades": [{"trade_id": t["trade_id"], "agency_id": t["agency_id"]} for t in state["trades"]],
            "ticks": ticks + [["g", civ], [living["key"], carp]],
        })
        self.assertEqual(result["entities_created"], 1)
        self.assertEqual(result["lines_created"], 2)
        self.assertEqual(self.line(project, "Garden", "civ").rvt_agency_id, self.ag_civil)

    def test_trade_taken_off(self):
        project, _ = self.onboard()
        state = project.with_user(self.coordinator).rvt_onboard_state()
        col = self.trade["col"].id
        # colour is unticked everywhere and taken off the list: its plan line goes
        result = self.Project.with_user(self.coordinator).rvt_onboard({
            "project_id": project.id, "entities": state["entities"],
            "trades": [{"trade_id": t["trade_id"], "agency_id": t["agency_id"]} for t in state["trades"] if t["trade_id"] != col],
            "ticks": [t for t in state["ticks"] if t[1] != col],
        })
        self.assertEqual(result["plan_removed"], 0, "lines of an unlisted trade are not touched, so the plan line stays")
        lines = self.env["project.task"].search([
            ("project_id", "=", project.id), ("rvt_kind", "=", "work"), ("rvt_trade_id", "=", col)])
        lines.unlink()
        result = self.Project.with_user(self.coordinator).rvt_onboard({
            "project_id": project.id,
            "trades": [{"trade_id": t["trade_id"], "agency_id": t["agency_id"]} for t in state["trades"] if t["trade_id"] != col],
        })
        self.assertEqual(result["plan_removed"], 1)
        self.assertNotIn("col", project.rvt_trade_plan_ids.mapped("trade_id.code"))

    def test_existing_project_keeps_hand_made_tasks(self):
        project = self.Project.create({"name": "Patel Bungalow"})
        Task = self.env["project.task"]
        room = Task.create({"name": "Drawing room", "project_id": project.id})
        sub = Task.create({"name": "Furniture work", "project_id": project.id, "parent_id": room.id})
        mom = Task.create({"name": "MOM master", "project_id": project.id})
        dated = Task.create({"name": "17/11/2025", "project_id": project.id})
        self.assertFalse(project.rvt_onboarded)
        state = project.with_user(self.coordinator).rvt_onboard_state()
        self.assertEqual([t["name"] for t in state["earlier_tasks"]], ["Drawing room"], "date and MOM tasks are not rooms")
        living = self.env.ref("rvt_base.entity_type_living")
        kitchen = self.env.ref("rvt_base.entity_type_kitchen")
        result = self.Project.with_user(self.coordinator).rvt_onboard({
            "project_id": project.id, "site_kind": "home",
            "coordinator_ids": [self.coordinator.id],
            "entities": [
                {"key": "a", "task_id": room.id, "entity_type_id": living.id},
                {"key": "b", "name": "Kitchen", "entity_type_id": kitchen.id},
            ],
            "trades": [{"trade_id": self.trade["carp"].id, "agency_id": self.ag_carp.id},
                       {"trade_id": self.trade["elec"].id, "agency_id": self.ag_elec.id}],
        })
        self.assertEqual(result["entities_created"], 1, "the earlier room task is used, not doubled")
        self.assertEqual(room.rvt_kind, "entity")
        self.assertEqual(room.name, "Drawing room")
        self.assertTrue(sub.exists())
        self.assertFalse(sub.rvt_kind, "its hand-made sub-task is untouched")
        self.assertEqual(sub.parent_id, room)
        self.assertFalse(mom.rvt_kind)
        self.assertFalse(dated.rvt_kind)
        # the earlier room got no lines by default (it is not new); the new kitchen did
        self.assertEqual(len(room.rvt_line_ids), 0)
        self.assertEqual(set(self.line(project, "Kitchen", "carp").mapped("rvt_trade_id.code")), {"carp"})
        self.assertEqual(room.rvt_line_count, 0)
        self.assertEqual(room.rvt_entity_state, "not_started")

    def test_mark_entity_from_the_task(self):
        project = self.Project.create({"name": "Mehta Office"})
        room = self.env["project.task"].create({"name": "Chairman cabin", "project_id": project.id})
        sub = self.env["project.task"].create({"name": "Paint work", "project_id": project.id, "parent_id": room.id})
        room.with_user(self.coordinator).action_rvt_mark_entity()
        self.assertEqual(room.rvt_kind, "entity")
        with self.assertRaises(UserError):
            sub.with_user(self.coordinator).action_rvt_mark_entity()

    def test_client_reuse(self):
        project, _ = self.onboard()
        client = project.rvt_client_id
        contact = project.rvt_client_contact_ids
        self.Project.with_user(self.coordinator).rvt_onboard({
            "project_id": project.id, "client_name": "mr. nirav  shah", "client_phone": "+91 98250 70099"})
        self.assertEqual(project.rvt_client_id, client, "the same client is not created twice")
        self.assertEqual(project.rvt_client_contact_ids, contact)
        self.assertEqual(contact.phone, "+91 98250 70099")
        self.Project.with_user(self.coordinator).rvt_onboard({
            "project_id": project.id,
            "client_contacts": [{"id": contact.id}, {"name": "Hetal Shah", "phone": "+91 98250 70012"}]})
        self.assertEqual(project.rvt_client_contact_ids.mapped("name"), ["Nirav Shah", "Hetal Shah"])

    def test_who_may_onboard(self):
        with self.assertRaises(UserError):
            self.Project.with_user(self.coordinator).rvt_onboard({"name": "  "})
        with self.assertRaises(AccessError):
            self.Project.with_user(self.agency_user).rvt_onboard({"name": "Not for me"})
        with self.assertRaises(AccessError):
            self.Project.with_user(self.agency_user).rvt_onboard_proposal(self.preset_3bhk.id)
        project, _ = self.onboard()
        with self.assertRaises(AccessError):
            self.Project.with_user(self.outsider).rvt_onboard({"project_id": project.id, "site_area": "Thaltej"})

    def test_grid(self):
        project, _ = self.onboard()
        self.line(project, "Kitchen", "civ").rvt_set_state("done")
        self.line(project, "Kitchen", "elec").rvt_set_state("working")
        grid = project.with_user(self.designer).rvt_grid()
        self.assertEqual(grid["entities"][-1]["name"], "Whole site", "the whole site comes last")
        self.assertEqual([t["code"] for t in grid["trades"]], ["civ", "elec", "plmb", "pop", "carp", "col"])
        plumber = next(t for t in grid["trades"] if t["code"] == "plmb")
        self.assertTrue(plumber["undecided"])
        self.assertTrue(plumber["late"])
        self.assertEqual(plumber["decide_by"], fields.Date.to_string(self.days(-6)))
        colour = next(t for t in grid["trades"] if t["code"] == "col")
        self.assertTrue(colour["undecided"])
        self.assertFalse(colour["late"])
        kitchen = next(e for e in grid["entities"] if e["name"] == "Kitchen")
        self.assertEqual((kitchen["state"], kitchen["done"], kitchen["lines"]), ("in_progress", 1, 6))
        cells = {(c["entity_id"], c["trade_id"]): c for c in grid["cells"]}
        self.assertEqual(cells[(kitchen["id"], self.trade["civ"].id)]["state"], "done")
        self.assertEqual(cells[(kitchen["id"], self.trade["elec"].id)]["agency"], "Jay Electric")
        self.assertNotIn((kitchen["id"], self.trade["tile"].id), cells)
