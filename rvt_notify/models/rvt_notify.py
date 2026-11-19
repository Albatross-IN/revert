import logging
import re

from odoo import api, models

from odoo.addons.rvt_project.models.rvt_picture import day_month, plural

_logger = logging.getLogger(__name__)

LANG_OF = {"gu_IN": "gu", "hi_IN": "hi"}
# on a test copy: the numbers that are really messaged (see test_numbers)
TEST_NUMBERS = "rvt.notify_test_numbers"
# staff are told in the app (and by a push once the app is there), never on WhatsApp
STAFF_EVENTS = ("drawing_approval_needed", "drawing_question")


def e164(phone):
    """A mobile number as WhatsApp wants it. Numbers are typed the local way
    ("98250 41120", "098250…"); the studio is in India, so ten digits get +91."""
    digits = re.sub(r"\D", "", phone or "")
    if len(digits) == 11 and digits.startswith("0"):
        digits = digits[1:]
    if len(digits) == 10:
        digits = "91" + digits
    return "+" + digits if len(digits) >= 11 else False


def fill(text, values):
    """{key} -> value for the keys we know; anything else stays as typed."""
    return re.sub(r"\{(\w+)\}", lambda m: str(values[m.group(1)]) if values.get(m.group(1)) is not None else m.group(0), text or "")


