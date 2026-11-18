from odoo.tests import new_test_user, tagged

from .common import PASSWORD, ApiCase
from odoo.addons.rvt_notify.models.rvt_notify import e164


@tagged("post_install", "-at_install")
class TestAuth(ApiCase):

    def test_health(self):
        answer = self.get("/health")
        self.assertEqual(answer.status_code, 200)
        self.assertEqual(answer.json()["status"], "ok")

    def test_staff_login_and_me(self):
        session = self.login(self.coordinator)
        self.assertEqual(session["me"]["role"], "staff")
        self.assertEqual(session["me"]["roles"], ["coordinator"])
        self.assertEqual((session["me"]["name"], session["me"]["short"]), ("Meera Joshi", "Meera"))
        self.assertEqual(session["expires_in"], 86400)
        me = self.get("/me", session["access_token"]).json()
        self.assertEqual(me["id"], self.coordinator.id)
        self.assertEqual(me["prefs"], {"lang": "en", "push": {"drawings": True, "points": True, "bills": True, "reminders": True}})
        self.assertEqual(len(me["devices"]), 1)
        self.assertTrue(me["devices"][0]["this"])
        self.assertRefused(self.get("/me"), 401, "AUTH")
        self.assertRefused(self.get("/me", "not-a-token"), 401, "AUTH")

    def test_wrong_password_and_who_may_not(self):
        self.assertRefused(self.post("/auth/login", {"login": self.coordinator.login, "password": "nope"}), 401, "AUTH")
        self.assertRefused(self.post("/auth/login", {"login": "nobody", "password": "nope"}), 401, "AUTH")
        plain = new_test_user(self.env, "t_plain_internal", groups="base.group_user")
        plain.password = PASSWORD
        self.assertRefused(self.post("/auth/login", {"login": plain.login, "password": PASSWORD}), 403, "FORBIDDEN")
        self.assertRefused(self.post("/auth/login", {"login": "x"}), 422, "VALIDATION")

    def test_refresh_and_logout(self):
        session = self.login(self.designer)
        fresh = self.post("/auth/refresh", {"refresh_token": session["refresh_token"]})
        self.assertEqual(fresh.status_code, 200)
        self.assertEqual(self.get("/me", fresh.json()["access_token"]).status_code, 200)
        self.assertRefused(self.post("/auth/refresh", {"refresh_token": session["access_token"]}), 401, "AUTH")
        self.assertEqual(self.post("/auth/logout", token=session["access_token"]).status_code, 200)
        self.assertRefused(self.get("/me", session["access_token"]), 401, "AUTH")
        self.assertRefused(self.post("/auth/refresh", {"refresh_token": session["refresh_token"]}), 401, "AUTH")

    def test_signing_in_again_on_a_device_ends_its_old_session(self):
        first = self.login(self.designer, device="phone-1")
        other = self.login(self.designer, device="tablet-2")
        again = self.login(self.designer, device="phone-1")
        self.assertRefused(self.get("/me", first["access_token"]), 401)
        self.assertEqual(self.get("/me", other["access_token"]).status_code, 200, "another device is not touched")
        self.assertEqual(self.get("/me", again["access_token"]).status_code, 200)

    def test_preferences_device_and_password(self):
        token = self.token(self.coordinator)
        prefs = self.call("PUT", "/me/preferences", {"lang": "gu", "push": {"bills": False, "nonsense": True}}, token).json()
        self.assertEqual(prefs, {"lang": "gu", "push": {"drawings": True, "points": True, "bills": False, "reminders": True}})
        self.assertEqual(self.coordinator.partner_id.rvt_lang, "gu")
        self.assertEqual(self.post("/me/device", {"push_token": "fcm-token-1", "name": "Galaxy M31"}, token).status_code, 200)
        device = self.env["rvt.api.device"].search([("user_id", "=", self.coordinator.id)])
        self.assertEqual((device.push_token, device.name), ("fcm-token-1", "Galaxy M31"))
        other = self.login(self.coordinator, device="tablet")["access_token"]
        self.assertRefused(self.call("PUT", "/me/password", {"old": "wrong", "new": "another-pw-22"}, token), 422)
        self.assertRefused(self.call("PUT", "/me/password", {"old": PASSWORD, "new": "short"}, token), 422)
        self.assertEqual(self.call("PUT", "/me/password", {"old": PASSWORD, "new": "another-pw-22"}, token).status_code, 200)
        self.assertEqual(self.get("/me", token).status_code, 200, "this device stays signed in")
        self.assertRefused(self.get("/me", other), 401)
        self.assertRefused(self.post("/auth/login", {"login": self.coordinator.login, "password": PASSWORD}), 401)

    # ---- agencies and clients: number and code -------------------------
    def test_agency_signs_in_with_a_code(self):
        asked = self.post("/auth/otp/request", {"phone": self.carp_phone, "lang": "gu"})
        self.assertEqual(asked.status_code, 200, asked.text)
        body = asked.json()
        self.assertEqual((body["role"], body["sent"], body["expires_in"]), ("agency", False, 600))
        self.assertEqual(len(body["test_code"]), 4, "a test copy shows the code; the live database never does")
        log = self.env["rvt.notify.log"].search([("event", "=", "otp")], order="id desc", limit=1)
        self.assertEqual((log.state, log.phone, log.lang), ("held", "+919824418830", "gu"))
        self.assertIn(body["test_code"], log.text)
        self.assertRefused(self.post("/auth/otp/verify", {"phone": self.carp_phone, "code": "0000" if body["test_code"] != "0000" else "1111"}), 401, "WRONG_CODE")
        session = self.post("/auth/otp/verify", {"phone": self.carp_phone, "code": body["test_code"], "device": {"uid": "m31"}}).json()
        me = session["me"]
        self.assertEqual((me["role"], me["name"], me["login"]), ("agency", "Bherubhai Suthar", ""))
        self.assertEqual(me["agency"]["name"], "Mahadev Furniture")
        self.assertEqual(me["prefs"]["lang"], "gu")
        user = self.env["res.users"].browse(me["id"])
        self.assertTrue(user.share and user.has_group("rvt_base.group_rvt_agency"))
        self.assertEqual(user.partner_id, self.carp_person, "the account is the contact itself, made at the first sign-in")
        self.assertRefused(self.post("/auth/otp/verify", {"phone": self.carp_phone, "code": body["test_code"]}), 401, "WRONG_CODE")
        again = self.otp(self.carp_phone)
        self.assertEqual(again["me"]["id"], me["id"], "the same account the next time")
        self.assertRefused(self.post("/auth/login", {"login": user.login, "password": ""}), 401)

    def test_client_signs_in_with_a_code(self):
        session = self.otp(self.client_phone)
        self.assertEqual((session["me"]["role"], session["me"]["name"]), ("client", "Nirav Shah"))
        user = self.env["res.users"].browse(session["me"]["id"])
        self.assertTrue(user.has_group("rvt_base.group_rvt_client"))

    def test_a_number_on_two_contact_cards(self):
        """The same mobile number stands on two cards (the office entered the person twice) and the
        other card has an account already. This card still gets in, with an account of its own."""
        twin = self.env["res.partner"].create({"name": "Bherubhai (earlier card)", "phone": self.carp_phone})
        self.env["res.users"].with_context(no_reset_password=True).create({
            "name": twin.name, "login": "rvt:%s" % e164(self.carp_phone), "partner_id": twin.id,
            "group_ids": [(6, 0, [self.env.ref("rvt_base.group_rvt_client").id])]})
        answer = self.otp(self.carp_phone)
        self.assertEqual(answer["me"]["role"], "agency")
        self.assertEqual(answer["me"]["name"], self.carp_person.name)

    def test_unknown_number_wrong_tries_and_too_many_codes(self):
        self.assertRefused(self.post("/auth/otp/request", {"phone": "90000 00001"}), 404, "UNKNOWN_NUMBER")
        self.assertRefused(self.post("/auth/otp/request", {"phone": "123"}), 422, "VALIDATION")
        code = self.post("/auth/otp/request", {"phone": self.elec_phone}).json()["test_code"]
        wrong = "0000" if code != "0000" else "1111"
        for _i in range(5):
            self.assertRefused(self.post("/auth/otp/verify", {"phone": self.elec_phone, "code": wrong}), 401, "WRONG_CODE")
        self.assertRefused(self.post("/auth/otp/verify", {"phone": self.elec_phone, "code": code}), 401, "WRONG_CODE",)
        for _i in range(4):
            self.assertEqual(self.post("/auth/otp/request", {"phone": self.elec_phone}).status_code, 200)
        self.assertRefused(self.post("/auth/otp/request", {"phone": self.elec_phone}), 422, "VALIDATION")

    def test_client_link(self):
        token = self.token(self.coordinator)
        url = self.get("/projects/%s/client-link?contact_id=%s" % (self.project.id, self.client_contact.id), token).json()["url"]
        link = url.rsplit("/", 1)[1]
        session = self.post("/auth/link", {"token": link, "device": {"uid": "browser"}})
        self.assertEqual(session.status_code, 200, session.text)
        self.assertEqual(session.json()["me"]["role"], "client")
        me = self.get("/me", session.json()["access_token"]).json()
        self.assertEqual(me["link_project_id"], self.project.id)
        self.assertRefused(self.post("/auth/link", {"token": "nonsense"}), 401)
        self.assertRefused(self.post("/auth/link", {"token": token}), 401, "AUTH")
        self.assertRefused(self.get("/projects/%s/client-link?contact_id=%s" % (self.project.id, self.carp_person.id), token), 422)
