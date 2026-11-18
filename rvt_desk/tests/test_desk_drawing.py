from odoo.exceptions import AccessError, UserError
from odoo.tests import HttpCase, tagged

from odoo.addons.rvt_drawing.tests.common import PDF, DrawingCommon


@tagged("post_install", "-at_install")
class TestDeskDrawing(DrawingCommon):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Desk = cls.env["rvt.desk"]

    def op(self, name, args, user=None):
        return self.Desk.with_user(user or self.designer).op(name, args)

    def row(self, drawing, user=None):
        snap = self.Desk.with_user(user or self.designer).snapshot()
        return next(d for d in snap["drawings"] if d["id"] == "d%s" % drawing.id)

    def test_feature_is_on(self):
        snap = self.Desk.with_user(self.designer).snapshot()
        self.assertTrue(snap["features"]["drawings"])

    def test_the_whole_flow_through_the_desk(self):
        drawing = self.drawing("CD", "Wardrobe details", "carp", for_client=True, needs=True, due=1)
        ref = "d%s" % drawing.id
        row = self.row(drawing)
        self.assertEqual((row["code"], row["no"], row["title"], row["t"], row["st"], row["due"]),
                         ("CD", 1, "Wardrobe details", "carp", "to_draw", 1))
        self.assertEqual(row["ds"], "s%s" % self.designer.id)
        self.assertEqual(row["revs"], [dict(row["revs"][0], n=1, st="draft", file=False, rc=[], client=None)])
        self.op("dstart", {"drawing": ref})
        self.assertEqual(self.row(drawing)["st"], "in_progress")
        with self.assertRaises(UserError):
            self.op("send_for_approval", {"drawing": ref, "note": "", "file": "", "name": ""})
        self.op("send_for_approval", {"drawing": ref, "note": "With loft", "file": PDF, "name": "wardrobe.pdf"})
        row = self.row(drawing)
        self.assertEqual((row["st"], row["revs"][0]["st"], row["revs"][0]["file"], row["revs"][0]["fname"]),
                         ("awaiting", "awaiting", True, "wardrobe.pdf"))
        self.assertEqual((row["revs"][0]["sentBy"], row["revs"][0]["sentOn"], row["revs"][0]["note"]),
                         ("s%s" % self.designer.id, 0, "With loft"))
        with self.assertRaises(AccessError):
            self.op("approve", {"drawing": ref})
        self.op("send_back", {"drawing": ref, "note": "Loft depth"}, self.principal)
        row = self.row(drawing)
        self.assertEqual((row["st"], row["revs"][0]["st"], row["revs"][0]["back"]), ("in_progress", "draft", "Loft depth"))
        self.op("send_for_approval", {"drawing": ref, "note": "", "file": "", "name": ""})   # the PDF on file goes again
        self.op("approve", {"drawing": ref}, self.principal)
        self.assertEqual(self.row(drawing)["st"], "approved")
        # a line waits for it; releasing frees the line
        line = self.line(self.project, "Master bedroom", "carp")
        self.op("set_line", {"line": "l%s" % line.id, "state": "wait", "cause": "drawing", "ref": ref, "note": ""})
        self.assertEqual(line.rvt_wait_drawing_id, drawing)
        snap = self.Desk.with_user(self.designer).snapshot()
        project = next(p for p in snap["projects"] if p["id"] == self.project.id)
        self.assertEqual(next(l for l in project["lines"] if l["id"] == "l%s" % line.id)["ref"], ref)
        self.assertIn("B2", [b["k"] for b in project["pic"]["blockers"]])
        release = next(n for n in project["pic"]["next"]["revert"] if n["sec"] == "release")
        self.assertEqual(release["act"], ["release", ref, "Release"])
        result = self.op("release", {"drawing": ref, "to": ["a%s" % self.ag_carp.id, "client"]})
        self.assertEqual(result, {"freed": 1})
        row = self.row(drawing)
        self.assertEqual((row["st"], row["revs"][0]["relOn"]), ("released", 0))
        self.assertEqual(row["revs"][0]["rc"], [
            {"to": "a%s" % self.ag_carp.id, "sent": 0, "opened": None, "at": ""},
            {"to": "client", "sent": 0, "opened": None, "at": ""}])
        self.assertEqual(row["revs"][0]["client"]["dec"], "pending")
        drawing.rvt_open(self.ag_carp)
        drawing.rvt_client_decide("approved", partner=self.client_contact)
        row = self.row(drawing)
        self.assertEqual(row["revs"][0]["rc"][0]["opened"], 0)
        self.assertTrue(row["revs"][0]["rc"][0]["at"])
        self.assertEqual((row["revs"][0]["client"]["dec"], row["revs"][0]["client"]["by"]), ("approved", "Nirav Shah"))
        # questions: logged from a call, answered
        result = self.op("ask", {"drawing": ref, "by": "a%s" % self.ag_carp.id, "name": "Bherubhai Suthar", "text": "Loft 18 or 24?"})
        question = self.row(drawing)["q"][0]
        self.assertEqual((question["id"], question["by"], question["byName"], question["via"], question["ans"]),
                         (result["id"], "a%s" % self.ag_carp.id, "Bherubhai Suthar", "office", None))
        self.op("ask", {"drawing": ref, "by": "client", "name": "", "text": "Can it be white?"})
        self.assertEqual(self.row(drawing)["q"][1]["by"], "client")
        self.op("answer", {"question": result["id"], "text": "24 in."})
        self.assertEqual(self.row(drawing)["q"][0]["ans"], "24 in.")
        # the next revision
        self.op("new_revision", {"drawing": ref})
        row = self.row(drawing)
        self.assertEqual((row["st"], [r["st"] for r in row["revs"]]), ("in_progress", ["released", "draft"]))
        with self.assertRaises(AccessError):
            self.op("dstart", {"drawing": ref}, self.outsider)
        with self.assertRaises(UserError):
            self.op("dstart", {"drawing": "d0"})

    def test_onboarding_step_five(self):
        Desk = self.Desk.with_user(self.coordinator)
        snap = Desk.snapshot()
        project = next(p for p in snap["projects"] if p["id"] == self.project.id)
        s = lambda user: "s%s" % user.id
        result = Desk.op("onboard", {
            "pid": self.project.id, "name": "Shah Residence", "client": "Mr. Nirav Shah", "cphone": "",
            "kind": "home", "label": "3 BHK + garden", "billedTo": "client",
            "principal": s(self.principal), "designers": [s(self.designer)], "coords": [s(self.coordinator)],
            "ents": [{"u": i + 1, "n": e["n"], "ty": e["ty"], "id": e["id"]} for i, e in enumerate(project["ents"])],
            "tr": {x["t"]: {"on": True, "ag": x["ag"] or "", "by": 7} for x in project["plan"]},
            "ticks": [[str(next(i + 1 for i, e in enumerate(project["ents"]) if e["id"] == l["e"])), l["t"]] for l in project["lines"]],
            "dr": [{"code": "FL", "n": "Furniture layout", "t": "", "ds": s(self.designer), "due": 7, "client": True, "appr": True},
                   {"code": "EL", "n": "Electrical layout", "t": "elec", "ds": s(self.designer2), "due": 9, "client": True, "appr": False},
                   {"code": "AD", "n": "Bar counter details", "t": "", "ds": "", "due": 14, "client": False, "appr": True}],
        })
        self.assertEqual((result["nl"], result["nd"]), (0, 3))
        drawings = {d.code: d for d in self.project.rvt_drawing_ids}
        self.assertEqual(drawings["FL"].due_date, self.days(7))
        self.assertTrue(drawings["FL"].needs_client_approval)
        self.assertEqual(drawings["EL"].trade_id.code, "elec")
        self.assertEqual(drawings["EL"].designer_id, self.designer2)
        self.assertFalse(drawings["AD"].needs_client_approval)
        self.assertTrue(drawings["AD"].designer_id)
        today = Desk.snapshot()["today"]
        self.assertFalse([i for i in today if i["sec"] == "draw"], "nothing to draw for the coordinator")
        mine = [i for i in self.Desk.with_user(self.designer2).snapshot()["today"] if i["sec"] == "draw"]
        self.assertEqual([i["text"] for i in mine], ["Draw and send EL-01 Electrical layout"])


@tagged("post_install", "-at_install")
class TestDeskDrawingPdf(DrawingCommon, HttpCase):

    def test_pdf_for_staff_on_the_team_only(self):
        drawing = self.drawing("EL", "Electrical layout", "elec")
        self.send(drawing)
        revision = drawing.current_revision_id
        self.authenticate("t_designer", "t_designer")
        response = self.url_open("/rvt/desk/revision/%s/pdf" % revision.id)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.content.startswith(b"%PDF"))
        self.assertEqual(self.url_open("/rvt/desk/revision/999999/pdf").status_code, 404)
        self.authenticate("t_outsider", "t_outsider")
        self.assertEqual(self.url_open("/rvt/desk/revision/%s/pdf" % revision.id).status_code, 404)
        self.authenticate("t_agency", "t_agency")
        self.assertEqual(self.url_open("/rvt/desk/revision/%s/pdf" % revision.id).status_code, 404)
