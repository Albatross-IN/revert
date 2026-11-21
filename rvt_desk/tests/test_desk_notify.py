from odoo.exceptions import AccessError
from odoo.tests import tagged

from odoo.addons.rvt_mom.tests.common import MomCommon


@tagged("post_install", "-at_install")
class TestDeskNotify(MomCommon):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Desk = cls.env["rvt.desk"]

    def op(self, name, args, user=None):
        return self.Desk.with_user(user or self.coordinator).op(name, args)

    def snap(self, user=None):
        return self.Desk.with_user(user or self.coordinator).snapshot()

    def test_setup_shows_the_truth(self):
        snap = self.snap()
        self.assertTrue(snap["features"]["wa"])
        self.assertTrue(snap["set"]["testcopy"])
        self.assertFalse(snap["set"]["sending"])
        self.assertEqual(snap["set"]["number"], "", "no number is paired on the development copy")
        templates = snap["masters"]["templates"]
        self.assertEqual(set(templates["drawing_released"]), {"en", "gu", "hi"})
        self.assertIn("{code}", templates["otp"]["en"])
        # an owner flips the switch; on a test copy it still does not send
        with self.assertRaises(AccessError):
            self.op("setting", {"key": "sending", "value": True})
        self.op("setting", {"key": "sending", "value": True}, self.owner)
        self.assertTrue(self.env["ir.config_parameter"].sudo().get_bool("rvt.notify_sending_on"))
        self.assertFalse(self.snap()["set"]["sending"])

    def test_remind_and_the_log(self):
        result = self.op("remind", {"to": "a%s" % self.ag_carp.id, "project": self.project.id, "text": "Point 9: loft depth"})
        self.assertEqual(result, {"sent": 0})
        self.op("remind", {"to": "client", "project": self.project.id, "text": "Please have a look at the layout."})
        log = self.snap()["wa"]
        client, agency = log[0], log[1]
        self.assertEqual((agency["name"], agency["ph"], agency["ev"], agency["st"], agency["held"]),
                         ("Bherubhai Suthar", "+919824418830", "remind", "held", True))
        self.assertIn("Test copy", agency["why"])
        self.assertEqual(agency["on"], 0)
        self.assertEqual((client["name"], client["text"]), ("Nirav Shah", "Reminder · Shah Residence: Please have a look at the layout."))
        self.assertFalse([m for m in self.snap(self.outsider)["wa"] if m["id"] in (client["id"], agency["id"])],
                         "the log follows the project")

    def test_invite(self):
        contact = self.client_contact
        result = self.op("invite", {"project": self.project.id, "contact": contact.id})
        self.assertEqual(result, {"invited": 1})
        row = next(p for p in self.snap()["projects"] if p["id"] == self.project.id)
        self.assertTrue(row["client"]["contacts"][0]["inv"])
        self.assertEqual(self.snap()["wa"][0]["ev"], "invite")
        # "invited" does not hide a message that never left: a test copy holds it, and the screen says so
        self.assertEqual(row["client"]["contacts"][0]["invst"], "held")
        self.assertIn("Test copy", row["client"]["contacts"][0]["invwhy"])
        # onboarding step 6
        project = next(p for p in self.snap()["projects"] if p["id"] == self.project.id)
        s = lambda user: "s%s" % user.id
        out = self.op("onboard", {
            "pid": self.project.id, "name": "Shah Residence", "client": "Mr. Nirav Shah", "cphone": "",
            "kind": "home", "label": "3 BHK + garden", "billedTo": "client",
            "principal": s(self.principal), "designers": [s(self.designer)], "coords": [s(self.coordinator)],
            "ents": [{"u": i + 1, "n": e["n"], "ty": e["ty"], "id": e["id"]} for i, e in enumerate(project["ents"])],
            "tr": {x["t"]: {"on": True, "ag": x["ag"] or "", "by": 7} for x in project["plan"]},
            "ticks": [[str(next(i + 1 for i, e in enumerate(project["ents"]) if e["id"] == l["e"])), l["t"]] for l in project["lines"]],
            "inv": ["a%s" % self.ag_elec.id, "client"],
        })
        self.assertEqual(out["inv"], 2)
