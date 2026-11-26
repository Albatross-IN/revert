from odoo import api, models
from odoo.exceptions import UserError


class RvtDesk(models.AbstractModel):
    _inherit = "rvt.desk"

    @api.model
    def _access_needed_by_op(self):
        return dict(super()._access_needed_by_op(), client_link="projects")

    def _op_client_link(self, a):
        """The address a client contact opens without installing the app or signing in ("Copy link")."""
        from ..routers.auth import client_link
        project = self.env["project.project"].browse(int(str(a.get("project") or 0).lstrip("p") or 0)).exists()
        if not project:
            raise UserError(self.env._("Choose the project."))
        project.check_access("read")
        contacts = project.sudo().rvt_client_contact_ids
        person = contacts.filtered(lambda c: c.id == int(a.get("contact") or 0)) or contacts[:1]
        if not person:
            raise UserError(self.env._("Add a client contact with a mobile number first."))
        return {"url": client_link(self.env, project, person[:1]), "name": person[:1].name}
