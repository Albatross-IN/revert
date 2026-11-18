from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.tests import new_test_user, tagged

from .common import PNG, MomCommon


@tagged("post_install", "-at_install")
class TestMom(MomCommon):

    def test_visit_numbers_are_the_rank_of_the_date(self):
        v1 = self.Visit.create({"project_id": self.project.id, "date": self.days(-12), "state": "finished"})
        v2 = self.Visit.create({"project_id": self.project.id, "date": self.days(-5), "state": "finished"})
        self.assertEqual((v1.number, v2.number), (1, 2))
        today = self.start()
        self.assertEqual((today.number, today.date, today.state), (3, self.today, "open"))
        self.assertEqual(today.started_by_id, self.coordinator)
        self.assertEqual(today.attendees, "Meera")
        self.assertEqual(self.start(), today, "the open visit is taken up again, not doubled")
        # a visit entered later for an earlier date takes its place in the order
        early = self.Visit.create({"project_id": self.project.id, "date": self.days(-20), "state": "finished"})
        self.assertEqual((early.number, v1.number, v2.number, today.number), (1, 2, 3, 4))
        today.with_user(self.coordinator).action_finish()
        self.assertEqual(today.state, "finished")
        again = self.start()
        self.assertEqual((again, again.state), (today, "open"), "the same day's visit is reopened")
        other, _ = self.onboard(name="Mehta Office")
        self.assertEqual(self.Visit.create({"project_id": other.id, "date": self.today}).number, 1, "numbers are per project")
        with self.assertRaises(AccessError):
            self.Visit.with_user(self.outsider).rvt_start(self.project.id)

    def test_points_serial_and_defaults(self):
        visit = self.start()
        a = self.add("Wardrobe loft depth 24 in. Check with the site beam", partner=self.ag_carp, visit=visit, entity_id=self.master.id)
        b = self.add("Add 2 points near the study table", partner=self.ag_elec, visit=visit)
        c = self.add("Choose the kitchen platform stone", kind="client", due=4)
        d = self.add("Send the revised kitchen elevation", kind="staff", user_id=self.designer.id)
        e = self.add("Send tile samples for toilet 1", kind="vendor", party_name="Asian Tiles (vendor)")
        self.assertEqual([p.number for p in (a, b, c, d, e)], [1, 2, 3, 4, 5], "one serial per project, visit or not")
        self.assertEqual(a.trade_id.code, "carp", "the agency's trade on this project")
        self.assertEqual(a.raised_by_id, self.coordinator)
        self.assertEqual((a.state, a.sent_count), ("open", 0))
        self.assertEqual(c.partner_id, self.client_partner)
        self.assertFalse(c.client_confirmed, "client points wait for the office by default")
        self.assertFalse(c.visit_id, "raised from the office")
        self.assertEqual((a.party_label, c.party_label, d.party_label, e.party_label),
                         ("Mahadev Furniture", "Mr. Nirav Shah", "Riya Trivedi", "Asian Tiles (vendor)"))
        with self.assertRaises(UserError):
            self.add("   ", partner=self.ag_carp)
        with self.assertRaises(ValidationError):
            self.add("For nobody", kind="agency")
        with self.assertRaises(ValidationError):
            self.add("For nobody", kind="staff")
        with self.assertRaises(AccessError):
            self.add("Not my project", partner=self.ag_carp, user=self.outsider)

    def test_client_confirmation_setting(self):
        held = self.add("Confirm the wall colour for bedroom 2", kind="client")
        self.assertFalse(held.client_confirmed)
        held.with_user(self.coordinator).action_confirm()
        self.assertTrue(held.client_confirmed)
        self.env["ir.config_parameter"].sudo().set_bool("rvt.client_points_need_confirmation", False)
        direct = self.add("Share the appliance list", kind="client")
        self.assertTrue(direct.client_confirmed, "with the setting off the client sees it at once")

    def test_close_reopen_and_the_waiting_line(self):
        point = self.add("Close chasing near the kitchen window", partner=self.ag_civil, entity_id=self.kitchen.id)
        self.assertEqual(point.trade_id.code, "civ")
        line = self.line(self.project, "Kitchen", "civ")
        self.assertEqual(line.rvt_cell()["open_points"], 1)
        self.assertEqual(point.rvt_cell_line(), line.id, "the last open point of this cell: the screen offers “mark done”")
        second = self.add("Fill the gap under the sill", partner=self.ag_civil, entity_id=self.kitchen.id)
        self.assertFalse(point.rvt_cell_line(), "another point is still open in the cell")
        self.assertFalse(line._rvt_can_remove(), "a cell that carries points is not removed by unticking")
        with self.assertRaises(AccessError):
            point.with_user(self.outsider).action_close("no")
        point.with_user(self.coordinator).action_close("Done, checked on site", PNG)
        self.assertEqual((point.state, point.closed_by_id, point.closed_on, point.close_note),
                         ("closed", self.coordinator, self.today, "Done, checked on site"))
        self.assertTrue(point.has_close_photo)
        self.assertEqual(second.rvt_cell_line(), line.id)
        point.with_user(self.coordinator).action_reopen()
        self.assertEqual(point.state, "open")
        # a line waiting for a client item is free when the item closes
        item = self.add("Choose the kitchen platform stone", kind="client")
        carp = self.line(self.project, "Kitchen", "carp")
        carp.rvt_set_state("waiting", cause="client", point_id=item.id)
        self.assertEqual(carp.rvt_wait_point_id, item)
        item.action_confirm()
        item.rvt_client_done(self.client_contact)
        self.assertEqual(item.state, "closed")
        self.assertIn("Nirav Shah", item.close_note)
        self.assertEqual(carp.rvt_work_state, "not_started")
        with self.assertRaises(UserError):
            item.rvt_client_done(self.client_contact)

    def test_offline_batch_is_created_once(self):
        visit = self.start()
        batch = [
            {"project_id": self.project.id, "visit_id": visit.id, "text": "Shift the TV unit 4 in. to the left",
             "for_kind": "agency", "partner_id": self.ag_carp.id, "client_uid": "phone-1-a"},
            {"project_id": self.project.id, "visit_id": visit.id, "text": "Raise the garden tap wall by 6 in.",
             "for_kind": "agency", "partner_id": self.ag_civil.id, "client_uid": "phone-1-b", "photo": PNG},
        ]
        first = self.Point.with_user(self.coordinator).rvt_add(batch)
        again = self.Point.with_user(self.coordinator).rvt_add(batch)
        self.assertEqual(first, again, "replaying the same batch gives the same points")
        self.assertEqual(len(visit.point_ids), 2)
        self.assertTrue(self.Point.browse(first[1]).has_photo)

    def test_send_party(self):
        visit = self.start()
        a = self.add("Wardrobe loft depth 24 in.", partner=self.ag_carp, visit=visit)
        self.add("Shift the TV unit", partner=self.ag_carp, visit=visit)
        self.add("Add 2 points near the study", partner=self.ag_elec, visit=visit)
        closed = self.add("Bring laminate samples", partner=self.ag_carp, visit=visit)
        closed.action_close("Shown")
        result = visit.with_user(self.coordinator).rvt_send_party(self.ag_carp.id)
        self.assertEqual(result, {"points": 2, "new": 2, "sent": 0}, "no sender installed: held, nothing marked as sent")
        self.assertEqual(a.sent_count, 0)
        self.assertEqual(visit._rvt_party_people(self.ag_carp).name, "Bherubhai Suthar")
        # when a sender is there, the points are marked and later ones count as new
        sent = []
        self.patch(type(self.env["rvt.notify"]), "send", lambda self_, event, record, people, **kw: sent.append((event, people, kw)) or 1)
        result = visit.with_user(self.coordinator).rvt_send_party(self.ag_carp.id)
        self.assertEqual(result, {"points": 2, "new": 2, "sent": 1})
        self.assertEqual(sent[0][0], "mom_party_pdf")
        self.assertEqual(sent[0][1].name, "Bherubhai Suthar")
        self.assertEqual(a.sent_count, 1)
        self.add("Fix the drawer channels", partner=self.ag_carp, visit=visit)
        result = visit.with_user(self.coordinator).rvt_send_party(self.ag_carp.id)
        self.assertEqual((result["points"], result["new"]), (3, 1), "sent again, with the new one marked")
        self.assertEqual(visit.rvt_send_party(self.ag_pop.id), {"points": 0, "new": 0, "sent": 0})

    def test_pdf_content(self):
        visit = self.start()
        self.add("Wardrobe loft depth 24 in.", partner=self.ag_carp, visit=visit, entity_id=self.master.id, photo=PNG)
        self.add("Add 2 points near the study table", partner=self.ag_elec, visit=visit)
        self.add("Confirm the wall colour", kind="client", visit=visit)
        Report = self.env["ir.actions.report"]
        html = Report._render_qweb_html("rvt_mom.action_report_visit", visit.ids, data={"party": False})[0].decode()
        for text in ("Minutes of meeting", "Shah Residence", "Wardrobe loft depth 24 in.", "Add 2 points near the study table",
                     "Mahadev Furniture", "Jay Electric", "Master bedroom", "All parties", "NEW", "data:image/png;base64,"):
            self.assertIn(text, html)
        party = {"kind": "agency", "partner_id": self.ag_carp.id}
        html = Report._render_qweb_html("rvt_mom.action_report_visit", visit.ids, data={"party": party})[0].decode()
        self.assertIn("Wardrobe loft depth 24 in.", html)
        self.assertNotIn("Add 2 points near the study table", html, "a party's PDF holds only its own points")
        self.assertNotIn("Confirm the wall colour", html)
        html = Report._render_qweb_html("rvt_mom.action_report_open_points", self.project.ids)[0].decode()
        self.assertIn("Open points", html)
        self.assertIn("Confirm the wall colour", html)
        document = visit.with_user(self.coordinator).rvt_pdf(party)   # the test run renders it without the PDF engine
        self.assertIn(b"Wardrobe loft depth 24 in.", document)
        with self.assertRaises(AccessError):
            visit.with_user(self.outsider).rvt_pdf()

    # ---- access -------------------------------------------------------
    def test_agency_reads_only_its_own_points(self):
        mine = self.add("Wardrobe loft depth 24 in.", partner=self.ag_carp)
        theirs = self.add("Add 2 points near the study table", partner=self.ag_elec)
        staff = self.add("Send the revised elevation", kind="staff", user_id=self.designer.id)
        client = self.add("Choose the stone", kind="client")
        seen = self.Point.with_user(self.agency_user).search([])
        self.assertEqual(seen, mine)
        for point in (theirs, staff, client):
            with self.assertRaises(AccessError):
                point.with_user(self.agency_user).read(["text"])
        with self.assertRaises(AccessError):
            mine.with_user(self.agency_user).write({"state": "closed"})
        with self.assertRaises(AccessError):
            mine.with_user(self.agency_user).action_close("done")
        with self.assertRaises(AccessError):
            self.Point.with_user(self.agency_user).rvt_add([{"project_id": self.project.id, "text": "x", "for_kind": "staff"}])

    def test_client_reads_its_confirmed_items_only(self):
        client_user = new_test_user(self.env, "t_client_pt", groups="rvt_base.group_rvt_client", partner_id=self.client_contact.id)
        held = self.add("Confirm the wall colour", kind="client")
        shown = self.add("Choose the kitchen platform stone", kind="client")
        shown.action_confirm()
        self.add("Wardrobe loft", partner=self.ag_carp)
        self.assertEqual(self.Point.with_user(client_user).search([]), shown)
        with self.assertRaises(AccessError):
            held.with_user(client_user).read(["text"])
        stranger = new_test_user(self.env, "t_client_pt2", groups="rvt_base.group_rvt_client")
        self.assertFalse(self.Point.with_user(stranger).search([]))

    def test_staff_follow_the_project(self):
        point = self.add("Wardrobe loft", partner=self.ag_carp)
        self.assertIn(point, self.Point.with_user(self.designer).search([("project_id", "=", self.project.id)]))
        self.assertFalse(self.Point.with_user(self.outsider).search([("project_id", "=", self.project.id)]))
