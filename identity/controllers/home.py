# -*- coding: utf-8 -*-
"""Web-client URL prefix.

Stock Odoo 20 serves the backend under ``/odoo``.  Identity serves it under a
configurable prefix (``identity_web_prefix`` in the server config file,
default ``app``) and turns ``/odoo/...`` into a permanent redirect so
bookmarks, e-mails and third-party modules that still build ``/odoo`` links
keep working.  Routes are static, so changing the prefix needs a restart.
"""
from urllib.parse import urlsplit, urlunsplit

from odoo.http import request, route

from odoo.addons.web.controllers import home as web_home

from ..models.identity_brand import STOCK_PREFIX, WEB_PREFIX, swap_prefix


def _to_stock_prefix(path):
    """``/<prefix>/foo?x`` → ``/odoo/foo?x`` (inverse of ``swap_prefix``)."""
    if WEB_PREFIX == STOCK_PREFIX or not path:
        return path
    if path == f'/{WEB_PREFIX}' or path.startswith((f'/{WEB_PREFIX}/', f'/{WEB_PREFIX}?', f'/{WEB_PREFIX}#')):
        return f'/{STOCK_PREFIX}' + path[len(WEB_PREFIX) + 1:]
    return path


class IdentityHome(web_home.Home):

    @route()
    def index(self, *args, **kw):
        response = super().index(*args, **kw)
        location = response.headers.get('Location') if hasattr(response, 'headers') else None
        if location and location.startswith('/odoo'):
            response.headers['Location'] = swap_prefix(location)
        return response

    @route([
        f'/{WEB_PREFIX}',
        f'/{WEB_PREFIX}/<path:subpath>',
        '/web',
        '/scoped_app/<path:subpath>',
    ], type='http', auth='none')
    def web_client(self, s_action=None, **kw):
        return super().web_client(s_action=s_action, **kw)

    @route([f'/{STOCK_PREFIX}', f'/{STOCK_PREFIX}/<path:subpath>'], type='http', auth='none', readonly=True)
    def web_client_legacy_prefix(self, subpath='', **kw):
        """Permanent redirect of stock ``/odoo`` URLs to the branded prefix."""
        if WEB_PREFIX == STOCK_PREFIX:
            return self.web_client(**kw)
        target = f'/{WEB_PREFIX}' + (f'/{subpath}' if subpath else '')
        query = request.httprequest.query_string.decode()
        if query:
            target += '?' + query
        return request.redirect(target, code=301, local=True)

    @route()
    def web_login(self, redirect=None, **kw):
        # The login page shows an OpenGraph preview (record title, link) for
        # backend links, which it recognises by their stock "/odoo" prefix.
        response = super().web_login(redirect=_to_stock_prefix(redirect), **kw)
        qcontext = getattr(response, 'qcontext', None)
        if qcontext and qcontext.get('og_url'):
            url = urlsplit(qcontext['og_url'])
            qcontext['og_url'] = urlunsplit(url._replace(path=swap_prefix(url.path)))
        return response

    def _login_redirect(self, uid, redirect=None):
        url = super()._login_redirect(uid, redirect=redirect)
        return swap_prefix(url) if isinstance(url, str) else url
