from odoo import _, api, fields, models
from odoo.exceptions import AccessError


class ProjectTask(models.Model):
    _inherit = 'project.task'

    # Hung off res_id exactly like core's own activity_ids, narrowed to MOM
    # entries by domain. Deliberately NOT keyed on mom_task_id: that is a
    # stored computed field, so the list would silently miss any activity
    # whose backfill had not run. One2many.read() forces active_test=False,
    # so closed entries are included without extra handling here or in the view.
    mom_activity_ids = fields.One2many(
        'mail.activity',
        'res_id',
        domain=[
            ('res_model', '=', 'project.task'),
            ('activity_type_id.is_mom', '=', True),
        ],
        string='MOM Entries',
        groups='base.group_user',
        help='Minutes of Meeting entries recorded on this task, open and closed.'
    )

    mom_meeting_ids = fields.One2many(
        'mom.meeting',
        'task_id',
        string='MOM Meetings',
        help='Legacy Minutes of Meeting records, superseded by MOM activities.'
    )

    mom_unsynced_count = fields.Integer(
        string='MOM Lines To Sync',
        compute='_compute_mom_unsynced_count',
        help='Legacy MOM meeting lines on this task with no MOM activity yet.'
    )

    agenda = fields.Text('Details', tracking=True)

    person_ids = fields.One2many(
        'person.person',
        'task_id',
        string='Responsibilities'
    )

    @api.depends('mom_meeting_ids')
    def _compute_mom_unsynced_count(self):
        lines = self.mapped('mom_meeting_ids')
        synced_ids = lines._find_synced_line_ids()
        for task in self:
            task.mom_unsynced_count = len([
                line for line in task.mom_meeting_ids if line.id not in synced_ids
            ])

    def action_sync_mom_activities(self):
        """Backfill MOM activities from this task's legacy MOM meeting lines."""
        if not self.env.user.has_group('project.group_project_manager'):
            raise AccessError(
                _('Only Project Managers can sync MOM activities.'))

        created, unmatched = self.mapped('mom_meeting_ids')._sync_to_activities()

        if not created:
            title = _('Nothing to sync')
            message = _('Every MOM meeting line on this task already has a MOM entry.')
            notification_type = 'info'
        else:
            title = _('MOM entries synced')
            message = _('%s MOM meeting line(s) synced.', created)
            if unmatched:
                message += _(
                    ' %s could not be matched to a contact — set "Related To" '
                    'manually on those entries.', unmatched)
            notification_type = 'warning' if unmatched else 'success'

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': title,
                'message': message,
                'type': notification_type,
                'next': {'type': 'ir.actions.act_window_close'},
            },
        }
