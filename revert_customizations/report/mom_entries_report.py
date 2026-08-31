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
        return {
            'doc_ids': projects.ids,
            'doc_model': 'project.project',
            'docs': projects,
            'rows_by_project': {
                project.id: project._get_mom_report_rows(filters)
                for project in projects
            },
        }
