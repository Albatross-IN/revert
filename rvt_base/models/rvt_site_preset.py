from odoo import api, fields, models

from .rvt_entity_type import SITE_KINDS


class RvtSitePreset(models.Model):
    _name = "rvt.site.preset"
    _description = "Site preset"
    _order = "sequence, id"

    name = fields.Char(required=True, translate=True)
    site_kind = fields.Selection(SITE_KINDS, string="Kind of site", required=True, default="home")
    line_ids = fields.One2many("rvt.site.preset.line", "preset_id", string="Entities", copy=True)
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)

    def rvt_entities(self):
        """The entity list this preset proposes: one dict per entity, numbered
        when a type occurs more than once, with the "Whole site" entity last."""
        self.ensure_one()
        out = []
        for line in self.line_ids:
            for i in range(1, line.count + 1):
                name = line.entity_type_id.name if line.count == 1 else f"{line.entity_type_id.name} {i}"
                out.append({
                    "name": name,
                    "entity_type_id": line.entity_type_id.id,
                    "trade_ids": line.entity_type_id.trade_ids.ids,
                })
        whole = self.env["rvt.entity.type"].search([("is_whole_site", "=", True)], limit=1)
        if whole:
            out.append({"name": whole.name, "entity_type_id": whole.id, "trade_ids": whole.trade_ids.ids})
        return out


class RvtSitePresetLine(models.Model):
    _name = "rvt.site.preset.line"
    _description = "Site preset line"
    _order = "sequence, id"

    preset_id = fields.Many2one("rvt.site.preset", required=True, ondelete="cascade", index=True)
    entity_type_id = fields.Many2one("rvt.entity.type", string="Entity type", required=True, ondelete="restrict")
    count = fields.Integer(default=1, required=True)
    sequence = fields.Integer(default=10)

    _count_positive = models.Constraint("check (count > 0)", "The count must be at least 1.")

    @api.depends("entity_type_id", "count")
    def _compute_display_name(self):
        for line in self:
            name = line.entity_type_id.name or ""
            line.display_name = f"{name} × {line.count}" if line.count > 1 else name
