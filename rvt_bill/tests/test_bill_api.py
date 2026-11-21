from odoo.tests import tagged

from odoo.addons.rvt_api.tests.common import ApiCase
from odoo.addons.rvt_mom.tests.common import PNG


@tagged("post_install", "-at_install")
class TestBillApi(ApiCase):
    """Bills through HTTP, role by role: what each may do, and what each is shown."""

    def setUp(self):
        super().setUp()
        self.staff = self.token(self.coordinator)
        self.boss = self.login(self.owner, device="phone-owner")["access_token"]
        self.agency = self.otp(self.carp_phone)["access_token"]
        self.other_agency = self.otp(self.elec_phone, device="phone-8")["access_token"]

    def ask(self, **extra):
        body = dict({"project_id": self.project.id, "agency_id": self.ag_carp.id, "what": "Carpentry, stage 1"}, **extra)
        answer = self.post("/bills", body, self.staff)
        self.assertEqual(answer.status_code, 200, answer.text)
        return answer.json()

    def agency_bill(self, token, bill_id):
        snap = self.get("/agency/snapshot", token).json()
        return next((b for b in snap["bills"] if b["id"] == bill_id), None)

    def test_asked_uploaded_from_the_phone_accepted_and_paid_in_two_parts(self):
        asked = self.ask(up_to=120000)
        number = int(asked["id"][1:])
        self.assertEqual((asked["st"], asked["billedTo"], asked["t"], asked["amount"]), ("asked", "client", "carp", None))
        self.assertIsNone(asked["upto"], "the coordinator who typed the ceiling does not read it back: amounts are the owner's")

        # the agency: the request is on its home and in its list; the ceiling and who asked are not
        snap = self.get("/agency/snapshot", self.agency).json()
        self.assertTrue(snap["features"]["bills"])
        mine = next(b for b in snap["bills"] if b["id"] == asked["id"])
        self.assertEqual((mine["st"], mine["upto"], mine["askedBy"], mine["pay"]), ("asked", None, None, []))
        home = self.get("/agency/home", self.agency).json()
        self.assertEqual([b["id"] for b in home["asks"]], [asked["id"]], "Revert asks")
        self.assertIsNone(self.agency_bill(self.other_agency, asked["id"]), "another agency never sees it")
        self.assertRefused(self.post("/agency/bills/%s/upload" % number, {"no": "JE/1", "amount": 500}, self.other_agency), 403)

        # a photographed bill from the phone
        self.assertRefused(self.post("/agency/bills/%s/upload" % number, {"no": "MF/118", "amount": 0, "photo": PNG}, self.agency), 422)
        sent = self.post("/agency/bills/%s/upload" % number, {"no": "MF/118", "amount": 100000, "photo": PNG}, self.agency)
        self.assertEqual(sent.status_code, 200, sent.text)
        self.assertEqual(sent.json()["st"], "submitted")
        self.assertEqual(self.agency_bill(self.agency, asked["id"])["amount"], 100000, "its own amount, as it wrote it")
        self.assertRefused(self.post("/agency/bills/%s/upload" % number, {"no": "MF/118", "amount": 90000}, self.agency), 422)
        picture = self.get("/files/bill/%s/document" % number, self.agency)
        self.assertEqual((picture.status_code, picture.headers["Content-Type"]), (200, "image/png"))
        self.assertEqual(self.get("/files/bill/%s/document" % number, self.other_agency).status_code, 403)

        # the office: sees the document and the state, not the amount; accepts
        row = next(b for b in self.get("/bills?project_id=%s" % self.project.id, self.staff).json() if b["id"] == asked["id"])
        self.assertEqual((row["st"], row["amount"], row["pay"], row["doc"]), ("submitted", 0, [], "image"))
        self.assertEqual(self.get("/files/bill/%s/document" % number, self.staff).status_code, 200)
        self.assertRefused(self.post("/agency/bills/%s/upload" % number, {"no": "x", "amount": 1}, self.staff), 403)
        self.assertRefused(self.post("/bills/%s/review" % number, {"ok": False, "reason": ""}, self.staff), 422)
        accepted = self.post("/bills/%s/review" % number, {"ok": True}, self.staff)
        self.assertEqual(accepted.json()["st"], "accepted")

        # the owner records two part payments; nobody else can
        self.assertRefused(self.post("/bills/%s/payments" % number, {"amount": 1000, "by": "client"}, self.staff), 403)
        self.assertRefused(self.post("/bills/%s/payments" % number, {"amount": 1000, "by": "client"}, self.agency), 403)
        first = self.post("/bills/%s/payments" % number, {"amount": 40000, "by": "client", "mode": "upi", "file": PNG}, self.boss)
        self.assertEqual(first.status_code, 200, first.text)
        self.assertEqual((first.json()["st"], first.json()["amount"], len(first.json()["pay"])), ("part_paid", 100000, 1))
        seen = self.agency_bill(self.agency, asked["id"])
        self.assertEqual((seen["st"], seen["pay"]), ("part_paid", []), "the agency sees Part paid, and no payment")
        self.assertRefused(self.post("/bills/%s/payments" % number, {"amount": 60001, "by": "revert"}, self.boss), 422)
        last = self.post("/bills/%s/payments" % number, {"amount": 60000, "by": "revert"}, self.boss).json()
        self.assertEqual((last["st"], [(p["amount"], p["by"], p["mode"], p["proof"]) for p in last["pay"]]),
                         ("paid", [(40000, "client", "UPI", True), (60000, "revert", "Bank transfer", False)]))
        seen = self.agency_bill(self.agency, asked["id"])
        self.assertEqual((seen["st"], seen["pay"], seen["amount"]), ("paid", [], 100000))
        proof = last["pay"][0]["id"]
        self.assertEqual(self.get("/files/payment/%s/proof" % proof, self.boss).status_code, 200)
        self.assertRefused(self.get("/files/payment/%s/proof" % proof, self.staff), 403)

        # the staff snapshot carries the same split
        staff_row = next(b for b in self.get("/staff/snapshot", self.staff).json()["bills"] if b["id"] == asked["id"])
        self.assertEqual((staff_row["st"], staff_row["amount"], staff_row["pay"]), ("paid", 0, []))
        boss_row = next(b for b in self.get("/staff/snapshot", self.boss).json()["bills"] if b["id"] == asked["id"])
        self.assertEqual((boss_row["amount"], len(boss_row["pay"])), (100000, 2))

    def test_the_client_has_nothing_of_bills(self):
        asked = self.ask()
        number = int(asked["id"][1:])
        self.post("/agency/bills/%s/upload" % number, {"no": "MF/2", "amount": 5000, "photo": PNG}, self.agency)
        client = self.otp(self.client_phone, device="phone-7")["access_token"]
        snap = self.get("/client/snapshot", client).json()
        self.assertFalse(snap["features"]["bills"])
        self.assertEqual(snap["bills"], [])
        self.assertRefused(self.get("/bills", client), 403)
        self.assertRefused(self.get("/agency/bills", client), 403)
        self.assertEqual(self.get("/files/bill/%s/document" % number, client).status_code, 404)

    def test_the_staff_app_works_through_operations(self):
        op = lambda name, args, token=None: self.post("/staff/op", {"name": name, "args": args}, token or self.staff)
        made = op("ask_bill", {"project": self.project.id, "agency": "a%s" % self.ag_carp.id, "trade": "carp", "what": "Wardrobes", "billedTo": "revert"})
        self.assertEqual(made.status_code, 200, made.text)
        bill = made.json()["id"]
        self.assertEqual(op("upload_bill", {"bill": bill, "no": "MF/30", "amount": 30000, "file": PNG}).status_code, 200)
        self.assertEqual(op("bill_to", {"bill": bill, "to": "client"}).status_code, 200)
        self.assertEqual(op("review_bill", {"bill": bill, "ok": True}).status_code, 200)
        self.assertRefused(op("pay_bill", {"bill": bill, "amount": 10000, "by": "client", "mode": "UPI"}), 403)
        self.assertEqual(op("pay_bill", {"bill": bill, "amount": 10000, "by": "client", "mode": "UPI"}, self.boss).status_code, 200)
        record = self.env["rvt.bill"].browse(int(bill[1:]))
        self.assertEqual((record.state, record.billed_to, record.sudo().payment_ids.mode), ("part_paid", "client", "upi"))
        listed = self.get("/agency/bills", self.agency).json()
        self.assertEqual([(b["id"], b["st"]) for b in listed if b["id"] == bill], [(bill, "part_paid")])
