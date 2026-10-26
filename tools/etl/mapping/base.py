"""Phase 'base': reference maps (ir.model, fields, subtypes, activity types, currencies), users
(password hashes, TOTP secrets, group membership, settings, login history), partners. Adapted
from the mark 19→20 ETL for an Odoo 18 source: res.partner.mobile no longer exists on 20 (the
number moves to phone), res.partner.title is gone, legacy tz aliases are normalised."""
import logging

from ..core import OrmStep, FuncStep, SqlStep, TableCopy
from .. import config

_logger = logging.getLogger("etl.base")

S = config.SRC_SCHEMA


# --------------------------------------------------------------------- reference id maps
def _refmaps(engine, ctx):
    """idmap rows every later phase needs: mail subtypes + activity types by xmlid, then name;
    ir.model / ir.model.fields by name; the company; currencies by code."""
    cr = engine.cr
    n = {}
    for model, table, namecol, extra in (
        ("mail.message.subtype", "mail_message_subtype", "name", "AND coalesce(a.res_model,'') = coalesce(b.res_model,'')"),
        ("mail.activity.type", "mail_activity_type", "name", ""),
    ):
        cr.execute(f"""INSERT INTO etl_idmap (model, old_id, new_id)
                       SELECT %s, d18.res_id, d20.res_id FROM {S}.ir_model_data d18
                       JOIN ir_model_data d20 ON d20.module = d18.module AND d20.name = d18.name AND d20.model = %s
                       WHERE d18.model = %s AND d18.module NOT IN ('__export__') ON CONFLICT DO NOTHING""",
                   (model, model, model))
        x = cr.rowcount
        cr.execute(f"""INSERT INTO etl_idmap (model, old_id, new_id)
                       SELECT %s, a.id, min(b.id) FROM {S}.{table} a JOIN {table} b
                         ON b.{namecol}->>'en_US' = a.{namecol}->>'en_US' {extra}
                       WHERE a.id NOT IN (SELECT old_id FROM etl_idmap WHERE model = %s) GROUP BY a.id ON CONFLICT DO NOTHING""",
                   (model, model))
        n[model] = (x, cr.rowcount)
    cr.execute(f"""INSERT INTO etl_idmap (model, old_id, new_id)
                   SELECT 'ir.model.fields', a.id, b.id FROM {S}.ir_model_fields a
                   JOIN ir_model_fields b ON b.model = a.model AND b.name = a.name ON CONFLICT DO NOTHING""")
    n["ir.model.fields"] = cr.rowcount
    cr.execute(f"""INSERT INTO etl_idmap (model, old_id, new_id)
                   SELECT 'ir.model', a.id, b.id FROM {S}.ir_model a JOIN ir_model b ON b.model = a.model ON CONFLICT DO NOTHING""")
    n["ir.model"] = cr.rowcount
    cr.execute(f"INSERT INTO etl_idmap (model, old_id, new_id) SELECT 'res.company', id, 1 FROM {S}.res_company ON CONFLICT DO NOTHING")
    cr.execute(f"""INSERT INTO etl_idmap (model, old_id, new_id)
                   SELECT 'res.currency', a.id, b.id FROM {S}.res_currency a JOIN res_currency b ON b.name = a.name
                   ON CONFLICT DO NOTHING""")
    engine.idmap._cache.clear()
    return n


REFMAPS = FuncStep("base.refmaps", _refmaps)


# ----------------------------------------------------------------------------- users
def _user_transform(vals, row, ctx):
    """name/email live on the 18 partner; passwords are copied by SQL afterwards."""
    p = ctx["src"].row("res_partner", row["partner_id"], ("name", "email", "phone", "tz", "lang", "function"))
    if p:
        vals.setdefault("name", p["name"])
        for k in ("email", "tz", "function", "phone"):
            if p.get(k):
                vals.setdefault(k, config.TZ_ALIASES.get(p[k], p[k]) if k == "tz" else p[k])
        vals["lang"] = p.get("lang") or "en_US"
    if vals.get("tz"):
        vals["tz"] = config.TZ_ALIASES.get(vals["tz"], vals["tz"])
    vals.pop("password", None)
    vals.pop("company_ids", None)
    vals["company_id"] = ctx["env"].company.id
    vals["company_ids"] = [(6, 0, [ctx["env"].company.id])]
    return vals


