import json
import logging
import re

from markupsafe import Markup

from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)

EMAIL_RE = re.compile(r'^[^\s@]+@[^\s@]+\.[^\s@]+$')

# form field -> label in the lead's Notes, in display order
DETAILS = [
    ('plan', 'Project'),
    ('property', 'Property'),
    ('area', 'Area (sq ft)'),
    ('city', 'City or area'),
    ('start', 'Start'),
    ('budget', 'Budget'),
    ('pref', 'Reach on'),
    ('note', 'Note'),
]


class RevertWebsiteLead(http.Controller):

    @http.route('/rvt/lead', type='http', auth='public', methods=['POST'], csrf=False, save_session=False)
    def website_lead(self, **kwargs):
        try:
            data = json.loads(request.httprequest.get_data(as_text=True) or '{}')
        except ValueError:
            return self._reply(400, error='bad_request')
        if not isinstance(data, dict):
            return self._reply(400, error='bad_request')

        def get(key, size=200):
            value = data.get(key)
            return str(value).strip()[:size] if value is not None else ''

        if get('website'):  # honeypot: humans never see this field
            _logger.info('website lead dropped (honeypot) from %s', request.httprequest.remote_addr)
            return self._reply(200, ok=True)

        name = get('name', 100)
        digits = re.sub(r'\D', '', get('phone', 30))
        digits = re.sub(r'^(91|0)(?=\d{10}$)', '', digits)
        email = get('email', 120)
        if len(name) < 2 or len(digits) != 10:
            return self._reply(400, error='invalid')
        if email and not EMAIL_RE.match(email):
            email = ''

        details = {key: get(key, 1000 if key == 'note' else 200) for key, _label in DETAILS}
        notes = Markup('<br/>').join(
            Markup('<b>%s:</b> %s') % (label, details[key]) for key, label in DETAILS if details[key]
        )
        env = request.env
        team = env['crm.team'].sudo().search([], limit=1)
        lead = env['crm.lead'].sudo().create({
            'name': f"Website: {details['plan'] or 'Enquiry'} - {name}",
            'contact_name': name,
            'phone': f'+91 {digits}',
            'email_from': email or False,
            'city': details['city'] or False,
            'description': Markup('<p>Enquiry from the website (revert.co.in)</p><p>%s</p>') % notes,
            'team_id': team.id or False,
            'user_id': False,
            'source_id': env.ref('rvt_website_lead.utm_source_revert_website').id,
            'medium_id': env.ref('utm.utm_medium_website').id,
        })
        _logger.info('website lead %s created from %s', lead.id, request.httprequest.remote_addr)
        return self._reply(200, ok=True)

    def _reply(self, status, **payload):
        return request.make_json_response(payload, status=status)
