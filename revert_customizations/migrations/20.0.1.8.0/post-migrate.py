"""Give every MOM entry a visit date, then rank the visits.

Until now the day an entry was created stood in for the day of the visit.
That day is written into the new field for every existing entry, so the
field is made explicit and editable without inventing anything.

Visit numbers are then re-derived from those dates under the new rule: per
project, the earliest date minuted is visit 1, the next visit 2, and so on.
This overwrites numbers set by hand or by the wizard's old default, which had
been handing out visit 1 regardless of date; a number that disagrees with its
date's rank is wrong by definition now that the rank is the number.

Both steps skip what is already right, so this is safe to run again.
"""
import logging

from odoo import SUPERUSER_ID, api

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    if not version:
        return

    env = api.Environment(cr, SUPERUSER_ID, {})
    Activity = env['mail.activity'].with_context(active_test=False)

    # Straight SQL: an ORM write of the date would re-rank the project once
    # per entry, and the ranking is done once for all of them below anyway.
    # The timezone is the one context_today would use for this environment,
    # matching how the 1.6.0 renumbering read creation days.
    cr.execute("""
        UPDATE mail_activity AS a
           SET mom_visit_date = (a.create_date AT TIME ZONE 'UTC' AT TIME ZONE %s)::date
          FROM mail_activity_type AS t
         WHERE t.id = a.activity_type_id
           AND t.is_mom
           AND a.mom_visit_date IS NULL
    """, [env.user.tz or 'UTC'])
    dated = cr.rowcount
    Activity.invalidate_model(['mom_visit_date'])

    projects = Activity._read_group(
        [('activity_type_id.is_mom', '=', True), ('mom_project_id', '!=', False)],
        groupby=['mom_project_id'])
    renumbered = Activity._mom_renumber_visits(
        [project.id for project, in projects])

    _logger.info(
        'MOM visits: %s entry(ies) dated from their creation day; %s renumbered '
        'by date rank across %s project(s).', dated, renumbered, len(projects))
