from collections import defaultdict

from odoo import models, fields, api

MOM_ACTIVITY_TYPE_XMLID = 'revert_customizations.mail_activity_type_mom'


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

    # ------------------------------------------------------------------
    # Sync to MOM activities
    # ------------------------------------------------------------------

    def _find_synced_line_ids(self):
        """Ids of the lines in self that already have a MOM activity.

        Synced entries are archived, so the search has to ignore active_test
        or every line would look unsynced and be duplicated on every run.
        """
        if not self:
            return set()
        synced = self.env['mail.activity'].sudo().with_context(active_test=False).search([
            ('mom_meeting_id', 'in', self.ids),
        ])
        return set(synced.mapped('mom_meeting_id').ids)

    def _sync_to_activities(self):
        """Create one archived MOM activity per not-yet-synced line.

        This is a one-time backfill, not a mirror: a line that already has an
        activity is left alone, however it was edited afterwards. Both the
        "Sync Activities" button and the upgrade migration call this, so there
        is a single mapping in the codebase.

        :return: (created count, count whose Related To matched no contact)
        """
        activity_type = self.env.ref(MOM_ACTIVITY_TYPE_XMLID, raise_if_not_found=False)
        if not activity_type:
            return 0, 0

        synced_ids = self._find_synced_line_ids()
        lines = self.filtered(lambda line: line.task_id and line.id not in synced_ids)
        if not lines:
            return 0, 0

        Activity = self.env['mail.activity']
        Partner = self.env['res.partner']
        model_id = self.env['ir.model']._get_id('project.task')

        lines_by_task = defaultdict(lambda: self.browse())
        for line in lines.sorted(lambda line: (line.task_id.id, line.seq)):
            lines_by_task[line.task_id] += line

        # Grouped by project, not one flat batch. mail.activity.create()
        # subscribes followers with a single browse(res_ids).message_subscribe()
        # per user, and project.task.message_subscribe() removes each matching
        # project follower from that partner list. Tasks spanning two projects
        # that share a follower make it remove the same partner twice and raise
        # "list.remove(x): x not in list".
        vals_by_project = defaultdict(list)
        created = 0
        unmatched = 0

        for task, task_lines in lines_by_task.items():
            # Numbers already in use on the task, archived entries included.
            existing = Activity.sudo().with_context(active_test=False).search([
                ('res_model', '=', 'project.task'),
                ('res_id', '=', task.id),
                ('activity_type_id.is_mom', '=', True),
            ])
            taken = set(existing.mapped('mom_sequence'))
            highest = max(taken | {0})

            for line in task_lines:
                # Keep the legacy number when it is free, otherwise append
                # after the highest in use so no two entries share a Sr. No.
                if line.seq and line.seq not in taken:
                    sequence = line.seq
                else:
                    highest += 1
                    sequence = highest
                taken.add(sequence)
                highest = max(highest, sequence)

                partner = Partner
                if line.related_to:
                    partner = Partner.search(
                        [('name', '=', line.related_to.strip())], limit=1)

                note_parts = []
                if line.remarks:
                    note_parts.append(line.remarks)
                if line.related_to and not partner:
                    unmatched += 1
                    note_parts.append(
                        'Related To could not be matched to a contact: %s '
                        '(please set it manually).' % line.related_to)
                note = '<p>%s</p>' % '</p><p>'.join(note_parts) if note_parts else False

                vals_by_project[task.project_id.id].append({
                    'activity_type_id': activity_type.id,
                    'res_model_id': model_id,
                    'res_model': 'project.task',
                    'res_id': task.id,
                    'summary': line.remarks or 'MOM entry %s' % sequence,
                    'note': note,
                    'date_deadline': line.end_date or line.create_date.date(),
                    'user_id': line.create_uid.id or self.env.uid,
                    'mom_partner_id': partner.id or False,
                    'mom_site_photo': line.site_photo or False,
                    'mom_sequence': sequence,
                    'mom_meeting_id': line.id,
                    'active': False,
                    # Carry the legacy line's own audit stamps across. The ORM
                    # only defaults these (models.py: vals.setdefault), so a
                    # synced entry keeps the date the minute was really
                    # recorded instead of the date it was synced.
                    'create_date': line.create_date,
                    'create_uid': line.create_uid.id or self.env.uid,
                })

        for project_vals in vals_by_project.values():
            Activity.with_context(
                mail_activity_quick_update=True,
                mail_notrack=True,
                mom_skip_subscribe=True,
            ).create(project_vals)
            created += len(project_vals)
        return created, unmatched


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