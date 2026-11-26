{
    "name": "Revert — Project onboarding, entities and work lines",
    "summary": "Team, trade plan, one task per room and one work line per trade",
    "description": """
Release 1, phase P2 (docs/implementation_plan_r1.md).

A project is set up once: its client and team, its rooms and zones (one task
each), the trades it needs with the agency chosen for each, and which trade
works in which room. Each ticked room × trade becomes a work line that
carries its own state; "Waiting" always names its cause.

Onboarding is a model method (project.project.rvt_onboard) so the desk and
the app call the same code. Tasks made by hand keep working as before.
""",
    "version": "20.0.1.2.0",
    "category": "Services/Project",
    "license": "LGPL-3",
    "author": "Albatross",
    "website": "https://albatross.work",
    "depends": ["rvt_base", "project"],
    "data": [
        "security/rvt_project_security.xml",
        "security/ir.access.csv",
        "data/rvt_project_actions.xml",
        "views/rvt_project_trade_views.xml",
        "views/project_project_views.xml",
        "views/project_task_views.xml",
    ],
    "installable": True,
}
