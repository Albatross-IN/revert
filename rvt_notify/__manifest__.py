{
    "name": "Revert — Messages on WhatsApp",
    "summary": "One sender for every message: texts in three languages, a delivery log, a hard switch",
    "description": """
Release 1, phase P6 (docs/implementation_plan_r1.md).

Every message to an agency or a client leaves through this module and no
other: a released drawing with its link, a party's MOM as a PDF, a client
item, a reminder on a staff member's tap, an invitation, a sign-in code.
The wording is kept per event and language (English, Gujarati, Hindi);
every send is logged with its outcome.

"Sending on" is a switch. It is off by default, and nothing ever leaves a
test copy of the database whatever the switch says: such messages are
logged as held.
""",
    "version": "20.0.1.3.1",
    "category": "Services/Project",
    "license": "LGPL-3",
    "author": "Albatross",
    "website": "https://albatross.work",
    "depends": ["rvt_mom", "open_whatsapp_connector"],
    "data": [
        "security/ir.access.csv",
        "data/rvt_notify_template_data.xml",
        "views/rvt_notify_views.xml",
        "views/owa_access_views.xml",
    ],
    "installable": True,
}
