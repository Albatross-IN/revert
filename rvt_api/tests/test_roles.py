import base64
from urllib.parse import unquote

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
        live = snap["set"]["live"]
        self.assertEqual((live["ch"], bool(live["v"])), (self.env["rvt.live"].channel(), True), "what an open screen listens to")
        self.assertIsInstance(snap["notes"], list)
        same = self.get("/staff/snapshot", token, headers={"If-None-Match": answer.headers["ETag"]})
        self.assertEqual(same.status_code, 304, "nothing changed: nothing is sent again")
        weak = self.get("/staff/snapshot", token, headers={"If-None-Match": "W/" + answer.headers["ETag"]})
        self.assertEqual(weak.status_code, 304, "a proxy that compresses marks the tag as weak")
        self.assertEqual(answer.headers.get("Content-Encoding"), "gzip", "the largest answer travels compressed")
        plain = self.get("/staff/snapshot", token, headers={"Accept-Encoding": "identity"})
        self.assertNotIn("Content-Encoding", plain.headers)
        self.assertEqual(plain.json()["me"], snap["me"])
        self.assertEqual(plain.headers["ETag"], answer.headers["ETag"], "one tag for both forms")
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
        # choosing an agency links its contact person: the link is checked against the caller,
        # not against the anonymous user the request began as
        plan = self.project.rvt_trade_plan_ids.filtered(lambda p: p.trade_id.code == "carp")
        chosen = self.post("/staff/op", {"name": "assign", "args": {"project": self.project.id, "trade": "carp", "agency": "a%s" % self.ag_carp2.id}}, token)
        self.assertEqual(chosen.status_code, 200, chosen.text)
        plan.invalidate_recordset()
        self.assertEqual(plan.agency_id, self.ag_carp2)
        self.assertEqual(plan.contact_ids.mapped("name"), ["Mukesh Mistry"])

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
        small = self.get("/files/point/%s/photo?size=thumb" % self.mine.id, token)
        self.assertEqual((small.status_code, small.headers["Content-Type"]), (200, "image/jpeg"), "a list gets a small copy")
        self.assertEqual(self.get("/files/point/%s/photo?size=view" % self.mine.id, token).headers["Content-Type"], "image/jpeg")
        self.assertRefused(self.get("/files/point/%s/photo?close=1" % self.mine.id, token), 404)
        visit = self.start()
        self.add("One", partner=self.ag_carp, visit=visit)
        self.assertEqual(self.get("/files/visit/%s/pdf?partner_id=%s" % (visit.id, self.ag_carp.id), token).status_code, 200)
        self.assertEqual(self.get("/files/project/%s/open-points" % self.project.id, token).status_code, 200)
        by_agency = self.get("/files/project/%s/points-pdf?party=a%s&state=all" % (self.project.id, self.ag_carp.id), token)
        self.assertEqual((by_agency.status_code, by_agency.headers["Content-Type"]), (200, "application/pdf"))
        self.assertIn("Points - Shah Residence - Mahadev Furniture.pdf", unquote(by_agency.headers["Content-Disposition"]))
        by_visit = self.get("/files/project/%s/points-pdf?visit_id=%s" % (self.project.id, visit.id), token)
        self.assertIn("MOM - Shah Residence - visit %s.pdf" % visit.number, unquote(by_visit.headers["Content-Disposition"]))
        self.assertRefused(self.get("/files/project/%s/points-pdf" % self.project.id, self.otp(self.carp_phone)["access_token"]), 403)
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
        # its own point, marked done with a photo of the finished work
        self.assertRefused(self.post("/agency/points/%s/done" % self.mine.id, {"note": "done"}, token), 422)
        done = self.post("/agency/points/%s/done" % self.mine.id, {"note": "Loft fixed", "photo": PNG}, token)
        self.assertEqual((done.status_code, done.json()), (200, {"ok": True}), done.text)
        self.assertEqual((self.mine.state, self.mine.review_state, self.mine.close_note, self.mine.closed_by_partner_id.name),
                         ("open", "to_check", "Loft fixed", "Bherubhai Suthar"), "done by the agency waits for the office to look")
        self.assertEqual(self.get("/files/point/%s/photo?close=1" % self.mine.id, token).status_code, 200)
        row = next(p for p in self.get("/agency/snapshot", token).json()["points"] if p["id"] == "pt%s" % self.mine.id)
        self.assertEqual((row["st"], row["rev"], row["cphoto"], row["doneBy"], row["doneOn"]), ("open", "check", True, "Bherubhai Suthar", 0))
        self.assertRefused(self.post("/agency/points/%s/done" % self.theirs.id, {"photo": PNG}, token), 403)
        self.assertEqual(self.post("/me/notifications/seen", {}, token).json(), {"ok": True})
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

    def test_screen_slices_carry_nothing_of_others(self):
        self.wardrobe.rvt_ask(self.ag_carp, "Loft 18 or 24?", person_name="Bherubhai Suthar")
        self.wardrobe.rvt_ask(self.client_partner, "Can it be white?", via="office", person_name="Nirav Shah")
        self.wardrobe.released_revision_id.note = "Internal: check the beam before release"
        token = self.otp(self.carp_phone)["access_token"]
        snap = self.get("/agency/snapshot", token).json()
        key = "a%s" % self.ag_carp.id
        self.assertEqual((snap["role"], snap["me"]), ("agency", key))
        self.assertEqual(snap["agencies"][0]["people"][0]["n"], "Bherubhai Suthar", "the person signed in comes first")
        self.assertEqual([d["title"] for d in snap["drawings"]], ["Wardrobe details"])
        drawing = snap["drawings"][0]
        self.assertEqual((drawing["st"], len(drawing["revs"])), ("released", 1))
        self.assertEqual([r["to"] for r in drawing["revs"][0]["rc"]], [key], "not the client's receipt")
        self.assertEqual(drawing["revs"][0]["note"], "", "the office's notes stay in the office")
        self.assertEqual([q["text"] for q in drawing["q"]], ["Loft 18 or 24?"], "not the client's question")
        self.assertEqual({p["party"] for p in snap["points"]}, {key})
        project = next(p for p in snap["projects"] if p["id"] == self.project.id)
        self.assertEqual({l["t"] for l in project["lines"]}, {"carp"})
        self.assertEqual({l["ag"] for l in project["lines"]}, {key})
        self.assertEqual(project["client"], {"id": False, "n": "", "contacts": []}, "the client is not the agency's business")
        self.assertNotIn("pic", project)
        token = self.otp(self.client_phone)["access_token"]
        snap = self.get("/client/snapshot", token).json()
        self.assertEqual((snap["role"], snap["clientPid"]), ("client", self.project.id))
        self.assertEqual([d["title"] for d in snap["drawings"]], ["Wardrobe details"])
        drawing = snap["drawings"][0]
        self.assertEqual([r["to"] for r in drawing["revs"][0]["rc"]], ["client"])
        self.assertEqual(drawing["revs"][0]["client"]["dec"], "pending")
        self.assertEqual([q["text"] for q in drawing["q"]], ["Can it be white?"])
        self.assertEqual([p["text"] for p in snap["points"]], ["Choose the kitchen platform stone"])
        self.assertEqual(snap["projects"][0]["client"]["contacts"][0]["n"], "Nirav Shah")
        self.assertEqual(snap["projects"][0]["lines"], [], "a client sees no work lines")

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

    def test_the_link_serves_the_screens_and_the_drawing(self):
        """The link opens the app's screens in a browser. The page holds no data; the drawing
        opens from the client's own receipt link, which records the opening."""
        staff = self.token(self.coordinator)
        made = self.post("/staff/op", {"name": "client_link", "args": {"project": self.project.id}}, staff)
        self.assertEqual(made.status_code, 200, made.text)
        self.assertEqual(made.json()["name"], self.client_contact.name)
        path = "/rvt/c/" + made.json()["url"].rsplit("/", 1)[1]
        page = self.url_open(path)
        self.assertEqual(page.status_code, 200)
        self.assertIn("window.RVT_LINK=", page.text)
        self.assertIn("/rvt_api/static/app/app.js", page.text)
        self.assertNotIn(self.project.name, page.text, "the page itself carries nothing of the project")
        self.assertEqual(page.headers.get("Cache-Control"), "no-store")
        self.assertEqual(page.headers.get("Referrer-Policy"), "no-referrer")
        self.assertEqual(self.url_open("/rvt/c/not-a-link").status_code, 404)
        self.assertEqual(self.url_open("/rvt_api/static/app/app.js").status_code, 200, "the screens are in the module")
        token = self.post("/auth/link", {"token": path.rsplit("/", 1)[1], "device": {"uid": "browser-1", "platform": "web"}}).json()["access_token"]
        row = next(d for d in self.get("/client/snapshot", token).json()["drawings"] if d["id"] == "d%s" % self.wardrobe.id)
        self.assertTrue(row["url"].startswith("/rvt/d/"), row.get("url"))
        receipt = self.wardrobe.released_revision_id.receipt_ids.filtered(lambda r: r.token == row["url"].rsplit("/", 1)[1])
        self.assertIn(receipt.partner_id, self.project.rvt_client_id | self.project.rvt_client_contact_ids, "the client's own receipt")
        receipt.opened_on = False        # the drawing was opened in the app before; here it is the link that counts
        sheet = self.url_open(row["url"])
        self.assertEqual(sheet.headers["Content-Type"], "application/pdf")
        receipt.invalidate_recordset()
        self.assertTrue(receipt.opened_on, "opening the sheet from the page is recorded")
        # an agency's drawing carries the firm's own link, never another receiver's
        agency = self.otp(self.carp_phone)["access_token"]
        mine = next(d for d in self.get("/agency/snapshot", agency).json()["drawings"] if d["id"] == "d%s" % self.wardrobe.id)
        firm = self.wardrobe.released_revision_id.receipt_ids.filtered(lambda r: r.partner_id.commercial_partner_id == self.ag_carp)
        self.assertEqual(mine["url"], "/rvt/d/%s" % firm[:1].token)

    def test_a_token_after_a_restart_keeps_the_role(self):
        """After a restart the first thing the server hears from a phone is a request with a token,
        not a sign-in. The person's role must come out the same, and stay."""
        agency = self.otp(self.carp_phone)
        client = self.otp(self.client_phone)
        staff = self.token(self.coordinator)
        self.env.transaction.invalidate_ormcache()   # what a restart does to the groups the framework remembers
        self.assertEqual(self.get("/agency/home", agency["access_token"]).status_code, 200)
        self.assertEqual(self.get("/client/home", client["access_token"]).status_code, 200)
        self.assertEqual(self.get("/staff/snapshot", staff).status_code, 200)
        self.assertEqual(self.get("/me", agency["access_token"]).json()["role"], "agency")
        self.assertEqual(self.get("/me", client["access_token"]).json()["role"], "client")
        self.env.transaction.invalidate_ormcache()
        again = self.post("/auth/refresh", {"refresh_token": client["refresh_token"]})
        self.assertEqual(again.json()["me"]["role"], "client", again.text)

    def test_agency_and_client_snapshots_say_when_nothing_changed(self):
        tags = {}
        for phone, path in ((self.carp_phone, "/agency/snapshot"), (self.client_phone, "/client/snapshot")):
            token = self.otp(phone)["access_token"]
            first = self.get(path, token)
            self.assertEqual(first.status_code, 200, first.text)
            self.assertTrue(first.json()["projects"])
            tags[path] = (token, first.headers["ETag"])
            self.assertEqual(self.get(path, token, headers={"If-None-Match": first.headers["ETag"]}).status_code, 304)
        self.add("One more for the carpenter", partner=self.ag_carp)
        token, tag = tags["/agency/snapshot"]
        again = self.get("/agency/snapshot", token, headers={"If-None-Match": tag})
        self.assertEqual(again.status_code, 200, "something changed: the new state is sent")
        self.assertNotEqual(again.headers["ETag"], tag)

    def test_staff_are_refused_the_other_apps(self):
        token = self.token(self.coordinator)
        self.assertRefused(self.get("/agency/home", token), 403, "FORBIDDEN")
        self.assertRefused(self.get("/client/home", token), 403, "FORBIDDEN")
