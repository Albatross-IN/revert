# -*- coding: utf-8 -*-
from odoo import models
from odoo.http import request

PARAM = "web_theme_glass.enabled"

# Community dark mode: Odoo Community has no dark colour scheme (web_enterprise ships the dark
# variables, the switch and the cookie handling). The theme fills the gap with its own dark
# palette (community_dark.scss), compiled into web.assets_web_dark BEFORE Odoo's primary
# variables, and honours the same `color_scheme` cookie Enterprise uses — only when
# web_enterprise is not installed, so an Enterprise database is never touched.
# The same pair goes into the lazily loaded dark bundle (graph, pivot — and gantt, grid, map… where
# installed), compiled on its own: without it those views came out with the light palette.
COMMUNITY_DARK_ASSETS = [
    {
        "name": "web_theme_glass: community dark variables",
        "bundle": bundle,
        "directive": "before",
        "target": "web/static/src/scss/primary_variables.scss",
        "path": "web_theme_glass/static/src/scss/community_dark.scss",
        "sequence": 20,     # after the bundle's own `include` (manifest lines count as 16)
    }
    for bundle in ("web.assets_web_dark", "web.assets_backend_lazy_dark")
] + [
    {
        # Bootstrap's tint/shade swapped for a dark ground (emphasis inks, subtle grounds)
        "name": "web_theme_glass: community dark colour functions",
        "bundle": bundle,
        "directive": "after",
        "target": "web/static/lib/bootstrap/scss/_functions.scss",
        "path": "web_theme_glass/static/src/scss/community_dark_functions.scss",
        "sequence": 20,
    }
    for bundle in ("web.assets_web_dark", "web.assets_backend_lazy_dark")
]


class IrHttp(models.AbstractModel):
    _inherit = "ir.http"

    def _glass_is_community(self):
        return "web_enterprise" not in self.env.registry._init_modules

    def webclient_rendering_context(self):
        # Adds one boolean to the qcontext of ``web.webclient_bootstrap`` so the
        # template can put ``o_theme_glass`` on <body>. Evaluated once per page load
        # (the bootstrap page is ``Cache-Control: no-store``), no extra RPC, no JS.
        ctx = super().webclient_rendering_context()
        ctx["glass_theme_enabled"] = self.env["res.config.settings"]._glass_theme_enabled()
        # `o_glass_community` on <body>: the Community-only readability rules (community.scss)
        # hang on it, so an Enterprise page is never affected by them
        ctx["glass_community"] = self._glass_is_community()
        return ctx

    def color_scheme(self):
        # Community: Odoo answers "light" whatever the cookie says; read the cookie the way
        # web_enterprise does. Enterprise: untouched (super() is web_enterprise's own logic).
        scheme = super().color_scheme()
        if scheme == "light" and self._glass_is_community() and request:
            if request.httprequest.cookies.get("color_scheme") == "dark":
                return "dark"
        return scheme

    def init(self):
        # Runs at every install / update of the module: keep exactly one ir.asset record for
        # the Community dark variables when web_enterprise is absent, none when it is present.
        super().init()
        Asset = self.env["ir.asset"].sudo()
        community = self._glass_is_community()
        for values in COMMUNITY_DARK_ASSETS:
            record = Asset.search([("path", "=", values["path"]), ("bundle", "=", values["bundle"])], limit=1)
            if community and not record:
                Asset.create(values)
            elif record and not community:
                record.unlink()
