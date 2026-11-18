import re

from odoo.exceptions import AccessError, UserError
from odoo.tests import tagged

from odoo.addons.rvt_mom.tests.common import MomCommon

from ..models.rvt_notify import e164, fill
from ..models.rvt_notify_template import CLIENT_EVENTS

# docs/rules.md §6.1: words a client never reads
NOT_FOR_CLIENTS = ("delayed", "late", "overdue", "stuck", "pending from your side")


@tagged("post_install", "-at_install")
class TestNotify(MomCommon):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Notify = cls.env["rvt.notify"]
        cls.Log = cls.env["rvt.notify.log"]
        cls.icp = cls.env["ir.config_parameter"].sudo()
        cls.carp_person = cls.env["res.partner"].search([("parent_id", "=", cls.ag_carp.id), ("name", "=", "Bherubhai Suthar")])
        cls.ag_carp.lang = "gu_IN"
        cls.ag_elec.lang = "hi_IN"

    def go_live(self):
        """As on production: not a test copy, the switch on, a number paired. The connector itself is replaced."""
        self.icp.set_bool("database.is_neutralized", False)
        self.icp.set_bool("rvt.notify_sending_on", True)
        self.sent = []
        Notify = type(self.Notify)
        self.patch(Notify, "_account", lambda self_: self.env["res.partner"].browse(1))
        self.patch(Notify, "_wa_send_text", lambda self_, account, number, text: self.sent.append(("text", number, text)) or True)
        self.patch(Notify, "_wa_send_file", lambda self_, account, number, text, name, data, mimetype="application/pdf":
                   self.sent.append(("file", number, text, name, data[:4])) or True)

    def setUp(self):
        super().setUp()
        # the copy has its own log rows: only what this test writes counts
        self.log_floor = self.Log.search([], order="id desc", limit=1).id

    def logs(self, event):
        return self.Log.search([("event", "=", event), ("id", ">", self.log_floor)], order="id")

    # ---- helpers ------------------------------------------------------
    def test_numbers_and_filling(self):
        self.assertEqual(e164("98250 41120"), "+919825041120")
        self.assertEqual(e164("098250-41120"), "+919825041120")
        self.assertEqual(e164("+91 98250 41120"), "+919825041120")
        self.assertFalse(e164("12345"))
        self.assertFalse(e164(False))
        self.assertEqual(fill("{site}: {text} {unknown}", {"site": "Shah Residence", "text": "ok"}), "Shah Residence: ok {unknown}")

    def test_every_event_has_its_three_languages(self):
        Template = self.env["rvt.notify.template"]
        for event in ("drawing_released", "drawing_client", "mom_party_pdf", "client_item", "bill_asked", "bill_returned",
                      "bill_accepted", "bill_paid", "invite", "remind", "otp"):
            langs = set(Template.search([("event", "=", event)]).mapped("lang"))
            self.assertEqual(langs, {"en", "gu", "hi"}, event)
        self.assertEqual(Template.text_for("drawing_question", "gu"), Template.text_for("drawing_question", "en"),
                         "a missing language falls back to English")

    def test_client_wording(self):
        for template in self.env["rvt.notify.template"].search([("event", "in", CLIENT_EVENTS)]):
            for word in NOT_FOR_CLIENTS:
                self.assertIsNone(re.search(r"\b%s\b" % word, template.text, re.I), "%s: “%s”" % (template.display_name, word))

    # ---- the switch ---------------------------------------------------
    def test_nothing_leaves_a_test_copy(self):
        self.assertTrue(self.Notify.is_test_copy(), "the development database is a neutralised copy")
        self.icp.set_bool("rvt.notify_sending_on", True)
        self.assertFalse(self.Notify.sending_on(), "the switch cannot send from a test copy")
        sent = self.project.with_user(self.coordinator).rvt_remind("Please share where the work stands.", agency_id=self.ag_carp.id)
        self.assertEqual(sent, 0)
        row = self.logs("remind")
        self.assertEqual((row.state, row.name, row.phone), ("held", "Bherubhai Suthar", "+919824418830"))
        self.assertIn("Test copy", row.reason)
        self.assertEqual(row.text, "યાદ અપાવવા · Shah Residence: Please share where the work stands.")
        self.assertEqual((row.project_id, row.sent_by_id), (self.project, self.coordinator))

    def test_switch_off_holds(self):
        self.icp.set_bool("database.is_neutralized", False)
        self.assertFalse(self.Notify.sending_on(), "off until somebody switches it on")
        self.project.with_user(self.coordinator).rvt_remind("Open EL-01.", agency_id=self.ag_elec.id)
        row = self.logs("remind")
        self.assertEqual(row.state, "held")
        self.assertEqual(row.reason, "Sending is off in Setup.")
        self.assertEqual(row.lang, "hi")

    def test_no_number_paired_and_no_number_on_contact(self):
        self.icp.set_bool("database.is_neutralized", False)
        self.icp.set_bool("rvt.notify_sending_on", True)
        self.assertTrue(self.Notify.sending_on())
        self.project.with_user(self.coordinator).rvt_remind("Open EL-01.", agency_id=self.ag_elec.id)
        self.assertEqual(self.logs("remind").state, "failed")
        self.assertIn("paired", self.logs("remind").reason)
        self.client_contact.phone = False
        self.project.with_user(self.coordinator).rvt_remind("Please look at the layout.", client=True)
        self.assertEqual(self.logs("remind")[-1].state, "no_number")

    # ---- events -------------------------------------------------------
    def test_released_drawing_goes_with_its_link(self):
        self.go_live()
        drawing = self.drawing("FL", "Furniture layout", for_client=True, needs=True)
        self.release(drawing, [self.ag_carp, self.ag_elec], client=True)
        by_number = {s[1]: s[2] for s in self.sent}
        receipts = {r.partner_id: r for r in drawing.released_revision_id.receipt_ids}
        carp = by_number["+919824418830"]
        self.assertTrue(carp.startswith("નવું ડ્રોઇંગ · Shah Residence: FL-01 Furniture layout · રિવિઝન 1."), "Gujarati for this agency")
        self.assertTrue(carp.endswith(receipts[self.ag_carp].rvt_link()), "each receiver has its own link")
        elec = [s for s in self.sent if s[1] in ("+919879022014",)][0][2]
        self.assertTrue(elec.startswith("नई ड्रॉइंग"), "Hindi for that one")
        client = by_number["+919825070011"]
        self.assertTrue(client.startswith("Shah Residence: your Furniture layout (rev 1) is ready."))
        self.assertIn(receipts[self.client_partner].rvt_link(), client)
        self.assertEqual(self.logs("drawing_released").mapped("state"), ["sent", "sent"])
        self.assertEqual(self.logs("drawing_client").state, "sent")
        self.assertEqual(self.logs("drawing_client").res_model, "rvt.drawing.receipt")

    def test_staff_are_told_in_the_app(self):
        self.go_live()
        drawing = self.drawing("CD", "Wardrobe details", "carp")
        self.send(drawing)
        row = self.logs("drawing_approval_needed")
        self.assertEqual((row.state, row.user_id), ("in_app", self.principal))
        self.assertEqual(row.text, "Shah Residence: CD-01 Wardrobe details rev 1 waits for your approval.")
        self.assertFalse(self.sent, "staff get no WhatsApp message")
        drawing.with_user(self.principal).action_approve()
        drawing.with_user(self.designer).action_release([self.ag_carp.id])
        drawing.rvt_ask(self.ag_carp, "Loft 18 or 24?", person_name="Bherubhai Suthar")
        row = self.logs("drawing_question")
        self.assertEqual((row.state, row.user_id), ("in_app", self.designer))
        self.assertIn("Loft 18 or 24?", row.text)

    def test_party_pdf(self):
        self.go_live()
        visit = self.start()
        a = self.add("Wardrobe loft depth 24 in.", partner=self.ag_carp, visit=visit)
        self.add("Shift the TV unit", partner=self.ag_carp, visit=visit)
        self.add("Add 2 points", partner=self.ag_elec, visit=visit)
        result = visit.with_user(self.coordinator).rvt_send_party(self.ag_carp.id)
        self.assertEqual(result, {"points": 2, "new": 2, "sent": 1})
        kind, number, text, name, head = self.sent[0]
        self.assertEqual((kind, number), ("file", "+919824418830"))
        self.assertEqual(text, "મિનિટ્સ · Shah Residence · મુલાકાત 1 · %s %s: તમારા માટે 2 points. PDF જોડેલ છે." % (
            self.today.day, ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"][self.today.month - 1]))
        self.assertEqual(name, "MOM - Visit 1 - Mahadev Furniture.pdf")
        self.assertEqual(a.sent_count, 1, "the points carry their sent tick")
        self.assertEqual(self.logs("mom_party_pdf").document, "MOM - Visit 1 - Mahadev Furniture.pdf")
        # a point added afterwards: sent again, counted as new
        self.add("Fix the drawer channels", partner=self.ag_carp, visit=visit)
        visit.with_user(self.coordinator).rvt_send_party(self.ag_carp.id)
        self.assertIn("3 points (1 new)", self.sent[1][2])

    def test_client_item(self):
        self.go_live()
        item = self.add("Choose the kitchen platform stone", kind="client", due=4)
        self.assertFalse(self.sent, "not before the office confirms it")
        item.with_user(self.coordinator).action_confirm()
        self.assertEqual(self.sent[0][1], "+919825070011")
        self.assertIn("we need your go-ahead on “Choose the kitchen platform stone”", self.sent[0][2])
        self.assertEqual(item.sent_count, 1)

    def test_remind(self):
        self.go_live()
        project = self.project.with_user(self.coordinator)
        self.assertEqual(project.rvt_remind("Point 9: loft depth", agency_id=self.ag_carp.id), 1)
        self.assertEqual(self.sent[0][2], "યાદ અપાવવા · Shah Residence: Point 9: loft depth")
        self.assertEqual(project.rvt_remind("Please have a look at the layout.", client=True), 1)
        self.assertEqual(self.sent[1][2], "Reminder · Shah Residence: Please have a look at the layout.")
        with self.assertRaises(UserError):
            project.rvt_remind("  ", agency_id=self.ag_carp.id)
        with self.assertRaises(UserError):
            project.rvt_remind("Hello", agency_id=self.ag_carp2.id)
        with self.assertRaises(AccessError):
            self.project.with_user(self.outsider).rvt_remind("Hello", agency_id=self.ag_carp.id)
        with self.assertRaises(AccessError):
            self.project.with_user(self.agency_user).rvt_remind("Hello", client=True)

    def test_invite(self):
        self.go_live()
        project = self.project.with_user(self.coordinator)
        count = project.rvt_invite([self.ag_carp.id, self.ag_carp2.id], self.client_contact.ids)
        self.assertEqual(count, 2, "the agency's contact person and the client; an agency off the project is left out")
        self.assertTrue(self.carp_person.rvt_invited_on)
        self.assertTrue(self.client_contact.rvt_invited_on)
        texts = {s[1]: s[2] for s in self.sent}
        self.assertTrue(texts["+919824418830"].startswith("Shah Residence: Revert એ તમને ઉમેર્યા છે."))
        self.assertTrue(texts["+919825070011"].startswith("Shah Residence: Revert has added you."))
        # step 6 of onboarding invites whoever was ticked
        result = self.Project.with_user(self.coordinator).rvt_onboard({
            "project_id": self.project.id, "invite": {"agency_ids": [self.ag_elec.id], "client": False}})
        self.assertEqual(result["invited"], 1)

    def test_a_failing_message_does_not_break_the_action(self):
        self.go_live()

        def boom(self_, account, number, text):
            raise RuntimeError("the helper service is down")
        self.patch(type(self.Notify), "_wa_send_text", boom)
        drawing = self.drawing("EL", "Electrical layout", "elec")
        self.release(drawing, [self.ag_elec])
        self.assertEqual(drawing.state, "released", "the drawing is released even though the message failed")
        row = self.logs("drawing_released")
        self.assertEqual(row.state, "failed")
        self.assertIn("helper service is down", row.reason)

    def test_log_follows_the_project(self):
        self.project.with_user(self.coordinator).rvt_remind("Hello", agency_id=self.ag_carp.id)
        self.assertTrue(self.Log.with_user(self.designer).search([("project_id", "=", self.project.id)]))
        self.assertFalse(self.Log.with_user(self.outsider).search([("project_id", "=", self.project.id)]))
        with self.assertRaises(AccessError):
            self.Log.with_user(self.agency_user).search([])
