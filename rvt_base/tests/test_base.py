from odoo.exceptions import AccessError
from odoo.tests import TransactionCase, new_test_user, tagged
from odoo.tools import mute_logger


@tagged("post_install", "-at_install")
class TestRvtBase(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.owner = new_test_user(cls.env, "rvt_owner", groups="rvt_base.group_rvt_owner")
        cls.principal = new_test_user(cls.env, "rvt_principal", groups="rvt_base.group_rvt_principal")
        cls.designer = new_test_user(cls.env, "rvt_designer", groups="rvt_base.group_rvt_designer")
        cls.coordinator = new_test_user(cls.env, "rvt_coord", groups="rvt_base.group_rvt_coordinator")
        cls.agency_user = new_test_user(cls.env, "rvt_agency", groups="rvt_base.group_rvt_agency")

    # ---- master lists -------------------------------------------------
    def test_master_lists_loaded(self):
        env = self.env
        self.assertEqual(env["rvt.trade"].search_count([]), 15)
        self.assertEqual(env["rvt.drawing.type"].search_count([]), 29)
        self.assertEqual(env["rvt.drawing.type"].search_count([("trade_id", "=", False)]), 5, "general set")
        self.assertEqual(env["rvt.site.preset"].search_count([]), 7)
        whole = env["rvt.entity.type"].search([("is_whole_site", "=", True)])
        self.assertEqual(len(whole), 1)
        toilet = env.ref("rvt_base.entity_type_toilet")
        self.assertEqual(
            set(toilet.trade_ids.mapped("code")),
            {"civ", "tile", "stone", "elec", "plmb", "pop", "alu"})

    def test_trade_names_in_gujarati_and_hindi(self):
        langs = dict(self.env["res.lang"].get_installed())
        self.assertIn("gu_IN", langs)
        self.assertIn("hi_IN", langs)
        carp = self.env.ref("rvt_base.trade_carp")
        self.assertEqual(carp.name, "Carpenter")
        self.assertEqual(carp.with_context(lang="gu_IN").name, "સુથાર")
        self.assertEqual(carp.with_context(lang="hi_IN").name, "बढ़ई")

    def test_preset_entities(self):
        preset = self.env.ref("rvt_base.preset_3bhk")
        ents = preset.rvt_entities()
        names = [e["name"] for e in ents]
        self.assertEqual(len(ents), 13, "12 rooms and the whole site")
        self.assertIn("Master bedroom", names)
        self.assertIn("Bedroom 2", names)
        self.assertIn("Bedroom 3", names)
        self.assertNotIn("Bedroom 1", names, "the master bedroom is the first")
        self.assertIn("Toilet 3", names)
        self.assertIn("Kitchen", names)
        self.assertEqual(names[-1], "Whole site")
        kitchen = next(e for e in ents if e["name"] == "Kitchen")
        self.assertIn(self.env.ref("rvt_base.trade_plmb").id, kitchen["trade_ids"])
        empty = self.env.ref("rvt_base.preset_empty").rvt_entities()
        self.assertEqual([e["name"] for e in empty], ["Whole site"])

    @mute_logger("odoo.sql_db")
    def test_unique_codes(self):
        with self.assertRaises(Exception), self.cr.savepoint():
            self.env["rvt.trade"].create({"name": "Second civil", "short_name": "Civ2", "code": "civ"})
        with self.assertRaises(Exception), self.cr.savepoint():
            self.env["rvt.drawing.type"].create({"name": "Another", "code": "EL"})

    # ---- roles --------------------------------------------------------
    def test_role_ladder(self):
        self.assertEqual(self.owner.rvt_roles(), ["owner"])
        self.assertTrue(self.owner.has_group("rvt_base.group_rvt_principal"), "an owner may do what the principal does")
        self.assertEqual(self.principal.rvt_roles(), ["principal"])
        self.assertEqual(self.designer.rvt_roles(), ["designer"])
        self.assertTrue(self.designer.has_group("rvt_base.group_rvt_staff"))
        self.assertTrue(self.coordinator.has_group("rvt_base.group_rvt_staff"))
        self.assertFalse(self.designer.has_group("rvt_base.group_rvt_principal"))
        self.assertEqual(self.agency_user.rvt_roles(), ["agency"])
        self.assertFalse(self.agency_user.has_group("base.group_user"))

    def test_set_roles(self):
        user = new_test_user(self.env, "rvt_plain", groups="base.group_user")
        user.rvt_set_roles(["designer", "coordinator"])
        self.assertEqual(user.rvt_roles(), ["designer", "coordinator"])
        user.rvt_set_roles(["owner"])
        self.assertEqual(user.rvt_roles(), ["owner"])
        user.rvt_set_roles(["owner", "principal"])
        self.assertEqual(user.rvt_roles(), ["owner", "principal"])
        user.rvt_set_roles([])
        self.assertEqual(user.rvt_roles(), [])
        self.assertFalse(user.has_group("rvt_base.group_rvt_staff"))
        with self.assertRaises(ValueError):
            user.rvt_set_roles(["agency"])

    # ---- access -------------------------------------------------------
    def test_master_list_access(self):
        Trade = self.env["rvt.trade"]
        self.assertTrue(Trade.with_user(self.designer).search([]))
        self.assertTrue(Trade.with_user(self.agency_user).search([]), "an agency reads trade names")
        with self.assertRaises(AccessError):
            Trade.with_user(self.designer).create({"name": "Lift", "short_name": "Lift", "code": "lift"})
        with self.assertRaises(AccessError):
            self.env["rvt.entity.type"].with_user(self.agency_user).search([])
        trade = Trade.with_user(self.owner).create({"name": "Lift", "short_name": "Lift", "code": "lift"})
        etype = self.env["rvt.entity.type"].with_user(self.owner).create({
            "name": "Lift lobby", "site_kind": "other", "trade_ids": [(6, 0, trade.ids)]})
        preset = self.env["rvt.site.preset"].with_user(self.owner).create({
            "name": "Lobby only", "site_kind": "other",
            "line_ids": [(0, 0, {"entity_type_id": etype.id, "count": 2})]})
        self.assertEqual([e["name"] for e in preset.rvt_entities()], ["Lift lobby 1", "Lift lobby 2", "Whole site"])
        self.env["rvt.drawing.type"].with_user(self.owner).create({"name": "Lift details", "code": "LF", "trade_id": trade.id})

    # ---- settings -----------------------------------------------------
    def test_settings_defaults_and_change(self):
        config = self.env["rvt.config"].with_user(self.designer)
        self.assertEqual(config.get(), {
            "release_needs_approval": True,
            "client_points_need_confirmation": True,
            "limit_not_opened_days": 2,
            "limit_question_days": 1,
            "limit_bill_review_days": 3,
            "limit_stuck_days": 7,
        })
        settings = self.env["res.config.settings"].create({
            "rvt_release_needs_approval": False, "rvt_limit_stuck_days": 10})
        settings.execute()
        self.assertFalse(config.get("release_needs_approval"), "an unticked setting must read back as off")
        self.assertTrue(config.get("client_points_need_confirmation"))
        self.assertEqual(config.get("limit_stuck_days"), 10)

    # ---- agencies -----------------------------------------------------
    def test_agency_partner(self):
        agency = self.env["res.partner"].create({
            "name": "Mahadev Furniture", "rvt_is_agency": True,
            "rvt_trade_ids": [(6, 0, self.env.ref("rvt_base.trade_carp").ids)]})
        person = self.env["res.partner"].create({"name": "Bherubhai", "parent_id": agency.id, "phone": "+91 98244 18830"})
        self.assertEqual(agency.rvt_trade_ids.code, "carp")
        self.assertEqual(person.commercial_partner_id, agency)

    # ---- live screens ---------------------------------------------------
    def test_open_screens_are_told_once_per_change(self):
        Live = self.env["rvt.live"]
        info = Live.info()
        self.assertTrue(info["ch"].startswith("rvt_live_") and len(info["ch"]) == 41, "a name nobody can guess")
        self.assertEqual(info["ch"], Live.channel(), "the same name every time")
        self.assertTrue(info["v"])
        self.env.cr.precommit.data.pop("rvt.live", None)
        before = self.env["bus.bus"].sudo()._bus_last_id()
        Live.touch()
        Live.touch()
        self.assertTrue(self.env.cr.precommit.data.get("rvt.live"), "a second change in the same step asks nothing more")
        self.env.cr.precommit.run()
        self.assertEqual(self.env["bus.bus"].sudo()._bus_last_id() - before, 1, "one message, however many changes")
        self.env.cr.precommit.data.pop("rvt.live", None)
        Live.with_context(rvt_quiet=True).touch()
        self.assertFalse(self.env.cr.precommit.data.get("rvt.live"), "a quiet change tells nobody")

    # ---- photos on their way to a screen ----------------------------------
    def test_a_list_gets_a_small_copy_of_a_photo(self):
        import base64
        import io

        from PIL import Image

        from odoo.addons.rvt_base.photos import sized

        big = io.BytesIO()
        Image.new("RGB", (3000, 2000), (120, 90, 60)).save(big, "JPEG", quality=95)
        photo = big.getvalue()
        thumb, view = sized(photo, "thumb"), sized(photo, "view")
        self.assertEqual(Image.open(io.BytesIO(thumb)).size, (480, 320))
        self.assertEqual(Image.open(io.BytesIO(view)).size, (1600, 1067))
        self.assertLess(len(thumb), len(view))
        self.assertIs(sized(photo), photo, "without a size the photo travels as it was taken")
        self.assertIs(sized(photo, "huge"), photo)
        pdf = base64.b64decode("JVBERi0xLjQK")
        self.assertEqual(sized(pdf, "thumb"), pdf, "what is not an image travels as it is")
