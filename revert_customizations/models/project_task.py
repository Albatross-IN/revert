from odoo import models, fields


class ProjectTask(models.Model):
    _inherit = 'project.task'

    mom_meeting_ids = fields.One2many(
        'mom.meeting',
        'task_id',
        string='MOM Meetings',
        help='Minutes of Meeting records for this task'
    )

    agenda = fields.Text('Details', tracking=True, placeholder="Write opening agenda here...")

    person_ids = fields.One2many(
        'person.person',
        'task_id',
        string='Responsibilities'
    )