def _after_users(ctx):
    eng = ctx["engine"]; cr = eng.cr
    # the 18 partner of every migrated user maps onto the 20 user's partner (authors, followers, ...)
    cr.execute(f"""INSERT INTO etl_idmap (model, old_id, new_id)
                   SELECT 'res.partner', s.partner_id, u.partner_id
                   FROM etl_idmap m JOIN {S}.res_users s ON s.id = m.old_id JOIN res_users u ON u.id = m.new_id
                   WHERE m.model = 'res.users' ON CONFLICT DO NOTHING""")
    # OdooBot / admin (ids 1, 2 on both sides)
    cr.execute(f"""INSERT INTO etl_idmap (model, old_id, new_id)
                   SELECT 'res.users', s.id, s.id FROM {S}.res_users s WHERE s.id IN (1, 2) ON CONFLICT DO NOTHING""")
    cr.execute(f"""INSERT INTO etl_idmap (model, old_id, new_id)
                   SELECT 'res.partner', s.partner_id, u.partner_id FROM {S}.res_users s JOIN res_users u ON u.id = s.id
                   WHERE s.id IN (1, 2) ON CONFLICT DO NOTHING""")
    # the base-xmlid special users (public, portal template) map by xmlid
    cr.execute(f"""INSERT INTO etl_idmap (model, old_id, new_id)
                   SELECT 'res.users', d18.res_id, d20.res_id FROM {S}.ir_model_data d18
                   JOIN ir_model_data d20 ON d20.module = d18.module AND d20.name = d18.name AND d20.model = 'res.users'
                   WHERE d18.model = 'res.users' ON CONFLICT DO NOTHING""")
    cr.execute(f"""INSERT INTO etl_idmap (model, old_id, new_id)
                   SELECT 'res.partner', s.partner_id, u.partner_id
                   FROM etl_idmap m JOIN {S}.res_users s ON s.id = m.old_id JOIN res_users u ON u.id = m.new_id
                   WHERE m.model = 'res.users' ON CONFLICT DO NOTHING""")
    # password hashes (same passlib scheme on both versions) -- INCLUDING admin, so the
    # production admin credential works on the target
    cr.execute(f"""UPDATE res_users u SET password = s.password
                   FROM etl_idmap m JOIN {S}.res_users s ON s.id = m.old_id
                   WHERE m.model = 'res.users' AND u.id = m.new_id AND s.password IS NOT NULL AND u.id >= 2""")
    _logger.info("users: %d password hashes copied", cr.rowcount)
    cr.execute(f"""UPDATE res_users u SET totp_secret = s.totp_secret
                   FROM etl_idmap m JOIN {S}.res_users s ON s.id = m.old_id
                   WHERE m.model = 'res.users' AND u.id = m.new_id AND s.totp_secret IS NOT NULL AND u.id > 2""")
    eng.idmap._cache.pop("res.partner", None); eng.idmap._cache.pop("res.users", None)


SPECIAL_USERS = f"(SELECT res_id FROM {S}.ir_model_data WHERE model = 'res.users' AND module = 'base')"
USER_SKIP = {"password", "partner_id", "totp_secret", "api_key_ids", "action_id", "company_ids", "log_ids", "device_ids",
             "res_users_settings_id", "groups_id", "group_ids", "odoobot_state", "odoobot_failed", "sidebar_type"}
USERS = OrmStep(
    "res.users", where=f"id > 2 AND id NOT IN {SPECIAL_USERS}", key=["login"],
    skip=USER_SKIP,
    rename={"groups_id": "group_ids"},
    transform=_user_transform, after=_after_users, context={"no_reset_password": True},
)
# group membership resolved by group xmlid (natural resolver returns None for unknown groups);
# groups that no longer exist on 20 drop silently.
GROUPS = OrmStep(
    "res.users", name="res.users.groups", where=f"id > 2 AND id NOT IN {SPECIAL_USERS}",
    write_mapped=True, restore_dates=False,
    skip={"login", "password", "partner_id", "signature", "active", "notification_type", "company_id", "company_ids",
          "odoobot_state", "odoobot_failed", "tz", "share", "action_id", "karma", "totp_secret", "sidebar_type",
          "res_users_settings_id", "email", "login_date", "calendar_default_privacy", "device_ids", "api_key_ids",
          "log_ids"},
    rename={"groups_id": "group_ids"},
    transform=lambda vals, row, ctx: {"group_ids": vals["group_ids"]} if vals.get("group_ids") else None,
)


