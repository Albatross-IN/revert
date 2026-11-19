from odoo.exceptions import AccessError, UserError
from odoo.tests import HttpCase, tagged

from odoo.addons.rvt_mom.tests.common import PNG, MomCommon


@tagged("post_install", "-at_install")
class TestDeskMom(MomCommon):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Desk = cls.env["rvt.desk"]

    def op(self, name, args, user=None):
        return self.Desk.with_user(user or self.coordinator).op(name, args)

    def snap(self, user=None):
        return self.Desk.with_user(user or self.coordinator).snapshot()

    def test_a_site_visit_through_the_desk(self):
        self.assertTrue(self.snap()["features"]["mom"])
        vid = self.op("start_visit", {"project": self.project.id})["id"]
        self.assertEqual(self.op("start_visit", {"project": self.project.id})["id"], vid, "the open visit, not a second one")
        carp, elec = "a%s" % self.ag_carp.id, "a%s" % self.ag_elec.id
        kitchen = "e%s" % self.kitchen.id
        p1 = self.op("add_point", {"pid": self.project.id, "vid": vid, "kind": "agency", "party": carp, "text": "Wardrobe loft depth 24 in.",
                                   "e": kitchen, "due": 2, "photo": PNG})["id"]
        p2 = self.op("add_point", {"pid": self.project.id, "vid": vid, "kind": "agency", "party": elec, "text": "Add 2 points near the study", "e": "", "due": 1, "photo": ""})["id"]
        p3 = self.op("add_point", {"pid": self.project.id, "vid": vid, "kind": "client", "party": "client", "text": "Confirm the wall colour", "e": "", "due": 4})["id"]
        p4 = self.op("add_point", {"pid": self.project.id, "vid": vid, "kind": "staff", "party": "s%s" % self.designer.id, "text": "Send the revised elevation", "due": 1})["id"]
        p5 = self.op("add_point", {"pid": self.project.id, "vid": vid, "kind": "vendor", "party": "Asian Tiles (vendor)", "text": "Send tile samples", "due": None})["id"]
        snap = self.snap()
        visit = next(v for v in snap["visits"] if v["id"] == vid)
        self.assertEqual((visit["pid"], visit["no"], visit["date"], visit["st"], visit["att"]), (self.project.id, 1, 0, "open", ["Meera"]))
        self.assertEqual(next(p for p in snap["projects"] if p["id"] == self.project.id)["visitNo"], 1)
        rows = {p["id"]: p for p in snap["points"]}
        first = rows[p1]
        self.assertEqual((first["n"], first["kind"], first["party"], first["e"], first["t"], first["due"], first["st"]),
                         (1, "agency", carp, kitchen, "carp", 2, "open"))
        self.assertTrue(first["photo"] and first["fresh"] and first["confirmed"])
        self.assertEqual(first["by"], "s%s" % self.coordinator.id)
        self.assertEqual((rows[p3]["party"], rows[p3]["confirmed"]), ("client", False))
        self.assertEqual(rows[p4]["party"], "s%s" % self.designer.id)
        self.assertEqual((rows[p5]["party"], rows[p5]["due"]), ("Asian Tiles (vendor)", None))
        # send, close, confirm, finish
        self.assertEqual(self.op("send_party", {"visit": vid, "key": carp}), {"points": 1, "new": 1, "sent": 0})
        self.assertEqual(self.op("send_party", {"visit": vid, "key": "client"}), {"points": 0, "new": 0, "sent": 0})
        self.op("close_point", {"point": p2, "note": "Marked on site", "photo": PNG})
        self.op("confirm_point", {"point": p3})
        self.op("finish_visit", {"visit": vid})
        snap = self.snap()
        rows = {p["id"]: p for p in snap["points"]}
        self.assertEqual((rows[p2]["st"], rows[p2]["note"], rows[p2]["closedOn"], rows[p2]["cphoto"]), ("closed", "Marked on site", 0, True))
        self.assertTrue(rows[p3]["confirmed"])
        self.assertEqual(next(v for v in snap["visits"] if v["id"] == vid)["st"], "finished")
        self.assertEqual((rows[p1]["on"], rows[p1]["doneBy"]), (0, None), "when it was raised, for the photo taken before")
        # not right after all: the point is opened again
        self.op("reopen_point", {"point": p2})
        again = next(p for p in self.snap()["points"] if p["id"] == p2)
        self.assertEqual((again["st"], again["note"], again["cphoto"]), ("open", "", False))
        self.op("close_point", {"point": p2, "note": "Marked on site", "photo": PNG})
        # a date chosen by hand arrives as days from today, like the quick choices
        far = self.op("add_point", {"pid": self.project.id, "kind": "vendor", "party": "A vendor", "text": "Far date", "due": 45})["id"]
        self.assertEqual(next(p for p in self.snap()["points"] if p["id"] == far)["due"], 45)
        self.env["rvt.point"].browse(int(far[2:])).unlink()
        # a line waits for the client's item
        line = self.line(self.project, "Kitchen", "carp")
        self.op("set_line", {"line": "l%s" % line.id, "state": "wait", "cause": "client", "ref": p3, "note": ""})
        self.assertEqual(line.rvt_wait_point_id.id, int(p3[2:]))
        project = next(p for p in self.snap()["projects"] if p["id"] == self.project.id)
        self.assertEqual(next(l for l in project["lines"] if l["id"] == "l%s" % line.id)["ref"], p3)
        self.assertEqual(project["pic"]["progress"]["pt"], [1, 5, 4, 0])
        with self.assertRaises(AccessError):
            self.op("add_point", {"pid": self.project.id, "kind": "staff", "party": "s%s" % self.designer.id, "text": "x"}, self.outsider)
        with self.assertRaises(UserError):
            self.op("close_point", {"point": "pt0"})

    def test_client_point_without_confirmation_is_told_at_once(self):
        self.env["ir.config_parameter"].sudo().set_bool("rvt.client_points_need_confirmation", False)
        sent = []
        self.patch(type(self.env["rvt.notify"]), "send", lambda self_, event, record, people, **kw: sent.append(event) or 1)
        pid = self.op("add_point", {"pid": self.project.id, "kind": "client", "party": "client", "text": "Share the appliance list", "due": 3})["id"]
        self.assertEqual(sent, ["client_item"])
        row = next(p for p in self.snap()["points"] if p["id"] == pid)
        self.assertEqual((row["confirmed"], row["sent"], row["fresh"]), (True, 1, False))

    def test_earlier_mom_report_is_for_owners(self):
        with self.assertRaises(AccessError):
            self.op("etl_report", {})
        if "mom_partner_id" not in self.env["mail.activity"]._fields:
            self.skipTest("the earlier MOM is not installed")
        report = self.op("etl_report", {}, self.owner)
        self.assertIn("rows", report)
        self.assertEqual(report["source"], report["moved"] + report["left"])


