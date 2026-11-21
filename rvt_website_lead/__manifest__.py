{
    'name': 'Revert Website Leads',
    'version': '20.0.1.0.0',
    'category': 'Sales/CRM',
    'summary': 'Enquiry form on revert.co.in creates a CRM lead',
    'description': """
The static website https://revert.co.in posts its "Book my site visit" form to /api/lead; nginx on that
site proxies it to /rvt/lead on erp.revert.co.in (and blocks /rvt/lead on the ERP host itself).
Each enquiry becomes a crm.lead: source "Website (revert.co.in)", medium Website, the first sales team,
no salesperson, the form's answers in Notes. A hidden honeypot field drops bots silently.
    """,
    'author': 'Albatross',
    'license': 'LGPL-3',
    'depends': ['crm'],
    'data': [
        'data/utm_data.xml',
    ],
    'installable': True,
}
