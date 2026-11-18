# -*- coding: utf-8 -*-
import hashlib

from odoo import models, tools
from odoo.http.stream import Stream
from odoo.tools.image import image_process
from odoo.tools.mimetypes import guess_mimetype

# sha1 of Odoo's stock favicon, which the website module stores as the
# default value of ``website.favicon``
_STOCK_FAVICON_SHA1 = None


def _stock_favicon_sha1():
    global _STOCK_FAVICON_SHA1  # noqa: PLW0603
    if _STOCK_FAVICON_SHA1 is None:
        try:
            with tools.file_open('web/static/img/favicon.ico', 'rb') as f:
                _STOCK_FAVICON_SHA1 = hashlib.sha1(f.read()).hexdigest()
        except FileNotFoundError:
            _STOCK_FAVICON_SHA1 = ''
    return _STOCK_FAVICON_SHA1


class IrBinary(models.AbstractModel):
    _inherit = 'ir.binary'

    def _record_to_stream(self, record, field_name):
        """``/web/image/website/<id>/favicon`` (and any other favicon field)
        still holding Odoo's stock favicon → serve the brand favicon."""
        stream = super()._record_to_stream(record, field_name)
        if field_name != 'favicon' or record._name == 'res.company' or stream.type == 'url':
            return stream
        data = stream.read()
        if not data or hashlib.sha1(data).hexdigest() != _stock_favicon_sha1():
            return stream
        icon = self.env['identity.brand']._company().identity_icon
        if icon:
            data = icon.content
            try:
                data = image_process(data, size=(64, 64), crop='center')
            except Exception:  # noqa: BLE001 - keep the original bytes on unknown formats
                pass
            mimetype = guess_mimetype(data, default='image/png')
            return Stream(type='data', data=data, size=len(data), mimetype=mimetype,
                          download_name='favicon.svg' if mimetype == 'image/svg+xml' else 'favicon.png')
        return Stream.from_path('identity/static/src/img/brand/favicon.png')
