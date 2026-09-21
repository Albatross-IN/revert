from collections import defaultdict

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError

MOM_RES_MODEL = 'project.task'


class MailActivity(models.Model):
    _inherit = 'mail.activity'

    is_mom = fields.Boolean(
        related='activity_type_id.is_mom',
        string='Is a MOM Entry'
    )
    mom_partner_id = fields.Many2one(
        'res.partner',
        string='Related To',
        ondelete='restrict',
        index='btree_not_null',
        help='The person or company this MOM point concerns.'
    )
    mom_site_photo = fields.Image(
        string='Site Photo',
        max_width=1920,
        max_height=1920,
        help='Photo of the site condition being minuted.'
    )
    mom_visit_date = fields.Date(
        string='Visit Date',
        default=fields.Date.context_today,
        help='The day the site visit this entry was minuted on took place. '
             'The Visit No# is the rank of this date among the dates minuted '
             'in the project.'
    )
    mom_visit_no = fields.Integer(
        string='Visit No#',
        readonly=True,
        copy=False,
        help='Which site visit this MOM entry belongs to: the first date '
             'minuted in the project is visit 1, the next visit 2, and so on. '
             'Derived from the Visit Date and never set by hand.'
    )
    mom_sequence = fields.Integer(
        string='Sequence',
        readonly=True,
        copy=False,
        help='Serial number of this MOM entry within its task.'
    )
    mom_task_id = fields.Many2one(
        'project.task',
        string='MOM Task',
        compute='_compute_mom_task_id',
        store=True,
        index='btree_not_null',
        ondelete='cascade',
        help='The task this MOM entry belongs to. res_id is a loose reference '
             'that cannot be joined or grouped on, so MOM entries carry a real '
             'relation for reporting.'
    )
    mom_project_id = fields.Many2one(
        'project.project',
        string='MOM Project',
        related='mom_task_id.project_id',
        store=True,
        index='btree_not_null',
        help='The project the MOM entry rolls up to. Recomputed by the ORM when '
             'a task is moved to another project.'
    )
    mom_meeting_id = fields.Many2one(
        'mom.meeting',
        string='Legacy MOM Line',
        ondelete='set null',
        copy=False,
        index='btree_not_null',
        help='The legacy MOM meeting line this entry was synced from. Its presence '
             'is what stops a line being synced twice.'
    )

    mom_end_date = fields.Date(
        string='End Date',
        compute='_compute_mom_end_date',
        help='The end date actually recorded for this MOM entry. Blank when '
             'none was ever recorded: date_deadline is required on an '
             'activity, so a date had to be inferred when the entry was '
             'synced, and that inferred date is not passed off as real.'
    )

    # ------------------------------------------------------------------
    # Reporting relations
    # ------------------------------------------------------------------

    @api.depends('mom_meeting_id.end_date', 'date_deadline', 'date_done', 'active')
    def _compute_mom_end_date(self):
        for activity in self:
            if activity.mom_meeting_id:
                # Synced from a legacy line: that line's end date is the truth,
                # blank when it never had one. Its date_done is only the moment
                # the sync archived it, which would be meaningless here.
                activity.mom_end_date = activity.mom_meeting_id.end_date
            elif not activity.active and activity.date_done:
                # Closed in Odoo: the date it was actually marked done, not the
                # deadline it was originally given.
                activity.mom_end_date = activity.date_done
            else:
                activity.mom_end_date = activity.date_deadline

    @api.depends('res_model', 'res_id', 'activity_type_id.is_mom')
    def _compute_mom_task_id(self):
        mom = self.filtered(
            lambda activity: activity.is_mom
            and activity.res_model == MOM_RES_MODEL
            and activity.res_id
        )
        (self - mom).mom_task_id = False
        if not mom:
            return
        # res_id can point at a task that no longer exists; storing it would
        # break the foreign key.
        live_ids = set(self.env[MOM_RES_MODEL].browse(
            set(mom.mapped('res_id'))).exists().ids)
        for activity in mom:
            activity.mom_task_id = (
                activity.res_id if activity.res_id in live_ids else False)

    # ------------------------------------------------------------------
    # Constraints
    # ------------------------------------------------------------------

    @api.constrains('activity_type_id', 'mom_partner_id')
    def _check_mom_partner_id(self):
        """Related To is mandatory on an open MOM entry.

        Archived entries are skipped so migrated history with an unmatched
        contact is never rejected.
        """
        for activity in self:
            if activity.active and activity.is_mom and not activity.mom_partner_id:
                raise ValidationError(
                    _('"Related To" is required on a MOM activity.')
                )

    # ------------------------------------------------------------------
    # Sequence
    # ------------------------------------------------------------------

    @api.model
    def _mom_local_date(self, timestamp):
        """The user-timezone calendar date of a stored UTC timestamp."""
        if not timestamp:
            return False
        return fields.Datetime.context_timestamp(self, timestamp).date()

    # Writes to these can change which visit an entry is in, or which
    # project's visits it counts towards.
    _MOM_VISIT_TRIGGERS = frozenset(
        ['mom_visit_date', 'activity_type_id', 'res_model', 'res_id'])

    @api.model
    def _mom_renumber_visits(self, project_ids):
        """Give every MOM entry in these projects its visit number.

        A visit is a day on site and its number is chronological: the earliest
        date minuted in the project is visit 1, the next date visit 2, and so
        on. The number is therefore a function of the project's dates, not
        anything stored per entry, and any change to a date re-ranks the
        whole project — a back-dated entry moves every later visit up by one.
        Closed entries count: a visit does not disappear when its points are
        settled.

        Returns how many entries changed number.
        """
        project_ids = [project_id for project_id in project_ids if project_id]
        if not project_ids:
            return 0
        entries = self.sudo().with_context(active_test=False).search([
            ('activity_type_id.is_mom', '=', True),
            ('mom_project_id', 'in', project_ids),
        ])
        by_project = defaultdict(list)
        for entry in entries:
            by_project[entry.mom_project_id.id].append(entry)

        changed = 0
        for project_entries in by_project.values():
            dates = sorted({e.mom_visit_date for e in project_entries if e.mom_visit_date})
            rank = {day: number for number, day in enumerate(dates, start=1)}
            for entry in project_entries:
                number = rank.get(entry.mom_visit_date, 0)
                if entry.mom_visit_no != number:
                    # Only the number moves, which is not a trigger, so this
                    # does not re-enter write()'s renumbering.
                    entry.write({'mom_visit_no': number})
                    changed += 1
        return changed

    @api.model
    def _mom_next_sequence(self, res_id, exclude_id=False):
        """Next serial number for MOM entries on the given task.

        Archived activities are counted, so a number freed by closing or
        deleting an entry is never handed out twice.
        """
        if not res_id:
            return 0
        domain = [
            ('res_model', '=', MOM_RES_MODEL),
            ('res_id', '=', res_id),
            ('activity_type_id.is_mom', '=', True),
        ]
        if exclude_id:
            domain.append(('id', '!=', exclude_id))
        last = self.sudo().with_context(active_test=False).search(
            domain, order='mom_sequence desc', limit=1)
        return (last.mom_sequence or 0) + 1

    # ------------------------------------------------------------------
    # Defaults
    # ------------------------------------------------------------------

    @api.onchange('activity_type_id')
    def _onchange_activity_type_id_mom(self):
        """Suggest the task's customer as Related To."""
        if not self.is_mom or self.mom_partner_id:
            return
        if self.res_model == MOM_RES_MODEL and self.res_id:
            task = self.env[MOM_RES_MODEL].browse(self.res_id).exists()
            if task.partner_id:
                self.mom_partner_id = task.partner_id

    # ------------------------------------------------------------------
    # Dashboard actions
    # ------------------------------------------------------------------

    def action_mom_open_form(self):
        """Open this entry in Odoo's own activity dialog.

        The MOM dashboard is a client action with no record behind it, so
        editing an entry goes through the standard activity popup rather than
        a bespoke form. That popup already carries the MOM fields, and its
        footer buttons work here because the record is a real one rather than
        a one2many line being staged on a parent form.
        """
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('MOM Entry'),
            'res_model': 'mail.activity',
            'res_id': self.id,
            'view_mode': 'form',
            'views': [(self.env.ref('mail.mail_activity_view_form_popup').id, 'form')],
            'target': 'new',
        }

    def action_mom_mark_done(self, feedback=None):
        """Close MOM entries from the dashboard, recording the closing note.

        A guard over the standard action_feedback rather than a reimplementation
        of it: the note still reaches the task's chatter the usual way, and
        keep_done on the MOM type archives the entry instead of deleting it, so
        it stays in the report as Closed. The guard is what stops the dashboard
        being a route to completing any activity in the database by id.
        """
        if any(not activity.is_mom for activity in self):
            raise UserError(
                _('Only MOM entries can be closed from the MOM dashboard.'))
        open_entries = self.filtered('active')
        if not open_entries:
            raise UserError(_('This MOM entry is already closed.'))
        open_entries.action_feedback(feedback=feedback or False)
        return True

    # ------------------------------------------------------------------
    # CRUD
    # ------------------------------------------------------------------

    @api.model_create_multi
    def create(self, vals_list):
        activities = super().create(vals_list)
        for activity in activities:
            if (activity.is_mom and not activity.mom_sequence
                    and activity.res_model == MOM_RES_MODEL):
                activity.mom_sequence = self._mom_next_sequence(
                    activity.res_id, exclude_id=activity.id)
        self._mom_renumber_visits(
            set(activities.filtered('is_mom').mapped('mom_project_id').ids))
        return activities

    def write(self, vals):
        becoming_mom = leaving_mom = self.browse()
        if 'activity_type_id' in vals:
            new_type = self.env['mail.activity.type'].browse(vals['activity_type_id'])
            if new_type.is_mom:
                becoming_mom = self.filtered(lambda a: not a.is_mom)
            else:
                leaving_mom = self.filtered('is_mom')

        # Projects whose visits may re-rank: the ones the entries are in now,
        # and the ones they end up in after the write.
        renumber = set()
        if vals.keys() & self._MOM_VISIT_TRIGGERS:
            renumber |= set(self.filtered('is_mom').mapped('mom_project_id').ids)

        res = super().write(vals)

        if vals.keys() & self._MOM_VISIT_TRIGGERS:
            renumber |= set(self.filtered('is_mom').mapped('mom_project_id').ids)
            self._mom_renumber_visits(renumber)

        if leaving_mom:
            # The fields no longer apply: drop the values so nothing orphaned
            # is printed on the MOM report.
            super(MailActivity, leaving_mom).write({
                'mom_partner_id': False,
                'mom_site_photo': False,
                'mom_sequence': 0,
                'mom_visit_no': 0,
            })
        for activity in becoming_mom:
            if not activity.mom_sequence and activity.res_model == MOM_RES_MODEL:
                super(MailActivity, activity).write({
                    'mom_sequence': self._mom_next_sequence(
                        activity.res_id, exclude_id=activity.id),
                })
        return res

    def unlink(self):
        # Deleting the last entry of a date removes that visit, so the ones
        # after it close up.
        project_ids = set(self.filtered('is_mom').mapped('mom_project_id').ids)
        res = super().unlink()
        self._mom_renumber_visits(project_ids)
        return res
