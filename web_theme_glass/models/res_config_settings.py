# -*- coding: utf-8 -*-
from odoo import api, fields, models

PARAM = "web_theme_glass.enabled"


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    glass_theme_enabled = fields.Boolean(
        string="Glass Theme",
        config_parameter=PARAM,
        default=True,
        help="Apply the frosted-glass styling to the backend. "
             "Turning it off restores the standard Odoo look without uninstalling.",
    )

    @api.model
    def _glass_theme_enabled(self):
        # Odoo 20 stores a boolean setting as "True" / "False" (`set_bool`); a database that has
        # never saved the settings has no parameter yet, and the theme is on (the field default).
        return self.env["ir.config_parameter"].sudo().get_bool(PARAM, True)
