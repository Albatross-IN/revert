# -*- coding: utf-8 -*-
"""Central brand resolution.

Everything that needs to know "what is the brand" (templates, controllers,
JS session, text replacement) goes through ``identity.brand``.  Values come
from the current company, then from the server config file, then from the
module's built-in defaults, so every page renders sensibly even before the
administrator has configured anything.
"""
import functools
import os
import re

from odoo import api, models, tools
from odoo.tools import BinaryBytes

MODULE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
APPS_ICON_DIR = os.path.join(MODULE_DIR, 'static', 'src', 'img', 'apps')
GLYPH_ICON_DIR = os.path.join(APPS_ICON_DIR, 'glyph')

# Built-in defaults (used when nothing is configured / no database)
DEFAULTS = {
    'name': 'Identity',
    'url': '',
    'support_url': '',
    'documentation_url': '',
    'theme_color': '#141A2C',
    'bot_name': 'Assistant',
    'powered_by': True,
}

# Global behaviour switches (ir.config_parameter keys → default)
PARAMS = {
    'identity.replace_text': True,
    'identity.custom_icons': True,
    'identity.hide_external_links': True,
}

# Stock Odoo image assets that get rewritten in every rendered page
ASSET_REWRITES = (
    ('/web/static/img/odoo_logo_tiny.png', '/identity/image/logo'),
    ('/web/static/img/logo.png', '/identity/image/logo'),
    ('/web/static/img/logo2.png', '/identity/image/logo'),
    ('/web/static/img/nologo.png', '/identity/image/logo'),
    ('/web/static/img/favicon.ico', '/identity/image/favicon'),
    ('/web/static/img/odoo-icon-ios.png', '/identity/image/apple'),
    ('/web/static/img/odoo-icon-192x192.png', '/identity/image/icon?size=192'),
    ('/web/static/img/odoo-icon-512x512.png', '/identity/image/icon?size=512'),
    # login page OpenGraph preview (Odoo marketing artwork)
    ('/web/static/img/og_image.png', '/identity/image/icon?size=512'),
)


# ---------------------------------------------------------------------------
# Web-client URL prefix (stock Odoo: /odoo).  Routes are static, so the value
# comes from the server config file (``identity_web_prefix``) and changing it
# needs a restart.  ``/odoo/...`` stays available as a permanent redirect.
# ---------------------------------------------------------------------------
STOCK_PREFIX = 'odoo'
RESERVED_PREFIXES = ('web', 'my', 'mail', 'website', 'shop', 'scoped_app', 'identity')


def _configured_prefix():
    value = (tools.config.get('identity_web_prefix') or 'app').strip().strip('/')
    if not re.fullmatch(r'[a-z0-9][a-z0-9_-]{0,40}', value) or value in RESERVED_PREFIXES:
        return 'app'
    return value


WEB_PREFIX = _configured_prefix()


def web_prefix():
    return WEB_PREFIX


def swap_prefix(path):
    """``/odoo/foo?x`` → ``/<prefix>/foo?x`` (no-op when the prefix is odoo)."""
    if WEB_PREFIX == STOCK_PREFIX or not path:
        return path
    if path == f'/{STOCK_PREFIX}' or path.startswith((f'/{STOCK_PREFIX}/', f'/{STOCK_PREFIX}?', f'/{STOCK_PREFIX}#')):
        return f'/{WEB_PREFIX}' + path[len(STOCK_PREFIX) + 1:]
    return path


def rewrite_prefix_in_html(text):
    """Rewrite quoted ``/odoo`` links inside rendered markup."""
    if WEB_PREFIX == STOCK_PREFIX or '/odoo' not in text:
        return text
    return re.sub(r'''(["'])/odoo(?=[/?#"'])''', r'\1/' + WEB_PREFIX, text)


def config_value(key):
    """Optional override from the server config file, e.g.
    ``identity_name = Acme`` under ``[options]``."""
    value = tools.config.get('identity_%s' % key)
    return value if value not in (None, '', 'None', 'False') else None


def config_default(key):
    return config_value(key) or DEFAULTS[key]


def static_defaults():
    """Brand dict for contexts without a database (database manager)."""
    return {
        'name': config_default('name'),
        'url': config_default('url'),
        'support_url': config_default('support_url'),
        'documentation_url': config_default('documentation_url'),
        'theme_color': config_default('theme_color'),
        'bot_name': config_default('bot_name'),
        'powered_by': True,
        'company_id': False,
        'logo_url': '/identity/image/logo',
        'icon_url': '/identity/image/icon',
        'favicon_url': '/identity/image/favicon',
        'apple_icon_url': '/identity/image/apple',
        'replace_text': True,
        'custom_icons': True,
        'hide_external_links': True,
        'web_prefix': web_prefix(),
    }


def debrand_text(text, brand):
    """Replace the Odoo brand in a piece of text.  Case-sensitive on purpose:
    ``odoo.com`` URLs, module names and ``odoo.*`` identifiers stay intact."""
    if not text or 'Odoo' not in text:
        return text
    text = text.replace('OdooBot', brand['bot_name'])
    return text.replace('Odoo', brand['name'])


