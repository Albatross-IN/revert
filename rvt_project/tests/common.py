from datetime import timedelta

from odoo import fields
from odoo.tests import TransactionCase, new_test_user


class RvtCommon(TransactionCase):
    """People, agencies and one onboarded 3 BHK, shared by the Revert test suites.
    Invented names only."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        env = cls.env
        cls.today = env["rvt.config"].today()
        cls.days = staticmethod(lambda n: cls.today + timedelta(days=n))
        user = lambda login, groups, name: new_test_user(env, login, groups=groups, name=name)
        cls.owner = user("t_owner", "rvt_base.group_rvt_owner", "Parul Vora")
        cls.principal = user("t_principal", "rvt_base.group_rvt_owner,rvt_base.group_rvt_principal", "Ar. Pranav Vora")
        cls.coordinator = user("t_coord", "rvt_base.group_rvt_coordinator", "Meera Joshi")
        cls.designer = user("t_designer", "rvt_base.group_rvt_designer", "Riya Trivedi")
        cls.designer2 = user("t_designer2", "rvt_base.group_rvt_designer", "Amit Parmar")
        cls.outsider = user("t_outsider", "rvt_base.group_rvt_designer", "Kiran Dave")
        # The suites' coordinator also sets projects up, handles bills and sees every project: ticked by hand, as an
        # owner may do for a coordinator. The roles' own ticks are tested on people of their own (test_access_ticks).
        ref = env.ref
        cls.coordinator.write({"group_ids": [(4, ref("rvt_base.group_rvt_acc_%s" % key).id) for key in ("projects", "bills", "allprojects")]})

        cls.trade = {t.code: t for t in env["rvt.trade"].search([])}
        Partner = env["res.partner"]

        def agency(name, codes, people):
            firm = Partner.create({
                "name": name, "rvt_is_agency": True,
                "rvt_trade_ids": [(6, 0, [cls.trade[c].id for c in codes])]})
            for person, phone in people:
                Partner.create({"name": person, "phone": phone, "parent_id": firm.id})
            return firm

        cls.ag_civil = agency("Ramesh Construction", ["civ", "tile"], [("Rameshbhai Prajapati", "+91 98250 41120")])
        cls.ag_elec = agency("Jay Electric", ["elec"], [("Jaybhai Solanki", "+91 98790 22014"), ("Vipul (site)", "+91 97250 60318")])
        cls.ag_carp = agency("Mahadev Furniture", ["carp"], [("Bherubhai Suthar", "+91 98244 18830")])
        cls.ag_carp2 = agency("Shree Wood Works", ["carp"], [("Mukesh Mistry", "+91 96620 51177")])
        cls.ag_pop = agency("Shree POP", ["pop"], [("Rajkumar Sharma", "+91 98980 30092")])

        cls.agency_user = new_test_user(
            env, "t_agency", groups="rvt_base.group_rvt_agency", name="Bherubhai Suthar (app)")
        cls.agency_user.partner_id.parent_id = cls.ag_carp
        cls.other_agency_user = new_test_user(
            env, "t_agency2", groups="rvt_base.group_rvt_agency", name="Jaybhai Solanki (app)")
        cls.other_agency_user.partner_id.parent_id = cls.ag_elec

        cls.Project = env["project.project"]
        cls.preset_3bhk = env.ref("rvt_base.preset_3bhk")
        # a client is one card per mobile number. A copy of a live database may hold a card with the
        # number of these fixtures' client; inside the test it gives the number up.
        digits = lambda phone: "".join(c for c in phone or "" if c.isdigit())[-10:]
        Partner.with_context(active_test=False).search([("phone", "like", "700")]).filtered(
            lambda p: digits(p.phone).startswith("98250700")).write({"phone": False})

    @classmethod
    def onboard_vals(cls, **extra):
        proposal = cls.Project.with_user(cls.coordinator).rvt_onboard_proposal(cls.preset_3bhk.id)
        t = cls.trade
        vals = {
            "name": "Shah Residence",
            "client_name": "Mr. Nirav Shah", "client_phone": "+91 98250 70011",
            "site_area": "Bopal", "site_address": "B-204, Sun Sky Park, Bopal, Ahmedabad",
            "site_kind": "home", "site_label": "3 BHK + garden", "billed_to": "client",
            "principal_id": cls.principal.id,
            "designer_ids": [cls.designer.id, cls.designer2.id],
            "coordinator_ids": [cls.coordinator.id],
            "entities": [dict(e, key="n%s" % i) for i, e in enumerate(proposal["entities"])],
            "trades": [
                {"trade_id": t["civ"].id, "agency_id": cls.ag_civil.id},
                {"trade_id": t["elec"].id, "agency_id": cls.ag_elec.id},
                {"trade_id": t["plmb"].id, "agency_id": False, "decide_by": fields.Date.to_string(cls.days(-6))},
                {"trade_id": t["pop"].id, "agency_id": cls.ag_pop.id},
                {"trade_id": t["carp"].id, "agency_id": cls.ag_carp.id},
                {"trade_id": t["col"].id, "agency_id": False},
            ],
        }
        vals.update(extra)
        return vals

    @classmethod
    def onboard(cls, user=None, **extra):
        result = cls.Project.with_user(user or cls.coordinator).rvt_onboard(cls.onboard_vals(**extra))
        return cls.Project.browse(result["project_id"]), result

    def line(self, project, entity_name, code):
        return self.env["project.task"].search([
            ("project_id", "=", project.id), ("rvt_kind", "=", "work"),
            ("parent_id.name", "=", entity_name), ("rvt_trade_id", "=", self.trade[code].id)])
