from odoo.tests import HttpCase, tagged

from .common import PDF, DrawingCommon


@tagged("post_install", "-at_install")
class TestDrawingLink(DrawingCommon, HttpCase):

    def test_link_records_the_first_opening(self):
        drawing = self.drawing("SB", "Switchboard details", "elec")
        self.release(drawing, [self.ag_elec, self.ag_pop])
        receipts = {r.partner_id: r for r in drawing.released_revision_id.receipt_ids}
        receipt = receipts[self.ag_elec]
        self.assertFalse(receipt.opened_on)
        response = self.url_open("/rvt/d/%s" % receipt.token)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers["Content-Type"], "application/pdf")
        self.assertIn("inline", response.headers["Content-Disposition"])
        self.assertTrue(response.content.startswith(b"%PDF"))
        receipt.invalidate_recordset()
        self.assertTrue(receipt.opened_on, "opening the link marks the drawing as opened")
        self.assertFalse(receipts[self.ag_pop].opened_on, "only for that receiver")
        self.assertEqual(self.url_open("/rvt/d/not-a-real-token").status_code, 404)
        # an old link shows the current revision once a new one is released to the same receiver
        old_token = receipt.token
        drawing.with_user(self.designer).action_new_revision()
        drawing.current_revision_id.file_name = "SB-01_rev2.pdf"
        self.release(drawing, [self.ag_elec])
        response = self.url_open("/rvt/d/%s" % old_token)
        self.assertIn("SB-01_rev2.pdf", response.headers["Content-Disposition"], "receivers only ever see the current revision")
        new_receipt = drawing.released_revision_id.receipt_ids
        new_receipt.invalidate_recordset()
        self.assertTrue(new_receipt.opened_on)
