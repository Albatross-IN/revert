# -*- coding: utf-8 -*-
import functools
import json
import logging

from odoo.http import Controller, request, route
from odoo.http.stream import STATIC_CACHE, Stream
from odoo.tools import BinaryBytes, file_open
from odoo.tools.image import image_process
from odoo.tools.mimetypes import guess_mimetype

from odoo.addons.web.controllers import database as web_database
from odoo.addons.web.controllers.binary import Binary
from odoo.addons.web.controllers.webmanifest import WebManifest

from ..models.identity_brand import (ASSET_REWRITES, STOCK_PREFIX, WEB_PREFIX, custom_icon_url, debrand_text,
                                     rewrite_prefix_in_html, static_defaults, swap_prefix)

_logger = logging.getLogger(__name__)

STATIC_IMAGES = {
    'logo': 'identity/static/src/img/brand/logo.svg',
    'icon': 'identity/static/src/img/brand/icon-512.png',
    'apple': 'identity/static/src/img/brand/icon-180.png',
    'favicon': 'identity/static/src/img/brand/favicon.png',
}
KIND_FIELD = {'logo': 'identity_logo', 'icon': 'identity_icon', 'apple': 'identity_icon', 'favicon': 'identity_icon'}
KIND_SIZE = {'apple': 180, 'favicon': 64}


def _company_from_request(company_id=None):
    """Company for an ``auth='none'`` request: explicit id, then the session
    user's company, then the first company."""
    if not request.db:
        return None
    Company = request.env['res.company'].sudo()
    if company_id:
        company = Company.browse(int(company_id)).exists()
        if company:
            return company
    if request.session.uid:
        user = request.env['res.users'].sudo().browse(request.session.uid).exists()
        if user and user.company_id:
            return user.company_id
    return Company.search([], order='id', limit=1)


def _static_response(path):
    stream = Stream.from_path(path)
    stream.max_age = STATIC_CACHE
    return stream.get_response()


def _binary_response(value, kind, size=None, last_modified=None):
    """Response for a binary field value (:class:`~odoo.tools.BinaryValue`)."""
    data = value.content
    mimetype = guess_mimetype(data, default='image/png')
    if mimetype != 'image/svg+xml' and size:
        try:
            data = image_process(data, size=(size, size), crop='center')
        except Exception:  # noqa: BLE001 - keep original bytes on unknown formats
            _logger.debug("Identity: could not resize %s image", kind, exc_info=True)
    ext = {'image/svg+xml': 'svg', 'image/jpeg': 'jpg', 'image/webp': 'webp', 'image/gif': 'gif'}.get(mimetype, 'png')
    stream = Stream(type='data', data=data, size=len(data), mimetype=mimetype,
                    download_name=f'{kind}.{ext}', last_modified=last_modified,
                    max_age=STATIC_CACHE)
    return stream.get_response()


class IdentityController(Controller):

    @route(['/identity/image/<string:kind>'], type='http', auth='none', cors='*', readonly=True)
    def identity_image(self, kind, company=None, size=None, **kw):
        """Brand images: logo | icon | apple | favicon.  Falls back to the
        module's built-in assets when nothing is configured."""
        if kind not in STATIC_IMAGES:
            raise request.not_found()
        try:
            company_rec = _company_from_request(company)
        except Exception:  # noqa: BLE001 - e.g. module not installed in this db
            company_rec = None
        if company_rec and KIND_FIELD[kind] in company_rec._fields:
            value = company_rec[KIND_FIELD[kind]]
            if value:
                px = KIND_SIZE.get(kind) or (int(size) if size and size.isdigit() else None)
                return _binary_response(value, kind, px, company_rec.write_date)
        if kind == 'icon' and size and size.isdigit() and int(size) <= 192:
            return _static_response('identity/static/src/img/brand/icon-192.png')
        return _static_response(STATIC_IMAGES[kind])

    @route(['/favicon.ico'], type='http', auth='none', readonly=True)
    def favicon(self, **kw):
        return self.identity_image('favicon')


class IdentityBinary(Binary):

    @route()
    def company_logo(self, dbname=None, **kw):
        """Serve the brand logo instead of Odoo's when there is no database
        or the company still uses the default (Odoo-branded) logo."""
        try:
            company = _company_from_request(kw.get('company'))
        except Exception:  # noqa: BLE001
            company = None
        if company is None:
            return _static_response(STATIC_IMAGES['logo'])
        if company and 'identity_logo' in company._fields and (company.uses_default_logo or not company.logo_web):
            if company.identity_logo:
                return _binary_response(company.identity_logo, 'logo', None, company.write_date)
            return _static_response(STATIC_IMAGES['logo'])
        return super().company_logo(dbname=dbname, **kw)


