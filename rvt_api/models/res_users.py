from odoo import api, models

from odoo.addons.rvt_notify.models.rvt_notify import e164
from odoo.addons.rvt_project.models.rvt_picture import short_name


class ResUsers(models.Model):
    _inherit = "res.users"

    def rvt_api_role(self):
        """Which app a person gets: staff, agency or client. Nothing for anybody else."""
        self.ensure_one()
        if self.has_group("rvt_base.group_rvt_staff"):
            return "staff"
        if self.has_group("rvt_base.group_rvt_agency"):
            return "agency"
        if self.has_group("rvt_base.group_rvt_client"):
            return "client"
        return False

    def rvt_api_me(self):
        self.ensure_one()
        partner = self.partner_id.sudo()
        role = self.rvt_api_role()
        me = {
            "id": self.id, "name": self.name, "short": short_name(self.name), "role": role,
            "roles": [r for r in self.rvt_roles() if r in ("owner", "principal", "designer", "coordinator")],
            "login": self.login if role == "staff" else "", "phone": partner.phone or "",
            "prefs": partner.rvt_prefs(),
        }
        if role == "agency":
            firm = partner.commercial_partner_id
            me["agency"] = {"id": firm.id, "name": firm.name, "trades": firm.rvt_trade_ids.mapped("code")}
        return me

    @api.model
    def _rvt_person_for_phone(self, phone):
        """Who may sign in with this number: an agency's person, or a client contact of an onboarded
        project. Returns (partner, role), or nothing."""
        number = e164(phone)
        if not number:
            return self.env["res.partner"], False
        Partner = self.env["res.partner"].sudo()
        tail = number[-10:]
        candidates = Partner.search([("phone", "!=", False), ("phone", "like", tail[-4:])])
        candidates = candidates.filtered(lambda p: e164(p.phone) == number)
        Project = self.env["project.project"].sudo()
        for person in candidates:
            if person.commercial_partner_id.rvt_is_agency:
                return person, "agency"
        for person in candidates:
            if Project.search_count([("rvt_onboarded", "=", True), ("rvt_client_contact_ids", "in", person.ids)]):
                return person, "client"
        return self.env["res.partner"], False

    @api.model
    def _rvt_user_for_person(self, person, role):
        """The app account of an agency person or a client contact; made at their first sign-in.
        It has no password: the code on WhatsApp is the only way in."""
        person = person.sudo()
        user = self.sudo().with_context(active_test=False).search([("partner_id", "=", person.id)], limit=1)
        group = self.env.ref("rvt_base.group_rvt_agency" if role == "agency" else "rvt_base.group_rvt_client")
        if user:
            if user.share and group not in user.group_ids:
                user.write({"group_ids": [(4, group.id)]})
            if not user.active:
                user.active = True
            return user
        return self.sudo().with_context(no_reset_password=True).create({
            "name": person.name, "login": "rvt:%s" % e164(person.phone), "partner_id": person.id,
            "group_ids": [(6, 0, [group.id])],
        })
