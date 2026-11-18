from odoo.tests import tagged

from .common import MomCommon


@tagged("post_install", "-at_install")
class TestMomPicture(MomCommon):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.project.rvt_trade_plan_ids.filtered(lambda p: p.trade_id.code == "plmb").agency_id = cls.ag_civil

    def pic(self, user=None):
        return self.project.with_user(user or self.coordinator).rvt_picture()

    def blockers(self, picture, rule):
        return [b for b in picture["blockers"] if b["rule"] == rule]

    def test_progress(self):
        self.add("One", partner=self.ag_carp, due=-1)
        self.add("Two", partner=self.ag_elec, due=3)
        done = self.add("Three", partner=self.ag_pop)
        done.action_close("ok")
        picture = self.pic()
        self.assertEqual(picture["progress"]["points"], [1, 3, 2, 1])
        self.assertEqual(picture["week"]["closed"], 1)

    def test_b7_point_past_its_date(self):
        point = self.add("Wardrobe loft depth 24 in.", partner=self.ag_carp, due=-1, entity_id=self.master.id)
        self.add("Shift the TV unit", partner=self.ag_carp, due=5)
        staff = self.add("Send the revised kitchen elevation", kind="staff", user_id=self.designer.id, due=-2)
        picture = self.pic()
        rows = self.blockers(picture, "B7")
        self.assertEqual(len(rows), 2, "only the two that are past their date")
        agency = next(b for b in rows if "Mahadev" in b["text"])
        self.assertEqual(agency["text"], "Mahadev Furniture: point %s past its date" % point.number)
        self.assertEqual(agency["sub"], "Wardrobe loft depth 24 in.")
        self.assertEqual((agency["holds"], agency["actor"], agency["age"]), ("Master bedroom · Carpenter", "Mahadev Furniture", 1))
        self.assertEqual(agency["action"]["key"], "remind")
        self.assertEqual(agency["action"]["agency_id"], self.ag_carp.id)
        mine = next(b for b in rows if "Riya" in b["text"])
        self.assertEqual(mine["action"], {"key": "closept", "label": "Close", "point_id": staff.id})
        self.assertEqual(picture["status"], "attention")
        point.action_close("done")
        staff.action_close("sent")
        self.assertFalse(self.blockers(self.pic(), "B7"))

    def test_b4_client_item_past_its_date(self):
        item = self.add("Choose the kitchen platform stone", kind="client", due=-3, entity_id=self.kitchen.id)
        picture = self.pic()
        self.assertFalse(self.blockers(picture, "B4"), "not confirmed yet: the client has not seen it")
        todo = next(n for n in picture["next"]["revert"] if n["section"] == "confirm")
        self.assertEqual(todo["text"], "Confirm client point %s before the client sees it" % item.number)
        self.assertTrue(todo["office"])
        self.assertFalse(picture["next"]["client"])
        item.action_confirm()
        picture = self.pic()
        blocker = self.blockers(picture, "B4")[0]
        self.assertEqual(blocker["text"], "Client: Choose the kitchen platform stone")
        self.assertEqual((blocker["holds"], blocker["actor"], blocker["age"]), ("Kitchen", "Mr. Nirav Shah", 3))
        row = picture["next"]["client"][0]
        self.assertEqual((row["text"], row["late"], row["point_id"]), ("Choose the kitchen platform stone", True, item.id))
        chase = [i for i in self.Project.with_user(self.coordinator).rvt_today() if i["section"] == "client"]
        self.assertEqual(chase[0]["text"], "Chase Mr. Nirav Shah: Choose the kitchen platform stone")

    def test_today_for_the_office_and_for_staff(self):
        self.add("Confirm the wall colour", kind="client")
        mine = self.add("Send the revised kitchen elevation", kind="staff", user_id=self.designer.id, due=1)
        sections = lambda user: [i["section"] for i in self.Project.with_user(user).rvt_today() if i["project_id"] == self.project.id]
        self.assertIn("confirm", sections(self.coordinator))
        self.assertIn("confirm", sections(self.owner), "the office's items also show to an owner")
        self.assertNotIn("confirm", sections(self.designer))
        todo = next(i for i in self.Project.with_user(self.designer).rvt_today() if i["section"] == "point")
        self.assertEqual(todo["text"], "Send the revised kitchen elevation")
        self.assertEqual(todo["sub"], "point %s · by tomorrow" % mine.number)

    def test_agency_slice(self):
        first = self.add("Wardrobe loft depth 24 in.", partner=self.ag_carp, due=-1)
        self.add("Shift the TV unit 4 in. to the left", partner=self.ag_carp, due=5)
        agency = next(a for a in self.pic()["next"]["agencies"] if a["name"] == "Mahadev Furniture")
        self.assertEqual((agency["points"], agency["overdue"]), (2, 1))
        self.assertEqual(agency["sub"], "next: Wardrobe loft depth 24 in., by yesterday")
        self.assertEqual(agency["remind"], "Point %s: Wardrobe loft depth 24 in. (by yesterday)" % first.number)
        # a waiting line speaks before the next point
        self.line(self.project, "Kitchen", "carp").rvt_set_state("waiting", cause="material", note="Ply")
        agency = next(a for a in self.pic()["next"]["agencies"] if a["name"] == "Mahadev Furniture")
        self.assertEqual(agency["sub"], "waiting for material: Ply")

    def test_wait_text_names_the_client_item(self):
        item = self.add("Choose the kitchen platform stone", kind="client")
        line = self.line(self.project, "Kitchen", "carp")
        line.rvt_set_state("waiting", cause="client", point_id=item.id)
        agency = next(a for a in self.pic()["next"]["agencies"] if a["name"] == "Mahadev Furniture")
        self.assertEqual(agency["sub"], "waiting for client: Choose the kitchen platform stone")
