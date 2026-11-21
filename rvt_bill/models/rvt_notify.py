"""One more message: the office hears in the app that an agency uploaded a bill."""
from odoo import fields, models

from odoo.addons.rvt_api.models.rvt_notify import PREF_OF

# the "Bills" switch of the profile page silences it, like the other bill messages
PREF_OF.setdefault("bill_submitted", "bills")


class RvtNotifyTemplate(models.Model):
    _inherit = "rvt.notify.template"

    event = fields.Selection(
        selection_add=[("bill_submitted", "Bill uploaded by the agency (staff, in the app)")],
        ondelete={"bill_submitted": "cascade"})
