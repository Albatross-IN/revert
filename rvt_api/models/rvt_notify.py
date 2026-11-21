"""The app's side of messages: the language chosen in the app, and the push notification."""
import json
import logging
import time

import jwt
import requests

from odoo import api, models

_logger = logging.getLogger(__name__)

# which switch of the profile page silences which event
PREF_OF = {
    "drawing_released": "drawings", "drawing_client": "drawings", "drawing_approval_needed": "drawings", "drawing_question": "drawings",
    "mom_party_pdf": "points", "client_item": "points", "point_change": "points",
    "bill_asked": "bills", "bill_returned": "bills", "bill_accepted": "bills", "bill_paid": "bills",
    "remind": "reminders",
}


class RvtNotify(models.AbstractModel):
    _inherit = "rvt.notify"

    @api.model
    def _lang(self, partner):
        return partner.rvt_lang or partner.parent_id.rvt_lang or super()._lang(partner)

    @api.model
    def send(self, event, record, recipients, **values):
        sent = super().send(event, record, recipients, **values)
        if recipients and recipients._name == "res.partner" and event in PREF_OF and self.sending_on():
            for partner in recipients.sudo():
                user = partner.user_ids[:1]
                if user:
                    self._push(user, event, self.render(event, record, partner, values), record)
        return sent

    @api.model
    def _push(self, user, event, text, record):
        """A notification on the person's phones, unless they switched that kind off or this is a test copy."""
        if not self.sending_on():
            return 0
        partner = user.sudo().partner_id
        pref = PREF_OF.get(event)
        if pref and not partner["rvt_push_%s" % pref]:
            return 0
        tokens = self.env["rvt.api.device"].sudo().search([("user_id", "=", user.id), ("push_token", "!=", False)]).mapped("push_token")
        if not tokens:
            return 0
        data = {"event": event, "model": record._name if record else "", "id": str(record.id) if record else ""}
        try:
            return self._fcm_send(tokens, "Revert", text.split("\n")[0][:180], data)
        except Exception:  # noqa: BLE001  (a notification must never break the action behind it)
            _logger.exception("rvt_api: push failed")
            return 0

    # ---- Firebase Cloud Messaging (HTTP v1) --------------------------------
    @api.model
    def _fcm_account(self):
        raw = self.env["ir.config_parameter"].sudo().get_str("rvt_api.fcm_service_account")
        try:
            return json.loads(raw) if raw else None
        except ValueError:
            return None

    @api.model
    def _fcm_send(self, tokens, title, body, data):
        account = self._fcm_account()
        if not account:
            return 0
        now = int(time.time())
        assertion = jwt.encode({
            "iss": account["client_email"], "scope": "https://www.googleapis.com/auth/firebase.messaging",
            "aud": account["token_uri"], "iat": now, "exp": now + 3000}, account["private_key"], algorithm="RS256")
        grant = requests.post(account["token_uri"], timeout=10, data={
            "grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer", "assertion": assertion})
        grant.raise_for_status()
        headers = {"Authorization": "Bearer %s" % grant.json()["access_token"]}
        url = "https://fcm.googleapis.com/v1/projects/%s/messages:send" % account["project_id"]
        sent = 0
        for token in tokens:
            answer = requests.post(url, timeout=10, headers=headers, json={"message": {
                "token": token, "notification": {"title": title, "body": body}, "data": data}})
            if answer.status_code == 200:
                sent += 1
            elif answer.status_code in (400, 404):
                # the phone no longer has the app: forget its token
                self.env["rvt.api.device"].sudo().search([("push_token", "=", token)]).write({"push_token": False})
        return sent
