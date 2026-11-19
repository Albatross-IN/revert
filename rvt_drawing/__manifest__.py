{
    "name": "Revert — Drawings: register, approval, release",
    "summary": "Every drawing of a project, its revisions, who received it and who opened it",
    "description": """
Release 1, phase P4 (docs/implementation_plan_r1.md).

Drawings are planned at onboarding from the standard sets. A designer uploads
the PDF and sends it for approval; the principal approves; it is released to
the agencies of its trade and, where marked, to the client. Each receiver gets
a link; the first opening is recorded. A new release supersedes the one before.
The client approves or asks for a change with one tap; questions on a drawing
stay on the designer's list until answered.

The project picture learns what is late and who is waiting (rules B2, B3, B4,
B8, B9).
""",
    "version": "20.0.1.0.1",
    "category": "Services/Project",
    "license": "LGPL-3",
    "author": "Albatross",
    "website": "https://albatross.work",
    "depends": ["rvt_project"],
    "data": [
        "security/ir.access.csv",
        "views/rvt_drawing_views.xml",
    ],
    "installable": True,
}
