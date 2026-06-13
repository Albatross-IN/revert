{
    'name': 'Revert Customizations',
    'version': '18.0.1.0.0',
    'category': 'Project',
    'summary': 'Custom project task enhancements with MOM meetings',
    'description': """
        This module extends project tasks with MOM (Minutes of Meeting) functionality.
        Features:
        - Add MOM meeting records to project tasks
        - Auto-incremental sequence per task
        - Track meeting details and site photos
    """,
    'author': 'Your Company',
    'website': 'https://www.yourcompany.com',
    'depends': ['project', 'project_enterprise'],
    'data': [
        'security/ir.model.access.csv',
        'views/project_task_views.xml',
        'views/project_task_report.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}