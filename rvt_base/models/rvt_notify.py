import logging

from odoo import api, models

_logger = logging.getLogger(__name__)


class RvtNotify(models.AbstractModel):
    """The one door for messages to people. Other modules never send by themselves; they call

        self.env["rvt.notify"].send(event, record, recipients, **values)

    Until the WhatsApp module (rvt_notify) is installed nothing leaves: the call is
    written to the server log and reported as held."""
    _name = "rvt.notify"
    _description = "Revert messages"

    @api.model
    def send(self, event, record, recipients, **values):
        """event: a key such as 'drawing_released'; record: what it is about;
        recipients: partners (agency people, client contacts) or users (staff).
        Returns the number of messages that left."""
        _logger.info(
            "rvt.notify held (no sender installed): %s on %s for %s", event,
            "%s,%s" % (record._name, record.id) if record else "-", recipients.mapped("display_name") if recipients else [])
        return 0

    @api.model
    def sending_on(self):
        return False