def _admin_groups(engine, ctx):
    """uid 2 is excluded from the USERS/GROUPS steps (it exists on both sides), so its
    DB-granted memberships must be carried by group xmlid. Additive only."""
    cr = engine.cr
    cr.execute(f"""INSERT INTO res_groups_users_rel (gid, uid)
                   SELECT tg.res_id, 2 FROM {S}.res_groups_users_rel r
                   JOIN {S}.ir_model_data sd ON sd.model = 'res.groups' AND sd.res_id = r.gid
                   JOIN ir_model_data tg ON tg.model = 'res.groups' AND tg.module = sd.module
                                        AND tg.name = sd.name
                   WHERE r.uid = 2
                     AND NOT EXISTS (SELECT 1 FROM res_groups_users_rel e
                                     WHERE e.gid = tg.res_id AND e.uid = 2)""")
    added = cr.rowcount
    cr.execute(f"""UPDATE res_users u SET notification_type = s.notification_type
                   FROM {S}.res_users s WHERE u.id = 2 AND s.id = 2
                     AND s.notification_type IS NOT NULL
                     AND u.notification_type IS DISTINCT FROM s.notification_type""")
    synced = cr.rowcount
    # users that exist on both sides were not created by the ORM lane: carry their signature
    cr.execute(f"""UPDATE res_users u SET signature = s.signature
                   FROM etl_idmap m JOIN {S}.res_users s ON s.id = m.old_id
                   WHERE m.model = 'res.users' AND u.id = m.new_id AND u.signature IS DISTINCT FROM s.signature""")
    return dict(admin_groups_added=added, notification_synced=synced, signatures=cr.rowcount)


ADMIN_GROUPS = FuncStep("res.users.admin_groups", _admin_groups)

# ----------------------------------------------------------------------------- reference data
PCATEG = OrmStep("res.partner.category", key=["name"], order="parent_path, id", batch=1,
                 skip={"parent_path", "partner_ids"})

# ----------------------------------------------------------------------------- partners
PARTNER_SKIP = {"commercial_partner_id", "commercial_company_name", "complete_name", "user_ids", "signup_token",
                "signup_type", "signup_expiration", "partner_share", "same_vat_partner_id",
                "same_company_registry_partner_id", "message_bounce", "email_normalized", "phone_sanitized",
                "im_status", "contact_address", "contact_address_complete", "channel_ids", "starred_message_ids",
                "bank_ids", "child_ids", "ref_company_ids", "self", "meeting_ids", "calendar_last_notif_ack",
                "task_ids", "ocn_token", "is_created_by_ocr", "visitor_ids", "partner_gid", "additional_info",
                "online_partner_information"}


def _partner_retry(vals, err):
    """20 refuses malformed VAT numbers: keep the string in the notes and retry without it."""
    if "VAT" in err and vals.get("vat"):
        vals["comment"] = (vals.get("comment") or "") + f"<p>VAT (as entered on v18, invalid format): {vals['vat']}</p>"
        vals["vat"] = False
        return vals
    if "res_partner_check_name" in err:
        vals["name"] = vals.get("name") or vals.get("email") or "Unnamed contact"
        vals["type"] = "contact"
        return vals
    return None


def _partner_transform(vals, row, ctx):
    if not vals.get("name") and not vals.get("is_company") and vals.get("type", "contact") == "contact":
        vals["name"] = row.get("email") or row.get("phone") or row.get("mobile") or f"Unnamed contact #{row['id']}"
    # res.partner.mobile is gone on 20: the number becomes the phone, or is kept in the notes
    mobile = (row.get("mobile") or "").strip()
    if mobile:
        if not vals.get("phone"):
            vals["phone"] = mobile
        elif mobile != vals["phone"]:
            vals["comment"] = (vals.get("comment") or "") + f"<p>Mobile (v18): {mobile}</p>"
    return vals


def _company_partner_premap(engine, ctx):
    """mkdb already created the company partner; prod's company partner must land ON it."""
    cr, env = engine.cr, engine.env
    cr.execute(f"SELECT partner_id FROM {S}.res_company ORDER BY id LIMIT 1")
    old = cr.fetchone()[0]
    new = env.company.partner_id.id
    if not engine.idmap.get("res.partner", old):
        engine.idmap.add_many("res.partner", [(old, new)])
    return dict(mapped={old: new})


COMPANY_PARTNER = FuncStep("res.partner.company_premap", _company_partner_premap)

PARTNERS_1 = OrmStep(
    "res.partner", name="res.partner.roots",
    where=f"parent_id IS NULL AND id NOT IN (SELECT partner_id FROM {S}.res_users WHERE partner_id IS NOT NULL)",
    skip=PARTNER_SKIP, transform=_partner_transform, batch=400, retry=_partner_retry,
    write_mapped=True,   # the pre-mapped company partner gets prod's values written
)
PARTNERS_2 = OrmStep(
    "res.partner", name="res.partner.children",
    where=f"parent_id IS NOT NULL AND id NOT IN (SELECT partner_id FROM {S}.res_users WHERE partner_id IS NOT NULL)",
    skip=PARTNER_SKIP, transform=_partner_transform, batch=400, retry=_partner_retry,
)
# base.default_user (18's template user, gone on 20) is not migrated, so neither is its partner
DEFAULT_USER_PARTNER = (f"(SELECT u.partner_id FROM {S}.res_users u JOIN {S}.ir_model_data d ON d.model = 'res.users'"
                        f" AND d.res_id = u.id AND d.module = 'base' AND d.name = 'default_user')")
