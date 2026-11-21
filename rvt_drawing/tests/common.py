import base64

from odoo.addons.rvt_project.tests.common import RvtCommon

PDF = base64.b64encode(b"%PDF-1.4\n1 0 obj<</Type/Catalog>>endobj\ntrailer<</Root 1 0 R>>\n%%EOF\n").decode()


class DrawingCommon(RvtCommon):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.project, _ = cls.onboard()
        cls.Drawing = cls.env["rvt.drawing"]
        cls.client_partner = cls.project.rvt_client_id
        cls.client_contact = cls.project.rvt_client_contact_ids

    @classmethod
    def drawing(cls, code, title, trade=None, designer=None, due=5, for_client=False, needs=False, **extra):
        return cls.Drawing.create(dict({
            "project_id": cls.project.id, "code": code, "name": title,
            "trade_id": cls.trade[trade].id if trade else False,
            "designer_id": (designer or cls.designer).id, "due_date": cls.days(due),
            "for_client": for_client, "needs_client_approval": needs,
        }, **extra))

    def send(self, drawing, user=None, note=None):
        return drawing.with_user(user or self.designer).action_send_for_approval(PDF, None, note)

    def release(self, drawing, agencies=None, client=False, user=None):
        drawing = drawing.with_user(user or self.designer)
        if drawing.state in ("to_draw", "in_progress"):
            self.send(drawing)
        if drawing.state == "awaiting_approval":
            drawing.with_user(self.principal).action_approve()
        return drawing.action_release([a.id for a in (agencies or [])], client=client)
