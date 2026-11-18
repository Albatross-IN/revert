# -*- coding: utf-8 -*-
{
    "name": "Glass Workspace - Split View, Left Pane, Mobile Shell",
    "summary": "Per-user navigation preference (Odoo top bar or a left pane), Split Form View "
               "beside list & kanban, floating chatter and an app-like phone shell — built on the Glass theme.",
    "description": """
Glass Workspace
===============
Adds the behaviours the Glass theme cannot do with CSS alone. Everything is a per-user
preference (My Preferences → Glass Workspace) and defaults to stock Odoo behaviour:

* **Split Form View** — with the switch on, opening a record from a list or kanban shows its
  form in a panel beside the list instead of navigating away. The panel *is* Odoo's own form
  view (header buttons, statusbar, sheet, chatter); nothing is redrawn.
* **Left pane** — optional application pane (full or icons) next to the untouched top bar.
* **Mobile shell** — a bottom tab bar on phones (Apps · Menu · Activity · Account) that opens
  Odoo's own app drawer, activity menu and account menu (restyled by the theme), a stage picker
  for grouped kanbans, a settings-section picker, "Show more" per stacked stage, previous / next
  and a month picker in the calendar, and a vertical gantt.
* **Floating chatter** — on the desktop split view the chatter pops out into a movable,
  resizable window that follows the selected record; on phones a button in the form, on
  kanban cards and list rows opens the record's chatter in a small window, full screen or a
  bubble. It is Odoo's own chatter — any model with mail.thread, custom modules included.
    """,
    "version": "20.0.1.0.0",
    "category": "Themes/Backend",
    "author": "Hardik Anavadia",
    "website": "https://github.com/hardikanavadia",
    "license": "OPL-1",
    "depends": ["web", "mail", "web_theme_glass"],
    # No XML data: preferences live entirely in the slide-out panel + session_info, so we
    # never touch Odoo's own user/settings views (keeps stock Odoo forms exactly as shipped).
    "data": [],
    "assets": {
        "web.assets_backend": [
            # FIRST in the bundle: template extensions must precede every app's primary copy of
            # web.FormView / web.KanbanRecord / web.ListRenderer.RecordRow (Odoo applies to a
            # primary copy only the extensions registered before it) — stock apps and customer
            # modules alike get the phone chatter buttons this way.
            ("prepend", "web_glass_workspace/static/src/chatter/chatter_button.xml"),
            ("prepend", "web_glass_workspace/static/src/mobile/kanban_more.xml"),
            ("prepend", "web_glass_workspace/static/src/mobile/calendar_nav.xml"),
            # the navigation path (Back key · page button · pager)
            ("prepend", "web_glass_workspace/static/src/nav/crumbs.xml"),
            "web_glass_workspace/static/src/nav/crumbs.js",
            "web_glass_workspace/static/src/nav/crumbs.scss",
            "web_glass_workspace/static/src/prefs/glass_prefs_service.js",
            "web_glass_workspace/static/src/prefs/prefs_panel.js",
            "web_glass_workspace/static/src/prefs/prefs_panel.xml",
            "web_glass_workspace/static/src/prefs/prefs_panel.scss",
            "web_glass_workspace/static/src/prefs/user_menu_items.js",
            "web_glass_workspace/static/src/split/split_panel.js",
            "web_glass_workspace/static/src/split/split_panel.xml",
            "web_glass_workspace/static/src/split/split_panel.scss",
            "web_glass_workspace/static/src/split/split_views.js",
            "web_glass_workspace/static/src/split/split_views.xml",
            "web_glass_workspace/static/src/chatter/chatter_store.js",
            "web_glass_workspace/static/src/chatter/chatter_window.js",
            "web_glass_workspace/static/src/chatter/chatter_window.xml",
            "web_glass_workspace/static/src/chatter/chatter_window.scss",
            "web_glass_workspace/static/src/chatter/chatter_button.js",
            "web_glass_workspace/static/src/pane/left_pane.js",
            "web_glass_workspace/static/src/pane/left_pane.xml",
            "web_glass_workspace/static/src/pane/left_pane.scss",
            "web_glass_workspace/static/src/pane/navbar_toggle.js",
            ("prepend", "web_glass_workspace/static/src/pane/navbar_toggle.xml"),
            "web_glass_workspace/static/src/mobile/stage_store.js",
            "web_glass_workspace/static/src/mobile/kanban_stage_patch.js",
            "web_glass_workspace/static/src/mobile/kanban_more.js",
            "web_glass_workspace/static/src/mobile/calendar_nav.js",
            "web_glass_workspace/static/src/mobile/burger_menu.js",
            "web_glass_workspace/static/src/mobile/mobile_shell.js",
            "web_glass_workspace/static/src/mobile/mobile_shell.xml",
            "web_glass_workspace/static/src/mobile/mobile_shell.scss",
        ],
        # The phone gantt (static/src/mobile/gantt_phone.{xml,js,scss}) is NOT listed here: it
        # extends and imports Enterprise's web_gantt, which lives in the on-demand bundle
        # web.assets_backend_lazy. Community has that bundle too (Chart.js) but no web_gantt, so a
        # manifest entry made every Community graph screen log "Missing (extension) parent
        # templates" (BUG-0048). models/ir_http.py registers the three files as ir.asset records of
        # web.assets_backend_lazy (the template prepended) only where web_gantt is installed.
    },
    "installable": True,
    "application": False,
    "auto_install": False,
}