@tagged("post_install", "-at_install")
class TestDeskMomFiles(MomCommon, HttpCase):

    def test_pdf_and_photo_routes(self):
        visit = self.start()
        point = self.add("Wardrobe loft depth 24 in.", partner=self.ag_carp, visit=visit, photo=PNG)
        self.authenticate("t_coord", "t_coord")
        photo = self.url_open("/rvt/desk/point/%s/photo" % point.id)
        self.assertEqual((photo.status_code, photo.headers["Content-Type"]), (200, "image/png"))
        self.assertEqual(self.url_open("/rvt/desk/point/%s/photo?size=thumb" % point.id).headers["Content-Type"], "image/jpeg")
        self.assertEqual(self.url_open("/rvt/desk/point/%s/photo?close=1" % point.id).status_code, 404, "no closing photo yet")
        document = self.url_open("/rvt/desk/mom/pdf?kind=mom&a=v%s&b=a%s" % (visit.id, self.ag_carp.id))
        self.assertEqual(document.status_code, 200)
        self.assertEqual(self.url_open("/rvt/desk/mom/pdf?kind=open&a=%s" % self.project.id).status_code, 200)
        self.add("Add 2 points near the study", partner=self.ag_elec, visit=visit)
        whole = self.url_open("/rvt/desk/mom/pdf?kind=mom&a=v%s&b=all" % visit.id).text
        self.assertIn("All parties", whole)
        self.assertIn("Add 2 points near the study", whole)
        self.assertNotIn("Add 2 points near the study", document.text, "one party's PDF holds only its points")
        # the points of the project, cut by agency or by visit
        by_agency = self.url_open("/rvt/desk/mom/pdf?kind=points&a=%s&b=a%s&st=all" % (self.project.id, self.ag_carp.id)).text
        self.assertIn("Wardrobe loft depth 24 in.", by_agency)
        self.assertNotIn("Add 2 points near the study", by_agency)
        by_visit = self.url_open("/rvt/desk/mom/pdf?kind=points&a=%s&b=all&v=v%s" % (self.project.id, visit.id)).text
        self.assertIn("Add 2 points near the study", by_visit)
        self.authenticate("t_outsider", "t_outsider")
        self.assertEqual(self.url_open("/rvt/desk/mom/pdf?kind=points&a=%s&b=all" % self.project.id).status_code, 404)
        self.assertEqual(self.url_open("/rvt/desk/point/%s/photo" % point.id).status_code, 404)
        self.assertEqual(self.url_open("/rvt/desk/mom/pdf?kind=mom&a=v%s&b=all" % visit.id).status_code, 404)
        self.assertEqual(self.url_open("/rvt/desk/mom/pdf?kind=open&a=%s" % self.project.id).status_code, 404)
