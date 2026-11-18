"""Bills in the agency app: its own bills and their states. Never a payment, never a total."""
from odoo import models


class RvtApi(models.AbstractModel):
    _inherit = "rvt.api"

    def _agency_bills(self, firm):
        return self.env["rvt.bill"].search([("agency_id", "=", firm.id)], order="asked_on desc, id desc")

    def _agency_home_extra(self, data, firm):
        super()._agency_home_extra(data, firm)
        Desk = self.env["rvt.desk"]
        today = self.env["rvt.config"].today()
        off = lambda date: (date - today).days if date else None
        rows = [Desk._bill_row(b, off, money=True, payments=False) for b in self._agency_bills(firm)]
        for row in rows:
            row["upto"] = None
        data["bills"] = rows
        data["asks"] = [r for r in rows if r["st"] in ("asked", "returned")]

    def _agency_screen_extra(self, data, firm, off):
        super()._agency_screen_extra(data, firm, off)
        Desk = self.env["rvt.desk"]
        rows = [Desk._bill_row(b, off, money=True, payments=False) for b in self._agency_bills(firm)]
        for row in rows:
            # its own amount, as it wrote it; not what the office set as a ceiling, nor who asked
            row.update({"upto": None, "askedBy": None})
        data["bills"] = rows
        data["features"] = dict(data.get("features") or {}, bills=True)
