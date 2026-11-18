import hashlib
import secrets
from datetime import timedelta

from odoo import api, fields, models
from odoo.exceptions import UserError

OTP_MINUTES = 10
OTP_TRIES = 5
OTP_PER_HOUR = 5


class RvtApiDevice(models.Model):
    """One phone (or browser) a person signed in on. Signing out, or being signed out, ends its tokens."""
    _name = "rvt.api.device"
    _description = "App device"
    _order = "last_seen desc, id desc"

    user_id = fields.Many2one("res.users", required=True, ondelete="cascade", index=True)
    uid = fields.Char(string="Device id", required=True, index=True)
    name = fields.Char()
    platform = fields.Char()
    app_version = fields.Char()
    push_token = fields.Char(help="Where the app's notifications are sent.")
    epoch = fields.Integer(default=1, help="Raised to sign this device out.")
    last_seen = fields.Datetime()
    active = fields.Boolean(default=True)

    _user_uid_uniq = models.Constraint("unique (user_id, uid)", "This device is registered already.")

    @api.model
    def _rvt_register(self, user, info):
        info = info or {}
        uid = (info.get("uid") or "").strip() or secrets.token_hex(8)
        device = self.sudo().with_context(active_test=False).search([("user_id", "=", user.id), ("uid", "=", uid)], limit=1)
        vals = {
            "name": info.get("name") or False, "platform": info.get("platform") or False,
            "app_version": info.get("app_version") or False, "last_seen": fields.Datetime.now(), "active": True,
        }
        if info.get("push_token"):
            vals["push_token"] = info["push_token"]
        if device:
            device.write(dict(vals, epoch=device.epoch + 1))
        else:
            device = self.sudo().create(dict(vals, user_id=user.id, uid=uid))
        return device

    def _touch(self):
        """At most one write a quarter of an hour, so reading never fights over the row."""
        now = fields.Datetime.now()
        if not self.last_seen or now - self.last_seen > timedelta(minutes=15):
            self.sudo().write({"last_seen": now})

    def _sign_out(self):
        self.sudo().write({"epoch": self.epoch + 1, "push_token": False, "active": False})


class RvtApiOtp(models.Model):
    """A sign-in code sent to a mobile number. Only its hash is kept."""
    _name = "rvt.api.otp"
    _description = "Sign-in code"
    _order = "id desc"

    phone = fields.Char(required=True, index=True)
    partner_id = fields.Many2one("res.partner", required=True, ondelete="cascade")
    code_hash = fields.Char(required=True)
    expires_on = fields.Datetime(required=True)
    tries = fields.Integer(default=0)
    used = fields.Boolean(default=False)

    @api.model
    def _hash(self, phone, code):
        return hashlib.sha256(("%s:%s" % (phone, code)).encode()).hexdigest()

    @api.model
    def _rvt_issue(self, phone, partner):
        """A fresh four-digit code. Earlier codes for the number stop working."""
        hour_ago = fields.Datetime.now() - timedelta(hours=1)
        if self.sudo().search_count([("phone", "=", phone), ("create_date", ">", hour_ago)]) >= OTP_PER_HOUR:
            raise UserError(self.env._("Too many codes were asked for this number. Try again in an hour."))
        self.sudo().search([("phone", "=", phone), ("used", "=", False)]).write({"used": True})
        code = "%04d" % secrets.randbelow(10000)
        self.sudo().create({
            "phone": phone, "partner_id": partner.id, "code_hash": self._hash(phone, code),
            "expires_on": fields.Datetime.now() + timedelta(minutes=OTP_MINUTES),
        })
        return code

    @api.model
    def _rvt_verify(self, phone, code):
        """The partner the code was sent to, or nothing. A wrong code counts; five end it."""
        otp = self.sudo().search([("phone", "=", phone), ("used", "=", False)], limit=1)
        if not otp or otp.expires_on < fields.Datetime.now():
            return self.env["res.partner"]
        if otp.tries >= OTP_TRIES:
            otp.used = True
            return self.env["res.partner"]
        if otp.code_hash != self._hash(phone, (code or "").strip()):
            otp.tries += 1
            return self.env["res.partner"]
        otp.used = True
        return otp.partner_id

    @api.autovacuum
    def _gc(self):
        self.sudo().search([("create_date", "<", fields.Datetime.now() - timedelta(days=2))]).unlink()


class RvtApiMedia(models.Model):
    """A photo or a PDF sent ahead of the action that uses it, so a slow network retries the file alone."""
    _name = "rvt.api.media"
    _description = "Uploaded file"

    user_id = fields.Many2one("res.users", required=True, ondelete="cascade", index=True, default=lambda self: self.env.user)
    name = fields.Char()
    mimetype = fields.Char()
    data = fields.Binary(attachment=True, required=True)
    client_uid = fields.Char(index=True, help="Given by the phone: the same file sent twice is kept once.")

    @api.model
    def _take(self, user, media_id):
        """The file's content as base64, for the action that uses it."""
        if not media_id:
            return False
        media = self.sudo().browse(int(media_id)).exists()
        if not media or media.user_id != user:
            raise UserError(self.env._("That file was not uploaded from this account."))
        return media.data.to_base64()

    @api.autovacuum
    def _gc(self):
        self.sudo().search([("create_date", "<", fields.Datetime.now() - timedelta(days=7))]).unlink()
