"""The official (Meta) WhatsApp app installed next to this connector keeps its chats."""
from unittest.mock import patch

from odoo.tests import tagged

from .common import OwaTestCase

META_SEND = 'odoo.addons.whatsapp.tools.whatsapp_api.WhatsAppApi._send_whatsapp_to_identifier'


@tagged('post_install', '-at_install')
class TestMetaCoexist(OwaTestCase):

    def setUp(self):
        super().setUp()
        if 'whatsapp.account' not in self.env:
            self.skipTest("the official WhatsApp app is not installed")
        admin = self.env.ref('base.user_admin')
        self.account.is_default = True
        self.meta_account = self.env['whatsapp.account'].create({
            'name': 'Meta', 'account_uid': '1', 'phone_uid': '2', 'app_uid': '3',
            'app_secret': 's', 'token': 't', 'notify_user_ids': [(6, 0, admin.ids)],
        })
        self.customer = self.env['res.partner'].create({'name': 'Customer', 'phone': '+91 98765 43210'})
        self.meta_chat = self.env['discuss.channel'].create({
            'name': 'Customer', 'channel_type': 'whatsapp', 'whatsapp_number': '919876543210',
            'wa_account_id': self.meta_account.id, 'whatsapp_partner_id': self.customer.id,
        })
        self.meta_sends = []
        self.startPatcher(patch(META_SEND, lambda api, bsuid, number, *a, **k: (
            self.meta_sends.append(number) or {'msg_uid': f'wamid.{len(self.meta_sends)}'})))

    def test_meta_inbound_is_not_taken_over_nor_echoed(self):
        with self.mock_sidecar() as sidecar:
            self.meta_chat.message_post(body='Price please', message_type='whatsapp_message',
                                        author_id=self.customer.id, whatsapp_inbound_msg_uid='wamid.IN1')
            self.Message._send_cron()
        self.assertFalse(self.meta_chat.owa_account_id)
        self.assertFalse(self.Message.search([('message_type', '=', 'outbound')]))
        self.assertFalse(sidecar.called)

    def test_meta_reply_goes_out_once_through_meta(self):
        with self.mock_sidecar() as sidecar:
            self.meta_chat.with_user(self.env.ref('base.user_admin')).message_post(
                body='Here is the price', message_type='whatsapp_message')
            self.env['whatsapp.message']._send_cron()
            self.Message._send_cron()
        self.assertEqual(self.meta_sends, ['919876543210'])
        self.assertFalse(self.meta_chat.owa_account_id)
        self.assertFalse(sidecar.called)
