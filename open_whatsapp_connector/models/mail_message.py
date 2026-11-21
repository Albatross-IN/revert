from odoo import fields, models


class MailMessage(models.Model):
    _inherit = 'mail.message'

    message_type = fields.Selection(
        selection_add=[('whatsapp_message', 'WhatsApp Message')],
        ondelete={'whatsapp_message': 'set default'})
    owa_message_ids = fields.One2many(
        'owa.message', 'mail_message_id', string="WhatsApp Messages")

    def _store_message_fields(self, res, **kwargs):
        # Inject the delivery state (whatsappStatus) for WhatsApp messages so
        # the ✓✓ status icon renders on HISTORICAL messages too, plus the
        # "editable on WhatsApp" flag for the Discuss "Edit" action.
        # Odoo 20 port: mail.message._to_store()/Store.add_records_fields()
        # were removed; per-record values now go through the Store.FieldList
        # attr() API (same pattern as the official whatsapp module).
        super()._store_message_fields(res, **kwargs)

        def _owa(message):
            return message.sudo().owa_message_ids[:1]

        is_wa = lambda m: m.message_type == 'whatsapp_message'
        res.attr("whatsappStatus", lambda m: _owa(m).state or False, predicate=is_wa)
        res.attr("owaMessageId", lambda m: _owa(m).id or False, predicate=is_wa)

        def _editable(message):
            owa = _owa(message)
            acc = owa.wa_account_id
            return bool(
                owa.msg_uid
                and owa.message_type == 'outbound'
                and owa.state not in ('error', 'cancel')
                and acc and acc.connection_type == 'qr'
            )
        res.attr("owaEditable", _editable, predicate=is_wa)
