{
    "name": "Revert — Bills and payments",
    "summary": "A bill is asked for, uploaded, reviewed and paid; amounts are the owner's",
    "description": """
Release 1, phase P10 (docs/implementation_plan_r1.md).

The office asks an agency for a bill. The agency uploads it from its app
against that request (it cannot start one), or the office uploads it for the
agency. The office accepts it or returns it with the reason. The owner
records payments against an accepted bill: there is no payment without a
bill, so no advances. Each bill says whether it is billed to the client or
to Revert; the project gives the default.

Amounts are the owner's: other staff see the document and the state, the
agency sees its own bills and their states, and the client sees nothing of
this. The project picture learns rule B10: a submitted bill not reviewed
within the day limit.

In the desk, the API and the app the bill screens are the approved ones;
this module gives them their data and their operations.
""",
    "version": "20.0.1.1.0",
    "category": "Services/Project",
    "license": "LGPL-3",
    "author": "Albatross",
    "website": "https://albatross.work",
    "depends": ["rvt_api"],
    "data": [
        "security/ir.access.csv",
        "data/rvt_notify_template_data.xml",
        "views/rvt_bill_views.xml",
    ],
    "installable": True,
}
