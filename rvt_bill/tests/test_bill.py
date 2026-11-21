from psycopg2 import IntegrityError

from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.tests import tagged
from odoo.tools import mute_logger

from odoo.addons.rvt_mom.tests.common import PNG, MomCommon


@tagged("post_install", "-at_install")
class TestBill(MomCommon):
    """The rules of a bill: asked first, uploaded against the request, reviewed, then paid in
    parts by the owner. Amounts are the owner's."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Bill = cls.env["rvt.bill"]
        cls.Payment = cls.env["rvt.bill.payment"]
        cls.Log = cls.env["rvt.notify.log"]

    def setUp(self):
        super().setUp()
        self.log_floor = self.Log.search([], order="id desc", limit=1).id

    def logs(self, event):
        return self.Log.search([("event", "=", event), ("id", ">", self.log_floor)], order="id")

    def ask(self, what="Carpentry, stage 1", agency=None, user=None, **kw):
        agency = agency or self.ag_carp
        return self.Bill.with_user(user or self.coordinator).rvt_ask(self.project.id, agency.id, what, **kw)

    def accepted(self, amount=100000.0):
        bill = self.ask()
        bill.with_user(self.agency_user).rvt_upload("MF/118", amount, PNG)
        bill.with_user(self.coordinator).rvt_review(True)
        return bill

    # ------------------------------------------------------------------
    def test_asked_uploaded_accepted_paid_in_two_parts(self):
        bill = self.ask(up_to=120000)
        self.assertEqual(bill.state, "asked")
        self.assertEqual(bill.trade_id.code, "carp", "the trade is the agency's on this project")
        self.assertEqual(bill.asked_by_id, self.coordinator)
        self.assertEqual(bill.sudo().up_to_amount, 120000)
        self.assertEqual(len(self.logs("bill_asked")), 1, "the agency's contact person is told")

        bill.with_user(self.agency_user).rvt_upload("MF/118", 100000, PNG)
        self.assertEqual(bill.state, "submitted")
        self.assertEqual(bill.sudo().amount, 100000)
        self.assertEqual(bill.bill_number, "MF/118")
        self.assertEqual(bill.submitted_on, self.today)
        self.assertTrue(bill.has_document)
        self.assertEqual(self.logs("bill_submitted").mapped("user_id"), self.coordinator, "the office hears of it in the app")

        bill.with_user(self.coordinator).rvt_review(True)
        self.assertEqual(bill.state, "accepted")
        self.assertEqual(len(self.logs("bill_accepted")), 1)

        bill.with_user(self.owner).rvt_pay(40000, "client", "upi", PNG)
        self.assertEqual(bill.state, "part_paid")
        self.assertEqual(bill.sudo().balance, 60000)
        bill.with_user(self.owner).rvt_pay(60000, "revert", "bank")
        self.assertEqual(bill.state, "paid")
        self.assertEqual(bill.sudo().payment_ids.mapped("paid_by"), ["client", "revert"])
        self.assertTrue(bill.sudo().payment_ids[0].has_proof)
        texts = self.logs("bill_paid").mapped("text")
        self.assertEqual(len(texts), 2)
        self.assertIn("Part paid", texts[0])
        self.assertIn("Paid", texts[1])
        self.assertNotIn("40", "".join(texts), "the message carries the state, never an amount")

    def test_no_payment_without_an_accepted_bill(self):
        with self.assertRaises((IntegrityError, ValidationError)), mute_logger("odoo.sql_db"), self.cr.savepoint():
            self.Payment.with_user(self.owner).create({"amount": 5000, "paid_by": "client"})
            self.env.flush_all()
        bill = self.ask()
        with self.assertRaises(ValidationError):
            self.Payment.with_user(self.owner).create({"bill_id": bill.id, "amount": 5000})
        with self.assertRaises(ValidationError):
            bill.with_user(self.owner).rvt_pay(5000, "client")
        bill.with_user(self.agency_user).rvt_upload("MF/1", 20000)
        with self.assertRaises(ValidationError):
            bill.with_user(self.owner).rvt_pay(5000, "client")
        self.assertFalse(bill.sudo().payment_ids, "a submitted bill is not paid before it is accepted")

    def test_payments_add_up_to_the_bill_and_no_further(self):
        bill = self.accepted(50000)
        with self.assertRaises(ValidationError):
            bill.with_user(self.owner).rvt_pay(0, "client")
        with self.assertRaises(ValidationError) as refused:
            bill.with_user(self.owner).rvt_pay(60000, "client")
        self.assertIn("₹50,000", str(refused.exception))
        bill.with_user(self.owner).rvt_pay(30000, "client")
        with self.assertRaises(ValidationError) as refused:
            bill.with_user(self.owner).rvt_pay(20001, "client")
        self.assertIn("₹20,000", str(refused.exception))
        self.assertEqual(bill.state, "part_paid")
        payment = bill.sudo().payment_ids
        payment.unlink()
        self.assertEqual(bill.state, "accepted", "the state follows the payments")

    def test_only_the_office_starts_a_bill_and_only_its_agency_uploads(self):
        with self.assertRaises(AccessError):
            self.Bill.with_user(self.agency_user).rvt_ask(self.project.id, self.ag_carp.id, "My own bill")
        with self.assertRaises(AccessError):
            self.Bill.with_user(self.agency_user).create({
                "project_id": self.project.id, "agency_id": self.ag_carp.id, "trade_id": self.trade["carp"].id, "what": "x"})
        with self.assertRaises(UserError):
            self.ask(agency=self.ag_carp2)          # not an agency of this project
        with self.assertRaises(UserError):
            self.ask(what="  ")
        bill = self.ask()
        with self.assertRaises(AccessError):
            bill.with_user(self.other_agency_user).rvt_upload("JE/1", 1000)
        self.assertFalse(self.Bill.with_user(self.other_agency_user).search([("id", "=", bill.id)]), "another agency does not see it")
        self.assertEqual(self.Bill.with_user(self.agency_user).search([("id", "=", bill.id)]), bill)
        with self.assertRaises(UserError):
            bill.with_user(self.agency_user).rvt_upload("MF/1", 0)
        bill.with_user(self.agency_user).rvt_upload("MF/1", 1000)
        with self.assertRaises(UserError):
            bill.with_user(self.agency_user).rvt_upload("MF/1", 1200)     # already with the office
        with self.assertRaises(AccessError):
            bill.with_user(self.agency_user).rvt_review(True)

    def test_returned_with_a_reason_and_uploaded_again(self):
        bill = self.ask()
        bill.with_user(self.coordinator).rvt_upload("MF/7", 18000)        # the office uploads on the agency's behalf
        self.assertEqual(bill.sudo().uploaded_by_id, self.coordinator)
        self.assertFalse(self.logs("bill_submitted"), "the office does not tell itself")
        with self.assertRaises(UserError):
            bill.with_user(self.coordinator).rvt_review(False, "  ")
        bill.with_user(self.coordinator).rvt_review(False, "GST number is missing")
        self.assertEqual((bill.state, bill.return_reason), ("returned", "GST number is missing"))
        self.assertIn("GST number is missing", self.logs("bill_returned").text)
        bill.with_user(self.agency_user).rvt_upload("MF/7A", 18500, PNG)
        self.assertEqual((bill.state, bill.return_reason, bill.sudo().amount), ("submitted", False, 18500))
        with self.assertRaises(UserError):
            self.ask().with_user(self.coordinator).rvt_review(True)       # nothing uploaded yet

    def test_billed_to_follows_the_project_and_can_differ_per_bill(self):
        self.assertEqual(self.ask().billed_to, "client")
        self.assertEqual(self.ask(billed_to="revert").billed_to, "revert")
        self.project.sudo().rvt_billed_to_default = "revert"
        bill = self.ask()
        self.assertEqual(bill.billed_to, "revert")
        bill.with_user(self.coordinator).rvt_set_billed_to("client")
        self.assertEqual(bill.billed_to, "client")
        with self.assertRaises(UserError):
            bill.with_user(self.coordinator).rvt_set_billed_to("somebody")
        paid = self.accepted(1000)
        paid.with_user(self.owner).rvt_pay(1000, "client")
        with self.assertRaises(UserError):
            paid.with_user(self.coordinator).rvt_set_billed_to("revert")

    def test_amounts_are_the_owners(self):
        bill = self.accepted(75000)
        bill.with_user(self.owner).rvt_pay(25000, "revert")
        as_staff = bill.with_user(self.coordinator)
        self.assertEqual(as_staff.state, "part_paid", "staff see the state")
        self.assertTrue(as_staff.has_document)
        for field in ("amount", "up_to_amount", "paid_amount", "balance", "payment_ids"):
            with self.assertRaises(AccessError, msg=field):
                as_staff.read([field])
        with self.assertRaises(AccessError):
            as_staff.write({"amount": 1})
        with self.assertRaises(AccessError):
            as_staff.rvt_pay(1000, "client")
        with self.assertRaises(AccessError):
            self.Payment.with_user(self.coordinator).search([])
        with self.assertRaises(AccessError):
            self.Payment.with_user(self.agency_user).search([])
        self.assertEqual(bill.with_user(self.owner).read(["amount"])[0]["amount"], 75000)
        # the screens' rows: the owner gets the money, other staff a bill without it
        Desk = self.env["rvt.desk"]
        mine = lambda user: next(b for b in Desk.with_user(user).snapshot()["bills"] if b["id"] == "b%s" % bill.id)
        row = mine(self.coordinator)
        self.assertEqual((row["st"], row["amount"], row["upto"], row["pay"], row["doc"]), ("part_paid", 0, None, [], "image"))
        row = mine(self.owner)
        self.assertEqual((row["amount"], [(p["amount"], p["by"], p["mode"]) for p in row["pay"]]), (75000, [(25000, "revert", "Bank transfer")]))
        waiting = self.ask("Carpentry, stage 2", up_to=90000)
        row = next(b for b in Desk.with_user(self.coordinator).snapshot()["bills"] if b["id"] == "b%s" % waiting.id)
        self.assertIsNone(row["amount"], "nothing uploaded yet")
        self.assertTrue(Desk.with_user(self.coordinator).snapshot()["features"]["bills"])

    def test_a_staff_member_outside_the_project_has_no_bill_of_it(self):
        bill = self.ask()
        self.assertFalse(self.Bill.with_user(self.outsider).search([("id", "=", bill.id)]))
        with self.assertRaises(AccessError):
            bill.with_user(self.outsider).rvt_review(True)
        with self.assertRaises(AccessError):
            self.Bill.with_user(self.outsider).rvt_ask(self.project.id, self.ag_carp.id, "Not my project")

    def test_the_document_is_a_photo_or_a_pdf(self):
        bill = self.ask()
        with self.assertRaises(UserError):
            bill.with_user(self.agency_user).rvt_upload("MF/1", 1000, "bm90IGEgYmlsbA==")      # plain text
        self.assertEqual(bill.state, "asked")
        bill.with_user(self.agency_user).rvt_upload("MF/1", 1000, PNG)
        self.assertEqual(bill.document_name, "bill.png")

    def test_b10_a_submitted_bill_waits_for_review(self):
        bill = self.ask()
        bill.with_user(self.agency_user).rvt_upload("MF/9", 42000)
        picture = self.project.with_user(self.coordinator).rvt_picture()
        self.assertNotIn("B10", [b["rule"] for b in picture["blockers"]], "within the day limit it is only a thing to do")
        review = [n for n in picture["next"]["revert"] if n.get("section") == "bill"]
        self.assertEqual(len(review), 1)
        self.assertEqual(review[0]["action"], {"key": "bill", "label": "Review", "bill_id": bill.id})
        self.assertFalse(review[0]["late"])
        bill.sudo().submitted_on = self.days(-3)
        picture = self.project.with_user(self.coordinator).rvt_picture()
        blocker = next(b for b in picture["blockers"] if b["rule"] == "B10")
        self.assertEqual((blocker["age"], blocker["holds"]), (3, "Carpentry, stage 1"))
        self.assertIn("Mahadev Furniture", blocker["text"])
        today = self.Project.with_user(self.coordinator).rvt_today()
        self.assertTrue([t for t in today if t.get("section") == "bill" and t["late"]], "it is on the coordinator's Today")
        bill.with_user(self.coordinator).rvt_review(True)
        picture = self.project.with_user(self.coordinator).rvt_picture()
        self.assertNotIn("B10", [b["rule"] for b in picture["blockers"]])

    def test_the_desk_operations(self):
        Desk = self.env["rvt.desk"].with_user(self.coordinator)
        made = Desk.op("ask_bill", {"project": self.project.id, "agency": "a%s" % self.ag_carp.id, "trade": "carp",
                                    "what": "Wardrobes, stage 1", "upto": 80000, "billedTo": "revert"})
        bill = self.Bill.browse(int(made["id"][1:]))
        self.assertEqual((bill.what, bill.billed_to, bill.sudo().up_to_amount), ("Wardrobes, stage 1", "revert", 80000))
        Desk.op("upload_bill", {"bill": made["id"], "no": "MF/21", "amount": 64000, "file": PNG, "name": "bill.png"})
        self.assertEqual(bill.state, "submitted")
        Desk.op("bill_to", {"bill": made["id"], "to": "client"})
        self.assertEqual(bill.billed_to, "client")
        Desk.op("review_bill", {"bill": made["id"], "ok": True})
        with self.assertRaises(AccessError):
            Desk.op("pay_bill", {"bill": made["id"], "amount": 1000, "by": "client", "mode": "UPI"})
        self.env["rvt.desk"].with_user(self.owner).op("pay_bill", {"bill": made["id"], "amount": 64000, "by": "client", "mode": "Cheque", "file": PNG})
        self.assertEqual(bill.state, "paid")
        self.assertEqual(bill.sudo().payment_ids.mode, "cheque")
