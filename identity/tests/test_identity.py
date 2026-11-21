# -*- coding: utf-8 -*-
from unittest.mock import patch
from urllib.parse import urlsplit

from lxml import etree
from markupsafe import Markup

from odoo.tests import HttpCase, TransactionCase, tagged
from odoo.tools import BinaryBytes

from odoo.addons.mail_bot.models.mail_bot import MailBot as StockMailBot

from ..controllers.home import _to_stock_prefix
from ..models import identity_brand as ib
from ..models.identity_brand import STOCK_PREFIX, WEB_PREFIX


class IdentityCase:

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company = cls.env.company
        cls.company.write({
            'identity_name': 'Acme',
            'identity_url': 'https://acme.example',
            'identity_bot_name': 'Wile',
        })
        cls.Brand = cls.env['identity.brand']


@tagged('post_install', '-at_install')
class TestIdentityBrand(IdentityCase, TransactionCase):

    def test_brand_values(self):
        brand = self.Brand.get()
        self.assertEqual(brand['name'], 'Acme')
        self.assertEqual(brand['url'], 'https://acme.example')
        self.assertEqual(brand['bot_name'], 'Wile')
        self.assertEqual(brand['web_prefix'], WEB_PREFIX)
        self.assertEqual(brand['logo_url'], f'/identity/image/logo?company={self.company.id}')

    def test_debrand(self):
        self.assertEqual(self.Brand.debrand('Odoo and OdooBot, see odoo.com'), 'Acme and Wile, see odoo.com')

    def test_behaviour_switch_can_be_turned_off(self):
        # stored with set_bool: unticking must read back as False (in 19.0 an
        # unticked boolean deleted the parameter, which then read as True)
        self.env['res.config.settings'].create({'identity_replace_text': False}).execute()
        self.assertFalse(self.Brand._params()['replace_text'])
        self.assertEqual(self.Brand.debrand('Odoo'), 'Odoo')
        self.assertFalse(self.env['res.config.settings'].create({}).identity_replace_text)
        self.env['res.config.settings'].create({'identity_replace_text': True}).execute()
        self.assertTrue(self.Brand._params()['replace_text'])

    def test_glyph_icons(self):
        self.assertTrue(ib.custom_glyph_url('mail,static/description/icon.png').endswith('/apps/glyph/mail.svg'))
        self.assertTrue(ib.custom_glyph_url('/base/static/description/settings.png').endswith('/glyph/base__settings.svg'))
        self.assertIsNone(ib.custom_glyph_url('no_such_module,static/description/icon.png'))
        keys = ib.glyph_keys()
        self.assertIn('mail', keys)
        self.assertIn('base__settings', keys)
        self.assertIn('mail', self.env['ir.http']._identity_session_values()['identity_glyphs'])

    def test_debrand_bot_messages(self):
        from ..hooks import _debrand_bot_messages
        root = self.env.ref('base.partner_root')
        partner = self.env['res.partner'].create({'name': 'Bot target'})
        chat = partner.with_context(mail_create_nolog=True).message_post(
            body=Markup('<p>Hi, I am OdooBot. Odoo is great, see odoo.com</p>'),
            author_id=root.id, message_type='comment', subtype_xmlid='mail.mt_comment')
        mail = partner.with_context(mail_create_nolog=True).message_post(
            body=Markup('<p>Sent by OdooBot with Odoo</p>'),
            author_id=root.id, message_type='email_outgoing', subtype_xmlid='mail.mt_comment')
        # the test user is the superuser, whose partner *is* the bot: name an author
        other = partner.with_context(mail_create_nolog=True).message_post(
            body=Markup('<p>Odoo by a user</p>'), author_id=self.env.ref('base.partner_admin').id,
            message_type='comment', subtype_xmlid='mail.mt_comment')
        write_date = chat.write_date
        _debrand_bot_messages(self.env)
        self.assertEqual(str(chat.body), '<p>Hi, I am Wile. Acme is great, see odoo.com</p>')
        self.assertEqual(chat.write_date, write_date, "not a user edit: date untouched")
        self.assertIn('OdooBot with Odoo', str(mail.body), "sent e-mails are left as sent")
        self.assertIn('Odoo by a user', str(other.body), "only the bot's messages")
        # idempotent and a no-op once nothing matches
        _debrand_bot_messages(self.env)
        self.assertEqual(str(chat.body), '<p>Hi, I am Wile. Acme is great, see odoo.com</p>')

    def test_prefix_helpers(self):
        if WEB_PREFIX == STOCK_PREFIX:
            self.skipTest("stock prefix configured")
        self.assertEqual(ib.swap_prefix('/odoo'), f'/{WEB_PREFIX}')
        self.assertEqual(ib.swap_prefix('/odoo/crm?x=1'), f'/{WEB_PREFIX}/crm?x=1')
        self.assertEqual(ib.swap_prefix('/odoobar'), '/odoobar')
        self.assertEqual(ib.swap_prefix('/web/login'), '/web/login')
        self.assertEqual(_to_stock_prefix(f'/{WEB_PREFIX}/crm#x'), '/odoo/crm#x')
        self.assertEqual(ib.rewrite_prefix_in_html('<a href="/odoo/crm">x</a>'), f'<a href="/{WEB_PREFIX}/crm">x</a>')

    def test_custom_icons(self):
        self.assertTrue(ib.custom_icon_path('mail,static/description/icon.png').endswith('/mail.svg'))
        self.assertTrue(ib.custom_icon_path('/base/static/description/settings.png').endswith('/base__settings.svg'))
        self.assertIsNone(ib.custom_icon_path('no_such_module,static/description/icon.png'))
        self.assertIsNone(ib.custom_icon_path('../etc,passwd'))

        icon = self.env['ir.ui.menu']._read_image('mail,static/description/icon.png')
        self.assertIsInstance(icon, BinaryBytes)
        self.assertTrue(icon.content.lstrip().startswith(b'<svg'))

        module = self.env.ref('base.module_mail')
        self.assertTrue(module.icon_image.content.lstrip().startswith(b'<svg'))
        self.assertEqual(module.read(['icon'])[0]['icon'], '/identity/static/src/img/apps/mail.svg')

    def test_menu_icons_refresh(self):
        menu = self.env['ir.ui.menu'].search([('web_icon', '=like', 'mail,%')], limit=1)
        self.assertTrue(menu)
        self.env['ir.ui.menu']._identity_refresh_icons()
        self.assertTrue(menu.web_icon_data.content.lstrip().startswith(b'<svg'))
        self.env['ir.ui.menu'].with_context(identity_skip_icons=True)._identity_refresh_icons()
        self.assertFalse(menu.web_icon_data.content.lstrip().startswith(b'<svg'))

    def test_bot_sync(self):
        root = self.env.ref('base.partner_root')
        self.assertEqual(root.name, 'Wile')
        # the stock avatar is replaced by the brand icon...
        root.image_1920 = ib._stock_bot_avatar()
        self.env.invalidate_all()
        self.Brand._sync_bot()
        self.assertTrue(ib._same_binary(root.image_1920, ib._default_bot_avatar()))
        # ...a custom one is kept
        custom = ib._read_binary('identity/static/src/img/brand/icon-180.png')
        root.image_1920 = custom
        self.Brand._sync_bot()
        self.assertTrue(ib._same_binary(root.image_1920, custom))
        # uninstall puts everything back
        self.Brand._sync_bot(restore=True)
        self.assertEqual(root.name, 'OdooBot')
        self.assertTrue(ib._same_binary(root.image_1920, ib._stock_bot_avatar()))

    def test_bot_answers(self):
        with patch.object(StockMailBot, '_get_answer', return_value=[Markup('Hi from <b>Odoo</b>'), 'Odoo!']):
            answers = self.env['mail.bot']._get_answer(self.env['discuss.channel'], 'x', self.env['mail.message'])
        self.assertEqual(answers, [Markup('Hi from <b>Acme</b>'), 'Acme!'])
        self.assertIsInstance(answers[0], Markup)
        with patch.object(StockMailBot, '_get_answer', return_value=Markup('@OdooBot')):
            answer = self.env['mail.bot']._get_answer(self.env['discuss.channel'], 'x', self.env['mail.message'])
        self.assertEqual(answer, Markup('@Wile'))

    def test_settings_view(self):
        arch = self.env['res.config.settings'].get_view(view_type='form')['arch']
        self.assertNotIn('Odoo', arch)
        self.assertIn('/identity/static/src/img/apps/base__settings.svg', arch)
        self.assertIn('name="identity_edition"', arch)

    def test_templates(self):
        html = str(self.env['ir.qweb']._render('web.brand_promotion_message', {'_message': 'x', '_utm_medium': 'portal'}))
        self.assertIn('Powered by', html)
        self.assertIn('Acme', html)
        self.assertNotIn('odoo.com', html)
        self.company.identity_powered_by = False
        html = str(self.env['ir.qweb']._render('web.brand_promotion_message', {'_message': 'x', '_utm_medium': 'portal'}))
        self.assertNotIn('Powered by', html)
        for xmlid in ('mail.mail_notification_layout', 'mail.mail_notification_light', 'web.login_layout'):
            arch = etree.tostring(self.env.ref(xmlid)._get_combined_arch(), encoding='unicode')
            self.assertNotIn('www.odoo.com', arch, xmlid)


