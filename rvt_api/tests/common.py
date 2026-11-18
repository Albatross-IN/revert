import json

from odoo.tests import HttpCase

from odoo.addons.rvt_mom.tests.common import MomCommon

ROOT = "/api/rvt/v1"
PASSWORD = "revert-test-pw-1"


class ApiCase(MomCommon, HttpCase):
    """Real HTTP against the mounted API: the wiring is what is under test
    (the endpoint record, the bearer token, the error shape, each role's rights)."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        for user in (cls.owner, cls.principal, cls.coordinator, cls.designer, cls.designer2, cls.outsider):
            user.password = PASSWORD
        Partner = cls.env["res.partner"]
        cls.carp_person = Partner.search([("parent_id", "=", cls.ag_carp.id), ("name", "=", "Bherubhai Suthar")])
        cls.elec_person = Partner.search([("parent_id", "=", cls.ag_elec.id), ("name", "=", "Jaybhai Solanki")])
        cls.carp_phone, cls.elec_phone, cls.client_phone = "98244 18830", "98790 22014", "98250 70011"

    def setUp(self):
        super().setUp()
        # codes asked for by hand on this copy must not count against the tests
        self.env["rvt.api.otp"].sudo().search([]).unlink()

    def call(self, method, path, body=None, token=None, headers=None):
        head = dict(headers or {})
        if token:
            head["Authorization"] = "Bearer %s" % token
        data = None
        if body is not None:
            head["Content-Type"] = "application/json"
            data = json.dumps(body)
        self.env.flush_all()
        return self.url_open(ROOT + path, data=data, headers=head, method=method)

    def get(self, path, token=None, **kw):
        return self.call("GET", path, token=token, **kw)

    def post(self, path, body=None, token=None, **kw):
        return self.call("POST", path, body if body is not None else {}, token=token, **kw)

    def login(self, user, device="phone-1"):
        answer = self.post("/auth/login", {"login": user.login, "password": PASSWORD, "device": {"uid": device, "platform": "android"}})
        self.assertEqual(answer.status_code, 200, answer.text)
        return answer.json()

    def token(self, user):
        return self.login(user)["access_token"]

    def otp(self, phone, device="phone-9"):
        asked = self.post("/auth/otp/request", {"phone": phone})
        self.assertEqual(asked.status_code, 200, asked.text)
        code = asked.json()["test_code"]
        answer = self.post("/auth/otp/verify", {"phone": phone, "code": code, "device": {"uid": device}})
        self.assertEqual(answer.status_code, 200, answer.text)
        return answer.json()

    def assertRefused(self, answer, status, code=None):
        self.assertEqual(answer.status_code, status, answer.text)
        error = answer.json()["error"]
        if code:
            self.assertEqual(error["code"], code)
        self.assertTrue(error["message"])
