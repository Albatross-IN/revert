"""Link MOM activities created by the 18.0.1.1.0 migration to their source line.

That migration ran before mail.activity.mom_meeting_id existed, so the entries
it created carry no link back to the mom.meeting line they came from. Without
this backfill the "Sync Activities" button would see those lines as unsynced
and create a second activity for each one.

Matching is on (task, sequence), which is what the 18.0.1.1.0 migration
preserved. Only archived activities are considered, and a legacy line already
linked to an activity is never linked twice.
"""
import logging

from odoo import SUPERUSER_ID, api

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    if not version:
        return

    env = api.Environment(cr, SUPERUSER_ID, {})
    Activity = env['mail.activity'].with_context(active_test=False)

    orphans = Activity.search([
        ('res_model', '=', 'project.task'),
        ('activity_type_id.is_mom', '=', True),
        ('mom_meeting_id', '=', False),
        ('active', '=', False),
    ])
    if not orphans:
        return

    linked = 0
    for activity in orphans:
        line = env['mom.meeting'].search([
            ('task_id', '=', activity.res_id),
            ('seq', '=', activity.mom_sequence),
        ], limit=1)
        if not line:
            continue
        if Activity.search_count([('mom_meeting_id', '=', line.id)]):
            continue
        activity.mom_meeting_id = line.id
        linked += 1

    _logger.info('MOM sync backfill: %s activity(ies) linked to their legacy line.', linked)
