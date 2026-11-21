from odoo import http
from odoo.http import request
from odoo.http.stream import content_disposition


class RvtDrawingLink(http.Controller):

    @http.route("/rvt/d/<string:token>", type="http", auth="public", readonly=False, sitemap=False)
    def open_drawing(self, token, **kw):
        """The link a receiver gets. It records the first opening and shows the drawing:
        always the revision that is current for that receiver, never an older one."""
        receipt = request.env["rvt.drawing.receipt"].sudo().search([("token", "=", token)], limit=1)
        if not receipt:
            return request.not_found()
        drawing = receipt.drawing_id
        current = drawing.released_revision_id
        mine = current.receipt_ids.filtered(lambda r: r.partner_id == receipt.partner_id)
        if mine:
            mine[:1]._rvt_mark_opened()
            revision = current
        else:
            # this receiver is not on the newer release: it keeps the revision it was sent
            receipt._rvt_mark_opened()
            revision = receipt.revision_id
        if not revision.file:
            return request.not_found()
        name = revision.file_name or "%s_rev%s.pdf" % (drawing.sheet_no, revision.number)
        return request.make_response(revision.file.content, headers=[
            ("Content-Type", "application/pdf"),
            ("Content-Disposition", content_disposition(name, "inline")),
            ("Cache-Control", "private, no-store"),
            ("X-Robots-Tag", "noindex"),
        ])
