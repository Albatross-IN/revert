# -*- coding: utf-8 -*-
{
    "name": "Glass - Glassmorphic Backend Theme",
    "summary": "Frosted-glass backend theme for Odoo 20 — translucent panes over a soft colour field, forms as a bento "
               "of tiles, list rows as panes. Pure CSS, Odoo colour tokens, light & dark, one-click enable/disable.",
    "description": """
Glass — Glassmorphic Backend Theme
==================================
A frosted-glass restyling of the whole Odoo 20 backend: translucent panes with a bright hairline
edge, blurring a soft colour field behind them. The form sheet becomes a bento of panes — a status
pane (actions + pipeline), an identity pane (title, avatar), one pane per field group, a notebook
pane for the lines and a chatter pane beside them. List rows are slim panes with the field showing
between them; kanban lanes are the faintest layer of glass holding raised cards. Buttons, inputs,
dropdowns, dialogs, navbar, home menu, control panel, search, calendar, graph, pivot, settings and
the enterprise views are all drawn from the same four primitives: pane, seat, well, key.

* Performance oriented: SCSS compiled into ``web.assets_backend`` by Odoo's own asset pipeline
  (minified + cached). No JavaScript, no component patches, no extra RPC. Blur is budgeted:
  only containers blur (form panes, lanes, navbar, overlays), never rows or cards.
* Uses only Odoo's colour tokens for inks, states and accents, so it follows Community,
  Enterprise and Dark mode automatically; dark mode is charcoal glass over a deep field.
* Enable / disable at any time from *Settings → General Settings → Glass Theme*
  without uninstalling.
* Works with Community and Enterprise; no dependency on ``web_enterprise``.
* Needs a browser with ``backdrop-filter`` (Chrome, Edge, Safari, Firefox 103+); older
  browsers get the same panes without the blur.
    """,
    "version": "20.0.1.1.0",
    "category": "Themes/Backend",
    "author": "Hardik Anavadia",
    "website": "https://github.com/hardikanavadia",
    "license": "OPL-1",
    "price": 49.0,
    "currency": "EUR",
    "depends": ["web", "base_setup"],
    "data": [
        "views/webclient_templates.xml",
        "views/login_templates.xml",
        "views/res_config_settings_views.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "web_theme_glass/static/src/scss/tokens.scss",
            "web_theme_glass/static/src/scss/theme.scss",
            "web_theme_glass/static/src/scss/form_view.scss",
            "web_theme_glass/static/src/scss/glass.scss",       # the pane grammar: form bento, row panes, lanes (after form_view: it wins ties)
            "web_theme_glass/static/src/scss/discuss.scss",
            "web_theme_glass/static/src/scss/backlight.scss",
            "web_theme_glass/static/src/scss/mobile.scss",
            "web_theme_glass/static/src/scss/typography.scss",  # Inter + the seven-step scale (after the component layers: it wins ties)
            "web_theme_glass/static/src/scss/community.scss",   # Community-only rules (body.o_glass_community)
        ],
        # The sign-in page: a frontend page with its own small token set (light + dark)
        "web.assets_frontend": [
            "web_theme_glass/static/src/scss/login.scss",
        ],
        # Point of Sale UI (/pos/ui) — separate app bundle, themed self-contained
        "point_of_sale.assets_prod": [
            "web_theme_glass/static/src/scss/pos.scss",
        ],
        "point_of_sale.assets_prod_dark": [
            "web_theme_glass/static/src/scss/pos.scss",
            "web_theme_glass/static/src/scss/pos.dark.scss",
        ],
    },
    "images": ["static/description/screenshot_home.png"],
    "installable": True,
    "application": False,
    "auto_install": False,
}
