# -*- coding: utf-8 -*-
{
    'name': 'Identity',
    'summary': 'White-label Odoo 20: brand name, logos, favicon, PWA, texts and a full redesigned app icon set.',
    'description': """
Identity — Odoo 20 debranding
=============================

Replaces every visible Odoo brand element with your own identity:

* Page titles, favicon, apple-touch icon, PWA manifest / offline page
* Login page, database manager, portal / website footers, e-mail footers
* User menu (Help / My Odoo.com account / documentation links)
* Settings "About" block, upgrade dialogs
* Every "Odoo" occurrence in client-side texts, server-rendered pages
  and view labels (configurable)
* OdooBot name
* A complete redesigned application icon set (Community + Enterprise)

Configuration: Settings → Identity.
Defaults for pages served without a database (database manager) can be set
in the server config file: ``identity_name``, ``identity_url``.
""",
    'version': '20.0.2.0.0',
    'category': 'Hidden/Tools',
    'author': 'Identity',
    'license': 'LGPL-3',
    'depends': ['web', 'base_setup', 'mail', 'mail_bot'],
    'data': [
        'data/identity_data.xml',
        'views/res_config_settings_views.xml',
        'views/webclient_templates.xml',
        'views/mail_templates.xml',
    ],
    'assets': {
        # The web-client URL prefix ("/odoo") is hard-coded inside the router
        # module; swap the file for a prefix-aware copy (aliased to the same
        # module name) in every bundle that ships it.
        'web._assets_core': [
            ('replace', 'web/static/src/core/browser/router.js', 'identity/static/src/replace/router.js'),
        ],
        # shared: the text patch runs wherever OWL / _t runs
        'web.assets_frontend': [
            ('replace', 'web/static/src/core/browser/router.js', 'identity/static/src/replace/router.js'),
            'identity/static/src/js/debrand_text.js',
        ],
        'web.assets_backend': [
            ('replace', 'web/static/src/webclient/menus/menu_helpers.js', 'identity/static/src/replace/menu_helpers.js'),
            'identity/static/src/js/debrand_text.js',
            'identity/static/src/js/icons.js',
            'identity/static/src/scss/icons.scss',
            'identity/static/src/js/web_prefix_patch.js',
            'identity/static/src/js/webclient_patch.js',
            'identity/static/src/js/user_menu_patch.js',
            'identity/static/src/js/documentation_link_patch.js',
            'identity/static/src/js/upgrade_dialog_patch.js',
            'identity/static/src/js/edition_widget.js',
            'identity/static/src/xml/documentation_link.xml',
            'identity/static/src/xml/edition_widget.xml',
        ],
    },
    'images': ['static/description/icon.png'],
    'post_init_hook': 'post_init_hook',
    'uninstall_hook': 'uninstall_hook',
    'installable': True,
    'application': False,
    'auto_install': False,
}
