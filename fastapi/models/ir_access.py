# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class IrAccess(models.Model):
    """Add authenticated_partner_id in the access domain evaluation context.

    This comes from the current odoo environment, which is populated by the
    dependency method authenticated_partner_env or authenticated_partner
    when a route handler depends on one of them and is called by the FastAPI
    service layer.

    Odoo 20 port note: ir.rule was merged into ir.access. The old
    ``_eval_context``/``_compute_domain_keys`` pair maps to
    ``_eval_context``/``_get_access_context`` (the latter feeds
    ``env._access_context``, the ormcache key of ``_get_access_domain``).
    """

    _inherit = "ir.access"

    def _eval_context(self):
        ctx = super()._eval_context()
        ctx["authenticated_partner_id"] = self.env.context.get(
            "authenticated_partner_id", False
        )
        return ctx

    def _get_access_context(self):
        yield from super()._get_access_context()
        yield self.env.context.get("authenticated_partner_id", False)
