from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    rvt_desk_only = fields.Boolean(
        string="Staff see only the Revert window",
        config_parameter="rvt.desk_only", default=True)
