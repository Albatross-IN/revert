from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    rvt_release_needs_approval = fields.Boolean(
        string="Release needs the principal's approval",
        config_parameter="rvt.release_needs_approval", default=True)
    rvt_client_points_need_confirmation = fields.Boolean(
        string="Client points are confirmed by the office first",
        config_parameter="rvt.client_points_need_confirmation", default=True)
    rvt_limit_not_opened_days = fields.Integer(
        string="Released drawing not opened after (days)",
        config_parameter="rvt.limit_not_opened_days", default=2)
    rvt_limit_question_days = fields.Integer(
        string="Question unanswered after (working days)",
        config_parameter="rvt.limit_question_days", default=1)
    rvt_limit_bill_review_days = fields.Integer(
        string="Bill not reviewed after (days)",
        config_parameter="rvt.limit_bill_review_days", default=3)
    rvt_limit_stuck_days = fields.Integer(
        string="A project is stuck when a blocker is older than (days)",
        config_parameter="rvt.limit_stuck_days", default=7)
