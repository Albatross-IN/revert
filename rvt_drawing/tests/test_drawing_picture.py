from datetime import timedelta

from odoo import fields
from odoo.tests import tagged

from .common import DrawingCommon


@tagged("post_install", "-at_install")
class TestDrawingPicture(DrawingCommon):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # the plumber is decided so that only the rules under test speak
        cls.project.rvt_trade_plan_ids.filtered(lambda p: p.trade_id.code == "plmb").agency_id = cls.ag_civil

    def pic(self, user=None):
        return self.project.with_user(user or self.coordinator).rvt_picture()

    def blocker(self, picture, rule):
        return next((b for b in picture["blockers"] if b["rule"] == rule), None)

    def back_date(self, records, field, days):
        records.sudo().write({field: fields.Datetime.now() - timedelta(days=days)})

    def test_progress_and_week(self):
        a = self.drawing("EL", "Electrical layout", "elec")
        self.drawing("SB", "Switchboard details", "elec")
        self.release(a, [self.ag_elec])
        picture = self.pic()
        self.assertEqual(picture["progress"]["drawings"], [1, 2])
        self.assertEqual(picture["week"]["released"], 1)
        self.back_date(a.released_revision_id, "released_on", 9)
        self.assertEqual(self.pic()["week"]["released"], 0)

    def test_b3_drawing_past_its_date(self):
        drawing = self.drawing("EL", "Electrical layout", "elec", designer=self.designer2, due=-3)
        self.drawing("LT", "Lighting layout", "elec", due=3)
        picture = self.pic()
        blocker = self.blocker(picture, "B3")
        self.assertEqual(blocker["text"], "EL-01 Electrical layout not released")
        self.assertEqual(blocker["holds"], "lines of Electrical")
        self.assertEqual((blocker["actor"], blocker["who"], blocker["age"]), ("Amit", self.designer2.ids, 3))
        self.assertEqual(blocker["action"], {"key": "dwg", "label": "Open", "drawing_id": drawing.id})
        self.assertEqual(len([b for b in picture["blockers"] if b["rule"] == "B3"]), 1, "a drawing still in time is no blocker")
        self.assertEqual(picture["status"], "attention")
        # awaiting approval: the principal must act
        self.send(drawing, self.designer2)
        blocker = self.blocker(self.pic(), "B3")
        self.assertEqual((blocker["actor"], blocker["who"]), ("Pranav (approve)", self.principal.ids))
        self.assertEqual(blocker["action"]["key"], "approve")
        drawing.with_user(self.principal).action_approve()
        self.assertEqual(self.blocker(self.pic(), "B3")["action"]["key"], "release")
        drawing.with_user(self.designer2).action_release([self.ag_elec.id])
        self.assertIsNone(self.blocker(self.pic(), "B3"))

    def test_b2_line_waits_for_a_drawing(self):
        drawing = self.drawing("EL", "Electrical layout", "elec", designer=self.designer2, due=4)
        for room in ("Master bedroom", "Bedroom 2", "Whole site"):
            line = self.line(self.project, room, "elec")
            line.rvt_set_state("waiting", cause="drawing", drawing_id=drawing.id)
            line.rvt_wait_since = self.days(-3)
        picture = self.pic()
        blocker = self.blocker(picture, "B2")
        self.assertEqual(blocker["text"], "EL-01 Electrical layout not released")
        self.assertEqual(blocker["holds"], "3 work lines waiting · Jay Electric")
        self.assertEqual(blocker["age"], 3, "not late yet, but three days of waiting")
        self.assertIsNone(self.blocker(picture, "B3"))
        todo = next(n for n in picture["next"]["revert"] if n["section"] == "draw")
        self.assertEqual(todo["text"], "Draw and send EL-01 Electrical layout")
        self.assertEqual(todo["warn"], "Jay Electric waiting · 3 days")
        self.assertEqual(todo["who"], self.designer2.ids)
        agency = next(a for a in picture["next"]["agencies"] if a["name"] == "Jay Electric")
        self.assertEqual(agency["sub"], "waiting for EL-01 Electrical layout")
        self.release(drawing, [self.ag_elec], user=self.designer2)
        self.assertIsNone(self.blocker(self.pic(), "B2"), "releasing the drawing clears the blocker")

    def test_b4_client_approval_pending(self):
        drawing = self.drawing("FL", "Furniture layout", for_client=True, needs=True)
        self.release(drawing, [self.ag_carp], client=True)
        line = self.line(self.project, "Master bedroom", "carp")
        line.rvt_set_state("waiting", cause="client", drawing_id=drawing.id)
        picture = self.pic()
        self.assertIsNone(self.blocker(picture, "B4"), "sent today: not a blocker yet")
        item = picture["next"]["client"][0]
        self.assertEqual((item["text"], item["late"], item["drawing_id"]), ("Approve Furniture layout rev 1", False, drawing.id))
        agency = next(a for a in picture["next"]["agencies"] if a["name"] == "Mahadev Furniture")
        self.assertIn("has not opened FL-01", agency["sub"])
        self.back_date(drawing.released_revision_id, "released_on", 2)
        picture = self.pic()
        blocker = self.blocker(picture, "B4")
        self.assertEqual(blocker["text"], "Client: approve Furniture layout rev 1")
        self.assertEqual(blocker["holds"], "Master bedroom · Carpenter")
        self.assertEqual((blocker["actor"], blocker["who"], blocker["age"]), ("Mr. Nirav Shah", self.coordinator.ids, 2))
        self.assertTrue(blocker["action"]["client"])
        self.assertTrue(picture["next"]["client"][0]["late"])
        mine = [i for i in self.Project.with_user(self.coordinator).rvt_today() if i["section"] == "client"]
        self.assertEqual(mine[0]["text"], "Chase Mr. Nirav Shah: Approve Furniture layout rev 1")
        drawing.rvt_client_decide("approved", partner=self.client_contact)
        picture = self.pic()
        self.assertIsNone(self.blocker(picture, "B4"))
        self.assertFalse(picture["next"]["client"])

    def test_b8_released_drawing_not_opened(self):
        drawing = self.drawing("SB", "Switchboard details", "elec")
        self.release(drawing, [self.ag_elec])
        self.assertIsNone(self.blocker(self.pic(), "B8"))
        receipt = drawing.released_revision_id.receipt_ids
        self.back_date(receipt, "sent_on", 3)
        picture = self.pic()
        blocker = self.blocker(picture, "B8")
        self.assertEqual(blocker["text"], "Jay Electric has not opened SB-01 Switchboard details")
        self.assertEqual((blocker["actor"], blocker["age"], blocker["holds"]), ("Meera (chase)", 3, "its Electrical lines"))
        self.assertEqual(blocker["action"]["agency_id"], self.ag_elec.id)
        chase = next(n for n in picture["next"]["revert"] if n["section"] == "chase")
        self.assertEqual(chase["text"], "Chase Jay Electric to open SB-01")
        self.assertEqual(chase["sub"], "released 3 days ago, not opened")
        agency = next(a for a in picture["next"]["agencies"] if a["name"] == "Jay Electric")
        self.assertEqual((agency["unopened"], agency["remind"]), (1, "Please open SB-01 Switchboard details."))
        self.env["ir.config_parameter"].sudo().set_int("rvt.limit_not_opened_days", 5)
        self.assertIsNone(self.blocker(self.pic(), "B8"), "the day limit is a setting")
        self.env["ir.config_parameter"].sudo().set_int("rvt.limit_not_opened_days", 2)
        drawing.rvt_open(self.ag_elec)
        self.assertIsNone(self.blocker(self.pic(), "B8"))

    def test_b9_question_unanswered(self):
        drawing = self.drawing("FC", "False ceiling layout", "pop")
        self.release(drawing, [self.ag_pop])
        drawing.rvt_open(self.ag_pop)
        qid = drawing.rvt_ask(self.ag_pop, "Cove depth: 3 in. or 4 in.?", person_name="Rajkumar Sharma")
        question = self.env["rvt.drawing.question"].browse(qid)
        picture = self.pic()
        self.assertIsNone(self.blocker(picture, "B9"), "asked today")
        todo = next(n for n in picture["next"]["revert"] if n["section"] == "question")
        self.assertEqual((todo["text"], todo["late"]), ("Answer on FC-01 False ceiling layout", False))
        self.back_date(question, "asked_on", 3)
        picture = self.pic()
        blocker = self.blocker(picture, "B9")
        self.assertEqual(blocker["text"], "Question on FC-01 unanswered")
        self.assertEqual(blocker["sub"], "“Cove depth: 3 in. or 4 in.?” · Rajkumar Sharma")
        self.assertEqual((blocker["actor"], blocker["holds"]), ("Riya", "Shree POP’s lines"))
        self.assertTrue(next(n for n in picture["next"]["revert"] if n["section"] == "question")["late"])
        mine = [i for i in self.Project.with_user(self.designer).rvt_today() if i["section"] == "question"]
        self.assertEqual(len(mine), 1, "it is on the designer's Today")
        question.with_user(self.designer).action_answer("4 in.")
        self.assertIsNone(self.blocker(self.pic(), "B9"))

    def test_next_actions_through_the_flow(self):
        drawing = self.drawing("CD", "Wardrobe details", "carp", due=1)
        sections = lambda: [n["section"] for n in self.pic()["next"]["revert"] if n["action"].get("drawing_id") == drawing.id]
        self.assertEqual(sections(), ["draw"])
        self.send(drawing)
        todo = next(n for n in self.pic()["next"]["revert"] if n["section"] == "approve")
        self.assertEqual(todo["text"], "Approve CD-01 Wardrobe details rev 1")
        self.assertEqual(todo["sub"], "sent by Riya · today")
        self.assertEqual(todo["who"], self.principal.ids)
        self.assertIn("approve", [i["section"] for i in self.Project.with_user(self.principal).rvt_today()])
        drawing.with_user(self.principal).action_send_back("Loft depth")
        back = next(n for n in self.pic()["next"]["revert"] if n["section"] == "draw")
        self.assertIn("sent back: Loft depth", back["sub"])
        self.send(drawing)
        drawing.with_user(self.principal).action_approve()
        todo = next(n for n in self.pic()["next"]["revert"] if n["section"] == "release")
        self.assertEqual((todo["text"], todo["sub"]), ("Release CD-01 Wardrobe details rev 1", "approved by Pranav"))
        self.assertEqual(set(todo["who"]), {self.designer.id, self.principal.id})
        drawing.with_user(self.designer).action_release([self.ag_carp.id])
        self.assertEqual(sections(), [])
        # a change asked by the client puts it back as "change"
        drawing.write({"for_client": True, "needs_client_approval": True})
        drawing.with_user(self.designer).action_new_revision()
        self.release(drawing, [self.ag_carp], client=True)
        drawing.rvt_client_decide("change", "Add a shoe rack", partner=self.client_contact)
        todo = next(n for n in self.pic()["next"]["revert"] if n["section"] == "change")
        self.assertEqual(todo["text"], "Revise CD-01 Wardrobe details")
        self.assertIn("client asked for a change", todo["sub"])

    def test_working_without_a_drawing(self):
        self.drawing("EL", "Electrical layout", "elec")
        line = self.line(self.project, "Kitchen", "elec")
        line.rvt_set_state("working")
        self.line(self.project, "Kitchen", "civ").rvt_set_state("working")
        self.assertEqual(self.pic()["working_without_drawing"], line.ids,
                         "electrical has a drawing on the list and none released; civil has no drawing on the list")
