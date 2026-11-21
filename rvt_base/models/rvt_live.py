"""Live screens: when a record the screens show changes, every open screen is told
"something changed" and reads its own data again. Nothing else travels on that channel,
so listening to it gives no data away; its name still cannot be guessed."""
import hashlib
import hmac

from odoo import api, models


class RvtLive(models.AbstractModel):
    _name = "rvt.live"
    _description = "Live screens"

    @api.model
    def channel(self):
        secret = self.env["ir.config_parameter"].sudo().get_str("database.secret") or self.env.cr.dbname
        return "rvt_live_" + hmac.new(secret.encode(), b"rvt.live", hashlib.sha256).hexdigest()[:32]

    @api.model
    def info(self):
        """What a screen needs to listen: the channel, and the version the live connection asks for.
        (Nothing that moves by itself: the answer a screen reads stays the same while nothing changed.)"""
        from odoo.addons.bus.websocket import WebsocketConnectionHandler  # noqa: PLC0415  (not loaded in every process)

        return {"ch": self.channel(), "v": WebsocketConnectionHandler._VERSION}

    @api.model
    def touch(self):
        """Tell the open screens once, when this transaction is committed."""
        data = self.env.cr.precommit.data
        if data.get("rvt.live") or self.env.context.get("rvt_quiet"):
            return
        data["rvt.live"] = True
        self.env["bus.bus"].sudo()._sendone(self.channel(), "rvt.changed", {})


class RvtLiveMixin(models.AbstractModel):
    """For the models the screens are made of: any change to them is a change on the screens."""
    _name = "rvt.live.mixin"
    _description = "Changes reach the open screens"

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        self.env["rvt.live"].touch()
        return records

    def write(self, vals):
        res = super().write(vals)
        self.env["rvt.live"].touch()
        return res

    def unlink(self):
        res = super().unlink()
        self.env["rvt.live"].touch()
        return res
