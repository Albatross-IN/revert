{
    "name": "Revert — App API",
    "summary": "The back end of the Revert app for staff, agencies and clients",
    "description": """
Release 1, phase P7 (docs/implementation_plan_r1.md).

One API at /api/rvt/v1 for the app: staff sign in with their login and
password, agencies and clients with their mobile number and a code sent on
WhatsApp. Every endpoint is a thin layer over the model methods the desk
uses, and runs with the signed-in person's own rights, so an agency can
never read another agency's points, drawings or lines, and a client gets
only the drawings marked for the client and its own items.
""",
    "version": "20.0.1.3.1",
    "category": "Services/Project",
    "license": "LGPL-3",
    "author": "Albatross",
    "website": "https://albatross.work",
    "depends": ["rvt_desk", "rvt_notify", "fastapi"],
    "external_dependencies": {"python": ["PyJWT"]},
    "data": [
        "security/ir.access.csv",
        "data/ir_config_parameter.xml",
        "data/fastapi_endpoint.xml",
    ],
    "post_init_hook": "post_init_hook",
    "installable": True,
}
