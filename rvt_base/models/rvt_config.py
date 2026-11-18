from odoo import api, models

# key -> (type, default). Read through rvt.config so that every caller gets the
# same defaults and nobody needs read access on system parameters.
PARAMS = {
    "release_needs_approval": ("rvt.release_needs_approval", "bool", True),
    "client_points_need_confirmation": ("rvt.client_points_need_confirmation", "bool", True),
    "limit_not_opened_days": ("rvt.limit_not_opened_days", "int", 2),
    "limit_question_days": ("rvt.limit_question_days", "int", 1),
    "limit_bill_review_days": ("rvt.limit_bill_review_days", "int", 3),
    "limit_stuck_days": ("rvt.limit_stuck_days", "int", 7),
}


class RvtConfig(models.AbstractModel):
    _name = "rvt.config"
    _description = "Revert settings reader"

    @api.model
    def get(self, name=None):
        """Return one setting, or all of them as a dict when no name is given."""
        icp = self.env["ir.config_parameter"].sudo()
        if name:
            key, type_, default = PARAMS[name]
            return icp.get_bool(key, default) if type_ == "bool" else icp.get_int(key, default)
        return {n: self.get(n) for n in PARAMS}
