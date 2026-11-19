{
    "name": "Revert — Roles and master lists",
    "summary": "Roles, trades, entity types, site presets, standard drawing sets and settings",
    "description": """
Release 1 foundation (docs/implementation_plan_r1.md, phase P1).

Roles for staff, agencies and clients; the master lists that project
onboarding reads (trades, entity types with their usual trades, site
presets, standard drawing sets); the agency mark on contacts; and the
settings the project picture and the release flow depend on.
""",
    "version": "20.0.1.4.0",
    "category": "Services/Project",
    "license": "LGPL-3",
    "author": "Albatross",
    "website": "https://albatross.work",
    "depends": ["base", "base_setup", "mail", "bus"],
    "data": [
        "security/rvt_groups.xml",
        "security/ir.access.csv",
        "data/rvt_language_data.xml",
        "data/rvt_trade_data.xml",
        "data/rvt_trade_usual.xml",
        "data/rvt_entity_type_data.xml",
        "data/rvt_site_preset_data.xml",
        "data/rvt_drawing_type_data.xml",
        "views/rvt_master_views.xml",
        "views/res_partner_views.xml",
        "views/res_config_settings_views.xml",
        "views/rvt_menus.xml",
    ],
    "installable": True,
    "application": True,
}
