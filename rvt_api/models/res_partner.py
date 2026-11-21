from odoo import fields, models

APP_LANGS = [("en", "English"), ("gu", "ગુજરાતી"), ("hi", "हिंदी")]
PREFS = ("rvt_push_drawings", "rvt_push_points", "rvt_push_bills", "rvt_push_reminders")


class ResPartner(models.Model):
    _inherit = "res.partner"

    rvt_lang = fields.Selection(
        APP_LANGS, string="App language",
        help="Chosen in the app. Messages to this person are written in it too.")
    rvt_push_drawings = fields.Boolean(string="Notify: drawings", default=True)
    rvt_push_points = fields.Boolean(string="Notify: points", default=True)
    rvt_push_bills = fields.Boolean(string="Notify: bills", default=True)
    rvt_push_reminders = fields.Boolean(string="Notify: reminders", default=True)

    def rvt_prefs(self):
        self.ensure_one()
        partner = self.sudo()
        return {
            "lang": partner.rvt_lang or {"gu_IN": "gu", "hi_IN": "hi"}.get(partner.lang or partner.parent_id.lang, "en"),
            "push": {key[9:]: bool(partner[key]) for key in PREFS},
        }

    def rvt_set_prefs(self, lang=None, push=None):
        self.ensure_one()
        vals = {}
        if lang in dict(APP_LANGS):
            vals["rvt_lang"] = lang
        for key, value in (push or {}).items():
            if "rvt_push_%s" % key in PREFS:
                vals["rvt_push_%s" % key] = bool(value)
        if vals:
            self.sudo().write(vals)
        return self.rvt_prefs()
