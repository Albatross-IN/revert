# Copyright 2022 ACSONE SA/NV
# License LGPL-3.0 or later (http://www.gnu.org/licenses/LGPL).

{
    "name": "Odoo FastAPI",
    "summary": """
        Odoo FastAPI endpoint""",
    "version": "20.0.1.1.0",
    "license": "LGPL-3",
    "author": "ACSONE SA/NV,Odoo Community Association (OCA)",
    "maintainers": ["lmignon"],
    "website": "https://github.com/OCA/rest-framework",
    "depends": ["endpoint_route_handler"],
    "data": [
        "security/res_groups.xml",
        "views/fastapi_menu.xml",
        "views/fastapi_endpoint.xml",
        "views/fastapi_endpoint_demo.xml",
        'security/ir.access.csv',
    ],
    "demo": ["demo/fastapi_endpoint_demo.xml"],
    "external_dependencies": {
        "python": [
            "fastapi>=0.110.0",
            "python-multipart",
            "ujson",
            "a2wsgi>=1.10.6",
            "parse-accept-language",
        ]
    },
    "development_status": "Beta",
    "installable": True,
}
