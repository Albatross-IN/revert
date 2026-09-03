from odoo import api, models


class MomEntriesReport(models.AbstractModel):
    _name = 'report.revert_customizations.mom_entries_report'
    _description = 'MOM Entries Report'

    @api.model
    def _get_report_values(self, docids, data=None):
        """Rebuild the rows server-side from the filter state the dashboard sent,
        so the PDF matches exactly what is on screen — every matching entry,
        not just the page being viewed.
        """
        data = data or {}
        filters = data.get('filters') or {}
        # docids is empty when the action carried `data` (see
        # action_print_mom_entries), so fall back to the id passed in data.
        project_ids = docids or []
        if not project_ids and data.get('project_id'):
            project_ids = [data['project_id']]
        projects = self.env['project.project'].browse(project_ids)
        visits_by_project = {
            project.id: project._get_mom_report_groups(filters)
            for project in projects
        }
        return {
            'summary_by_project': {
                project_id: self._mom_visit_summary(visits)
                for project_id, visits in visits_by_project.items()
            },
            'doc_ids': projects.ids,
            'doc_model': 'project.project',
            'docs': projects,
            'visits_by_project': visits_by_project,
        }

    @api.model
    def _mom_visit_summary(self, visits):
        """Headline shown top-right of the page.

        A single visit gets its number and date; several get the span, and the
        individual dates stay on the per-visit headings in the body.
        """
        if not visits:
            return {'label': '', 'date': ''}
        if len(visits) == 1:
            return {
                'label': 'Visit %s' % visits[0]['visit_no'],
                'date': visits[0]['visit_date'],
            }
        numbers = [visit['visit_no'] for visit in visits]
        return {
            'label': 'Visits %s \u2013 %s' % (min(numbers), max(numbers)),
            'date': '',
        }
