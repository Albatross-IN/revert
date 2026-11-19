{
    "name": "Revert — MOM: visits and points",
    "summary": "Points written on site or raised from the office, per-party PDFs, and the move of earlier MOM entries",
    "description": """
Release 1, phase P5 (docs/implementation_plan_r1.md).

A point is one line: what is needed, from whom, by when, with an optional
photo, room and drawing. A MOM is the set of points written during one site
visit; a point raised from the office is the same record without a visit.
One record type serves the MOM, the agency's to-do and the client's pending
list.

Each party gets its own PDF of a visit; a point stays open until it is closed
with a note or a photo; a point for the client is shown to the client after
the office confirms it (a setting). The earlier MOM entries are moved into
these records by tools/etl_mom.py with a verification report.
""",
    "version": "20.0.1.2.1",
    "category": "Services/Project",
    "license": "LGPL-3",
    "author": "Albatross",
    "website": "https://albatross.work",
    "depends": ["rvt_drawing"],
    "data": [
        "security/ir.access.csv",
        "report/rvt_mom_reports.xml",
        "views/rvt_mom_views.xml",
    ],
    "installable": True,
}
