import json
import os
import re

from odoo import http
from odoo.http import request
from odoo.modules import get_module_path

# The page behind the link a client contact is sent: the app's own screens in the browser, for one
# project, without installing anything and without signing in. The page carries no data. Its script
# exchanges the token at /api/rvt/v1/auth/link and then uses the same endpoints as the app.
PAGE = """<!doctype html>
<html lang="en" class="app web" data-rv="light" data-pal="emerald">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="robots" content="noindex,nofollow">
<meta name="referrer" content="no-referrer">
<meta name="theme-color" content="#0D1426">
<title>Revert Architects</title>
<link rel="stylesheet" href="/rvt_desk/static/fonts/fonts.css">
<link rel="stylesheet" href="/rvt_api/static/app/styles.css?v=%(stamp)s">
</head>
<body>
<div id="app"></div>
<script>window.RVT_LINK=%(token)s;</script>
<script src="/rvt_api/static/app/app.js?v=%(stamp)s"></script>
</body>
</html>
"""
TOKEN = re.compile(r"^[A-Za-z0-9_\-]+\.[A-Za-z0-9_\-]+\.[A-Za-z0-9_\-]+$")


def _stamp():
    """Changes whenever the screens are synced again, so a browser never keeps an older copy."""
    folder = os.path.join(get_module_path("rvt_api"), "static", "app")
    try:
        return str(int(max(os.path.getmtime(os.path.join(folder, name)) for name in ("app.js", "styles.css"))))
    except OSError:
        return "0"


class RvtClientLink(http.Controller):

    @http.route("/rvt/c/<string:token>", type="http", auth="public", sitemap=False)
    def client_link(self, token, **kw):
        if not TOKEN.match(token or ""):
            return request.not_found()
        # an expired or withdrawn link still gets the page: the screens say so in the client's words
        body = PAGE % {"stamp": _stamp(), "token": json.dumps(token)}
        return request.make_response(body, headers=[
            ("Content-Type", "text/html; charset=utf-8"),
            ("Cache-Control", "no-store"),
            ("X-Robots-Tag", "noindex, nofollow"),
            ("Referrer-Policy", "no-referrer"),
            ("X-Frame-Options", "DENY"),
        ])