PARTNERS_USERS = OrmStep(
    "res.partner", name="res.partner.users",
    # id >= 2: admin exists on both sides, but its partner (name, e-mail, phone, timezone) is prod's
    where=f"id IN (SELECT partner_id FROM {S}.res_users WHERE partner_id IS NOT NULL AND id >= 2)"
          f" AND id NOT IN {DEFAULT_USER_PARTNER}",
    skip=PARTNER_SKIP | {"active", "type", "is_company", "user_id"}, transform=_partner_transform,
    write_mapped=True, restore_dates=False,
)
USER_PARTNER_NAMES = SqlStep("res.partner.users_names", f"""
    UPDATE res_partner p SET name = s.name, email = coalesce(nullif(s.email, ''), p.email)
    FROM etl_idmap m JOIN {{S}}.res_partner s ON s.id = m.old_id
    WHERE m.model = 'res.partner' AND p.id = m.new_id AND nullif(s.name, '') IS NOT NULL
      AND p.id IN (SELECT partner_id FROM res_users)
      AND (p.name IS DISTINCT FROM s.name OR p.email IS DISTINCT FROM coalesce(nullif(s.email, ''), p.email))""")


def _partner_fixups(engine, ctx):
    """Second pass once every partner exists: children re-linked, is_company and active restored
    (the ORM create lane drops both)."""
    cr = engine.cr
    cr.execute(f"""UPDATE res_partner c SET parent_id = pm.new_id
                   FROM etl_idmap m JOIN {S}.res_partner s ON s.id = m.old_id
                   JOIN etl_idmap pm ON pm.model = 'res.partner' AND pm.old_id = s.parent_id
                   WHERE m.model = 'res.partner' AND c.id = m.new_id AND s.parent_id IS NOT NULL
                     AND c.parent_id IS NULL AND pm.new_id <> c.id""")
    relinked = cr.rowcount
    cr.execute(f"""UPDATE res_partner p SET is_company = s.is_company
                   FROM etl_idmap m JOIN {S}.res_partner s ON s.id = m.old_id
                   WHERE m.model = 'res.partner' AND p.id = m.new_id
                     AND p.is_company IS DISTINCT FROM s.is_company""")
    is_company = cr.rowcount
    cr.execute(f"""UPDATE res_partner p SET active = s.active
                   FROM etl_idmap m JOIN {S}.res_partner s ON s.id = m.old_id
                   WHERE m.model = 'res.partner' AND p.id = m.new_id
                     AND p.active IS DISTINCT FROM s.active""")
    actives = cr.rowcount
    cr.execute("""UPDATE res_partner c SET commercial_partner_id = p.commercial_partner_id FROM res_partner p
                  WHERE p.id = c.parent_id AND c.is_company = false
                    AND c.commercial_partner_id IS DISTINCT FROM p.commercial_partner_id""")
    engine._restore_dates("res_partner", "res.partner")
    return dict(children_relinked=relinked, is_company_restored=is_company, active_restored=actives)


FIXUPS = FuncStep("res.partner.fixups", _partner_fixups)

USERS_SETTINGS = OrmStep(
    "res.users.settings", key=["user_id"],
    skip={"voice_active_duration", "is_discuss_sidebar_category_channel_open", "is_discuss_sidebar_category_chat_open",
          "use_push_to_talk", "push_to_talk_key", "volume_settings_ids", "channel_notifications",
          "calendar_default_privacy", "mute_until_dt"},
    transform=lambda v, r, c: v if v.get("user_id") else None,
)

# login history (Settings ▸ Users ▸ "Latest authentication")
USERS_LOG = TableCopy(
    "res.users.log", "res_users_log",
    joins=["JOIN etl_idmap u ON u.model = 'res.users' AND u.old_id = s.create_uid"],
    overrides={"id": "s.id + {OFF}", "create_uid": "u.new_id", "write_uid": "u.new_id"},
    register=("res.users.log", "res_users_log"), on_conflict="DO NOTHING",
)

STEPS = [REFMAPS, USERS, GROUPS, ADMIN_GROUPS, PCATEG, COMPANY_PARTNER, PARTNERS_1, PARTNERS_2, PARTNERS_USERS,
         USER_PARTNER_NAMES, FIXUPS, USERS_SETTINGS, USERS_LOG]
