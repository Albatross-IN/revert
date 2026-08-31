"""FR-10 — carry legacy mom.meeting lines over to MOM activities on upgrade.

The mapping itself lives in mom.meeting._sync_to_activities(), which is also
what the "Sync Activities" button calls, so the upgrade and the button can
never drift apart.
"""
import logging

from odoo import SUPERUSER_ID, api

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    if not version:
        return

    env = api.Environment(cr, SUPERUSER_ID, {})
    lines = env['mom.meeting'].search([('task_id', '!=', False)])
    if not lines:
        return

    created, unmatched = lines._sync_to_activities()
    _logger.info(
        'MOM migration: %s legacy line(s) migrated, %s with an unmatched Related To.',
        created, unmatched)