class IdentityWebManifest(WebManifest):

    def _brand(self):
        try:
            return request.env['identity.brand'].get()
        except Exception:  # noqa: BLE001
            return static_defaults()

    def _get_webmanifest(self):
        manifest = super()._get_webmanifest()
        brand = self._brand()
        icp = request.env['ir.config_parameter'].sudo()
        manifest['name'] = icp.get_str('web.web_app_name') or brand['name']
        manifest['scope'] = f'/{WEB_PREFIX}'
        manifest['start_url'] = f'/{WEB_PREFIX}'
        for shortcut in manifest.get('shortcuts', []):
            shortcut['url'] = swap_prefix(shortcut.get('url', ''))
        if manifest.get('share_target'):
            manifest['share_target']['action'] = swap_prefix(manifest['share_target']['action'])
        manifest['background_color'] = brand['theme_color']
        manifest['theme_color'] = brand['theme_color']
        manifest['icons'] = [{
            'src': brand['icon_url'] + ('&' if '?' in brand['icon_url'] else '?') + 'size=%s' % size,
            'sizes': f'{size}x{size}',
            'type': 'image/png',
        } for size in (192, 512)]
        if brand['custom_icons']:
            for shortcut in manifest.get('shortcuts', []):
                for icon in shortcut.get('icons', []):
                    custom = custom_icon_url(icon.get('src', ''))
                    if custom:
                        icon['src'] = custom
                        icon['type'] = 'image/svg+xml'
                        icon['sizes'] = 'any'
        return manifest

    def _icon_path(self):
        return 'identity/static/src/img/brand/icon-192.png'

    @route()
    def service_worker(self):
        response = super().service_worker()
        response.headers['Service-Worker-Allowed'] = f'/{WEB_PREFIX}'
        return response

    def _get_service_worker_content(self):
        body = super()._get_service_worker_content()
        if WEB_PREFIX != STOCK_PREFIX:
            body = body.replace('"/odoo', f'"/{WEB_PREFIX}').replace("'/odoo", f"'/{WEB_PREFIX}").replace('`/odoo', f'`/{WEB_PREFIX}')
        return body

    @route([f'/{WEB_PREFIX}/offline', f'/{STOCK_PREFIX}/offline'], type='http', auth='public', methods=['GET'], readonly=True)
    def offline(self):
        with file_open(self._icon_path(), 'rb') as f:
            icon = BinaryBytes(f.read())
        return request.render('web.webclient_offline', {
            'odoo_icon': icon,
            'identity': self._brand(),
        })

    @route()
    def scoped_app(self, app_id, path='', app_name=''):
        response = super().scoped_app(app_id, path=path, app_name=app_name)
        if getattr(response, 'qcontext', None) is not None:
            response.qcontext['apple_touch_icon'] = self._brand()['apple_icon_url']
        return response

    @route()
    def scoped_app_manifest(self, app_id, path, app_name=''):
        response = super().scoped_app_manifest(app_id, path, app_name=app_name)
        manifest = json.loads(response.get_data())
        manifest['background_color'] = manifest['theme_color'] = self._brand()['theme_color']
        return request.make_json_response(manifest, {'Content-Type': 'application/manifest+json'})

    def _get_scoped_app_icons(self, app_id):
        icons = super()._get_scoped_app_icons(app_id)
        if self._brand()['custom_icons']:
            custom = custom_icon_url(app_id)
            if custom:
                icons = [{'src': custom, 'sizes': 'any', 'type': 'image/svg+xml'}]
        return icons

    @route()
    def scoped_app_icon_png(self, app_id, add_padding=False):
        """Safari needs a PNG: serve the pre-rendered raster of our tile."""
        if self._brand()['custom_icons']:
            custom = custom_icon_url(app_id)
            if custom:
                png = custom.replace('/apps/', '/apps/png/').rsplit('.', 1)[0] + '.png'
                return _static_response(png.lstrip('/'))
        return super().scoped_app_icon_png(app_id, add_padding=add_padding)


# ---------------------------------------------------------------------------
# Database manager.  In Odoo 20 the page is rendered by the module-level
# ``_render_template`` function of ``web.controllers.database`` (no longer a
# controller method), which every route of that module looks up by name at
# call time: wrap it once so the selector, the manager and its error pages
# are all branded.  The page is served without a database, so the brand
# comes from the config file / built-in defaults.
# ---------------------------------------------------------------------------
def _brand_database_manager(html_out):
    brand = static_defaults()
    text = str(html_out)
    for old, new in ASSET_REWRITES:
        text = text.replace(old, new)
    text = rewrite_prefix_in_html(text)
    text = text.replace('<title>Odoo</title>', '<title>%s</title>' % brand['name'])
    return debrand_text(text, brand)


def _patch_database_manager():
    render = web_database._render_template
    if getattr(render, '_identity_wrapped', False):
        return

    @functools.wraps(render)
    def _render_template(**d):
        return _brand_database_manager(render(**d))

    _render_template._identity_wrapped = True
    web_database._render_template = _render_template


_patch_database_manager()