class RvtNotify(models.AbstractModel):
    _inherit = "rvt.notify"

    # ------------------------------------------------------------------
    # the switch
    # ------------------------------------------------------------------
    @api.model
    def is_test_copy(self):
        return self.env["ir.config_parameter"].sudo().get_bool("database.is_neutralized", False)

    @api.model
    def sending_on(self):
        """True only when the switch is on AND this is not a test copy of the database."""
        return self.env["ir.config_parameter"].sudo().get_bool("rvt.notify_sending_on", False) and not self.is_test_copy()

    @api.model
    def test_numbers(self):
        """On a test copy only: the mobile numbers that are really messaged, so a flow can be tried on the
        team's own phones (system parameter ``rvt.notify_test_numbers``, commas between the numbers).
        Empty, the usual case: nothing leaves a test copy. On the live database the parameter means nothing."""
        if not self.is_test_copy():
            return set()
        raw = self.env["ir.config_parameter"].sudo().get_str(TEST_NUMBERS, "")
        return {number for number in (e164(part) for part in re.split(r"[,;\n]+", raw)) if number}

    @api.model
    def _held_reason(self, number=None):
        """Why a message to this number stays here, or False when it may leave."""
        if self.is_test_copy():
            listed = self.test_numbers()
            if number and number in listed:
                return False
            if listed:
                return self.env._("Test copy of the database: this number is not one of its test numbers.")
            return self.env._("Test copy of the database: nothing is sent from it.")
        if not self.env["ir.config_parameter"].sudo().get_bool("rvt.notify_sending_on", False):
            return self.env._("Sending is off in Setup.")
        return False

    @api.model
    def _account(self):
        accounts = self.env["owa.account"].sudo().search([("session_state", "=", "connected")])
        return accounts.filtered("is_default")[:1] or accounts[:1]

    @api.model
    def number(self):
        """The dedicated number messages leave from, for Setup."""
        account = self._account()
        return account.phone_number or "" if account else ""

    # ------------------------------------------------------------------
    # what a message says
    # ------------------------------------------------------------------
    @api.model
    def _lang(self, partner):
        """Gujarati or Hindi when the person, or the firm they belong to, is set to it; English otherwise.
        (A new contact starts in the database's default language, so the firm's setting is what counts for its people.)"""
        return LANG_OF.get(partner.lang) or LANG_OF.get(partner.parent_id.lang) or "en"

    @api.model
    def _values(self, event, record, values):
        """The words that fill a template, from the record the message is about."""
        out = dict(values)
        project = False
        if record:
            project = record if record._name == "project.project" else getattr(record, "project_id", False)
        if project:
            out.setdefault("site", project.sudo().name)
        if event in ("drawing_released", "drawing_client") and record and record._name == "rvt.drawing.receipt":
            receipt = record.sudo()
            drawing = receipt.drawing_id
            out.update({"sheet": drawing.sheet_no, "title": drawing.name, "rev": receipt.revision_id.number,
                        "link": receipt.rvt_link()})
        elif event == "mom_party_pdf" and record:
            visit = record.sudo()
            points, fresh = values.get("points"), values.get("new") or 0
            count = plural(len(points), "point") if points is not None else ""
            if points is not None and fresh and fresh < len(points):
                count += " (%s new)" % fresh
            out.update({"no": visit.number, "date": day_month(visit.date), "count": count})
        elif event == "client_item" and record:
            point = record.sudo()
            out.update({"text": point.text, "date": day_month(point.due_date) if point.due_date else ""})
        elif event in ("drawing_approval_needed", "drawing_question") and record:
            drawing = record.sudo() if record._name == "rvt.drawing" else record.sudo().drawing_id
            out.update({"sheet": drawing.sheet_no, "title": drawing.name, "rev": drawing.current_revision_id.number})
            if record._name == "rvt.drawing.question":
                out["text"] = record.sudo().text
        return out

    @api.model
    def _document(self, event, record, values):
        """(file name, bytes) of the file that goes with the message, or None."""
        if event == "mom_party_pdf" and record and values.get("partner"):
            visit, partner = record.sudo(), values["partner"]
            kind = "agency" if partner.rvt_is_agency else "vendor"
            pdf = self.env["ir.actions.report"].sudo()._render_qweb_pdf(
                "rvt_mom.action_report_visit", visit.ids, data={"party": {"kind": kind, "partner_id": partner.id}})[0]
            return ("MOM - Visit %s - %s.pdf" % (visit.number, partner.name), pdf)
        return values.get("document") or None

    @api.model
    def render(self, event, record, person, values=None):
        """The text one person gets, in their language."""
        filled = self._values(event, record, values or {})
        text = fill(self.env["rvt.notify.template"].text_for(event, self._lang(person)), filled)
        if filled.get("link") and filled["link"] not in text:
            text = "%s\n%s" % (text, filled["link"])
        return text

    # ------------------------------------------------------------------
    # sending
    # ------------------------------------------------------------------
    @api.model
    def send(self, event, record, recipients, **values):
        """Send one event to people. ``recipients`` are partners (WhatsApp) or users (in the app).
        Every message is logged; the number that really left is returned."""
        if not recipients:
            return 0
        Log = self.env["rvt.notify.log"].sudo()
        project = False
        if record:
            project = record if record._name == "project.project" else getattr(record, "project_id", False)
        base = {
            "event": event, "project_id": project.id if project else False,
            "res_model": record._name if record else False, "res_id": record.id if record else False,
            "sent_by_id": self.env.uid,
        }
        if recipients._name == "res.users":
            filled = self._values(event, record, values)
            text = fill(self.env["rvt.notify.template"].text_for(event, "en"), filled)
            for user in recipients:
                Log.create(dict(base, user_id=user.id, name=user.name, lang="en", text=text, state="in_app"))
                self._push(user, event, text, record)
            return 0
        account = document = None
        sent = 0
        for partner in recipients.sudo():
            text = self.render(event, record, partner, values)
            number = e164(partner.phone)
            row = dict(base, partner_id=partner.id, name=partner.name, phone=number or partner.phone or "",
                       lang=self._lang(partner), text=text)
            if event == "mom_party_pdf":
                row["document"] = "MOM - Visit %s - %s.pdf" % (record.sudo().number, values["partner"].name) if values.get("partner") else False
            if not number:
                Log.create(dict(row, state="no_number", reason=self.env._("No mobile number on the contact.")))
                continue
            held = self._held_reason(number)
            if held:
                Log.create(dict(row, state="held", reason=held))
                continue
            if account is None:
                account = self._account() or False
            if not account:
                Log.create(dict(row, state="failed", reason=self.env._("No WhatsApp number is paired.")))
                continue
            try:
                if document is None:
                    document = self._document(event, record, values) or False
                ok = self._wa_send_file(account, number, text, *document) if document else self._wa_send_text(account, number, text)
                Log.create(dict(row, state="sent" if ok else "failed",
                                reason=False if ok else self.env._("The connector did not accept the message.")))
                sent += 1 if ok else 0
            except Exception as error:  # noqa: BLE001  (a failed message must never break the action that caused it)
                _logger.exception("rvt.notify: %s to %s failed", event, number)
                Log.create(dict(row, state="failed", reason=str(error)[:200]))
        return sent

    @api.model
    def _push(self, user, event, text, record):
        """Hook: the app's push notification (P7)."""
        return False

    # ---- the connector --------------------------------------------------
    @api.model
    def _wa_send_text(self, account, number, text):
        message = account._owa_send_text(number, text)
        if not message:
            return False
        message._send_message()
        return message.state not in ("error", "bounced", "cancel")

    @api.model
    def _wa_send_file(self, account, number, text, file_name, data, mimetype="application/pdf"):
        from odoo.addons.open_whatsapp_connector.tools.phone_validation import wa_phone_format
        from odoo.tools import plaintext2html
        env = self.env
        attachment = env["ir.attachment"].sudo().create({
            "name": file_name, "raw": data, "mimetype": mimetype, "res_model": "owa.account", "res_id": account.id})
        mail_message = env["mail.message"].sudo().create({
            "body": plaintext2html(text or ""), "message_type": "whatsapp_message", "attachment_ids": [(4, attachment.id)]})
        message = env["owa.message"].sudo().create({
            "mobile_number": wa_phone_format(env, number) or number, "message_type": "outbound", "state": "outgoing",
            "wa_account_id": account.id, "mail_message_id": mail_message.id})
        message._send_message()
        return message.state not in ("error", "bounced", "cancel")
