{
    'name': 'Revert Customizations',
    'version': '18.0.1.6.0',
    'category': 'Project',
    'summary': 'Custom project task enhancements with MOM meetings',
    'description': """
        This module extends project tasks with MOM (Minutes of Meeting) functionality.
        Features:
        - A "MOM" activity type available only on project tasks
        - Related To, Site Photo and a per-task serial number on MOM activities
        - Completed MOM entries are kept, not deleted, so the MOM report stays complete
        - MOM PDF report driven by MOM activities
        - "Sync Activities" button to backfill MOM activities from legacy MOM lines
        - Per-project MOM dashboard with filters and charts
        - Visit No# on MOM entries, one visit per day on site per project
    """,
    'author': 'Your Company',
    'website': 'https://www.yourcompany.com',
    'license': 'LGPL-3',
    'depends': ['project', 'project_enterprise'],
    'data': [
        'security/ir.model.access.csv',
        'data/mail_activity_type_data.xml',
        'data/mom_sync_action.xml',
        'views/mail_activity_views.xml',
        'views/project_project_views.xml',
        'views/project_task_views.xml',
        'views/project_task_report.xml',
        'report/mom_entries_report_templates.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'revert_customizations/static/src/mom_dashboard/mom_dashboard.js',
            'revert_customizations/static/src/mom_dashboard/mom_dashboard.xml',
            'revert_customizations/static/src/mom_dashboard/mom_dashboard.scss',
        ],
    },
    'installable': True,
    'auto_install': False,
    'application': False,
}
