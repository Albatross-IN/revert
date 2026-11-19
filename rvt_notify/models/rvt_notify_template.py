from odoo import api, fields, models

EVENTS = [
    ("drawing_released", "Drawing released (agency)"),
    ("drawing_client", "Drawing released (client)"),
    ("mom_party_pdf", "MOM of a visit, one party's points"),
    ("client_item", "Item raised for the client"),
    ("bill_asked", "Bill asked"),
    ("bill_returned", "Bill returned"),
    ("bill_accepted", "Bill accepted"),
    ("bill_paid", "Payment recorded on a bill"),
    ("invite", "Invitation to the app"),
    ("remind", "Reminder for one item"),
    ("otp", "Sign-in code"),
    ("drawing_approval_needed", "Drawing waits for approval (staff, in the app)"),
    ("drawing_question", "Question on a drawing (staff, in the app)"),
    ("point_done", "Point marked done by the agency (staff, in the app)"),
    ("point_change", "Change asked on a point the agency marked done"),
]
# events whose reader is the client: the wording rules of docs/rules.md §6.1 apply to them
CLIENT_EVENTS = ("drawing_client", "client_item")
LANGS = [("en", "English"), ("gu", "Gujarati"), ("hi", "Hindi")]


class RvtNotifyTemplate(models.Model):
    _name = "rvt.notify.template"
    _description = "Message text"
    _order = "event, lang"

    event = fields.Selection(EVENTS, required=True, index=True)
    lang = fields.Selection(LANGS, string="Language", required=True, default="en")
    text = fields.Text(required=True, help="Words in {braces} are filled in for each message.")

    _event_lang_uniq = models.Constraint("unique (event, lang)", "There is already a text for this event in this language.")

    @api.depends("event", "lang")
    def _compute_display_name(self):
        events = dict(EVENTS)
        for template in self:
            template.display_name = "%s · %s" % (events.get(template.event, template.event), template.lang)

    @api.model
    def text_for(self, event, lang):
        """The wording of an event in a language; English when that language is missing."""
        rows = {t.lang: t.text for t in self.sudo().search([("event", "=", event)])}
        return rows.get(lang) or rows.get("en") or "{text}"
