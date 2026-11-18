from odoo import fields
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.tests import new_test_user, tagged

from .common import PDF, DrawingCommon


@tagged("post_install", "-at_install")
class TestDrawing(DrawingCommon):

    def test_numbering(self):
        el1 = self.drawing("EL", "Electrical layout", "elec")
        el2 = self.drawing("el", "Electrical layout, first floor", "elec")
        fl = self.drawing("FL", "Furniture layout")
        self.assertEqual((el1.sheet_no, el2.sheet_no, fl.sheet_no), ("EL-01", "EL-02", "FL-01"))
        self.assertEqual(el1.display_name, "EL-01 Electrical layout")
        other, _ = self.onboard(name="Mehta Office")
        self.assertEqual(self.Drawing.create({"project_id": other.id, "code": "EL", "name": "Electrical layout"}).sheet_no, "EL-01",
                         "the running number is per project")
        self.assertEqual(el1.revision_ids.number, 1, "a drawing starts with revision 1 in draft")
        self.assertEqual(el1.revision_ids.state, "draft")
        with self.assertRaises(ValidationError):
            self.drawing("XX", "Odd", needs=True)

    def test_approval_on(self):
        drawing = self.drawing("CD", "Wardrobe details", "carp", for_client=True, needs=True)
        self.assertEqual(drawing.state, "to_draw")
        drawing.with_user(self.designer).action_start()
        self.assertEqual(drawing.state, "in_progress")
        with self.assertRaises(UserError):
            drawing.with_user(self.designer).action_send_for_approval()
        self.send(drawing, note="Master bedroom wardrobe with loft")
        revision = drawing.current_revision_id
        self.assertEqual((drawing.state, revision.state), ("awaiting_approval", "awaiting_approval"))
        self.assertEqual(revision.sent_by_id, self.designer)
        self.assertEqual(revision.file_name, "CD-01_rev1.pdf")
        self.assertEqual(revision.note, "Master bedroom wardrobe with loft")
        with self.assertRaises(UserError):
            drawing.with_user(self.designer).action_release([self.ag_carp.id])
        with self.assertRaises(AccessError):
            drawing.with_user(self.designer).action_approve()
        with self.assertRaises(AccessError):
            drawing.with_user(self.coordinator).action_send_back("no")
        # sent back with a reason, sent again, approved
        with self.assertRaises(UserError):
            drawing.with_user(self.principal).action_send_back(" ")
        drawing.with_user(self.principal).action_send_back("Loft depth to match the beam")
        self.assertEqual((drawing.state, revision.state, revision.back_note), ("in_progress", "draft", "Loft depth to match the beam"))
        drawing.with_user(self.designer).action_send_for_approval()
        self.assertFalse(revision.back_note)
        drawing.with_user(self.principal).action_approve()
        self.assertEqual((drawing.state, revision.state, revision.approved_by_id), ("approved", "approved", self.principal))
        with self.assertRaises(UserError):
            drawing.with_user(self.principal).action_approve()
        # an owner may approve as well: the owner role includes what the principal may do
        other = self.drawing("KD", "Kitchen details", "carp")
        self.send(other)
        other.with_user(self.owner).action_approve()
        self.assertEqual(other.state, "approved")

    def test_approval_off(self):
        self.env["ir.config_parameter"].sudo().set_bool("rvt.release_needs_approval", False)
        drawing = self.drawing("EL", "Electrical layout", "elec")
        self.send(drawing)
        self.assertEqual(drawing.state, "approved", "the designer goes straight to choosing receivers")
        self.assertEqual(drawing.current_revision_id.approved_by_id, self.designer)
        drawing.with_user(self.designer).action_release([self.ag_elec.id])
        self.assertEqual(drawing.state, "released")

    def test_receivers_proposal(self):
        wardrobe = self.drawing("CD", "Wardrobe details", "carp", for_client=True, needs=True)
        rows = wardrobe.with_user(self.designer).rvt_receivers()
        self.assertEqual(rows[0]["name"], "Mahadev Furniture", "the drawing's own trade comes first")
        self.assertTrue(rows[0]["own"] and rows[0]["ticked"])
        self.assertEqual(rows[0]["people"], "Bherubhai Suthar")
        self.assertEqual({r["name"] for r in rows if r["kind"] == "agency"},
                         {"Mahadev Furniture", "Ramesh Construction", "Jay Electric", "Shree POP"})
        self.assertEqual(rows[-1]["kind"], "client")
        self.assertTrue(rows[-1]["ticked"])
        switchboard = self.drawing("SB", "Switchboard details", "elec")
        self.assertNotIn("client", [r["kind"] for r in switchboard.rvt_receivers()], "not marked for the client")

    def test_release_and_supersede(self):
        drawing = self.drawing("FL", "Furniture layout", for_client=True, needs=True)
        with self.assertRaises(UserError):
            self.release(drawing)   # no receiver chosen
        result = self.release(drawing, [self.ag_carp, self.ag_carp2], client=True)
        self.assertEqual(result, {"freed": 0})
        rev1 = drawing.current_revision_id
        self.assertEqual((drawing.state, rev1.state), ("released", "released"))
        self.assertEqual(rev1.released_by_id, self.designer)
        self.assertEqual(rev1.receipt_ids.mapped("partner_id"), self.ag_carp | self.client_partner,
                         "an agency that is not on the project is not a receiver")
        self.assertEqual(rev1.client_decision, "pending")
        self.assertEqual(drawing.receiver_ids, self.ag_carp | self.client_partner)
        self.assertEqual(drawing.released_revision_id, rev1)
        # the next revision: receivers keep the released one until the new one goes out
        with self.assertRaises(UserError):
            self.drawing("WE", "Wall elevations").with_user(self.designer).action_new_revision()
        drawing.with_user(self.designer).action_new_revision("Study table moved")
        rev2 = drawing.current_revision_id
        self.assertEqual((rev2.number, rev2.state, drawing.state), (2, "draft", "in_progress"))
        self.assertEqual(drawing.released_revision_id, rev1)
        self.assertEqual(rev1.state, "released")
        self.release(drawing, [self.ag_carp, self.ag_pop], client=True)
        self.assertEqual((rev1.state, rev2.state), ("superseded", "released"))
        self.assertEqual(drawing.released_revision_id, rev2)
        self.assertEqual(drawing.receiver_ids, self.ag_carp | self.ag_pop | self.client_partner)

    def test_release_frees_waiting_lines(self):
        drawing = self.drawing("EL", "Electrical layout", "elec")
        master, living = self.line(self.project, "Master bedroom", "elec"), self.line(self.project, "Living room", "elec")
        with self.assertRaises(ValidationError):
            master.rvt_set_state("waiting", cause="drawing")
        master.rvt_set_state("waiting", cause="drawing", drawing_id=drawing.id)
        living.rvt_set_state("waiting", cause="drawing", drawing_id=drawing.id)
        self.assertEqual(master.rvt_wait_drawing_id, drawing)
        self.assertEqual(master.rvt_cell()["wait_drawing_id"], drawing.id)
        living.rvt_set_state("working")
        self.assertFalse(living.rvt_wait_drawing_id, "leaving Waiting clears what it waited for")
        living.rvt_set_state("waiting", cause="drawing", drawing_id=drawing.id)
        self.assertEqual(self.release(drawing, [self.ag_elec]), {"freed": 2})
        self.assertEqual((master.rvt_work_state, living.rvt_work_state), ("not_started", "not_started"))
        self.assertFalse(master.rvt_wait_drawing_id)

    def test_opened_and_questions(self):
        drawing = self.drawing("FC", "False ceiling layout", "pop", for_client=True, needs=True)
        self.release(drawing, [self.ag_pop, self.ag_elec], client=True)
        receipts = {r.partner_id: r for r in drawing.released_revision_id.receipt_ids}
        self.assertFalse(receipts[self.ag_pop].opened_on)
        person = self.env["res.partner"].search([("parent_id", "=", self.ag_pop.id)], limit=1)
        self.assertTrue(drawing.rvt_open(person), "one of the agency's people opens it: the agency has opened it")
        self.assertTrue(receipts[self.ag_pop].opened_on)
        first = receipts[self.ag_pop].opened_on
        self.assertFalse(drawing.rvt_open(person), "only the first opening is recorded")
        self.assertEqual(receipts[self.ag_pop].opened_on, first)
        self.assertFalse(drawing.rvt_open(self.ag_carp), "not a receiver")
        self.assertTrue(drawing.rvt_open(self.client_contact))
        self.assertEqual(receipts[self.ag_pop]._rvt_people().name, "Rajkumar Sharma")
        self.assertEqual(receipts[self.client_partner]._rvt_people(), self.client_contact)
        self.assertIn("/rvt/d/", receipts[self.ag_pop].rvt_link())
        # a question from the agency, answered by the designer
        qid = drawing.rvt_ask(person, "Cove depth near the beam: 3 in. or 4 in.?", via="app")
        question = self.env["rvt.drawing.question"].browse(qid)
        self.assertEqual((question.partner_id, question.asked_by_name, question.state), (self.ag_pop, "Rajkumar Sharma", "open"))
        with self.assertRaises(UserError):
            drawing.rvt_ask(person, "  ")
        with self.assertRaises(UserError):
            question.with_user(self.designer).action_answer("")
        question.with_user(self.designer).action_answer("4 in., as in section B")
        self.assertEqual((question.state, question.answered_by_id), ("answered", self.designer))
        logged = drawing.rvt_ask(self.client_partner, "Can the fan move to the centre?", via="office", person_name="Nirav Shah")
        self.assertEqual(self.env["rvt.drawing.question"].browse(logged).via, "office")

    def test_client_approves(self):
        drawing = self.drawing("WE", "Wall elevations", for_client=True, needs=True)
        line = self.line(self.project, "Master bedroom", "carp")
        self.release(drawing, [self.ag_carp], client=True)
        line.rvt_set_state("waiting", cause="client", drawing_id=drawing.id)
        with self.assertRaises(UserError):
            drawing.rvt_client_decide("maybe", partner=self.client_contact)
        drawing.rvt_client_decide("approved", partner=self.client_contact)
        revision = drawing.released_revision_id
        self.assertEqual(revision.client_decision, "approved")
        self.assertEqual(revision.client_decided_by, "Nirav Shah", "the record is the client's name, date and time")
        self.assertTrue(revision.client_decided_on)
        self.assertEqual(line.rvt_work_state, "not_started", "the line that waited for the client is free")
        with self.assertRaises(UserError):
            drawing.rvt_client_decide("approved", partner=self.client_contact)

    def test_client_asks_for_a_change(self):
        drawing = self.drawing("FL", "Furniture layout", for_client=True, needs=True, due=-8)
        self.release(drawing, [self.ag_carp], client=True)
        with self.assertRaises(UserError):
            drawing.rvt_client_decide("change", "", partner=self.client_contact)
        drawing.rvt_client_decide("change", "Please move the study table to the window side.", partner=self.client_contact)
        rev1 = drawing.released_revision_id
        self.assertEqual((rev1.client_decision, rev1.client_note), ("change", "Please move the study table to the window side."))
        rev2 = drawing.current_revision_id
        self.assertEqual((rev2.number, rev2.state), (2, "draft"))
        self.assertIn("Change asked by the client", rev2.note)
        self.assertEqual(drawing.state, "in_progress", "back on the designer's list")
        self.assertEqual(drawing.due_date, self.days(3))
        self.assertEqual(rev1.state, "released", "receivers keep revision 1 until revision 2 goes out")
        # no approval asked of the client when the drawing does not need it
        plain = self.drawing("DM", "Demolition layout", "civ", for_client=True)
        self.release(plain, [self.ag_civil], client=True)
        self.assertFalse(plain.released_revision_id.client_decision)

    def test_onboarding_creates_drawings(self):
        t = self.trade
        rows = self.Project.with_user(self.coordinator).rvt_drawing_proposal(
            [t["elec"].id, t["carp"].id], [self.designer.id, self.designer2.id])
        codes = [r["code"] for r in rows]
        self.assertEqual(codes[:5], ["ML", "FL", "WE", "3D", "DS"], "the general set first")
        self.assertEqual(set(codes[5:]), {"EL", "SB", "LT", "LC", "CD", "KD", "DD"})
        el = next(r for r in rows if r["code"] == "EL")
        self.assertEqual(el["designer_id"], self.designer2.id, "services drawings go to the second designer")
        self.assertEqual(el["due_date"], fields.Date.to_string(self.days(9)))
        self.assertTrue(next(r for r in rows if r["code"] == "ML")["ticked"], "the first of each set is ticked")
        self.assertFalse(next(r for r in rows if r["code"] == "DS")["ticked"])
        ticked = [r for r in rows if r["ticked"]]
        result = self.Project.with_user(self.coordinator).rvt_onboard({
            "project_id": self.project.id,
            "drawings": ticked + [{"code": "AD", "title": "Bar counter details", "trade_id": t["carp"].id,
                                   "designer_id": self.agency_user.id, "for_client": False, "needs_client_approval": True}],
        })
        self.assertEqual(result["drawings_created"], len(ticked) + 1)
        drawings = self.project.rvt_drawing_ids
        self.assertEqual(len(drawings), len(ticked) + 1)
        self.assertEqual(set(drawings.mapped("state")), {"to_draw"})
        bar = drawings.filtered(lambda d: d.code == "AD")
        self.assertEqual(bar.sheet_no, "AD-01")
        self.assertIn(bar.designer_id, self.designer | self.designer2, "somebody who is not staff cannot be the designer")
        self.assertFalse(bar.needs_client_approval, "not for the client, so no client approval")
        # the proposal now marks what exists
        again = self.Project.with_user(self.coordinator).rvt_drawing_proposal([t["elec"].id], [], self.project.id)
        self.assertTrue(next(r for r in again if r["code"] == "EL")["exists"])
        self.assertFalse(next(r for r in again if r["code"] == "EL")["ticked"])

    def test_designer_joins_the_team(self):
        self.assertNotIn(self.outsider, self.project.rvt_designer_ids)
        self.assertFalse(self.Drawing.with_user(self.outsider).search([("project_id", "=", self.project.id)]))
        drawing = self.drawing("LS", "Landscape layout", designer=self.outsider)
        self.assertIn(self.outsider, self.project.rvt_designer_ids, "a designer with a drawing here sees the project")
        self.assertEqual(self.Drawing.with_user(self.outsider).search([("project_id", "=", self.project.id)]), drawing)
        other = self.drawing("FB", "Fabrication details", "fab")
        other.designer_id = self.principal
        self.assertNotIn(self.principal, self.project.rvt_designer_ids, "the principal is on the team already")

    # ---- access -------------------------------------------------------
    def test_staff_access_follows_the_project(self):
        drawing = self.drawing("EL", "Electrical layout", "elec")
        self.assertIn(drawing, self.Drawing.with_user(self.designer2).search([("project_id", "=", self.project.id)]))
        self.assertFalse(self.Drawing.with_user(self.outsider).search([("project_id", "=", self.project.id)]))
        with self.assertRaises(AccessError):
            drawing.with_user(self.outsider).read(["name"])
        with self.assertRaises(AccessError):
            drawing.with_user(self.outsider).action_start()
        with self.assertRaises(AccessError):
            drawing.with_user(self.agency_user).action_start()

    def test_agency_sees_only_what_is_released_to_it(self):
        wardrobe = self.drawing("CD", "Wardrobe details", "carp")
        electrical = self.drawing("EL", "Electrical layout", "elec")
        draft = self.drawing("KD", "Kitchen details", "carp")
        carp_user, elec_user = self.agency_user, self.other_agency_user
        self.assertFalse(self.Drawing.with_user(carp_user).search([]), "nothing is released yet")
        self.release(wardrobe, [self.ag_carp])
        self.release(electrical, [self.ag_elec])
        self.assertEqual(self.Drawing.with_user(carp_user).search([]), wardrobe)
        self.assertEqual(self.Drawing.with_user(elec_user).search([]), electrical)
        with self.assertRaises(AccessError):
            electrical.with_user(carp_user).read(["name"])
        with self.assertRaises(AccessError):
            draft.with_user(carp_user).read(["name"])
        # only the released revision, never a draft or an older one
        wardrobe.with_user(self.designer).action_new_revision()
        Revision = self.env["rvt.drawing.revision"]
        seen = Revision.with_user(carp_user).search([("drawing_id", "=", wardrobe.id)])
        self.assertEqual(seen.mapped("number"), [1])
        self.assertEqual(self.Drawing.with_user(carp_user).search([]), wardrobe, "it keeps the drawing while revision 2 is drawn")
        self.release(wardrobe, [self.ag_carp])
        seen = Revision.with_user(carp_user).search([("drawing_id", "=", wardrobe.id)])
        self.assertEqual(seen.mapped("number"), [2], "the superseded revision goes out of sight")
        self.assertFalse(Revision.with_user(elec_user).search([("drawing_id", "=", wardrobe.id)]))
        with self.assertRaises(AccessError):
            wardrobe.with_user(carp_user).write({"name": "x"})
        # its own receipt and its own questions only
        Receipt = self.env["rvt.drawing.receipt"]
        self.assertEqual(Receipt.with_user(carp_user).search([]).mapped("partner_id"), self.ag_carp)
        with self.assertRaises(AccessError):
            Receipt.with_user(carp_user).search([]).read(["token"])
        wardrobe.rvt_ask(carp_user.partner_id, "Loft depth 18 or 24?")
        electrical.rvt_ask(elec_user.partner_id, "Which DB?")
        Question = self.env["rvt.drawing.question"]
        self.assertEqual(Question.with_user(carp_user).search([]).mapped("text"), ["Loft depth 18 or 24?"])

    def test_client_sees_only_drawings_marked_for_the_client(self):
        client_user = new_test_user(
            self.env, "t_client_dw", groups="rvt_base.group_rvt_client", partner_id=self.client_contact.id)
        layout = self.drawing("FL", "Furniture layout", for_client=True, needs=True)
        switchboard = self.drawing("SB", "Switchboard details", "elec")
        held = self.drawing("WE", "Wall elevations", for_client=True)
        self.release(layout, [self.ag_carp], client=True)
        self.release(switchboard, [self.ag_elec])
        self.release(held, [self.ag_carp], client=False)
        seen = self.Drawing.with_user(client_user).search([])
        self.assertEqual(seen, layout, "marked for the client AND released to the client")
        self.assertEqual(self.env["rvt.drawing.revision"].with_user(client_user).search([]).drawing_id, layout)
        other_client = new_test_user(self.env, "t_client_other_dw", groups="rvt_base.group_rvt_client")
        self.assertFalse(self.Drawing.with_user(other_client).search([]))
