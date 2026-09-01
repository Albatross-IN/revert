"""Renumber MOM visits by creation date.

A visit is now a day on site: every MOM entry recorded on the same date in the
same project belongs to one visit. Entries created before that rule existed all
carry the field default of 1, so they are renumbered here — per project,
oldest date first.

This overwrites visit numbers that were set by hand. Under the new rule a
number that disagrees with its entry's date is inconsistent by definition, and
leaving a mix of hand-set and date-derived numbers would make the dashboard's
visit filter untrustworthy.
"""
import logging
from collections import defaultdict

from odoo import SUPERUSER_ID, api

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    if not version:
        return

    env = api.Environment(cr, SUPERUSER_ID, {})
    Activity = env['mail.activity'].with_context(active_test=False)

    entries = Activity.search([
        ('activity_type_id.is_mom', '=', True),
        ('mom_project_id', '!=', False),
    ], order='create_date, id')
    if not entries:
        return

    by_project = defaultdict(lambda: defaultdict(list))
    for entry in entries:
        day = Activity._mom_local_date(entry.create_date)
        by_project[entry.mom_project_id.id][day].append(entry.id)

    renumbered = 0
    for days in by_project.values():
        for visit_no, day in enumerate(sorted(days, key=lambda d: (d is None, d)), start=1):
            batch = Activity.browse(days[day])
            stale = batch.filtered(lambda entry: entry.mom_visit_no != visit_no)
            if stale:
                stale.mom_visit_no = visit_no
                renumbered += len(stale)

    _logger.info(
        'MOM visits: %s entry(ies) renumbered across %s project(s).',
        renumbered, len(by_project))
