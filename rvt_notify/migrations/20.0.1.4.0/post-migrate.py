from odoo import SUPERUSER_ID, api


def migrate(cr, version):
    """The tick "WhatsApp connection" is new: owners get it, as their role brings it."""
    env = api.Environment(cr, SUPERUSER_ID, {})
    users = env["res.users"].with_context(active_test=False).search([("share", "=", False)])
    users.filtered(lambda u: u._rvt_role_set()).rvt_apply_role_access()
