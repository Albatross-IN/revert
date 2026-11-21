from odoo.exceptions import UserError, ValidationError
from odoo.tests import tagged
from odoo.tools import mute_logger

from .common import RvtCommon


@tagged("post_install", "-at_install")
class TestWorkLines(RvtCommon):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.project, _ = cls.onboard()

    def test_undecided_late(self):
        plan = {p.trade_id.code: p for p in self.project.rvt_trade_plan_ids}
        self.assertTrue(plan["plmb"].is_undecided_late)
        self.assertFalse(plan["col"].is_undecided_late, "undecided, but its date has not passed")
        self.assertFalse(plan["carp"].is_undecided_late)
        late = self.env["rvt.project.trade"].search([("project_id", "=", self.project.id), ("is_undecided_late", "=", True)])
        self.assertEqual(late, plan["plmb"])
        not_late = self.env["rvt.project.trade"].search([("project_id", "=", self.project.id), ("is_undecided_late", "=", False)])
        self.assertEqual(len(not_late), 5)
        plan["plmb"].agency_id = self.ag_civil
        self.assertFalse(plan["plmb"].is_undecided_late)
        self.assertFalse(plan["plmb"].decide_by, "the date goes once the agency is decided")

    def test_entity_state_from_lines(self):
        toilet = self.project.rvt_entity_ids.filtered(lambda e: e.name == "Toilet 1")
        lines = toilet.rvt_line_ids
        self.assertEqual(len(lines), 4)
        self.assertEqual(toilet.rvt_entity_state, "not_started")
        lines[0].rvt_set_state("working")
        self.assertEqual(toilet.rvt_entity_state, "in_progress")
        for line in lines:
            line.rvt_set_state("done")
        self.assertEqual(toilet.rvt_entity_state, "done")
        self.assertEqual((toilet.rvt_line_done_count, toilet.rvt_line_count), (4, 4))
        lines[1].rvt_set_state("waiting", cause="material", note="Tiles awaited")
        self.assertEqual(toilet.rvt_entity_state, "in_progress")
        self.assertEqual(toilet.rvt_line_done_count, 3)

    def test_waiting_needs_a_cause(self):
        line = self.line(self.project, "Master bedroom", "elec")
        with self.assertRaises(ValidationError):
            line.rvt_set_state("waiting")
        with self.assertRaises(ValidationError):
            line.rvt_set_state("waiting", cause="trade")
        with self.assertRaises(ValidationError):
            line.rvt_set_state("waiting", cause="trade", wait_trade_id=self.trade["elec"].id)
        with self.assertRaises(ValidationError):
            line.write({"rvt_work_state": "waiting"})
        cell = line.rvt_set_state("waiting", cause="trade", wait_trade_id=self.trade["pop"].id)
        self.assertEqual(cell["state"], "waiting")
        self.assertEqual(cell["cause"], "trade")
        self.assertEqual(line.rvt_wait_trade_id, self.trade["pop"])
        self.assertEqual(line.rvt_wait_since, self.today)
        # moving on clears the cause
        line.rvt_set_state("working")
        self.assertFalse(line.rvt_wait_cause)
        self.assertFalse(line.rvt_wait_trade_id)
        self.assertFalse(line.rvt_wait_since)
        self.assertEqual(line.rvt_started_on, self.today)
        with self.assertRaises(UserError):
            line.rvt_set_state("paused")
        with self.assertRaises(UserError):
            line.parent_id.rvt_set_state("working")

    def test_done_closes_the_task(self):
        line = self.line(self.project, "Kitchen", "civ")
        self.assertEqual(line.state, "01_in_progress")
        line.rvt_set_state("done")
        self.assertEqual(line.state, "1_done", "the earlier task views agree")
        self.assertEqual(line.rvt_done_on, self.today)
        self.assertEqual(line.rvt_started_on, self.today)
        line.rvt_set_state("working")
        self.assertEqual(line.state, "01_in_progress")
        self.assertFalse(line.rvt_done_on)
        line.rvt_set_state("not_started")
        self.assertFalse(line.rvt_started_on)

    def test_expected_finish(self):
        line = self.line(self.project, "Kitchen", "pop")
        cell = line.rvt_set_state("working", expected_finish=self.days(9))
        self.assertEqual(line.rvt_expected_finish, self.days(9))
        self.assertTrue(cell["expected_finish"])
        line.rvt_set_state("working", expected_finish=False)
        self.assertFalse(line.rvt_expected_finish)

    def test_agency_change_propagates(self):
        plan = self.project.rvt_trade_plan_ids.filtered(lambda p: p.trade_id.code == "carp")
        kitchen = self.line(self.project, "Kitchen", "carp")
        living = self.line(self.project, "Living room", "carp")
        # a second carpenter for the kitchen only
        kitchen.rvt_agency_id = self.ag_carp2
        other = self.env["res.partner"].create({"name": "Vishwakarma Interiors", "rvt_is_agency": True})
        plan.agency_id = other
        self.assertEqual(living.rvt_agency_id, other, "lines on the old default follow the plan")
        self.assertEqual(kitchen.rvt_agency_id, self.ag_carp2, "an overridden line stays")
        self.assertFalse(plan.contact_ids, "people of the old agency are dropped")
        self.assertIn(other, self.project.rvt_agency_ids)
        self.assertIn(self.ag_carp2, self.project.rvt_agency_ids)
        self.assertNotIn(self.ag_carp, self.project.rvt_agency_ids)
        # deciding an undecided trade fills its lines
        plumber = self.project.rvt_trade_plan_ids.filtered(lambda p: p.trade_id.code == "plmb")
        line = self.line(self.project, "Kitchen", "plmb")
        self.assertFalse(line.rvt_agency_id)
        plumber.agency_id = self.ag_civil
        self.assertEqual(line.rvt_agency_id, self.ag_civil)
        # and back to undecided
        plumber.agency_id = False
        self.assertFalse(line.rvt_agency_id)

    def test_contacts_belong_to_the_agency(self):
        plan = self.project.rvt_trade_plan_ids.filtered(lambda p: p.trade_id.code == "elec")
        stranger = self.env["res.partner"].search([("parent_id", "=", self.ag_carp.id)], limit=1)
        with self.assertRaises(ValidationError):
            plan.contact_ids = [(4, stranger.id)]

    @mute_logger("odoo.sql_db")
    def test_one_line_per_room_and_trade(self):
        kitchen = self.project.rvt_entity_ids.filtered(lambda e: e.name == "Kitchen")
        with self.assertRaises(Exception), self.cr.savepoint():
            self.env["project.task"].create({
                "parent_id": kitchen.id, "project_id": self.project.id,
                "rvt_kind": "work", "rvt_trade_id": self.trade["carp"].id})

    def test_line_shape_rules(self):
        Task = self.env["project.task"]
        hand_made = Task.create({"name": "Site clearing", "project_id": self.project.id})
        with self.assertRaises(ValidationError):
            Task.create({"parent_id": hand_made.id, "project_id": self.project.id,
                         "rvt_kind": "work", "rvt_trade_id": self.trade["civ"].id})
        kitchen = self.project.rvt_entity_ids.filtered(lambda e: e.name == "Kitchen")
        with self.assertRaises(ValidationError):
            Task.create({"name": "Nook", "parent_id": kitchen.id, "project_id": self.project.id, "rvt_kind": "entity"})
        with self.assertRaises(ValidationError):
            Task.create({"name": "No trade", "parent_id": kitchen.id, "project_id": self.project.id, "rvt_kind": "work"})
        # a hand-made sub-task under a room is fine and is not a work line
        sub = Task.create({"name": "Check the chimney position", "parent_id": kitchen.id, "project_id": self.project.id})
        self.assertFalse(sub.rvt_kind)
        self.assertEqual(kitchen.rvt_line_count, 6)
