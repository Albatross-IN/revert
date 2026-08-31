from odoo import api, fields, models

MOM_RES_MODEL = 'project.task'


class MailActivitySchedule(models.TransientModel):
    """The chatter's "Schedule Activity" dialog is this wizard, not a
    mail.activity form, so the MOM fields have to be offered here too and
    handed to the activity the wizard creates.
    """
    _inherit = 'mail.activity.schedule'

    is_mom = fields.Boolean(
        related='activity_type_id.is_mom',
        string='Is a MOM Entry'
    )
    mom_partner_id = fields.Many2one(
        'res.partner',
        string='Related To',
        compute='_compute_mom_partner_id',
        store=True,
        readonly=False,
        help='The person or company this MOM point concerns.'
    )
    mom_site_photo = fields.Image(
        string='Site Photo',
        max_width=1920,
        max_height=1920,
        help='Photo of the site condition being minuted.'
    )
    mom_sequence = fields.Integer(
        string='Sr. No.',
        compute='_compute_mom_sequence',
        help='Serial number this MOM entry will take on the task.'
    )

    def _mom_single_task(self):
        """The task being minuted, when the wizard applies to exactly one."""
        self.ensure_one()
        if not self.activity_type_id.is_mom or self.res_model != MOM_RES_MODEL:
            return self.env[MOM_RES_MODEL]
        records = self._get_applied_on_records()
        return records if len(records) == 1 else self.env[MOM_RES_MODEL]

    @api.depends('activity_type_id', 'res_ids')
    def _compute_mom_partner_id(self):
        """Suggest the task's customer as Related To."""
        for wizard in self:
            if not wizard.activity_type_id.is_mom:
                wizard.mom_partner_id = False
            elif not wizard.mom_partner_id:
                task = wizard._mom_single_task()
                wizard.mom_partner_id = task.partner_id.id or False

    @api.depends('activity_type_id', 'res_ids')
    def _compute_mom_sequence(self):
        """Show the number this entry will be given, before it is created."""
        for wizard in self:
            task = wizard._mom_single_task()
            wizard.mom_sequence = self.env['mail.activity']._mom_next_sequence(task.id)

    def _action_schedule_activities(self):
        """Carry the MOM values into the activity being created.

        activity_schedule() builds its create values from the ambient context,
        so default_* is enough and the core call stays untouched.
        """
        if self.activity_type_id.is_mom:
            self = self.with_context(
                default_mom_partner_id=self.mom_partner_id.id,
                default_mom_site_photo=self.mom_site_photo,
            )
        return super(MailActivitySchedule, self)._action_schedule_activities()
