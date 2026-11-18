from odoo import models

# role key -> group xml id; the order is the order shown to people
ROLE_GROUPS = [
    ("owner", "rvt_base.group_rvt_owner"),
    ("principal", "rvt_base.group_rvt_principal"),
    ("designer", "rvt_base.group_rvt_designer"),
    ("coordinator", "rvt_base.group_rvt_coordinator"),
    ("agency", "rvt_base.group_rvt_agency"),
    ("client", "rvt_base.group_rvt_client"),
]


class ResUsers(models.Model):
    _inherit = "res.users"

    def rvt_roles(self):
        """Role keys of this user, e.g. ['owner', 'principal'].

        The owner group implies the principal group (an owner may do what the
        principal does), but a person is *called* principal only when the role
        was given to them by name."""
        self.ensure_one()
        explicit = self.sudo().group_ids
        roles = []
        for key, xmlid in ROLE_GROUPS:
            if key == "principal":
                if self.env.ref(xmlid) in explicit:
                    roles.append(key)
            elif self.has_group(xmlid):
                roles.append(key)
        return roles

    def rvt_set_roles(self, roles):
        """Give exactly these staff roles (owner, principal, designer, coordinator)."""
        staff_roles = {"owner", "principal", "designer", "coordinator"}
        unknown = set(roles) - staff_roles
        if unknown:
            raise ValueError("Unknown role: %s" % ", ".join(sorted(unknown)))
        ref = self.env.ref
        role_groups = {key: ref(xmlid) for key, xmlid in ROLE_GROUPS if key in staff_roles}
        staff = ref("rvt_base.group_rvt_staff")
        for user in self:
            commands = [(3, group.id) for group in role_groups.values()] + [(3, staff.id)]
            commands += [(4, role_groups[key].id) for key in roles]
            if roles:
                commands.append((4, staff.id))
            user.sudo().write({"group_ids": commands})
        return True
