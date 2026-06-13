{
    'name': 'Admin Notes Viewer',
    'version': '18.0.1.0.0',
    'category': 'Administration',
    'summary': 'View all logged notes and completed activities globally.',
    'description': """
        Provides a global view for System Administrators to monitor manually typed notes
        and activity completion summaries across all objects in Odoo.
    """,
    'author': 'Your Company',
    'depends': ['mail', 'base'],
    'data': [
        'views/mail_message_views.xml',
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
