from odoo import fields, models
from odoo.exceptions import UserError


class ProjectProject(models.Model):
    _inherit = "project.project"

    def _rvt_people_of(self, agency):
        """An agency's contact people on this project."""
        self.ensure_one()
        plans = self.sudo().rvt_trade_plan_ids.filtered(lambda p: p.agency_id == agency)
        return plans.contact_ids or self.env["res.partner"].sudo().search([("parent_id", "=", agency.id)], order="id", limit=1)

    def rvt_remind(self, text, agency_id=None, client=False):
        """A short message for one item, on a staff member's tap. Nothing is chased by itself."""
        self.ensure_one()
        self._rvt_check_staff()
        self.check_access("read")
        text = (text or "").strip()
        if not text:
            raise UserError(self.env._("Say what the reminder is about."))
        project = self.sudo()
        if client:
            people = project.rvt_client_contact_ids
        else:
            agency = self.env["res.partner"].sudo().browse(agency_id).exists()
            if not agency or agency not in project.rvt_agency_ids:
                raise UserError(self.env._("That agency is not on this project."))
            people = project._rvt_people_of(agency)
        if not people:
            raise UserError(self.env._("There is nobody with a number to remind."))
        return self.env["rvt.notify"].send("remind", self, people, text=text)

    def rvt_invite(self, agency_ids=None, client_contact_ids=None):
        """Invite people to open the app with their number: an agency's contact people on this
        project, or client contacts. Returns how many people were invited."""
        self.ensure_one()
        self._rvt_check_staff()
        self.check_access("read")
        project = self.sudo()
        Partner = self.env["res.partner"].sudo()
        people = Partner
        for agency in Partner.browse(agency_ids or []).exists() & project.rvt_agency_ids:
            people |= project._rvt_people_of(agency)
        people |= Partner.browse(client_contact_ids or []).exists() & project.rvt_client_contact_ids
        if not people:
            return 0
        self.env["rvt.notify"].send("invite", self, people)
        people.write({"rvt_invited_on": fields.Datetime.now()})
        return len(people)

    def _rvt_onboard_extra(self, vals, result):
        """Onboarding step 6: invite whoever was ticked."""
        super()._rvt_onboard_extra(vals, result)
        invite = vals.get("invite") or {}
        result["invited"] = 0
        if invite.get("agency_ids") or invite.get("client"):
            contacts = self.rvt_client_contact_ids[:1].ids if invite.get("client") else []
            result["invited"] = self.rvt_invite(invite.get("agency_ids") or [], contacts)
