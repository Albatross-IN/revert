from odoo import _, api, fields, models

ENTRIES_PAGE_SIZE = 100
MOM_DATE_FORMAT = '%d-%b-%Y'
TOP_N = 10

# Colours for the "Top Related To" chart, applied by rank. The dashboard reads
# them off the payload rather than keeping its own copy, and the PDF paints the
# Related To cell from the same list, so a contact carries one colour from the
# chart through to the printout.
MOM_PARTNER_PALETTE = [
    '#0E6C7A', '#4B7BE5', '#C97A2B', '#5B8C5A', '#8B5CA8',
    '#B4544E', '#3F7F93', '#A9862F', '#6E7B8B', '#7C5CBF',
]


class ProjectProject(models.Model):
    _inherit = 'project.project'

    mom_activity_count = fields.Integer(
        string='MOM Entries',
        compute='_compute_mom_activity_count'
    )

    def _compute_mom_activity_count(self):
        counts = {}
        if self.ids:
            grouped = self.env['mail.activity'].with_context(active_test=False)._read_group(
                [('mom_project_id', 'in', self.ids),
                 ('activity_type_id.is_mom', '=', True)],
                groupby=['mom_project_id'],
                aggregates=['__count'],
            )
            counts = {project.id: count for project, count in grouped}
        for project in self:
            project.mom_activity_count = counts.get(project.id, 0)

    # ------------------------------------------------------------------
    # Actions
    # ------------------------------------------------------------------

    def action_open_mom_dashboard(self):
        """Open the MOM dashboard client action for this project."""
        self.ensure_one()
        return {
            'type': 'ir.actions.client',
            'tag': 'mom_dashboard',
            'name': _('MOM Dashboard'),
            'params': {
                'project_id': self.id,
                'project_name': self.display_name,
            },
            'context': {'active_id': self.id, 'active_model': 'project.project'},
        }

    # ------------------------------------------------------------------
    # Dashboard data
    # ------------------------------------------------------------------

    def _get_mom_base_domain(self):
        """Every MOM entry in this project, open and closed."""
        self.ensure_one()
        return [
            ('mom_project_id', '=', self.id),
            ('activity_type_id.is_mom', '=', True),
        ]

    def _get_mom_domain(self, filters=None):
        """The base domain narrowed by the dashboard's filter state.

        The single place a dashboard domain is built, so the totals, the charts
        and the table can never disagree about what is being counted.
        """
        self.ensure_one()
        filters = filters or {}
        domain = self._get_mom_base_domain()
        today = fields.Date.context_today(self)

        status = filters.get('status') or 'all'
        if status == 'open':
            domain += [('active', '=', True)]
        elif status == 'overdue':
            domain += [('active', '=', True), ('date_deadline', '<', today)]
        elif status == 'done':
            domain += [('active', '=', False)]

        if filters.get('date_from'):
            domain += [('date_deadline', '>=', filters['date_from'])]
        if filters.get('date_to'):
            domain += [('date_deadline', '<=', filters['date_to'])]
        if filters.get('partner_ids'):
            domain += [('mom_partner_id', 'in', filters['partner_ids'])]
        if filters.get('user_ids'):
            domain += [('user_id', 'in', filters['user_ids'])]
        if filters.get('task_ids'):
            domain += [('mom_task_id', 'in', filters['task_ids'])]
        if filters.get('visit_nos'):
            domain += [('mom_visit_no', 'in', filters['visit_nos'])]
        if filters.get('with_photo'):
            domain += [('mom_site_photo', '!=', False)]
        return domain

    def _get_mom_kpis(self, Activity, domain, today):
        open_total = Activity.search_count(domain + [('active', '=', True)])
        overdue = Activity.search_count(
            domain + [('active', '=', True), ('date_deadline', '<', today)])
        contacts = Activity._read_group(
            domain + [('mom_partner_id', '!=', False)],
            groupby=['mom_partner_id'],
        )
        return {
            'total': Activity.search_count(domain),
            'open': open_total,
            'overdue': overdue,
            'due_later': open_total - overdue,
            'done': Activity.search_count(domain + [('active', '=', False)]),
            'contacts': len(contacts),
            'photos': Activity.search_count(domain + [('mom_site_photo', '!=', False)]),
        }

    def _get_mom_by_period(self, Activity, domain):
        """Entries per month, split open vs closed, oldest first."""
        grouped = Activity._read_group(
            domain + [('date_deadline', '!=', False)],
            groupby=['date_deadline:month', 'active'],
            aggregates=['__count'],
        )
        buckets = {}
        for month, is_open, count in grouped:
            if not month:
                continue
            key = fields.Date.to_string(month)[:7]
            bucket = buckets.setdefault(key, {
                'key': key,
                'label': month.strftime('%b %Y'),
                'open': 0,
                'done': 0,
            })
            bucket['open' if is_open else 'done'] += count
        return [buckets[key] for key in sorted(buckets)]

    def _get_mom_partner_ranking(self, Activity, domain):
        """Contacts of the filtered entries, busiest first, each with a colour.

        Ordered and capped in Python rather than by SQL. The dashboard and the
        PDF build this list in separate requests and have to agree on which
        contact got which colour; `order='__count DESC'` leaves ties to the
        database, which is free to return them either way round.
        """
        self.ensure_one()
        grouped = Activity._read_group(
            domain + [('mom_partner_id', '!=', False)],
            groupby=['mom_partner_id'], aggregates=['__count'])
        ranked = sorted(
            grouped,
            key=lambda group: (-group[1], group[0].display_name, group[0].id),
        )[:TOP_N]
        return [
            {
                'id': partner.id,
                'label': partner.display_name,
                'value': count,
                'color': MOM_PARTNER_PALETTE[index % len(MOM_PARTNER_PALETTE)],
            }
            for index, (partner, count) in enumerate(ranked)
        ]

    def _mom_contrast_ink(self, color):
        """Black or white text, whichever stays readable on `color`."""
        red, green, blue = (int(color[index:index + 2], 16) for index in (1, 3, 5))
        luma = (0.2126 * red + 0.7152 * green + 0.0722 * blue) / 255
        return '#111111' if luma > 0.6 else '#FFFFFF'

    def _get_mom_partner_styles(self, filters=None):
        """Contact id -> the cell style matching that contact's bar on screen.

        Contacts outside the chart's top ten are absent, so they print
        unhighlighted rather than being given a colour the chart never showed.
        """
        self.ensure_one()
        Activity = self.env['mail.activity'].with_context(active_test=False)
        ranking = self._get_mom_partner_ranking(
            Activity, self._get_mom_domain(filters))
        return {
            row['id']: 'background-color: %s; color: %s;' % (
                row['color'], self._mom_contrast_ink(row['color']))
            for row in ranking
        }

    def _format_mom_date(self, value):
        """Dates are shown as 07-Sep-2026 throughout the MOM screens."""
        return value.strftime(MOM_DATE_FORMAT) if value else ''

    def _get_mom_entry_records(self, filters=None, offset=0, limit=None):
        """The MOM entries matching the filters, in serial order."""
        self.ensure_one()
        return self.env['mail.activity'].with_context(active_test=False).search(
            self._get_mom_domain(filters), order='mom_sequence, id',
            offset=offset, limit=limit)

    def _get_mom_entry_status(self, entry, today):
        if not entry.active:
            return 'done'
        if entry.date_deadline and entry.date_deadline < today:
            return 'overdue'
        return 'open'

    def _get_mom_report_rows(self, filters=None):
        """Every matching entry, unpaginated, for the PDF."""
        self.ensure_one()
        today = fields.Date.context_today(self)
        partner_styles = self._get_mom_partner_styles(filters)
        rows = []
        for entry in self._get_mom_entry_records(filters):
            created = (
                fields.Datetime.context_timestamp(self, entry.create_date)
                if entry.create_date else False)
            rows.append({
                'entry': entry,
                'sequence': entry.mom_sequence,
                'visit_no': entry.mom_visit_no,
                'task': entry.mom_task_id.display_name or entry.res_name or '',
                'summary': entry.summary or '',
                'partner': entry.mom_partner_id.display_name or '',
                'partner_style': partner_styles.get(entry.mom_partner_id.id, ''),
                'user': entry.user_id.display_name or '',
                'created': self._format_mom_date(created),
                'created_date': created.date() if created else False,
                'end_date': self._format_mom_date(entry.mom_end_date),
                'status': self._get_mom_entry_status(entry, today).capitalize(),
            })
        return rows

    def _get_mom_report_groups(self, filters=None):
        """Report rows grouped by visit, each with the date that visit ran.

        The visit date is taken from when its entries were recorded. Entries
        of one visit normally share a day; when they do not, the span is shown
        rather than picking one date and implying the rest.
        """
        self.ensure_one()
        groups = {}
        for row in self._get_mom_report_rows(filters):
            visit_no = row['visit_no'] or 0
            group = groups.setdefault(visit_no, {'visit_no': visit_no, 'rows': [], 'dates': []})
            group['rows'].append(row)
            if row['created_date']:
                group['dates'].append(row['created_date'])

        result = []
        for visit_no in sorted(groups):
            group = groups[visit_no]
            dates = sorted(group.pop('dates'))
            if dates:
                first = self._format_mom_date(dates[0])
                last = self._format_mom_date(dates[-1])
                group['visit_date'] = first if first == last else '%s – %s' % (first, last)
            else:
                group['visit_date'] = ''
            result.append(group)
        return result

    def action_print_mom_entries(self, filters=None):
        """PDF of the entries currently filtered on the dashboard."""
        self.ensure_one()
        # The id has to travel inside `data`: once an action carries data, the
        # web client builds /report/pdf/<name>?options=... and drops the record
        # ids from the URL path (web/.../reports/utils.js), so docids arrives
        # empty in _get_report_values.
        return self.env.ref(
            'revert_customizations.action_report_mom_entries'
        ).report_action(self, data={
            'project_id': self.id,
            'filters': filters or {},
        })

    def _get_mom_entries(self, Activity, domain, offset):
        entries = Activity.search(
            domain, order='mom_sequence, id',
            limit=ENTRIES_PAGE_SIZE, offset=offset)
        today = fields.Date.context_today(self)
        rows = []
        for entry in entries:
            created = (
                fields.Datetime.context_timestamp(self, entry.create_date)
                if entry.create_date else False)
            # mom_end_date is blank when no end date was ever recorded, so an
            # inferred deadline is never shown as if it were real. Same field
            # backs the task form's list, so the two always agree.
            end_date = entry.mom_end_date
            status = self._get_mom_entry_status(entry, today)
            rows.append({
                'id': entry.id,
                'sequence': entry.mom_sequence,
                'visit_no': entry.mom_visit_no,
                'summary': entry.summary or '',
                'task_id': entry.mom_task_id.id,
                'task_name': entry.mom_task_id.display_name or entry.res_name or '',
                'partner_name': entry.mom_partner_id.display_name or '',
                'user_name': entry.user_id.display_name or '',
                'date_deadline': self._format_mom_date(end_date),
                'created': self._format_mom_date(created),
                'created_full': (
                    created.strftime(MOM_DATE_FORMAT + ' %H:%M') if created else ''),
                'has_photo': bool(entry.mom_site_photo),
                'status': status,
            })
        return rows

    def _get_mom_filter_options(self, Activity):
        """Values that actually occur in this project's entries.

        Built from the unfiltered domain so narrowing one filter never empties
        the choices offered by another.
        """
        base = self._get_mom_base_domain()
        partners = Activity._read_group(
            base + [('mom_partner_id', '!=', False)],
            groupby=['mom_partner_id'], aggregates=['__count'])
        users = Activity._read_group(
            base + [('user_id', '!=', False)],
            groupby=['user_id'], aggregates=['__count'])
        tasks = Activity._read_group(
            base + [('mom_task_id', '!=', False)],
            groupby=['mom_task_id'], aggregates=['__count'])
        visits = Activity._read_group(
            base, groupby=['mom_visit_no'], aggregates=['__count'])
        as_options = lambda grouped: sorted(
            [{'id': record.id, 'name': record.display_name, 'count': count}
             for record, count in grouped],
            key=lambda option: (-option['count'], option['name']))
        return {
            'partners': as_options(partners),
            'users': as_options(users),
            'tasks': as_options(tasks),
            # Same {id, name, count} shape as the record-based options, so the
            # dashboard's picker component handles it unchanged.
            'visits': [
                {'id': visit_no, 'name': 'Visit %s' % visit_no, 'count': count}
                for visit_no, count in sorted(visits, key=lambda group: group[0] or 0)
            ],
        }

    def get_mom_dashboard_data(self, filters=None):
        """One payload per dashboard render.

        Aggregation stays on the server: the client sends a filter state and
        receives finished numbers. Runs in the user's environment, so record
        rules apply to the totals as well as to the rows.
        """
        self.ensure_one()
        filters = filters or {}
        Activity = self.env['mail.activity'].with_context(active_test=False)
        domain = self._get_mom_domain(filters)
        today = fields.Date.context_today(self)

        kpis = self._get_mom_kpis(Activity, domain, today)

        by_task = Activity._read_group(
            domain + [('mom_task_id', '!=', False)],
            groupby=['mom_task_id'], aggregates=['__count'],
            order='__count DESC', limit=TOP_N)

        offset = max(int(filters.get('offset') or 0), 0)
        return {
            'project_id': self.id,
            'project_name': self.display_name,
            'kpis': kpis,
            'by_status': [
                {'label': _('Due later'), 'value': kpis['due_later'], 'key': 'open'},
                {'label': _('Overdue'), 'value': kpis['overdue'], 'key': 'overdue'},
                {'label': _('Closed'), 'value': kpis['done'], 'key': 'done'},
            ],
            'by_partner': self._get_mom_partner_ranking(Activity, domain),
            'by_task': [
                {'id': task.id, 'label': task.display_name, 'value': count}
                for task, count in by_task
            ],
            'by_period': self._get_mom_by_period(Activity, domain),
            'entries': self._get_mom_entries(Activity, domain, offset),
            'entries_total': kpis['total'],
            'offset': offset,
            'page_size': ENTRIES_PAGE_SIZE,
            'filter_options': self._get_mom_filter_options(Activity),
        }
