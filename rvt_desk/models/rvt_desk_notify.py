"""Messages in the desk: the switch, the texts, the log, reminders and invitations."""
from odoo import api, models
from odoo.exceptions import UserError

from .rvt_desk import _num

STATE_WORD = {"sent": "sent", "held": "held", "failed": "failed", "no_number": "no number", "in_app": "in the app"}


class RvtDesk(models.AbstractModel):
    _inherit = "rvt.desk"

    @api.model
    def _features(self):
        return dict(super()._features(), wa=True)

    def _setting_keys(self):
        return dict(super()._setting_keys(), sending="rvt.notify_sending_on")

    def _snapshot_extra(self, data, projects, off, today):
        super()._snapshot_extra(data, projects, off, today)
        env = self.env
        Notify = env["rvt.notify"]
        config = env["rvt.config"]
        listed = sorted(Notify.test_numbers())
        data["set"].update({
            "sending": Notify.sending_on(), "number": Notify.number(), "testcopy": Notify.is_test_copy(),
            # a test copy may really message its test numbers (rvt.notify_test_numbers), and nobody else
            "testsend": bool(listed), "testlist": listed,
        })
        templates = {}
        for template in env["rvt.notify.template"].sudo().search([]):
            templates.setdefault(template.event, {})[template.lang] = template.text
        data["masters"]["templates"] = templates
        logs = env["rvt.notify.log"].search([], limit=150)
        data["wa"] = [{
            "id": log.id, "to": "a%s" % log.partner_id.id if log.partner_id else "",
            "name": log.name or "", "ph": log.phone or "", "text": log.text or "",
            "doc": {"label": log.document} if log.document else None,
            "on": off(config.to_date(log.create_date)), "at": self._clock(log.create_date),
            "ev": log.event, "held": log.state == "held", "st": STATE_WORD.get(log.state, log.state),
            "why": log.reason or "", "fresh": False,
        } for log in logs]
        contacts = projects.sudo().rvt_client_contact_ids
        invited = set(env["res.partner"].sudo().search([
            ("id", "in", contacts.ids), ("rvt_invited_on", "!=", False)]).ids)
        # what became of the last invitation: "invited" must not hide a message that never left
        last = {}
        for log in env["rvt.notify.log"].sudo().search(
                [("event", "=", "invite"), ("partner_id", "in", contacts.ids)], order="id"):
            last[log.partner_id.id] = log
        for row in data["projects"]:
            for contact in row["client"]["contacts"]:
                contact["inv"] = contact["id"] in invited
                log = last.get(contact["id"])
                contact["invst"] = STATE_WORD.get(log.state, log.state) if log else ""
                contact["invwhy"] = (log.reason or "") if log and log.state != "sent" else ""
        data["notes"] = env["rvt.notify.log"].rvt_mine()

    def _onboard_vals_extra(self, a):
        vals = super()._onboard_vals_extra(a)
        keys = a.get("inv") or []
        if keys:
            vals["invite"] = {"agency_ids": [_num(k) for k in keys if k != "client" and _num(k)], "client": "client" in keys}
        return vals

    # ------------------------------------------------------------------
    def _op_remind(self, a):
        project = self.env["project.project"].browse(_num(a.get("project"))).exists()
        if not project:
            raise UserError(self.env._("Choose the project."))
        to = a.get("to")
        sent = project.rvt_remind(a.get("text"), agency_id=None if to == "client" else _num(to), client=to == "client")
        return {"sent": sent}

    def _op_seen_notes(self, a):
        self.env["rvt.notify.log"].rvt_seen()

    def _op_invite(self, a):
        project = self.env["project.project"].browse(_num(a.get("project"))).exists()
        if not project:
            raise UserError(self.env._("Choose the project."))
        count = project.rvt_invite(
            [_num(a["agency"])] if a.get("agency") else [], [int(a["contact"])] if a.get("contact") else [])
        return {"invited": count}
