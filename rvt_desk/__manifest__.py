{
    "name": "Revert Desk",
    "summary": "The single window for staff: Today, Projects, Review, Setup and project onboarding",
    "description": """
Release 1, phase P3 (docs/implementation_plan_r1.md).

Staff work in one window. It opens on Today (what do I do now), shows every
project through its picture (progress, blockers, next actions) and its work
grid, runs the weekly Review and keeps the master lists in Setup. A project
is onboarded here in a few guided steps.

The screens follow the approved Release 1 preview. Other menus stay hidden
for staff; administrators keep them.
""",
    "version": "20.0.1.2.0",
    "category": "Services/Project",
    "license": "LGPL-3",
    "author": "Albatross",
    "website": "https://albatross.work",
    "depends": ["rvt_project", "rvt_drawing", "rvt_mom", "web"],
    "data": [
        "views/desk_templates.xml",
        "views/login_templates.xml",
        "views/res_config_settings_views.xml",
        "data/rvt_desk_menu.xml",
    ],
    "installable": True,
    "application": True,
}
