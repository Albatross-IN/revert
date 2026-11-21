from odoo.exceptions import AccessError
from odoo.tests import new_test_user, tagged

from .common import RvtCommon


@tagged("post_install", "-at_install")
class TestAccess(RvtCommon):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.project, _ = cls.onboard()
        cls.plain = cls.Project.create({"name": "Patel Bungalow"})
        cls.plain_task = cls.env["project.task"].create({"name": "Drawing room", "project_id": cls.plain.id})

    def seen(self, user):
        return self.Project.with_user(user).search([("id", "in", (self.project | self.plain).ids)])

    def test_staff_see_by_team(self):
        both = self.project | self.plain
        self.assertEqual(self.seen(self.owner), both)
        self.assertEqual(self.seen(self.principal), both)
        self.assertEqual(self.seen(self.designer), both, "a designer on the team")
        self.assertEqual(self.seen(self.coordinator), both)
        self.assertEqual(self.seen(self.outsider), self.plain, "not on the team: only what is not onboarded yet")

    def test_project_administrators_are_narrowed_too(self):
        # today every Revert user is a project administrator; the team rule still applies
        admin_like = new_test_user(
            self.env, "t_admin_like", groups="rvt_base.group_rvt_designer,project.group_project_manager")
        self.assertEqual(self.seen(admin_like), self.plain)
        self.project.rvt_designer_ids = [(4, admin_like.id)]
        self.assertEqual(self.seen(admin_like), self.project | self.plain)

    def test_tasks_follow_the_project(self):
        Task = self.env["project.task"]
        domain = [("project_id", "in", (self.project | self.plain).ids)]
        mine = Task.with_user(self.designer).search(domain)
        self.assertIn(self.plain_task, mine)
        self.assertTrue(mine.filtered(lambda t: t.project_id == self.project))
        theirs = Task.with_user(self.outsider).search(domain)
        self.assertEqual(theirs, self.plain_task)
        line = self.line(self.project, "Kitchen", "carp")
        with self.assertRaises(AccessError):
            line.with_user(self.outsider).rvt_set_state("working")
        line.with_user(self.designer).rvt_set_state("working")
        self.assertEqual(line.rvt_work_state, "working")
        with self.assertRaises(AccessError):
            self.project.with_user(self.outsider).rvt_grid()
        with self.assertRaises(AccessError):
            self.project.with_user(self.outsider).rvt_onboard_state()

    def test_trade_plan_follows_the_project(self):
        Plan = self.env["rvt.project.trade"]
        self.assertEqual(len(Plan.with_user(self.designer).search([("project_id", "=", self.project.id)])), 6)
        self.assertFalse(Plan.with_user(self.outsider).search([("project_id", "=", self.project.id)]))
        plan = self.project.rvt_trade_plan_ids.filtered(lambda p: p.trade_id.code == "col")
        with self.assertRaises(AccessError):
            plan.with_user(self.outsider).write({"note": "x"})
        plan.with_user(self.coordinator).write({"agency_id": self.ag_pop.id})
        self.assertEqual(plan.agency_id, self.ag_pop)

    def test_joining_and_leaving_the_team(self):
        self.Project.with_user(self.coordinator).rvt_onboard({
            "project_id": self.project.id, "designer_ids": [self.designer.id, self.outsider.id]})
        self.assertIn(self.project, self.seen(self.outsider))
        self.assertNotIn(self.project, self.seen(self.designer2), "taken off the team: the project goes from view")

    def test_agency_sees_its_slice(self):
        Task = self.env["project.task"]
        carp_user, elec_user = self.agency_user, self.other_agency_user
        self.assertEqual(self.seen(carp_user), self.project)
        self.assertEqual(self.seen(elec_user), self.project)
        lines = Task.with_user(carp_user).search([("project_id", "=", self.project.id), ("rvt_kind", "=", "work")])
        self.assertTrue(lines)
        self.assertEqual(lines.sudo().mapped("rvt_agency_id"), self.ag_carp, "only its own lines")
        rooms = Task.with_user(carp_user).search([("project_id", "=", self.project.id), ("rvt_kind", "=", "entity")])
        self.assertIn("Kitchen", rooms.mapped("name"))
        self.assertNotIn("Toilet 1", rooms.mapped("name"), "no carpentry in the toilet, so it is not shown")
        self.assertFalse(Task.with_user(carp_user).search([("id", "=", self.plain_task.id)]))
        elec_line = self.line(self.project, "Kitchen", "elec")
        with self.assertRaises(AccessError):
            elec_line.with_user(carp_user).read(["name"])
        with self.assertRaises(AccessError):
            lines[0].with_user(carp_user).write({"rvt_work_state": "done"})
        plan = self.env["rvt.project.trade"].with_user(carp_user).search([("project_id", "=", self.project.id)])
        self.assertEqual(plan.sudo().trade_id.code, "carp")
        # an agency that is on no trade of the project sees nothing
        stranger = new_test_user(self.env, "t_agency3", groups="rvt_base.group_rvt_agency")
        stranger.partner_id.parent_id = self.ag_carp2
        self.assertFalse(self.seen(stranger))
        self.assertFalse(Task.with_user(stranger).search([("project_id", "=", self.project.id)]))
        # until it is given one line
        self.line(self.project, "Kitchen", "carp").rvt_agency_id = self.ag_carp2
        self.assertEqual(self.seen(stranger), self.project)
        self.assertEqual(
            Task.with_user(stranger).search([("project_id", "=", self.project.id), ("rvt_kind", "=", "work")]).parent_id.name,
            "Kitchen")

    def test_client_sees_its_project_only(self):
        contact = self.project.rvt_client_contact_ids
        stranger = new_test_user(self.env, "t_client_other", groups="rvt_base.group_rvt_client")
        self.assertFalse(self.seen(stranger))
        client_user = new_test_user(self.env, "t_client", groups="rvt_base.group_rvt_client", partner_id=contact.id)
        self.assertEqual(self.seen(client_user), self.project)
        self.assertFalse(self.env["project.task"].with_user(client_user).search([("project_id", "=", self.project.id)]),
                         "a client sees no tasks")
        with self.assertRaises(AccessError):
            self.env["rvt.project.trade"].with_user(client_user).search([])
