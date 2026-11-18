import base64

from odoo.tests import tagged

from odoo.addons.rvt_drawing.tests.common import PDF
from odoo.addons.rvt_mom.tests.common import PNG

from .common import ApiCase


@tagged("post_install", "-at_install")
class TestRoles(ApiCase):
    """Each role through HTTP: what it may do and what it is refused."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.wardrobe = cls.drawing("CD", "Wardrobe details", "carp", for_client=True, needs=True)
        cls.electrical = cls.drawing("EL", "Electrical layout", "elec")
        cls.other, _ = cls.onboard(name="Mehta Office", client_name="Mehta & Co.", client_phone="+91 98240 55190")

    def setUp(self):
        super().setUp()
        self.release(self.wardrobe, [self.ag_carp], client=True)
        self.release(self.electrical, [self.ag_elec])
        self.mine = self.add("Wardrobe loft depth 24 in.", partner=self.ag_carp, photo=PNG, entity_id=self.master.id)
        self.theirs = self.add("Add 2 points near the study table", partner=self.ag_elec, photo=PNG)
        self.item = self.add("Choose the kitchen platform stone", kind="client", due=3)
        self.held = self.add("Confirm the wall colour", kind="client")
        self.item.action_confirm()

    # ---- staff ----------------------------------------------------------
    def test_staff_snapshot_and_operations(self):
        token = self.token(self.coordinator)
        answer = self.get("/staff/snapshot", token)
        self.assertEqual(answer.status_code, 200)
        snap = answer.json()
        self.assertEqual(snap["me"], "s%s" % self.coordinator.id)
        self.assertEqual(snap["me_info"]["role"], "staff")
        self.assertIn(self.project.id, [p["id"] for p in snap["projects"]])
        self.assertTrue(snap["features"]["drawings"] and snap["features"]["mom"] and snap["features"]["wa"])
        same = self.get("/staff/snapshot", token, headers={"If-None-Match": answer.headers["ETag"]})
        self.assertEqual(same.status_code, 304, "nothing changed: nothing is sent again")
        line = self.line(self.project, "Kitchen", "civ")
        done = self.post("/staff/op", {"name": "set_line", "args": {"line": "l%s" % line.id, "state": "work"}}, token)
        self.assertEqual(done.status_code, 200, done.text)
        self.assertEqual(line.rvt_work_state, "working")
        changed = self.get("/staff/snapshot", token, headers={"If-None-Match": answer.headers["ETag"]})
        self.assertEqual(changed.status_code, 200)
        self.assertRefused(self.post("/staff/op", {"name": "no_such_thing", "args": {}}, token), 422, "VALIDATION")
        self.assertRefused(self.post("/staff/op", {"name": "setting", "args": {"key": "approval", "value": False}}, token), 403, "FORBIDDEN")
        self.assertRefused(self.post("/staff/op", {"name": "set_line", "args": {"line": "l%s" % line.id, "state": "wait"}}, token), 422)
        self.assertEqual(line.rvt_work_state, "working", "a refused operation leaves nothing behind")

    def test_staff_endpoints_one_by_one(self):
        token = self.token(self.coordinator)
        pid = self.project.id
        self.assertEqual(len(self.get("/masters", token).json()["trades"]), 15)
        self.assertTrue(self.get("/me/today", token).json())
        rows = self.get("/projects", token).json()
        self.assertIn(pid, [r["project_id"] for r in rows])
        picture = self.get("/projects/%s/picture" % pid, token).json()
        self.assertEqual(picture["project_id"], pid)
        self.assertIn("blockers", picture)
        grid = self.get("/projects/%s/grid" % pid, token).json()
        self.assertEqual(len(grid["entities"]), 13)
        self.assertEqual(len(self.get("/onboarding/proposal?preset_id=%s" % self.preset_3bhk.id, token).json()["entities"]), 13)
        self.assertTrue(self.get("/projects/%s/onboarding" % pid, token).json()["onboarded"])
        added = self.post("/onboarding", {"project_id": pid, "entities": [{"key": "s", "name": "Study", "entity_type_id": self.env.ref("rvt_base.entity_type_study").id}]}, token)
        self.assertEqual(added.json()["entities_created"], 1)
        line = self.line(self.project, "Kitchen", "carp")
        cell = self.post("/work-lines/%s/state" % line.id, {"state": "waiting", "cause": "material", "note": "Ply"}, token).json()
        self.assertEqual((cell["state"], cell["cause"]), ("waiting", "material"))
        self.assertRefused(self.post("/work-lines/%s/state" % line.id, {"state": "waiting"}, token), 422)
        drawings = self.get("/drawings?project_id=%s" % pid, token).json()
        self.assertEqual({d["code"] for d in drawings}, {"CD", "EL"})
        visit = self.post("/visits", {"project_id": pid}, token).json()["id"]
        made = self.post("/points", {"points": [
            {"project_id": pid, "visit_id": visit, "text": "Shift the TV unit", "for_kind": "agency", "partner_id": self.ag_carp.id, "client_uid": "u-1"},
            {"project_id": pid, "visit_id": visit, "text": "Raise the tap wall", "for_kind": "agency", "partner_id": self.ag_civil.id, "client_uid": "u-2"}]}, token).json()
        again = self.post("/points", {"points": [
            {"project_id": pid, "visit_id": visit, "text": "Shift the TV unit", "for_kind": "agency", "partner_id": self.ag_carp.id, "client_uid": "u-1"}]}, token).json()
        self.assertEqual(again[0]["id"], made[0]["id"], "the same batch sent twice creates the points once")
        self.assertEqual(self.env["rvt.point"].search_count([("client_uid", "in", ("u-1", "u-2"))]), 2)
        self.assertEqual(self.post("/visits/%s/send-party" % visit, {"partner_id": self.ag_carp.id}, token).json()["points"], 1)
        closed = self.post("/points/%s/close" % made[0]["id"], {"note": "Done"}, token).json()
        self.assertTrue(closed["ok"])
        self.assertEqual(self.post("/points/%s/confirm" % self.held.id, {}, token).status_code, 200)
        self.assertEqual(self.post("/visits/%s/finish" % visit, {}, token).status_code, 200)
        self.assertEqual(self.post("/projects/%s/remind" % pid, {"text": "Please open CD-01.", "agency_id": self.ag_carp.id}, token).json(), {"sent": 0})
        self.assertEqual(self.post("/projects/%s/invite" % pid, {"client_contact_ids": self.client_contact.ids}, token).json(), {"invited": 1})
        self.assertRefused(self.get("/projects/999999/picture", token), 404, "NOT_FOUND")

    def test_drawing_flow_by_role(self):
        designer, principal = self.token(self.designer), self.token(self.principal)
        drawing = self.drawing("KD", "Kitchen details", "carp")
        base = "/drawings/%s" % drawing.id
        self.assertEqual(self.post(base + "/start", {}, designer).status_code, 200)
        self.assertRefused(self.post(base + "/send-for-approval", {}, designer), 422)
        self.assertEqual(self.post(base + "/send-for-approval", {"file": PDF, "note": "First issue"}, designer).status_code, 200)
        self.assertRefused(self.post(base + "/approve", {}, designer), 403, "FORBIDDEN")
        self.assertEqual(self.post(base + "/approve", {}, principal).status_code, 200)
        receivers = self.get(base + "/receivers", designer).json()
        self.assertEqual(receivers[0]["name"], "Mahadev Furniture")
        self.assertRefused(self.post(base + "/release", {"agency_ids": []}, designer), 422)
        self.assertEqual(self.post(base + "/release", {"agency_ids": [self.ag_carp.id]}, designer).json(), {"freed": 0})
        question = self.post(base + "/questions", {"partner_id": self.ag_carp.id, "text": "Shutter in ply or MDF?", "person": "Bherubhai"}, designer).json()["id"]
        self.assertEqual(self.post("/questions/%s/answer" % question, {"text": "Ply"}, designer).status_code, 200)
        self.assertEqual(self.post(base + "/new-revision", {"note": ""}, designer).status_code, 200)
        outsider = self.token(self.outsider)
        self.assertRefused(self.post(base + "/start", {}, outsider), 403)
        self.assertRefused(self.get("/projects/%s/picture" % self.project.id, outsider), 403)

    def test_files_and_uploads(self):
        token = self.token(self.coordinator)
        pdf = self.get("/files/revision/%s" % self.wardrobe.released_revision_id.id, token)
        self.assertEqual((pdf.status_code, pdf.headers["Content-Type"]), (200, "application/pdf"))
        self.assertEqual(self.get("/files/point/%s/photo" % self.mine.id, token).headers["Content-Type"], "image/png")
        self.assertRefused(self.get("/files/point/%s/photo?close=1" % self.mine.id, token), 404)
        visit = self.start()
        self.add("One", partner=self.ag_carp, visit=visit)
        self.assertEqual(self.get("/files/visit/%s/pdf?partner_id=%s" % (visit.id, self.ag_carp.id), token).status_code, 200)
        self.assertEqual(self.get("/files/project/%s/open-points" % self.project.id, token).status_code, 200)
        # a photo sent ahead, then used to close a point; the same upload twice is one file
        self.env.flush_all()
        sent = self.url_open("/api/rvt/v1/media", data={"client_uid": "photo-77"}, files={"file": ("site.png", base64.b64decode(PNG), "image/png")},
                             headers={"Authorization": "Bearer %s" % token})
        self.assertEqual(sent.status_code, 200, sent.text)
        media = sent.json()["id"]
        twice = self.url_open("/api/rvt/v1/media", data={"client_uid": "photo-77"}, files={"file": ("site.png", base64.b64decode(PNG), "image/png")},
                              headers={"Authorization": "Bearer %s" % token})
        self.assertEqual(twice.json()["id"], media)
        done = self.post("/staff/op", {"name": "close_point", "args": {"point": "pt%s" % self.mine.id, "note": "Checked", "photo_media_id": media}}, token)
        self.assertEqual(done.status_code, 200, done.text)
        self.assertTrue(self.mine.has_close_photo)
        other = self.token(self.designer)
        self.assertRefused(self.post("/staff/op", {"name": "close_point", "args": {"point": "pt%s" % self.theirs.id, "photo_media_id": media}}, other), 422)

    # ---- agency ---------------------------------------------------------
    def test_agency_sees_and_does_only_its_own(self):
        session = self.otp(self.carp_phone)
        token = session["access_token"]
        home = self.get("/agency/home", token).json()
        self.assertEqual(home["agency"]["name"], "Mahadev Furniture")
        self.assertEqual([p["text"] for p in home["points"]], ["Wardrobe loft depth 24 in."])
        self.assertEqual(home["points"][0]["area"], "Master bedroom")
        self.assertEqual([d["sheet"] for d in home["drawings"]], ["CD-01"])
        self.assertEqual(len(home["new_drawings"]), 1)
        site = next(s for s in home["sites"] if s["id"] == self.project.id)
        self.assertEqual({l["t"] for l in site["lines"]}, {"carp"}, "only its own lines")
        self.assertNotIn(self.other.id, [s["id"] for s in home["sites"]] if self.ag_carp not in self.other.rvt_agency_ids else [])
        # opening is recorded, once
        self.assertEqual(self.post("/agency/drawings/%s/open" % self.wardrobe.id, {}, token).json()["first"], True)
        self.assertEqual(self.post("/agency/drawings/%s/open" % self.wardrobe.id, {}, token).json()["first"], False)
        self.assertFalse(self.get("/agency/home", token).json()["new_drawings"])
        rev = self.wardrobe.released_revision_id
        self.assertEqual(self.get("/files/revision/%s?open=1" % rev.id, token).status_code, 200)
        self.assertEqual(self.get("/files/point/%s/photo" % self.mine.id, token).status_code, 200)
        asked = self.post("/agency/drawings/%s/questions" % self.wardrobe.id, {"text": "Loft 18 or 24?", "photo": PNG}, token)
        self.assertEqual(asked.status_code, 200, asked.text)
        question = self.env["rvt.drawing.question"].browse(asked.json()["id"])
        self.assertEqual((question.partner_id, question.asked_by_name, question.via), (self.ag_carp, "Bherubhai Suthar", "app"))
        self.assertEqual(self.get("/files/question/%s/photo" % question.id, token).status_code, 200)
        # what belongs to another agency, to the client or to staff is refused
        self.assertRefused(self.post("/agency/drawings/%s/open" % self.electrical.id, {}, token), 403)
        self.assertRefused(self.get("/files/revision/%s" % self.electrical.released_revision_id.id, token), 403)
        self.assertRefused(self.get("/files/point/%s/photo" % self.theirs.id, token), 403)
        self.assertRefused(self.get("/files/point/%s/photo" % self.item.id, token), 403)
        for path in ("/staff/snapshot", "/masters", "/me/today", "/projects", "/projects/%s/picture" % self.project.id,
                     "/drawings", "/client/home", "/files/visit/1/pdf"):
            self.assertRefused(self.get(path, token), 403, "FORBIDDEN")
        self.assertRefused(self.post("/staff/op", {"name": "set_line", "args": {}}, token), 403)
        self.assertRefused(self.post("/points/%s/close" % self.mine.id, {"note": "done"}, token), 403)
        self.assertRefused(self.post("/client/drawings/%s/decide" % self.wardrobe.id, {"decision": "approved"}, token), 403)
        self.assertRefused(self.call("PUT", "/me/password", {"old": "x", "new": "yyyyyyyyy"}, token), 403)

    # ---- client ---------------------------------------------------------
    def test_client_sees_and_does_only_its_own(self):
        token = self.otp(self.client_phone)["access_token"]
        home = self.get("/client/home", token).json()
        self.assertEqual([p["name"] for p in home["projects"]], ["Shah Residence"])
        project = home["projects"][0]
        self.assertEqual([d["sheet"] for d in project["drawings"]], ["CD-01"], "only what is marked for the client and released to it")
        self.assertEqual(project["drawings"][0]["decision"], "pending")
        self.assertEqual({w["kind"] for w in project["waiting"]}, {"drawing", "point"})
        self.assertEqual([w["text"] for w in project["waiting"] if w["kind"] == "point"], ["Choose the kitchen platform stone"],
                         "the item the office has not confirmed is not shown")
        self.assertEqual(self.post("/client/drawings/%s/open" % self.wardrobe.id, {}, token).json()["first"], True)
        self.assertEqual(self.get("/files/revision/%s?open=1" % self.wardrobe.released_revision_id.id, token).status_code, 200)
        self.assertRefused(self.post("/client/drawings/%s/decide" % self.wardrobe.id, {"decision": "change", "note": ""}, token), 422)
        self.assertEqual(self.post("/client/drawings/%s/decide" % self.wardrobe.id, {"decision": "approved"}, token).status_code, 200)
        revision = self.wardrobe.released_revision_id
        self.assertEqual((revision.client_decision, revision.client_decided_by), ("approved", "Nirav Shah"))
        self.assertEqual(self.post("/client/points/%s/done" % self.item.id, {}, token).status_code, 200)
        self.assertEqual(self.item.state, "closed")
        self.assertFalse(self.get("/client/home", token).json()["projects"][0]["waiting"], "nothing is needed from the client now")
        # refused
        self.assertRefused(self.post("/client/points/%s/done" % self.held.id, {}, token), 403)
        self.assertRefused(self.post("/client/points/%s/done" % self.mine.id, {}, token), 403)
        self.assertRefused(self.post("/client/drawings/%s/open" % self.electrical.id, {}, token), 403)
        self.assertRefused(self.get("/files/revision/%s" % self.electrical.released_revision_id.id, token), 403)
        self.assertRefused(self.get("/files/point/%s/photo" % self.mine.id, token), 403)
        for path in ("/staff/snapshot", "/agency/home", "/projects", "/masters"):
            self.assertRefused(self.get(path, token), 403, "FORBIDDEN")

    def test_a_link_opens_one_project_only(self):
        # the same person is a client contact of a second project
        self.other.rvt_client_contact_ids = [(4, self.client_contact.id)]
        layout = self.env["rvt.drawing"].create({
            "project_id": self.other.id, "code": "FL", "name": "Furniture layout", "designer_id": self.designer.id,
            "for_client": True, "needs_client_approval": True})
        layout.with_user(self.designer).action_send_for_approval(PDF)
        layout.with_user(self.principal).action_approve()
        layout.with_user(self.designer).action_release([], client=True)
        staff = self.token(self.coordinator)
        url = self.get("/projects/%s/client-link?contact_id=%s" % (self.project.id, self.client_contact.id), staff).json()["url"]
        token = self.post("/auth/link", {"token": url.rsplit("/", 1)[1]}).json()["access_token"]
        home = self.get("/client/home", token).json()
        self.assertEqual([p["id"] for p in home["projects"]], [self.project.id])
        self.assertRefused(self.post("/client/drawings/%s/decide" % layout.id, {"decision": "approved"}, token), 403)
        full = self.otp(self.client_phone)["access_token"]
        self.assertEqual(len(self.get("/client/home", full).json()["projects"]), 2, "signed in with the number, both projects show")

    def test_staff_are_refused_the_other_apps(self):
        token = self.token(self.coordinator)
        self.assertRefused(self.get("/agency/home", token), 403, "FORBIDDEN")
        self.assertRefused(self.get("/client/home", token), 403, "FORBIDDEN")
