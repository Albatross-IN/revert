"""Restore the real creation date on already-synced MOM entries.

Entries created by the earlier sync carry the timestamp of the sync run rather
than the date the minute was actually recorded, which made every migrated row
show the same "Created" date. The true value is on the mom.meeting line each
entry was synced from.

Done in SQL: create_date is an audit column, and this is a one-off correction
of historic rows, not a business write.
"""
import logging

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    if not version:
        return

    cr.execute("""
        UPDATE mail_activity a
           SET create_date = m.create_date,
               create_uid  = COALESCE(m.create_uid, a.create_uid)
          FROM mom_meeting m
         WHERE a.mom_meeting_id = m.id
           AND m.create_date IS NOT NULL
           AND a.create_date IS DISTINCT FROM m.create_date
    """)
    _logger.info(
        'MOM entries: creation date corrected on %s synced entry(ies).', cr.rowcount)
