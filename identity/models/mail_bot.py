# -*- coding: utf-8 -*-
from markupsafe import Markup

from odoo import models


class MailBot(models.AbstractModel):
    _inherit = 'mail.bot'

    def _get_answer(self, channel, body, message, command=False):
        """The bot may answer with one message or a list of messages."""
        answer = super()._get_answer(channel, body, message, command=command)
        if isinstance(answer, list):
            return [self._identity_debrand_answer(item) for item in answer]
        return self._identity_debrand_answer(answer)

    def _identity_debrand_answer(self, answer):
        if not answer or 'Odoo' not in str(answer):
            return answer
        debranded = self.env['identity.brand'].debrand(str(answer))
        return Markup(debranded) if isinstance(answer, Markup) else debranded
