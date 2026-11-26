from odoo import api, fields, models

# role key -> group xml id; the order is the order shown to people
ROLE_GROUPS = [
    ("owner", "rvt_base.group_rvt_owner"),
    ("principal", "rvt_base.group_rvt_principal"),
    ("designer", "rvt_base.group_rvt_designer"),
    ("coordinator", "rvt_base.group_rvt_coordinator"),
    ("agency", "rvt_base.group_rvt_agency"),
    ("client", "rvt_base.group_rvt_client"),
]

# what a person may do in the desk and the app, one tick each; key -> group xml id
ACCESS = [
    ("allprojects", "rvt_base.group_rvt_acc_allprojects"),
    ("projects", "rvt_base.group_rvt_acc_projects"),
    ("grid", "rvt_base.group_rvt_acc_grid"),
    ("drawings", "rvt_base.group_rvt_acc_drawings"),
    ("approve", "rvt_base.group_rvt_acc_approve"),
    ("mom", "rvt_base.group_rvt_acc_mom"),
    ("agencies", "rvt_base.group_rvt_acc_agencies"),
    ("bills", "rvt_base.group_rvt_acc_bills"),
    ("money", "rvt_base.group_rvt_acc_money"),
    ("setup", "rvt_base.group_rvt_acc_setup"),
    ("whatsapp", "rvt_notify.group_rvt_acc_whatsapp"),   # defined where the WhatsApp connector is a dependency
]
# the ticks a role brings when it is given (the office's table of 26 Nov 2026); they can be changed by hand after
ROLE_ACCESS = {
    "owner": [key for key, _x in ACCESS],
    "principal": ["allprojects", "projects", "grid", "drawings", "approve", "mom", "agencies", "bills", "money", "setup"],
    "designer": ["grid", "drawings", "mom"],
    "coordinator": ["grid", "drawings", "mom", "agencies"],
}
# Today's items, and the tick each needs
SECTION_ACCESS = {"approve": "approve", "draw": "drawings", "change": "drawings", "release": "drawings", "question": "drawings",
                  "chase": "drawings", "decide": "agencies", "confirm": "mom", "check": "mom", "point": "mom",
                  "client": "mom", "bill": "bills"}


class ResUsers(models.Model):
    _inherit = "res.users"

    rvt_access_ids = fields.Many2many(
        "res.groups", string="Revert access", compute="_compute_rvt_access_ids", inverse="_inverse_rvt_access_ids",
        domain=lambda self: [("id", "in", [g.id for g in self.env["res.users"]._rvt_access_groups().values()])],
        help="What this person may do in the Revert desk and app. Giving a Revert role ticks its usual ones.")

    @api.model
    def _rvt_access_groups(self):
        """{key: group} of the ticks that exist in this database."""
        out = {}
        for key, xmlid in ACCESS:
            group = self.env.ref(xmlid, raise_if_not_found=False)
            if group:
                out[key] = group
        return out

    @api.depends("group_ids")
    def _compute_rvt_access_ids(self):
        groups = self.env["res.groups"].browse([g.id for g in self._rvt_access_groups().values()])
        for user in self:
            user.rvt_access_ids = user.sudo().group_ids & groups

    def _inverse_rvt_access_ids(self):
        groups = self.env["res.groups"].browse([g.id for g in self._rvt_access_groups().values()])
        for user in self:
            wanted = user.rvt_access_ids & groups
            commands = [(3, g.id) for g in groups - wanted] + [(4, g.id) for g in wanted]
            user.sudo().with_context(rvt_access_by_hand=True).write({"group_ids": commands})

    def rvt_access(self):
        """The keys this person is ticked for, e.g. {'drawings', 'mom'}. This decides what the screens show."""
        self.ensure_one()
        mine = self.sudo().group_ids
        return {key for key, group in self._rvt_access_groups().items() if group in mine}

    def rvt_check_access(self, key):
        """Refuse when this person is not ticked for this; system administrators always pass.
        (Called on env.user, whose environment is always the superuser's: so the check is on the person, never on su.)"""
        self.ensure_one()
        if self.sudo().has_group("base.group_system") or key in self.rvt_access():
            return True
        from odoo.exceptions import AccessError
        labels = {k: g.name for k, g in self._rvt_access_groups().items()}
        raise AccessError(self.env._("You do not have the access \"%s\". Ask an owner to tick it in your Revert access.",
                                     labels.get(key, key)))

    def _rvt_role_set(self):
        return {key for key, xmlid in ROLE_GROUPS[:4] if self.env.ref(xmlid) in self.sudo().group_ids}

    def _rvt_follow_roles(self, before):
        """A role given brings its usual ticks; a role taken away takes the ticks that only it brought."""
        groups = self._rvt_access_groups()
        for user in self:
            now = user._rvt_role_set()
            old = before.get(user.id, set())
            if now == old:
                continue
            keep = {k for role in now for k in ROLE_ACCESS.get(role, [])}
            gone = {k for role in old - now for k in ROLE_ACCESS.get(role, [])} - keep
            new = {k for role in now - old for k in ROLE_ACCESS.get(role, [])}
            commands = [(4, groups[k].id) for k in new if k in groups] + [(3, groups[k].id) for k in gone if k in groups]
            if commands:
                super(ResUsers, user.sudo()).write({"group_ids": commands})

    def rvt_apply_role_access(self):
        """Give each person the usual ticks of the roles they hold (adds, never removes)."""
        groups = self._rvt_access_groups()
        for user in self:
            keys = {k for role in user._rvt_role_set() for k in ROLE_ACCESS.get(role, [])}
            commands = [(4, groups[k].id) for k in keys if k in groups]
            if commands:
                super(ResUsers, user.sudo()).write({"group_ids": commands})
        return True

    @api.model_create_multi
    def create(self, vals_list):
        users = super().create(vals_list)
        if not self.env.context.get("rvt_access_by_hand"):
            users._rvt_follow_roles({})
        return users

    def write(self, vals):
        if "group_ids" not in vals or self.env.context.get("rvt_access_by_hand"):
            return super().write(vals)
        before = {user.id: user._rvt_role_set() for user in self}
        res = super().write(vals)
        self._rvt_follow_roles(before)
        return res

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
            elif self.sudo().has_group(xmlid):     # sudo: see rvt_api_role (the groups cache)
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