def custom_icon_path(web_icon):
    """Return the Identity SVG for an Odoo ``web_icon`` value
    (``module,static/description/icon.png``) or a module name, if one exists.

    ``<module>__<basename>.svg`` wins when present (modules shipping several
    icons, e.g. base: settings / modules); otherwise ``<module>.svg`` replaces
    whatever icon file the module uses.
    """
    if not web_icon:
        return None
    if ',' in web_icon:
        module, res = web_icon.split(',', 1)
    elif '/static/' in web_icon:
        module, res = web_icon.lstrip('/').split('/', 1)
    else:
        module, res = web_icon, 'static/description/icon.png'
    module = module.strip().lstrip('/')
    base = os.path.splitext(os.path.basename(res))[0]
    if not re.fullmatch(r'[A-Za-z0-9_]+', module or '') or not re.fullmatch(r'[A-Za-z0-9_.-]+', base or ''):
        return None
    for name in (f'{module}__{base}.svg', f'{module}.svg'):
        path = os.path.join(APPS_ICON_DIR, name)
        if os.path.isfile(path):
            return path
    return None


def custom_glyph_url(web_icon):
    """URL of the glyph-only file matching ``web_icon`` (see custom_icon_path), or None."""
    path = custom_icon_path(web_icon)
    if not path:
        return None
    name = os.path.basename(path)
    if not os.path.isfile(os.path.join(GLYPH_ICON_DIR, name)):
        return None
    return '/identity/static/src/img/apps/glyph/' + name


@functools.lru_cache(maxsize=1)
def glyph_keys():
    """Keys (file names without .svg) of every glyph file, for the client-side lookup."""
    if not os.path.isdir(GLYPH_ICON_DIR):
        return ()
    return tuple(sorted(f[:-4] for f in os.listdir(GLYPH_ICON_DIR) if f.endswith('.svg')))


def custom_icon_url(web_icon):
    path = custom_icon_path(web_icon)
    if not path:
        return None
    return '/identity/static/src/img/apps/' + os.path.basename(path)


def _read_binary(path):
    """Addon file as a binary field value (empty when missing)."""
    try:
        with tools.file_open(path, 'rb') as f:
            return BinaryBytes(f.read())
    except FileNotFoundError:
        return BinaryBytes(b'')


# Odoo 20 ships the bot avatar as WebP; builds of ``mail`` that predate the
# switch still load the PNG.  The file is resolved through the addons path,
# i.e. from the ``mail`` module actually in use.
STOCK_BOT_AVATARS = ('mail/static/src/img/odoobot.webp', 'mail/static/src/img/odoobot.png')


@functools.lru_cache(maxsize=1)
def _stock_bot_avatar():
    for path in STOCK_BOT_AVATARS:
        value = _read_binary(path)
        if value:
            return value
    return BinaryBytes(b'')


def _default_bot_avatar():
    return _read_binary('identity/static/src/img/brand/icon-512.png')


def _same_binary(a, b):
    """Compare two binary field values by content.  (``checksum`` is not
    comparable across value types: attachment-backed values report the
    attachment's sha1, in-memory ones a sha256 of their bytes.)"""
    return bool(a) and bool(b) and a.size == b.size and a.content == b.content


class IdentityBrand(models.AbstractModel):
    _name = 'identity.brand'
    _description = 'Identity branding helper'

    @api.model
    def _params(self):
        icp = self.env['ir.config_parameter'].sudo()
        return {key.split('.', 1)[1]: icp.get_bool(key, default) for key, default in PARAMS.items()}

    @api.model
    def _company(self):
        try:
            return self.env.company.sudo()
        except Exception:  # noqa: BLE001 - no user / no company: fall back to first company
            return self.env['res.company'].sudo().search([], order='id', limit=1)

    @api.model
    def get(self):
        """Public: brand dictionary for QWeb (``request.env['identity.brand'].get()``)
        and RPC.  Contains only presentational data."""
        return self._get()

    @api.model
    def _get(self, company=None):
        company = (company or self._company()).sudo()
        params = self._params()
        cid = company.id
        qs = f'?company={cid}' if cid else ''
        return {
            'name': company.identity_name or config_value('name') or company.name or DEFAULTS['name'],
            'url': company.identity_url or config_value('url') or company.website or '',
            'support_url': company.identity_support_url or config_default('support_url'),
            'documentation_url': company.identity_documentation_url or config_default('documentation_url'),
            'theme_color': company.identity_theme_color or config_default('theme_color'),
            'bot_name': company.identity_bot_name or config_default('bot_name'),
            'powered_by': company.identity_powered_by,
            'company_id': cid,
            'logo_url': '/identity/image/logo' + qs,
            'icon_url': '/identity/image/icon' + qs,
            'favicon_url': '/identity/image/favicon' + qs,
            'apple_icon_url': '/identity/image/apple' + qs,
            'web_prefix': web_prefix(),
            **params,
        }

    @api.model
    def _sync_bot(self, restore=False):
        """Rename the bot partner after the configured bot name and give it
        the brand icon as avatar while it still wears the stock one.
        ``restore`` puts the stock name and avatar back (uninstall)."""
        root = self.env.ref('base.partner_root', raise_if_not_found=False)
        if not root:
            return
        root = root.sudo()
        stock_avatar = _stock_bot_avatar()
        if restore:
            root.write({'name': 'OdooBot', 'image_1920': stock_avatar or False})
            return
        vals = {}
        name = self.get()['bot_name']
        if root.name != name:
            vals['name'] = name
        current = root.image_1920
        brand_avatar = self._company().identity_icon or _default_bot_avatar()
        if not current or _same_binary(current, stock_avatar) or self.env.context.get('identity_force_avatar'):
            if brand_avatar and not _same_binary(current, brand_avatar):
                vals['image_1920'] = brand_avatar
        if vals:
            root.write(vals)

    @api.model
    def debrand(self, text, brand=None):
        """Replace the Odoo brand in ``text`` if text replacement is enabled."""
        if not text or 'Odoo' not in text:
            return text
        brand = brand or self.get()
        if not brand['replace_text']:
            return text
        return debrand_text(text, brand)
