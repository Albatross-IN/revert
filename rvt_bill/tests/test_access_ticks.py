from odoo.exceptions import AccessError, UserError
from odoo.tests import new_test_user, tagged

from odoo.addons.rvt_api.tests.common import PASSWORD, ApiCase


@tagged("post_install", "-at_install")
class TestAccessTicks(ApiCase):
    """What a person may do is one tick each (Settings > Users > Revert access). A role brings its usual ticks,
    as the office set them out on 26 Nov 2026; the desk, the app and the server follow the ticks."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        user = lambda login, groups, name: new_test_user(cls.env, login, groups=groups, name=name, password=PASSWORD)
        # people of each role with nothing ticked by hand (the shared coordinator of the suites has more)
        cls.d = user("t_acc_designer", "rvt_base.group_rvt_designer", "Kamal Designer")
        cls.c = user("t_acc_coord", "rvt_base.group_rvt_coordinator", "Chetan Coordinator")
        cls.pc = user("t_acc_principal", "rvt_base.group_rvt_principal", "Pooja Principal")
        cls.o = user("t_acc_owner", "rvt_base.group_rvt_owner", "Om Owner")
        cls.Desk = cls.env["rvt.desk"]
        # the designer works on the project of the suites, the coordinator is on no team
        cls.project.sudo().rvt_designer_ids = [(4, cls.d.id)]

    def op(self, name, args, user):
        return self.Desk.with_user(user).op(name, args)

    def test_a_role_brings_its_usual_ticks(self):
        self.assertEqual(self.d.rvt_access(), {"grid", "drawings", "mom"})
        self.assertEqual(self.c.rvt_access(), {"grid", "drawings", "mom", "agencies"})
        self.assertEqual(self.pc.rvt_access(), {"allprojects", "projects", "grid", "drawings", "approve", "mom", "agencies",
                                                "bills", "money", "setup"})
        self.assertEqual(self.o.rvt_access(), self.pc.rvt_access() | {"whatsapp"})
        # a second role adds its own; taking it away takes only what it alone brought; a tick given by hand stays
        self.d.write({"group_ids": [(4, self.env.ref("rvt_base.group_rvt_acc_bills").id)]})
        self.d.rvt_set_roles(["designer", "coordinator"])
        self.assertEqual(self.d.rvt_access(), {"grid", "drawings", "mom", "agencies", "bills"})
        self.d.rvt_set_roles(["designer"])
        self.assertEqual(self.d.rvt_access(), {"grid", "drawings", "mom", "bills"})
        # the user form's checkboxes are the same ticks
        self.d.rvt_access_ids = self.d.rvt_access_ids - self.env.ref("rvt_base.group_rvt_acc_bills")
        self.assertEqual(self.d.rvt_access(), {"grid", "drawings", "mom"})
        self.assertEqual(self.d.rvt_set_roles(["designer"]), True, "the same role again changes nothing")
        self.assertEqual(self.d.rvt_access(), {"grid", "drawings", "mom"})

    def test_the_server_refuses_what_is_not_ticked(self):
        refused = [("onboard", {"name": "Not mine"}), ("add_agency", {"name": "Some Firm"}),
                   ("assign", {"project": self.project.id, "trade": "plmb", "agency": "a%s" % self.ag_civil.id}),
                   ("setting", {"key": "approval", "value": False}), ("access", {"user": "s%s" % self.d.id, "key": "bills", "on": True}),
                   ("ask_bill", {"project": self.project.id, "agency": "a%s" % self.ag_carp.id, "what": "x"}),
                   ("approve", {"drawing": "d0"})]
        for name, args in refused:
            with self.assertRaises(AccessError, msg="a designer may not %s" % name):
                self.op(name, args, self.d)
        # a coordinator chooses agencies, but asks no bill and sets no project up
        with self.assertRaises(AccessError):
            self.op("ask_bill", {"project": self.project.id, "agency": "a%s" % self.ag_carp.id, "what": "x"}, self.c)
        with self.assertRaises(AccessError):
            self.op("onboard", {"name": "Not mine"}, self.c)
        with self.assertRaises(UserError, msg="a coordinator gets past the access check (and is asked for a name)"):
            self.op("add_agency", {"name": ""}, self.c)
        # the app's own routes follow the same ticks
        token = self.token(self.d)
        self.assertEqual(self.post("/onboarding", {"name": "Not mine"}, token).status_code, 403)
        self.assertEqual(self.post("/staff/op", {"name": "onboard", "args": {"name": "Not mine"}}, token).status_code, 403)
        self.assertEqual(self.get("/bills", token).status_code, 403)

    def test_each_person_sees_only_their_projects_and_their_functions(self):
        snap = self.Desk.with_user(self.d).snapshot()
        self.assertEqual([p["id"] for p in snap["projects"]], [self.project.id], "only the project whose team the designer is on")
        self.assertEqual(snap["acc"], ["drawings", "grid", "mom"])
        self.assertEqual(snap["bills"], [], "no bills without a bills tick")
        me = next(s for s in snap["staff"] if s["id"] == "s%s" % self.d.id)
        self.assertEqual(me["acc"], ["drawings", "grid", "mom"])
        self.assertFalse(self.Desk.with_user(self.c).snapshot()["projects"], "a coordinator on no team sees no project")
        everything = self.Desk.with_user(self.pc).snapshot()["projects"]
        self.assertGreater(len(everything), 1, "a principal sees every project")
        # Today: the coordinator of the project has a trade to decide; without the agencies tick it is not theirs
        decide = lambda user: [i for i in self.Desk.with_user(user).snapshot()["today"] if i["sec"] == "decide"]
        self.project.sudo().rvt_coordinator_ids = [(4, self.c.id)]
        self.assertTrue(decide(self.c))
        self.c.write({"group_ids": [(3, self.env.ref("rvt_base.group_rvt_acc_agencies").id)]})
        self.assertFalse(decide(self.c))

    def test_an_owner_ticks_access_from_setup(self):
        result = self.op("access", {"user": "s%s" % self.d.id, "key": "bills", "on": True}, self.o)
        self.assertIn("bills", result["acc"])
        self.assertTrue(self.op("ask_bill", {"project": self.project.id, "agency": "a%s" % self.ag_carp.id, "what": "Carpentry, stage 1"}, self.d)["id"])
        self.op("access", {"user": "s%s" % self.d.id, "key": "bills", "on": False}, self.pc)
        self.assertNotIn("bills", self.d.rvt_access(), "a principal has Setup too")
        with self.assertRaises(UserError):
            self.op("access", {"user": "s%s" % self.o.id, "key": "setup", "on": False}, self.o)
        with self.assertRaises(AccessError, msg="only an owner gives the owner role"):
            self.op("role", {"user": "s%s" % self.d.id, "role": "owner"}, self.pc)

    def test_amounts_and_approval_follow_their_ticks(self):
        bill = self.env["rvt.bill"].with_user(self.coordinator).rvt_ask(self.project.id, self.ag_carp.id, "Carpentry, stage 1", up_to=50000)
        self.assertEqual(bill.with_user(self.pc).up_to_amount, 50000, "a principal is ticked for amounts")
        self.pc.write({"group_ids": [(3, self.env.ref("rvt_base.group_rvt_acc_money").id)]})
        with self.assertRaises(AccessError):
            bill.with_user(self.pc).read(["up_to_amount"])
        self.assertTrue(self.env["rvt.drawing"].with_user(self.pc)._rvt_may_approve())
        self.assertFalse(self.env["rvt.drawing"].with_user(self.c)._rvt_may_approve())
