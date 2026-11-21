from odoo.exceptions import AccessError
from odoo.tests import tagged

from .common import RvtCommon


@tagged("post_install", "-at_install")
class TestPicture(RvtCommon):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.project, _ = cls.onboard()

    def pic(self, user=None):
        return self.project.with_user(user or self.coordinator).rvt_picture()

    def rules(self, picture):
        return [b["rule"] for b in picture["blockers"]]

    def test_progress_counts(self):
        lines = self.env["project.task"].search([("project_id", "=", self.project.id), ("rvt_kind", "=", "work")])
        self.line(self.project, "Kitchen", "civ").rvt_set_state("done")
        self.line(self.project, "Kitchen", "elec").rvt_set_state("working")
        self.line(self.project, "Kitchen", "pop").rvt_set_state("waiting", cause="material", note="Boards awaited")
        picture = self.pic()
        self.assertEqual(picture["progress"]["agencies"], [4, 6], "four of six trades have their agency")
        self.assertEqual(picture["progress"]["work"], [1, len(lines), 1, 1])
        self.assertEqual(picture["week"]["done"], 1)
        self.assertEqual(picture["week"]["started"], 2, "the line done today also started today")

    def test_b1_trade_undecided_past_its_date(self):
        picture = self.pic()
        b1 = [b for b in picture["blockers"] if b["rule"] == "B1"]
        self.assertEqual(len(b1), 1, "the plumber is late; colour is undecided but its date has not passed")
        blocker = b1[0]
        self.assertEqual(blocker["text"], "Plumbing agency undecided")
        self.assertEqual(blocker["age"], 6)
        self.assertTrue(blocker["critical"])
        self.assertEqual(blocker["who"], self.coordinator.ids)
        self.assertEqual(blocker["actor"], "Meera")
        held = self.env["project.task"].search_count([
            ("project_id", "=", self.project.id), ("rvt_kind", "=", "work"), ("rvt_trade_id", "=", self.trade["plmb"].id)])
        self.assertEqual(blocker["holds"], "%s work lines" % held)
        self.assertEqual(blocker["action"], {
            "key": "assign", "label": "Assign", "project_id": self.project.id, "trade": "plmb"})
        self.assertEqual(picture["status"], "stuck", "B1 alone makes the project stuck")
        # deciding the plumber clears it
        self.project.rvt_trade_plan_ids.filtered(lambda p: p.trade_id.code == "plmb").agency_id = self.ag_civil
        picture = self.pic()
        self.assertNotIn("B1", self.rules(picture))
        self.assertEqual(picture["status"], "ok")

    def test_b5_waits_for_another_trade(self):
        self.project.rvt_trade_plan_ids.filtered(lambda p: p.trade_id.code == "plmb").agency_id = self.ag_civil
        line = self.line(self.project, "Living room", "col")
        line.rvt_set_state("waiting", cause="trade", wait_trade_id=self.trade["carp"].id)
        line.rvt_wait_since = self.days(-2)
        picture = self.pic()
        blocker = next(b for b in picture["blockers"] if b["rule"] == "B5")
        self.assertEqual(blocker["text"], "Living room · Colour / polish waits for Carpenter (Mahadev Furniture)")
        self.assertEqual(blocker["actor"], "Mahadev Furniture", "that trade's agency must act")
        self.assertEqual(blocker["age"], 2)
        self.assertEqual(blocker["action"]["key"], "remind")
        self.assertEqual(blocker["action"]["agency_id"], self.ag_carp.id)
        self.assertEqual(picture["status"], "attention")
        # waiting for a trade whose agency is undecided: the office opens the cell
        line.rvt_set_state("waiting", cause="trade", wait_trade_id=self.trade["col"].id) if False else None
        other = self.line(self.project, "Kitchen", "carp")
        other.rvt_set_state("waiting", cause="trade", wait_trade_id=self.trade["col"].id)
        picture = self.pic()
        undecided = next(b for b in picture["blockers"] if b["rule"] == "B5" and "Kitchen" in b["text"])
        self.assertEqual(undecided["actor"], "Colour / polish")
        self.assertEqual(undecided["action"], {
            "key": "cell", "label": "Open", "project_id": self.project.id, "line_id": other.id})

    def test_b6_waits_for_material_and_stuck_after_a_week(self):
        self.project.rvt_trade_plan_ids.filtered(lambda p: p.trade_id.code == "plmb").agency_id = self.ag_civil
        line = self.line(self.project, "Bedroom 2", "carp")
        line.rvt_set_state("waiting", cause="material", note="Laminate shade 2187 awaited from the dealer")
        picture = self.pic()
        blocker = next(b for b in picture["blockers"] if b["rule"] == "B6")
        self.assertEqual(blocker["text"], "Bedroom 2 · Carpenter waits for material: Laminate shade 2187 awaited from the dealer")
        self.assertEqual(blocker["actor"], "Meera")
        self.assertEqual(blocker["age"], 0)
        self.assertEqual(picture["status"], "attention")
        line.rvt_wait_since = self.days(-7)
        self.assertEqual(self.pic()["status"], "stuck", "a blocker a week old makes the project stuck")
        self.env["ir.config_parameter"].sudo().set_int("rvt.limit_stuck_days", 10)
        self.assertEqual(self.pic()["status"], "attention", "the day limit is a setting")
        line.rvt_set_state("working")
        self.assertEqual(self.pic()["status"], "ok")

    def test_blockers_oldest_first(self):
        a = self.line(self.project, "Bedroom 2", "carp")
        a.rvt_set_state("waiting", cause="other", note="Lift not working")
        a.rvt_wait_since = self.days(-9)
        b = self.line(self.project, "Bedroom 3", "carp")
        b.rvt_set_state("waiting", cause="material", note="Hinges")
        picture = self.pic()
        self.assertEqual(self.rules(picture)[0], "B1", "an undecided trade comes first")
        ages = [x["age"] for x in picture["blockers"][1:]]
        self.assertEqual(ages, sorted(ages, reverse=True))

    def test_next_actions(self):
        picture = self.pic()
        decide = [n for n in picture["next"]["revert"] if n["section"] == "decide"]
        self.assertEqual(len(decide), 2, "plumber and colour are both to decide")
        plumber = next(n for n in decide if "plumbing" in n["text"])
        self.assertEqual(plumber["text"], "Decide the plumbing agency")
        self.assertTrue(plumber["late"])
        self.assertEqual(plumber["who"], self.coordinator.ids)
        self.assertEqual(plumber["project_id"], self.project.id)
        colour = next(n for n in decide if "colour" in n["text"])
        self.assertFalse(colour["late"])
        agencies = {a["name"]: a for a in picture["next"]["agencies"]}
        self.assertEqual(set(agencies), {"Ramesh Construction", "Jay Electric", "Shree POP", "Mahadev Furniture"})
        carp = agencies["Mahadev Furniture"]
        self.assertEqual(carp["trades"], "Carpenter")
        self.assertEqual((carp["done"], carp["working"], carp["waiting"]), (0, 0, 0))
        self.line(self.project, "Kitchen", "carp").rvt_set_state("working")
        self.line(self.project, "Living room", "carp").rvt_set_state("waiting", cause="material", note="Ply")
        carp = next(a for a in self.pic()["next"]["agencies"] if a["name"] == "Mahadev Furniture")
        self.assertEqual((carp["working"], carp["waiting"]), (1, 1))
        self.assertEqual(carp["sub"], "waiting for material: Ply")

    def test_today_is_the_same_items_filtered_to_me(self):
        mine = self.Project.with_user(self.coordinator).rvt_today()
        mine = [i for i in mine if i["project_id"] == self.project.id]
        self.assertEqual(sorted(i["text"] for i in mine), ["Decide the colour / polish agency", "Decide the plumbing agency"])
        designer = [i for i in self.Project.with_user(self.designer).rvt_today() if i["project_id"] == self.project.id]
        self.assertFalse(designer, "nothing is for the designer yet")
        self.assertFalse([i for i in self.Project.with_user(self.outsider).rvt_today() if i["project_id"] == self.project.id])

    def test_review_rows(self):
        plain = self.Project.create({"name": "Patel Bungalow"})
        rows = (self.project | plain).with_user(self.owner).rvt_picture_summary()
        row = next(r for r in rows if r["project_id"] == self.project.id)
        self.assertEqual(row["status"], "stuck")
        self.assertEqual(row["blockers"], 1)
        self.assertEqual(row["oldest"], {"text": "Plumbing agency undecided", "age": 6})
        self.assertEqual(next(r for r in rows if r["project_id"] == plain.id)["onboarded"], False)

    def test_who_reads_the_picture(self):
        self.pic(self.owner)
        self.pic(self.designer)
        with self.assertRaises(AccessError):
            self.pic(self.outsider)
        with self.assertRaises(AccessError):
            self.pic(self.agency_user)
