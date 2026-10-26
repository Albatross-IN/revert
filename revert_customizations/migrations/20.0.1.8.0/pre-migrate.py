"""Create the mom_visit_date column ahead of the ORM.

The field carries a default of today. When the ORM adds a column for a field
with a default it stamps every existing row with that default, which here
would date every historical MOM entry to the day of the upgrade and leave
nothing for the post-migration to backfill. Creating the bare column first
means the ORM finds it in place and leaves the rows NULL.
"""
from odoo.tools.sql import column_exists, create_column


def migrate(cr, version):
    if not version:
        return
    if not column_exists(cr, 'mail_activity', 'mom_visit_date'):
        create_column(cr, 'mail_activity', 'mom_visit_date', 'date')
