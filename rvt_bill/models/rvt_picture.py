"""What the project picture learns from bills: rule B10 and the office's "review the bill"."""
from odoo import api, fields, models

from odoo.addons.rvt_project.models.rvt_picture import day_month


class ProjectProject(models.Model):
    _inherit = "project.project"

    rvt_bill_ids = fields.One2many("rvt.bill", "project_id", string="Bills")

    def _rvt_picture_ctx(self):
        ctx = super()._rvt_picture_ctx()
        ctx["bills_to_review"] = self.env["rvt.bill"].sudo().search(
            [("project_id", "=", self.id), ("state", "=", "submitted")], order="submitted_on, id")
        return ctx

    @api.model
    def _rvt_blocker_rules(self):
        return super()._rvt_blocker_rules() + ["_rvt_b10_bill_not_reviewed"]

    def _rvt_bill_action(self, bill):
        return {"key": "bill", "label": self.env._("Review"), "bill_id": bill.id}

    def _rvt_b10_bill_not_reviewed(self, ctx):
        """B10: a bill is submitted and not reviewed within the day limit."""
        out = []
        limit = ctx["limits"]["limit_bill_review_days"]
        for bill in ctx["bills_to_review"]:
            age = (ctx["today"] - (bill.submitted_on or ctx["today"])).days
            if age < limit:
                continue
            out.append({
                "rule": "B10", "critical": False,
                "text": self.env._("Bill from %s not reviewed", bill.agency_id.name),
                "sub": bill.what, "holds": bill.what, "actor": self.env._("Office"), "who": ctx["coords"].ids,
                "age": age, "action": self._rvt_bill_action(bill),
            })
        return out

    @api.model
    def _rvt_next_builders(self):
        return super()._rvt_next_builders() + ["_rvt_next_bills"]

    def _rvt_next_bills(self, ctx, nxt):
        limit = ctx["limits"]["limit_bill_review_days"]
        for bill in ctx["bills_to_review"]:
            age = (ctx["today"] - (bill.submitted_on or ctx["today"])).days
            nxt["revert"].append({
                "section": "bill", "who": ctx["coords"].ids, "who_name": self.env._("Office"), "office": True,
                "text": self.env._("Review the bill from %s", bill.agency_id.name),
                "sub": self.env._("%(what)s · submitted %(date)s", what=bill.what, date=day_month(bill.submitted_on) if bill.submitted_on else ""),
                "warn": "", "late": age >= limit, "action": self._rvt_bill_action(bill),
            })
