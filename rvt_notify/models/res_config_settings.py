from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    rvt_notify_sending_on = fields.Boolean(
        string="Sending is on", config_parameter="rvt.notify_sending_on", default=False)
