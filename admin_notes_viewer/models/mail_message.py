from odoo import models, api

class MailMessage(models.Model):
    _inherit = 'mail.message'

    def action_open_related_document(self):
        """ Opens the related document form view for this message """
        self.ensure_one()
        if self.model and self.res_id:
            return {
                'type': 'ir.actions.act_window',
                'res_model': self.model,
                'res_id': self.res_id,
                'view_mode': 'form',
                'target': 'current',
            }
        return {
            'type': 'ir.actions.client', 
            'tag': 'display_notification', 
            'params': {
                'message': 'No related document found or document was deleted.', 
                'type': 'warning',
                'sticky': False,
            }
        }
