from odoo import fields
from odoo.exceptions import AccessError, UserError
from odoo.tests import tagged

from odoo.addons.rvt_project.tests.common import RvtCommon


@tagged("post_install", "-at_install")
class TestDesk(RvtCommon):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.project, _ = cls.onboard()
        cls.plain = cls.Project.create({"name": "Patel Bungalow"})
        Task = cls.env["project.task"]
        cls.room_task = Task.create({"name": "Drawing room", "project_id": cls.plain.id, "user_ids": [(6, 0, cls.coordinator.ids)]})
        Task.create({"name": "Furniture work", "project_id": cls.plain.id, "parent_id": cls.room_task.id})
        cls.Desk = cls.env["rvt.desk"]

    def snap(self, user=None):
        return self.Desk.with_user(user or self.coordinator).snapshot()

    def row(self, snapshot, project=None):
        return next(p for p in snapshot["projects"] if p["id"] == (project or self.project).id)

    def op(self, name, args, user=None):
        return self.Desk.with_user(user or self.coordinator).op(name, args)

    # ---- snapshot -----------------------------------------------------
    def test_snapshot_shape(self):
        snap = self.snap()
        self.assertEqual(snap["me"], "s%s" % self.coordinator.id)
        self.assertEqual(snap["today_date"], fields.Date.to_string(self.today))
        self.assertEqual(snap["set"]["lim"], {"open": 2, "q": 1, "bill": 3, "stuck": 7})
        masters = snap["masters"]
        self.assertEqual(len(masters["trades"]), 15)
        carp = next(t for t in masters["trades"] if t["id"] == "carp")
        self.assertEqual((carp["n"], carp["s"], carp["gu"], carp["hi"]), ("Carpenter", "Carp", "સુથાર", "बढ़ई"))
        self.assertEqual(set(masters["default_trades"]), {"civ", "tile", "elec", "plmb", "pop", "carp", "col"})
        bhk = next(p for p in masters["presets"] if p["n"] == "3 BHK")
        self.assertIn(["Bedroom", 2, 2], bhk["e"])
        me = next(u for u in snap["staff"] if u["id"] == snap["me"])
        self.assertEqual((me["n"], me["full"], me["roles"]), ("Meera", "Meera Joshi", ["coordinator"]))
        principal = next(u for u in snap["staff"] if u["id"] == "s%s" % self.principal.id)
        self.assertEqual((principal["n"], principal["roles"]), ("Pranav", ["owner", "principal"]))
        agency = next(a for a in snap["agencies"] if a["n"] == "Jay Electric")
        self.assertEqual(agency["tr"], ["elec"])
        self.assertEqual([p["n"] for p in agency["people"]][:2], ["Jaybhai Solanki", "Vipul (site)"])

    def test_project_row(self):
        p = self.row(self.snap())
        self.assertTrue(p["onb"])
        self.assertEqual((p["name"], p["label"], p["area"], p["kind"]), ("Shah Residence", "3 BHK + garden", "Bopal", "home"))
        self.assertEqual(p["client"]["n"], "Mr. Nirav Shah")
        self.assertEqual(p["client"]["contacts"][0]["n"], "Nirav Shah")
        self.assertEqual(p["principal"], "s%s" % self.principal.id)
        self.assertEqual(p["coords"], ["s%s" % self.coordinator.id])
        self.assertEqual(p["onbOn"], 0)
        self.assertEqual(len(p["ents"]), 13)
        self.assertEqual(p["ents"][-1]["n"], "Whole site")
        plan = {x["t"]: x for x in p["plan"]}
        self.assertEqual(plan["carp"]["ag"], "a%s" % self.ag_carp.id)
        self.assertEqual(plan["carp"]["people"], [0], "the first contact person, by position in the agency's people")
        self.assertIsNone(plan["plmb"]["ag"])
        self.assertEqual(plan["plmb"]["by"], -6)
        self.assertEqual(plan["col"]["by"], 7)
        line = next(l for l in p["lines"] if l["t"] == "carp")
        self.assertEqual((line["st"], line["ag"], line["cause"]), ("ns", None, None))
        self.assertTrue(line["e"].startswith("e"))
        # the picture, in the screen's shape
        pic = p["pic"]
        self.assertEqual(pic["status"], "stuck")
        self.assertEqual(pic["progress"]["ag"], [4, 6])
        b1 = pic["blockers"][0]
        self.assertEqual((b1["k"], b1["crit"], b1["age"]), ("B1", True, 6))
        self.assertEqual(b1["act"], ["assign", "%s|plmb" % self.project.id, "Assign"])
        self.assertEqual(b1["who"], ["s%s" % self.coordinator.id])
        self.assertEqual(len(pic["next"]["revert"]), 2)
        self.assertEqual(len(pic["next"]["agencies"]), 4)

    def test_not_onboarded_project_and_tasks(self):
        snap = self.snap()
        p = self.row(snap, self.plain)
        self.assertFalse(p["onb"])
        self.assertNotIn("pic", p)
        self.assertEqual(p["tasks"], [{"id": self.room_task.id, "n": "Drawing room", "stage": p["tasks"][0]["stage"], "subs": 1, "mom": 0, "moved": False}])
        self.assertEqual([t["n"] for t in snap["mytasks"]], ["Drawing room"])
        self.assertEqual(snap["mytasks"][0]["p"], "Patel Bungalow")

    def test_today_and_visibility(self):
        snap = self.snap()
        mine = [i for i in snap["today"] if i["pid"] == self.project.id]
        self.assertEqual(sorted(i["sec"] for i in mine), ["decide", "decide"])
        self.assertEqual(mine[0]["pname"], "Shah Residence")
        self.assertEqual(mine[0]["act"][0], "assign")
        outsider = self.snap(self.outsider)
        self.assertNotIn(self.project.id, [p["id"] for p in outsider["projects"]])
        self.assertIn(self.plain.id, [p["id"] for p in outsider["projects"]])
        with self.assertRaises(AccessError):
            self.snap(self.agency_user)
        with self.assertRaises(AccessError):
            self.op("assign", {}, self.agency_user)

    def test_waiting_line_in_snapshot(self):
        line = self.line(self.project, "Living room", "col")
        self.op("set_line", {"line": "l%s" % line.id, "state": "wait", "cause": "trade", "ref": "carp", "note": ""})
        line.rvt_wait_since = self.days(-3)
        row = next(l for l in self.row(self.snap())["lines"] if l["id"] == "l%s" % line.id)
        self.assertEqual((row["st"], row["cause"], row["ref"], row["since"]), ("wait", "trade", "carp", 3))

    # ---- operations ---------------------------------------------------
    def test_op_set_line(self):
        line = self.line(self.project, "Kitchen", "carp")
        ref = "l%s" % line.id
        self.op("set_line", {"line": ref, "state": "work", "cause": "", "ref": "", "note": "", "agency": ""})
        self.assertEqual(line.rvt_work_state, "working")
        self.assertEqual(line.rvt_agency_id, self.ag_carp)
        self.op("set_line", {"line": ref, "state": "wait", "cause": "material", "note": "Laminate awaited", "agency": "a%s" % self.ag_carp2.id})
        self.assertEqual((line.rvt_work_state, line.rvt_wait_cause, line.rvt_wait_note), ("waiting", "material", "Laminate awaited"))
        self.assertEqual(line.rvt_agency_id, self.ag_carp2, "a second carpenter for this line only")
        row = next(l for l in self.row(self.snap())["lines"] if l["id"] == ref)
        self.assertEqual(row["ag"], "a%s" % self.ag_carp2.id)
        self.op("set_line", {"line": ref, "state": "done", "agency": ""})
        self.assertEqual(line.rvt_work_state, "done")
        self.assertEqual(line.rvt_agency_id, self.ag_carp, "back to the plan's agency")
        with self.assertRaises(UserError):
            self.op("set_line", {"line": ref, "state": "paused"})
        with self.assertRaises(UserError):
            self.op("set_line", {"line": "l0", "state": "work"})
        with self.assertRaises(AccessError):
            self.op("set_line", {"line": ref, "state": "work"}, self.outsider)

    def test_op_assign(self):
        self.op("assign", {"project": self.project.id, "trade": "plmb", "agency": "a%s" % self.ag_civil.id})
        plan = self.project.rvt_trade_plan_ids.filtered(lambda p: p.trade_id.code == "plmb")
        self.assertEqual(plan.agency_id, self.ag_civil)
        self.assertEqual(plan.contact_ids.name, "Rameshbhai Prajapati")
        self.assertEqual(self.line(self.project, "Kitchen", "plmb").rvt_agency_id, self.ag_civil)
        self.op("assign", {"project": self.project.id, "trade": "plmb", "agency": "", "by": 14})
        self.assertFalse(plan.agency_id)
        self.assertEqual(plan.decide_by, self.days(14))
        with self.assertRaises(AccessError):
            self.op("assign", {"project": self.project.id, "trade": "plmb", "agency": ""}, self.outsider)

    def test_op_onboard_from_the_wizard(self):
        s = lambda user: "s%s" % user.id
        result = self.op("onboard", {
            "pid": "", "name": "Desai Dental Clinic", "client": "Dr. Rupal Desai", "cphone": "98980 44021",
            "address": "FF-12, Shivalik Arcade", "area": "Satellite", "kind": "clinic", "label": "Clinic · 2 chairs", "billedTo": "revert",
            "principal": s(self.principal), "designers": [s(self.designer)], "coords": [s(self.coordinator)],
            "ents": [{"u": 1, "n": "Consulting room 1", "ty": "Consulting room", "id": ""},
                     {"u": 2, "n": "Reception", "ty": "Reception / waiting", "id": ""},
                     {"u": 3, "n": "Whole site", "ty": "Whole site", "id": ""}],
            "tr": {"elec": {"on": True, "ag": "a%s" % self.ag_elec.id, "by": 7},
                   "carp": {"on": True, "ag": "", "by": 14},
                   "pop": {"on": False, "ag": "", "by": 7}},
            "ticks": [["1", "elec"], ["1", "carp"], ["2", "carp"], ["3", "elec"], ["1", "pop"]],
        })
        self.assertTrue(result["new"])
        self.assertEqual(result["nl"], 4, "a tick for a trade that is not on the project is ignored")
        project = self.Project.browse(result["pid"])
        self.assertEqual((project.rvt_site_kind, project.rvt_billed_to_default, project.rvt_site_area), ("clinic", "revert", "Satellite"))
        self.assertEqual(project.rvt_entity_ids.mapped("name"), ["Consulting room 1", "Reception", "Whole site"])
        self.assertEqual(project.rvt_entity_ids[0].rvt_entity_type_id.name, "Consulting room")
        plan = {p.trade_id.code: p for p in project.rvt_trade_plan_ids}
        self.assertEqual(set(plan), {"elec", "carp"})
        self.assertEqual(plan["carp"].decide_by, self.days(14))
        self.assertFalse(self.line(project, "Reception", "elec"))
        self.assertTrue(self.line(project, "Reception", "carp"))
        # project configuration: the same payload with the project's id and one more tick
        state = self.row(self.snap(), project)
        again = self.op("onboard", {
            "pid": project.id, "name": "Desai Dental Clinic", "client": "Dr. Rupal Desai", "cphone": "98980 44021",
            "kind": "clinic", "label": "Clinic · 2 chairs", "billedTo": "revert",
            "principal": s(self.principal), "designers": [s(self.designer)], "coords": [s(self.coordinator)],
            "ents": [{"u": i + 1, "n": e["n"], "ty": e["ty"], "id": e["id"]} for i, e in enumerate(state["ents"])],
            "tr": {"elec": {"on": True, "ag": "a%s" % self.ag_elec.id, "by": 7}, "carp": {"on": True, "ag": "", "by": 14}},
            "ticks": [["1", "elec"], ["1", "carp"], ["2", "carp"], ["3", "elec"], ["2", "elec"]],
        })
        self.assertFalse(again["new"])
        self.assertEqual(again["nl"], 1)
        self.assertEqual(len(project.rvt_entity_ids), 3)

    def test_op_task_entity(self):
        self.op("task_entity", {"task": self.room_task.id, "type": "Living room"})
        self.assertEqual(self.room_task.rvt_kind, "entity")
        self.assertEqual(self.room_task.rvt_entity_type_id.name, "Living room")
        row = self.row(self.snap(), self.plain)
        self.assertFalse(row["tasks"], "it is a room now, no longer an earlier task")

    def test_setup_is_for_owners(self):
        with self.assertRaises(AccessError):
            self.op("setting", {"key": "approval", "value": False})
        with self.assertRaises(AccessError):
            self.op("limit", {"key": "stuck", "value": 9})
        with self.assertRaises(AccessError):
            self.op("role", {"user": "s%s" % self.designer.id, "role": "coordinator"})
        self.op("setting", {"key": "approval", "value": False}, self.owner)
        self.op("limit", {"key": "stuck", "value": 9}, self.owner)
        snap = self.snap()
        self.assertFalse(snap["set"]["approval"])
        self.assertEqual(snap["set"]["lim"]["stuck"], 9)
        self.op("role", {"user": "s%s" % self.designer.id, "role": "coordinator"}, self.owner)
        self.assertEqual(self.designer.rvt_roles(), ["designer", "coordinator"])
        self.op("role", {"user": "s%s" % self.designer.id, "role": "designer"}, self.owner)
        self.assertEqual(self.designer.rvt_roles(), ["coordinator"])
        with self.assertRaises(UserError):
            self.op("role", {"user": "s%s" % self.owner.id, "role": "owner"}, self.owner)

    def test_master_lists_from_setup(self):
        toilet = self.env.ref("rvt_base.entity_type_toilet")
        self.assertNotIn("carp", toilet.trade_ids.mapped("code"))
        self.op("etype_trade", {"type": "Toilet", "trade": "carp"}, self.owner)
        self.assertIn("carp", toilet.trade_ids.mapped("code"))
        self.op("etype_trade", {"type": "Toilet", "trade": "carp"}, self.owner)
        self.assertNotIn("carp", toilet.trade_ids.mapped("code"))
        result = self.op("add_trade", {"name": "Modular kitchen", "gu": "મોડ્યુલર કિચન", "hi": ""}, self.owner)
        trade = self.env["rvt.trade"].search([("code", "=", result["id"])])
        self.assertEqual(trade.name, "Modular kitchen")
        self.assertEqual(trade.with_context(lang="gu_IN").name, "મોડ્યુલર કિચન")
        self.assertEqual(trade.with_context(lang="hi_IN").name, "Modular kitchen", "no Hindi given: the English name shows")
        result = self.op("add_agency", {"name": "Aqua Plumbing", "trades": ["plmb"], "lang": "hi", "person": "Sanjay Yadav", "phone": "99090 77451"})
        agency = self.env["res.partner"].browse(int(result["id"][1:]))
        self.assertTrue(agency.rvt_is_agency)
        self.assertEqual((agency.rvt_trade_ids.code, agency.lang), ("plmb", "hi_IN"))
        self.assertEqual(agency.child_ids.phone, "99090 77451")
        fl = self.env.ref("rvt_base.drawing_type_dm")
        self.assertTrue(fl.for_client)
        self.op("dtype_flag", {"id": fl.id, "flag": "appr"}, self.owner)
        self.assertTrue(fl.needs_client_approval)
        self.op("dtype_flag", {"id": fl.id, "flag": "client"}, self.owner)
        self.assertFalse(fl.for_client)
        self.assertFalse(fl.needs_client_approval, "not for the client, so nothing for the client to approve")
        with self.assertRaises(UserError):
            self.op("no_such_thing", {})

    # ---- one window ---------------------------------------------------
    def test_staff_see_only_the_revert_menu(self):
        Menu = self.env["ir.ui.menu"]
        revert = self.env.ref("rvt_base.menu_rvt_root")
        self.assertEqual(Menu.with_user(self.designer).get_user_roots(), revert)
        loaded = Menu.with_user(self.designer).load_menus(False)
        self.assertEqual(loaded["root"]["children"], [revert.id])
        admin = self.env.ref("base.user_admin")
        self.assertGreater(len(Menu.with_user(admin).get_user_roots()), 1, "administrators keep every menu")
        self.env["ir.config_parameter"].sudo().set_bool("rvt.desk_only", False)
        self.assertGreater(len(Menu.with_user(self.designer).get_user_roots()), 1, "the setting switches it off")