@tagged('post_install', '-at_install')
class TestIdentityHttp(IdentityCase, HttpCase):

    def test_prefix_redirect(self):
        if WEB_PREFIX == STOCK_PREFIX:
            self.skipTest("stock prefix configured")
        res = self.url_open('/odoo/crm?x=1', allow_redirects=False)
        self.assertEqual(res.status_code, 301)
        location = urlsplit(res.headers['Location'])
        self.assertEqual((location.path, location.query), (f'/{WEB_PREFIX}/crm', 'x=1'))
        res = self.url_open(f'/{WEB_PREFIX}/crm', allow_redirects=False)
        self.assertEqual(res.status_code, 303)
        self.assertIn(f'redirect=%2F{WEB_PREFIX}%2Fcrm', res.headers['Location'])

    def test_images(self):
        for url in ('/identity/image/logo', '/identity/image/icon?size=192', '/identity/image/apple',
                    '/identity/image/favicon', '/favicon.ico', '/web/binary/company_logo'):
            res = self.url_open(url)
            self.assertEqual(res.status_code, 200, url)
            self.assertTrue(res.headers['Content-Type'].startswith('image/'), url)
        self.assertEqual(self.url_open('/identity/image/nope').status_code, 404)

    def test_manifest_and_service_worker(self):
        manifest = self.url_open('/web/manifest.webmanifest').json()
        self.assertEqual((manifest['scope'], manifest['start_url']), (f'/{WEB_PREFIX}', f'/{WEB_PREFIX}'))
        self.assertEqual(manifest['name'], 'Acme')
        self.assertTrue(all(icon['src'].startswith('/identity/image/icon') for icon in manifest['icons']))
        res = self.url_open('/web/service-worker.js')
        self.assertEqual(res.headers['Service-Worker-Allowed'], f'/{WEB_PREFIX}')
        if WEB_PREFIX != STOCK_PREFIX:
            self.assertNotIn('"/odoo', res.text)
        scoped = self.url_open(f'/web/manifest.scoped_app_manifest?app_id=mail&path=/{WEB_PREFIX}/discuss').json()
        self.assertEqual(scoped['theme_color'], self.company.identity_theme_color)
        self.assertEqual(scoped['icons'][0]['src'], '/identity/static/src/img/apps/mail.svg')

    def test_login_page(self):
        res = self.url_open(f'/web/login?redirect=/{WEB_PREFIX}/discuss')
        self.assertEqual(res.status_code, 200)
        self.assertNotIn('Odoo', res.text)
        self.assertNotIn('odoo.com', res.text)
        self.assertIn('<title>', res.text)
        # OpenGraph preview of the backend link keeps the branded prefix
        self.assertIn(f'/{WEB_PREFIX}/discuss"', res.text)
        self.assertNotIn('/web/static/img/og_image.png', res.text)

    def test_offline_page(self):
        res = self.url_open(f'/{WEB_PREFIX}/offline')
        self.assertEqual(res.status_code, 200)
        self.assertIn('Acme will load', res.text)

    def test_database_selector(self):
        res = self.url_open('/web/database/selector')
        self.assertEqual(res.status_code, 200)
        self.assertNotIn('Odoo', res.text)
        self.assertNotIn('/web/static/img/logo2.png', res.text)

    def test_webclient(self):
        # Browser tests load the shared test-assets bundle.  In Odoo 20 the
        # tour of the auto-installed website_address_autocomplete imports
        # website_sale, which breaks that bundle (and every browser test of
        # the database) when website_sale is not installed.
        Module = self.env['ir.module.module']
        installed = set(Module.search([('state', '=', 'installed')]).mapped('name'))
        if 'website_address_autocomplete' in installed and 'website_sale' not in installed:
            self.skipTest("test assets broken by website_address_autocomplete without website_sale (Odoo issue)")
        code = """
            const { _t } = odoo.loader.modules.get("@web/core/l10n/translation");
            const { WEB_PREFIX } = odoo.loader.modules.get("@web/core/browser/router");
            const errors = [];
            if (WEB_PREFIX !== %(prefix)r) errors.push("router prefix: " + WEB_PREFIX);
            if (!location.pathname.startsWith("/" + WEB_PREFIX)) errors.push("url: " + location.pathname);
            if (String(_t("Odoo and OdooBot")) !== "Acme and Wile") errors.push("_t: " + _t("Odoo and OdooBot"));
            if (!document.title.includes("Acme")) errors.push("title: " + document.title);
            if (/\\bOdoo/.test(document.body.innerText)) errors.push("Odoo text in the web client");
            if (errors.length) {
                console.error(errors.join(" / "));
            } else {
                console.log("test successful");
            }
        """ % {'prefix': WEB_PREFIX}
        self.browser_js(f'/{WEB_PREFIX}', code, "odoo.isReady === true", login='admin')
