from datetime import timedelta

from odoo.exceptions import UserError
from odoo.tests import tagged

from .common import PNG, MomCommon


@tagged("post_install", "-at_install")
class TestMomEtl(MomCommon):
    """The move of earlier MOM entries, on invented entries. Skipped where the earlier MOM is not installed."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.has_legacy = "mom_partner_id" in cls.env["mail.activity"]._fields
        if not cls.has_legacy:
            return
        env = cls.env
        cls.mom_type = env["mail.activity.type"].with_context(active_test=False).search([("is_mom", "=", True)], limit=1)
        cls.mom_type.active = True
        cls.old = cls.Project.create({"name": "Patel Bungalow (earlier way)"})
        Task = env["project.task"]
        cls.task_a = Task.create({"name": "MOM master", "project_id": cls.old.id})
        cls.task_b = Task.create({"name": "17/11/2025", "project_id": cls.old.id})
        Partner = env["res.partner"]
        cls.rahul = Partner.create({"name": "Zz Rahulbhai Polishwala"})
        cls.rahul2 = Partner.create({"name": "zz rahul bhai (polish)"})
        cls.jitu = Partner.create({"name": "Zz Jitubhai Testwala"})
        model_id = env["ir.model"]._get_id("project.task")

        def entry(task, text, person, day, done=False, photo=False, note=False):
            activity = env["mail.activity"].create({
                "activity_type_id": cls.mom_type.id, "res_model_id": model_id, "res_id": task.id,
                "summary": text, "note": note or False, "mom_partner_id": (person or cls.jitu).id,
                "mom_visit_date": cls.days(day), "date_deadline": cls.days(day + 7), "user_id": cls.coordinator.id,
                "mom_site_photo": PNG if photo else False,
            })
            if not person:
                # entries synced from the earliest MOM lines carry no person; the form no longer allows it
                env.cr.execute("UPDATE mail_activity SET mom_partner_id = NULL WHERE id = %s", [activity.id])
                activity.invalidate_recordset(["mom_partner_id"])
            if done:
                activity.action_feedback(feedback="Done on site")
            return activity

        cls.e1 = entry(cls.task_a, "Polish sample for the main door", cls.rahul, -30)
        cls.e2 = entry(cls.task_a, "Check the seepage near the staircase", cls.jitu, -30, photo=True, note="<p>Near the <b>landing</b></p>")
        cls.e3 = entry(cls.task_b, "Fix the drawer channels in the kitchen", cls.rahul2, -20, done=True, photo=True)
        cls.e4 = entry(cls.task_b, "Client to confirm the puja door", None, -20)
        cls.entries = (cls.e1 | cls.e2 | cls.e3 | cls.e4).with_context(active_test=False)
        cls.before = env["rvt.point"].search_count([])

    def run_etl(self, **kw):
        report = self.env["rvt.mom.etl"].run(**kw)
        return report, next(r for r in report["projects"] if r["project_id"] == self.old.id)

    def test_dry_run_writes_nothing(self):
        if not self.has_legacy:
            self.skipTest("the earlier MOM is not installed")
        report, row = self.run_etl()
        self.assertFalse(report["applied"])
        self.assertEqual((row["entries"], row["open"], row["closed"], row["photos"], row["visits"]), (4, 3, 1, 2, 2))
        self.assertTrue(row["after"] is None or row["after"]["entries"] == 0, "nothing of this project is moved by a dry run")
        self.assertEqual(self.env["rvt.point"].search_count([]), self.before, "a dry run creates nothing")
        self.assertGreaterEqual(report["to_move"], 4)
        self.assertIn(("Zz Jitubhai Testwala", 1), report["unmapped"])
        self.assertIn(("Zz Rahulbhai Polishwala", 1), report["people"])
        with self.assertRaises(UserError):
            self.env["rvt.mom.etl"].with_user(self.coordinator).run()

    def test_move_and_verify(self):
        if not self.has_legacy:
            self.skipTest("the earlier MOM is not installed")
        report, row = self.run_etl(apply=True)
        self.assertTrue(row["equal"], "entries, open, closed, photos by checksum, visits and numbers all match")
        self.assertEqual(row["after"], {"entries": 4, "open": 3, "closed": 1, "photos": 2, "visits": 2})
        points = self.env["rvt.point"].search([("legacy_activity_id", "in", self.entries.ids)])
        by = {p.legacy_activity_id: p for p in points}
        p1, p2, p3, p4 = (by[e.id] for e in (self.e1, self.e2, self.e3, self.e4))
        self.assertEqual(p1.text, "Polish sample for the main door")
        self.assertEqual(p2.text, "Check the seepage near the staircase\nNear the landing", "the remark and its details")
        self.assertEqual((p1.for_kind, p1.partner_id), ("vendor", self.rahul), "no sheet: the person is kept as a vendor contact")
        self.assertEqual((p4.for_kind, p4.party_label), ("vendor", "Not named"))
        self.assertEqual(p1.number, self.e1.mom_sequence)
        self.assertEqual(p2.number, self.e2.mom_sequence)
        self.assertEqual((p1.visit_id.date, p1.visit_id.number), (self.days(-30), 1))
        self.assertEqual((p3.visit_id.date, p3.visit_id.number), (self.days(-20), 2))
        self.assertEqual(p1.visit_id.number, self.e1.mom_visit_no)
        self.assertEqual(p3.visit_id.state, "finished")
        self.assertEqual((p1.state, p3.state), ("open", "closed"))
        self.assertEqual(p3.close_note, "Done on site")
        self.assertTrue(p3.closed_on)
        self.assertEqual(p1.legacy_task_id, self.task_a)
        self.assertEqual(p3.legacy_task_id, self.task_b)
        self.assertFalse(p1.entity_id, "the room stays empty; the task link is kept instead")
        self.assertEqual(p1.raised_by_id, self.e1.create_uid)
        self.assertEqual(p1.raised_on, self.e1.create_date)
        self.assertTrue(p2.has_photo and p3.has_photo and not p1.has_photo)
        self.assertEqual(p2.photo.content, self.e2.mom_site_photo.content, "the photo is the same file")
        # the earlier entries are untouched
        self.assertEqual(len(self.entries.exists()), 4)
        self.assertTrue(self.e1.active)
        # a second run creates nothing
        again, row = self.run_etl(apply=True)
        self.assertEqual(again["created"], 0)
        self.assertTrue(row["equal"])
        self.assertEqual(len(self.env["rvt.point"].search([("legacy_activity_id", "in", self.entries.ids)])), 4)

    def test_mapping_sheet(self):
        if not self.has_legacy:
            self.skipTest("the earlier MOM is not installed")
        sheet = [
            {"person": "ZZ rahulbhai  polishwala", "kind": "agency", "agency": "Zz Polish Works", "trade": "Colour / polish", "phone": "98250 11223", "same_as": ""},
            {"person": "zz rahul bhai (polish)", "kind": "", "agency": "", "trade": "", "phone": "", "same_as": "Zz Rahulbhai Polishwala"},
            {"person": "Zz Jitubhai Testwala", "kind": "staff", "agency": "Riya Trivedi", "trade": "", "phone": "", "same_as": ""},
        ]
        report, row = self.run_etl(apply=True, mapping_rows=sheet)
        self.assertTrue(row["equal"])
        by = {p.legacy_activity_id: p for p in self.env["rvt.point"].search([("legacy_activity_id", "in", self.entries.ids)])}
        agency = by[self.e1.id].partner_id
        self.assertEqual((agency.name, agency.rvt_is_agency), ("Zz Polish Works", True))
        self.assertEqual(agency.rvt_trade_ids.code, "col")
        self.assertEqual((by[self.e1.id].for_kind, by[self.e1.id].trade_id.code), ("agency", "col"))
        self.assertEqual(by[self.e3.id].partner_id, agency, "the second spelling goes to the same agency, through the sheet")
        self.assertEqual(self.rahul.parent_id, agency, "the person becomes one of the agency's people")
        self.assertEqual(self.rahul.phone, "98250 11223")
        self.assertEqual((by[self.e2.id].for_kind, by[self.e2.id].user_id), ("staff", self.designer))
        mine = {"Zz Rahulbhai Polishwala", "zz rahul bhai (polish)", "Zz Jitubhai Testwala"}
        self.assertFalse(mine & {name for name, count in report["unmapped"]}, "everybody on the sheet is matched, whatever the capitals and spaces")

    def test_switch_off(self):
        if not self.has_legacy:
            self.skipTest("the earlier MOM is not installed")
        with self.assertRaises(UserError):
            self.env["rvt.mom.etl"].with_user(self.coordinator).switch_off_earlier_screens()
        done = self.env["rvt.mom.etl"].switch_off_earlier_screens()
        self.assertIn("activity type archived", done)
        self.assertFalse(self.mom_type.active)
        self.assertTrue(self.e1.exists(), "the earlier records stay")
        self.assertEqual(self.env["rvt.mom.etl"].switch_off_earlier_screens(), [], "a second call has nothing left to do")
