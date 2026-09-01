from datetime import datetime, time

import pytz

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

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
    mom_visit_no = fields.Integer(
        string='Visit No#',
        default=1,
        copy=False,
        help='Which site visit this MOM entry belongs to. Defaults to the '
             'number last used on the project, so a run of entries recorded '
             'for the same visit share it without being retyped.'
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

    @api.model
    def _mom_day_bounds_utc(self, day):
        """UTC range covering one calendar day in the user's timezone."""
        user_tz = pytz.timezone(self.env.user.tz or 'UTC')
        start = user_tz.localize(datetime.combine(day, time.min))
        end = user_tz.localize(datetime.combine(day, time.max))
        return (start.astimezone(pytz.UTC).replace(tzinfo=None),
                end.astimezone(pytz.UTC).replace(tzinfo=None))

    @api.model
    def _mom_visit_no_for_date(self, project_id, visit_date=None):
        """The visit number for a MOM recorded on `visit_date` in this project.

        A visit is a day on site: every MOM entry recorded on the same date in
        the same project belongs to the same visit and shares its number. A
        date with no entries yet opens the next visit.
        """
        if not project_id:
            return 1
        visit_date = visit_date or fields.Date.context_today(self)
        Activity = self.sudo().with_context(active_test=False)
        base = [
            ('activity_type_id.is_mom', '=', True),
            ('mom_project_id', '=', project_id),
        ]

        start, end = self._mom_day_bounds_utc(visit_date)
        same_day = Activity.search(
            base + [('create_date', '>=', start), ('create_date', '<=', end)],
            order='id desc', limit=1)
        if same_day:
            return same_day.mom_visit_no or 1

        highest = Activity.search(base, order='mom_visit_no desc', limit=1)
        return (highest.mom_visit_no or 0) + 1

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
        return activities

    def write(self, vals):
        becoming_mom = leaving_mom = self.browse()
        if 'activity_type_id' in vals:
            new_type = self.env['mail.activity.type'].browse(vals['activity_type_id'])
            if new_type.is_mom:
                becoming_mom = self.filtered(lambda a: not a.is_mom)
            else:
                leaving_mom = self.filtered('is_mom')

        res = super().write(vals)

        if leaving_mom:
            # The fields no longer apply: drop the values so nothing orphaned
            # is printed on the MOM report.
            super(MailActivity, leaving_mom).write({
                'mom_partner_id': False,
                'mom_site_photo': False,
                'mom_sequence': 0,
            })
        for activity in becoming_mom:
            if not activity.mom_sequence and activity.res_model == MOM_RES_MODEL:
                super(MailActivity, activity).write({
                    'mom_sequence': self._mom_next_sequence(
                        activity.res_id, exclude_id=activity.id),
                })
        return res
