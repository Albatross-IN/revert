from odoo import models, fields, api


class MomMeeting(models.Model):
    _name = 'mom.meeting'
    _description = 'Minutes of Meeting'
    _order = 'task_id, seq'

    task_id = fields.Many2one(
        'project.task',
        string='Task',
        required=True,
        ondelete='cascade'
    )
    seq = fields.Integer(
        string='Sequence',
        readonly=True,
        help='Auto-incremental sequence per task'
    )
    remarks = fields.Char(
        string='Remarks',
        help='Meeting remarks or notes'
    )
    related_to = fields.Char(
        string='Related To',
        help='What this meeting is related to'
    )
    end_date = fields.Date(
        string='End Date',
        help='Meeting end date'
    )
    site_photo = fields.Binary(
        string='Site Photo',
        help='Photo from the meeting site'
    )

    @api.model_create_multi
    def create(self, vals_list):
        """Auto-populate sequence when creating new records"""
        for vals in vals_list:
            if 'task_id' in vals and not vals.get('seq'):
                # Get the next sequence number for this task
                last_seq = self.search([
                    ('task_id', '=', vals['task_id'])
                ], order='seq desc', limit=1)
                vals['seq'] = (last_seq.seq + 1) if last_seq else 1
        return super().create(vals_list)

class Personas(models.Model):
    _name = 'person.person'
    _description = 'Personas'
    _order = 'task_id, seq'

    task_id = fields.Many2one(
        'project.task',
        string='Task',
        required=True,
        ondelete='cascade'
    )
    seq = fields.Integer(
        string='Sequence',
        readonly=True,
        help='Auto-incremental sequence per task'
    )
    from_client = fields.Char(
        string='From client'
    )
    from_architect = fields.Char(
        string='From Architect'
    )
    from_agency = fields.Char(
        string='From Contractor / Agency'
    )

    @api.model_create_multi
    def create(self, vals_list):
        """Auto-populate sequence when creating new records"""
        for vals in vals_list:
            if 'task_id' in vals and not vals.get('seq'):
                # Get the next sequence number for this task
                last_seq = self.search([
                    ('task_id', '=', vals['task_id'])
                ], order='seq desc', limit=1)
                vals['seq'] = (last_seq.seq + 1) if last_seq else 1
        return super().create(vals_list)