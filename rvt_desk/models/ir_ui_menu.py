from odoo import api, models


class IrUiMenu(models.Model):
    _inherit = "ir.ui.menu"

    def _rvt_desk_only(self):
        user = self.env.user
        return (user.has_group("rvt_base.group_rvt_staff")
                and not user.has_group("base.group_system")
                and self.env["ir.config_parameter"].sudo().get_bool("rvt.desk_only", True))

    @api.model
    def get_user_roots(self):
        roots = super().get_user_roots()
        if self._rvt_desk_only():
            keep = self.env.ref("rvt_base.menu_rvt_root", raise_if_not_found=False)
            roots = roots & keep if keep else roots.browse()
        return roots

    def _load_menus_blacklist(self):
        """Staff work in the Revert window only: every other application menu is
        hidden for them. System administrators keep all menus."""
        hidden = super()._load_menus_blacklist()
        if self._rvt_desk_only():
            keep = self.env.ref("rvt_base.menu_rvt_root", raise_if_not_found=False)
            roots = self.sudo().search([("parent_id", "=", False)])
            hidden = list(set(hidden) | set((roots - keep).ids if keep else roots.ids))
        return hidden
