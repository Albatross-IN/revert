# -*- coding: utf-8 -*-
from odoo.tests import HttpCase, tagged

from ..models.res_config_settings import PARAM


@tagged("post_install", "-at_install")
class TestGlassLogin(HttpCase):
    """The sign-in page is a frontend page: it carries the theme scope while
    the theme is enabled, and nothing of it when the theme is switched off."""

    def test_login_page_scoped_while_enabled(self):
        self.env["ir.config_parameter"].sudo().set_bool(PARAM, True)
        page = self.url_open("/web/login").text
        self.assertIn("o_theme_glass o_glass_login", page)

    def test_login_page_plain_while_disabled(self):
        self.env["ir.config_parameter"].sudo().set_bool(PARAM, False)
        page = self.url_open("/web/login").text
        self.assertNotIn("o_glass_login", page)
