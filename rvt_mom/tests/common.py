from odoo.addons.rvt_drawing.tests.common import DrawingCommon

PNG = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg=="


class MomCommon(DrawingCommon):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Point = cls.env["rvt.point"]
        cls.Visit = cls.env["rvt.visit"]
        cls.kitchen = cls.project.rvt_entity_ids.filtered(lambda e: e.name == "Kitchen")
        cls.master = cls.project.rvt_entity_ids.filtered(lambda e: e.name == "Master bedroom")

    def start(self, user=None):
        return self.Visit.browse(self.Visit.with_user(user or self.coordinator).rvt_start(self.project.id))

    def add(self, text, kind="agency", partner=None, visit=None, due=2, user=None, **extra):
        vals = dict({
            "project_id": self.project.id, "visit_id": visit.id if visit else False, "text": text, "for_kind": kind,
            "partner_id": partner.id if partner else False, "due_date": self.days(due) if due is not None else False,
        }, **extra)
        return self.Point.browse(self.Point.with_user(user or self.coordinator).rvt_add([vals]))
