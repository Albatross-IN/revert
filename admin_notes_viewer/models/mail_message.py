from odoo import models, fields, api
from odoo.fields import Domain


class MailMessage(models.Model):
    _inherit = 'mail.message'

    # In Odoo 20 record_name is a non-stored compute without a search method;
    # the "Document Name" search field of this module relied on it being
    # stored in 18. Provide a search that resolves the related documents'
    # display names model by model.
    record_name = fields.Char(search='_search_record_name')

    def _search_record_name(self, operator, value):
        if operator in Domain.NEGATIVE_OPERATORS or not isinstance(value, str) or not value:
            return Domain.TRUE
        domains = []
        models_seen = self.sudo()._read_group(
            [('model', '!=', False), ('res_id', '!=', False)], groupby=['model'])
        for (model_name,) in models_seen:
            if model_name not in self.env:
                continue
            Model = self.env[model_name]
            if Model._abstract or Model._transient or not Model._rec_name:
                continue
            if Model._rec_name not in Model._fields or not Model._fields[Model._rec_name]._description_searchable:
                continue
            ids = Model.sudo().search([(Model._rec_name, operator, value)]).ids
            if ids:
                domains.append(Domain('model', '=', model_name) & Domain('res_id', 'in', ids))
        return Domain.OR(domains) if domains else Domain.FALSE

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
