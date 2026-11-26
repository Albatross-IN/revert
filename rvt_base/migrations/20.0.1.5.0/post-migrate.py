from odoo import SUPERUSER_ID, api


def migrate(cr, version):
    """The access ticks are new: everybody who already holds a Revert role gets the usual ticks of their roles."""
    env = api.Environment(cr, SUPERUSER_ID, {})
    users = env["res.users"].with_context(active_test=False).search([("share", "=", False)])
    users.filtered(lambda u: u._rvt_role_set()).rvt_apply_role_access()
