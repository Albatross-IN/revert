# Copyright 2026 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/LGPL).

from urllib.parse import parse_qs, urlparse

from odoo.http import router
from odoo.http.router import db_filter

# Odoo 20 port note: Request._get_session_and_dbname() became the module
# function odoo.http.router._set_session_and_dbname(request), which assigns
# request.session / request.db itself. The router looks the function up on
# the module at call time, so rebinding the module attribute is enough.
_original_set_session_and_dbname = router._set_session_and_dbname


def _patched_set_session_and_dbname(request):
    _original_set_session_and_dbname(request)
    if not request.db:
        # Try to get the database from the request "db" param.
        # This is useful for multi-database environments.
        db = request.httprequest.args.get("db", "").strip()
        if not db:
            # For browser sub-requests (e.g. openapi.json or static assets
            # fetched by Swagger UI / ReDoc), the browser sets a Referer
            # header pointing to the docs page which may carry the "db"
            # query parameter.
            referer = request.httprequest.headers.get("Referer", "")
            if referer:
                parsed = urlparse(referer)
                db = parse_qs(parsed.query).get("db", [""])[0].strip()
        host = request.httprequest.environ.get("HTTP_HOST")
        if db and db_filter([db], host=host):
            request.session.db = db
            request.db = db


router._set_session_and_dbname = _patched_set_session_and_dbname
