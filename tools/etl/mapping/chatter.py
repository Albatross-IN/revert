"""Phase 'chatter' (SQL lane): attachments + filestore, messages, recipients, followers,
tracking values (module mail_tracking, added to the target set), notifications, mails,
reactions. Runs after every business phase. 18→20 drift handled by the shared-column copy:
mail_message.record_name, mail_notification.letter_id and mail_tracking_value.currency_id are
gone on 20. 18 stored tracked changes only in the side table with an empty body; 20 shows the
body, so TRACKING_BODIES renders them (same rule as the mark migration)."""
import logging
import os
import shutil

from ..core import SqlStep, TableCopy, FuncStep, IDM
from .. import config

_logger = logging.getLogger("etl.chatter")
S = config.SRC_SCHEMA
COMPANY = "(SELECT id FROM res_company ORDER BY id LIMIT 1)"


def _maps(engine, ctx):
    """etl_idmap rows for reference models matched by xmlid / name: subtypes, activity types, fields, models."""
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
    # EVERY module-data record maps by xmlid (whatsapp templates, blog posts, helpdesk teams,
    # hr jobs, mail templates ...): their chatter and attachments then migrate onto the fresh
    # module rows. Records a phase already mapped keep their mapping (ON CONFLICT DO NOTHING).
    cr.execute(f"""INSERT INTO etl_idmap (model, old_id, new_id)
                   SELECT d18.model, d18.res_id, d20.res_id FROM {S}.ir_model_data d18
                   JOIN ir_model_data d20 ON d20.module = d18.module AND d20.name = d18.name
                                         AND d20.model = d18.model
                   WHERE d18.module NOT IN ('__export__', 'studio_customization')
                     AND d18.model NOT LIKE 'ir.%'
                   ON CONFLICT DO NOTHING""")
    n["global_xmlids"] = cr.rowcount
    engine.idmap._cache.clear()
    for m in ("mail.message.subtype", "mail.activity.type", "ir.model.fields", "ir.model"):
        engine.idmap._cache.pop(m, None)
    return n


MAPS = FuncStep("chatter.maps", _maps)

# ORM-lane create hooks may post on their own (creation notes, assignment notices): purge every message/mail that landed on a MIGRATED record during
# the load — prod's real history replaces it, and no queued mail may survive into go-live.
PURGE_ETL_MESSAGES = SqlStep("chatter.purge_etl_messages", f"""
    DELETE FROM mail_mail w USING mail_message m
     WHERE w.mail_message_id = m.id AND m.id < {{OFF}} AND m.model IS NOT NULL
       AND EXISTS (SELECT 1 FROM etl_idmap x WHERE x.model = m.model AND x.new_id = m.res_id);
    DELETE FROM mail_message m
     WHERE m.id < {{OFF}} AND m.model IS NOT NULL
       AND EXISTS (SELECT 1 FROM etl_idmap x WHERE x.model = m.model AND x.new_id = m.res_id)""")

# 18's compiled asset bundles (ir.ui.view, url /web/assets/...) are never carried: 20 builds its own.
ATTACHMENTS = TableCopy(
    "ir.attachment", "ir_attachment",
    joins=["LEFT JOIN etl_idmap m ON m.model = s.res_model AND m.old_id = s.res_id"],
    where="(s.res_model IS NULL OR s.res_id IS NULL OR s.res_id = 0 OR m.new_id IS NOT NULL)"
          " AND coalesce(s.res_model, '') NOT IN ('ir.ui.menu', 'ir.module.module', 'mail.compose.message')"
          " AND coalesce(s.name, '') NOT LIKE '/web/assets/%' AND coalesce(s.url, '') NOT LIKE '/web/assets/%'",
    overrides={"id": "s.id + {OFF}", "res_id": "CASE WHEN s.res_id IS NULL OR s.res_id = 0 THEN s.res_id ELSE m.new_id END",
               "company_id": f"CASE WHEN s.company_id IS NOT NULL THEN {COMPANY} END",
               "original_id": "NULL", "website_id": "CASE WHEN s.website_id IS NOT NULL THEN 1 END",
               "theme_template_id": "NULL"},
    register=("ir.attachment", "ir_attachment"), chunk=50000, on_conflict="DO NOTHING",
)


def _filestore(engine, ctx):
    """Hard-link every migrated attachment file from the staged 18 filestore (same disk)."""
    env, cr = engine.env, engine.cr
    dst_root = env["ir.attachment"]._filestore()
    cr.execute(f"SELECT DISTINCT store_fname FROM ir_attachment WHERE id > {config.OFFSET} AND store_fname IS NOT NULL")
    names = [r[0] for r in cr.fetchall()]
    linked = existed = missing = 0
    for fname in names:
        src = os.path.join(config.FILESTORE_SRC, fname); dst = os.path.join(dst_root, fname)
        if os.path.exists(dst):
            existed += 1; continue
        if not os.path.exists(src):
            missing += 1; continue
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        try:
            os.link(src, dst)
        except OSError:
            shutil.copy2(src, dst)
        linked += 1
    if missing:
        _logger.warning("filestore: %d attachment files missing in %s", missing, config.FILESTORE_SRC)
    return dict(files=len(names), linked=linked, existed=existed, missing=missing, filestore=dst_root)


FILESTORE = FuncStep("chatter.filestore", _filestore)

MESSAGES = TableCopy(
    "mail.message", "mail_message",
    joins=["LEFT JOIN etl_idmap m ON m.model = s.model AND m.old_id = s.res_id",
           IDM("pa", "res.partner", "s.author_id"), IDM("st", "mail.message.subtype", "s.subtype_id"),
           IDM("at", "mail.activity.type", "s.mail_activity_type_id")],
    where="s.model IS NULL OR m.new_id IS NOT NULL",
    overrides={"id": "s.id + {OFF}", "parent_id": "NULL", "res_id": "m.new_id", "model": "s.model",
               "author_id": "pa.new_id", "author_guest_id": "NULL", "subtype_id": "st.new_id",
               "mail_activity_type_id": "at.new_id", "mail_server_id": "NULL",
               "record_company_id": f"CASE WHEN s.record_company_id IS NOT NULL THEN {COMPANY} END",
               "record_alias_domain_id": "NULL", "body": "etl_shift_urls(s.body, {OFF})"},
    register=("mail.message", "mail_message"), chunk=200000, on_conflict="DO NOTHING",
)


def _message_parents(engine, ctx):
    cr = engine.cr
    cr.execute(f"""UPDATE mail_message t SET parent_id = s.parent_id + {config.OFFSET}
                   FROM {S}.mail_message s
                   WHERE t.id = s.id + {config.OFFSET} AND s.parent_id IS NOT NULL AND t.parent_id IS NULL
                     AND EXISTS (SELECT 1 FROM mail_message x WHERE x.id = s.parent_id + {config.OFFSET})""")
    n = cr.rowcount
    cr.execute(f"""SELECT s.model, count(*) FROM {S}.mail_message s
                   WHERE NOT EXISTS (SELECT 1 FROM mail_message t WHERE t.id = s.id + {config.OFFSET})
                   GROUP BY 1 ORDER BY 2 DESC LIMIT 30""")
    dropped = {m or "(none)": c for m, c in cr.fetchall()}
    return dict(parents_linked=n, messages_dropped_by_model=dropped)


MESSAGE_PARENTS = FuncStep("mail.message.parents", _message_parents)

RECIPIENTS = SqlStep("mail.message.recipients", f"""
    INSERT INTO mail_message_res_partner_rel (mail_message_id, res_partner_id)
    SELECT r.mail_message_id + {{OFF}}, p.new_id FROM {{S}}.mail_message_res_partner_rel r
    JOIN mail_message t ON t.id = r.mail_message_id + {{OFF}}
    JOIN etl_idmap p ON p.model = 'res.partner' AND p.old_id = r.res_partner_id
    ON CONFLICT DO NOTHING""")

FOLLOWERS = TableCopy(
    "mail.followers", "mail_followers",
    joins=["LEFT JOIN etl_idmap m ON m.model = s.res_model AND m.old_id = s.res_id",
           IDM("p", "res.partner", "s.partner_id")],
    where="m.new_id IS NOT NULL AND p.new_id IS NOT NULL",
    overrides={"id": "s.id + {OFF}", "res_id": "m.new_id", "res_model": "s.res_model", "partner_id": "p.new_id"},
    on_conflict="DO NOTHING", register=("mail.followers", "mail_followers"), chunk=200000,
)
FOLLOWER_SUBTYPES = SqlStep("mail.followers.subtypes", f"""
    INSERT INTO mail_followers_mail_message_subtype_rel (mail_followers_id, mail_message_subtype_id)
    SELECT r.mail_followers_id + {{OFF}}, st.new_id FROM {{S}}.mail_followers_mail_message_subtype_rel r
    JOIN mail_followers f ON f.id = r.mail_followers_id + {{OFF}}
    JOIN etl_idmap st ON st.model = 'mail.message.subtype' AND st.old_id = r.mail_message_subtype_id
    ON CONFLICT DO NOTHING""")

TRACKING = TableCopy(
    "mail.tracking.value", "mail_tracking_value",
    joins=["JOIN mail_message t ON t.id = s.mail_message_id + {OFF}", IDM("f", "ir.model.fields", "s.field_id"),
           "LEFT JOIN {S}.ir_model_fields fld ON fld.id = s.field_id"],
    overrides={"id": "s.id + {OFF}", "mail_message_id": "t.id", "field_id": "f.new_id"},
    extra={"field_info": "CASE WHEN f.new_id IS NULL AND fld.id IS NOT NULL THEN jsonb_build_object('desc', fld.field_description->>'en_US', "
                         "'name', fld.name, 'sequence', 100, 'type', fld.ttype) END"},
    exclude={"currency_id"}, chunk=200000, on_conflict="DO NOTHING",
)

MAILS = TableCopy(
    "mail.mail", "mail_mail",
    joins=["JOIN mail_message t ON t.id = s.mail_message_id + {OFF}"],
    overrides={"id": "s.id + {OFF}", "mail_message_id": "t.id", "fetchmail_server_id": "NULL", "mailing_id": "NULL"},
    register=("mail.mail", "mail_mail"), chunk=50000, on_conflict="DO NOTHING",
)

SMS = TableCopy(
    "sms.sms", "sms_sms",
    joins=["JOIN mail_message t ON t.id = s.mail_message_id + {OFF}", IDM("pa", "res.partner", "s.partner_id")],
    overrides={"id": "s.id + {OFF}", "mail_message_id": "t.id", "partner_id": "pa.new_id", "sms_tracker_id": "NULL"},
    register=("sms.sms", "sms_sms"), chunk=50000, on_conflict="DO NOTHING",
)

NOTIFICATIONS = TableCopy(
    "mail.notification", "mail_notification",
    joins=["JOIN mail_message t ON t.id = s.mail_message_id + {OFF}", IDM("pa", "res.partner", "s.author_id"),
           IDM("rp", "res.partner", "s.res_partner_id"), "LEFT JOIN mail_mail mm ON mm.id = s.mail_mail_id + {OFF}",
           "LEFT JOIN sms_sms ss ON ss.id = s.sms_id_int + {OFF}"],
    overrides={"id": "s.id + {OFF}", "mail_message_id": "t.id", "author_id": "pa.new_id", "res_partner_id": "rp.new_id",
               "mail_mail_id": "mm.id", "sms_id_int": "ss.id", "letter_id": "NULL"},
    chunk=200000, on_conflict="DO NOTHING",
)

MSG_ATTACHMENTS = SqlStep("mail.message.attachments", f"""
    INSERT INTO message_attachment_rel (message_id, attachment_id)
    SELECT r.message_id + {{OFF}}, r.attachment_id + {{OFF}} FROM {{S}}.message_attachment_rel r
    JOIN mail_message t ON t.id = r.message_id + {{OFF}}
    JOIN ir_attachment a ON a.id = r.attachment_id + {{OFF}}
    ON CONFLICT DO NOTHING""")

REACTIONS = TableCopy(
    "mail.message.reaction", "mail_message_reaction",
    joins=["JOIN mail_message t ON t.id = s.message_id + {OFF}", IDM("p", "res.partner", "s.partner_id")],
    where="p.new_id IS NOT NULL",
    overrides={"id": "s.id + {OFF}", "message_id": "t.id", "partner_id": "p.new_id", "guest_id": "NULL"},
    on_conflict="DO NOTHING",
)

# 20 renders tracked values from the message body (message_type 'tracking'); 18 stored them
# only in the side table with an empty body -> rendered here in SQL, in 18's display rules.
TRACKING_BODIES = SqlStep("chatter.tracking_bodies", f"""
    CREATE OR REPLACE FUNCTION etl_html(t text) RETURNS text LANGUAGE sql IMMUTABLE AS
      $$ SELECT replace(replace(replace(coalesce(t, ''), '&', '&amp;'), '<', '&lt;'), '>', '&gt;') $$;
    WITH tv AS (
      SELECT v.mail_message_id,
             coalesce(f.tracking, (v.field_info->>'sequence')::int, 100) AS seq, v.id,
             coalesce(f.field_description->>'en_US', v.field_info->>'desc', f.name, v.field_info->>'name', '?') AS label,
             coalesce(f.ttype, v.field_info->>'type', 'char') AS ttype,
             v.old_value_char, v.new_value_char, v.old_value_text, v.new_value_text, v.old_value_integer,
             v.new_value_integer, v.old_value_float, v.new_value_float, v.old_value_datetime, v.new_value_datetime
      FROM mail_tracking_value v LEFT JOIN ir_model_fields f ON f.id = v.field_id
      WHERE v.mail_message_id - {{OFF}} BETWEEN {{LO}} AND {{HI}}
    ), disp AS (
      SELECT mail_message_id, seq, id, label,
             CASE ttype WHEN 'boolean' THEN CASE WHEN old_value_integer = 1 THEN 'Yes' WHEN old_value_integer = 0 THEN 'No' END
                        WHEN 'integer' THEN old_value_integer::text
                        WHEN 'float' THEN to_char(old_value_float, 'FM999,999,999,999,990.00')
                        WHEN 'monetary' THEN to_char(old_value_float, 'FM999,999,999,999,990.00')
                        WHEN 'date' THEN to_char(old_value_datetime, 'MM/DD/YYYY')
                        WHEN 'datetime' THEN to_char(old_value_datetime, 'MM/DD/YYYY HH24:MI:SS')
                        WHEN 'text' THEN old_value_text ELSE old_value_char END AS old_disp,
             CASE ttype WHEN 'boolean' THEN CASE WHEN new_value_integer = 1 THEN 'Yes' WHEN new_value_integer = 0 THEN 'No' END
                        WHEN 'integer' THEN new_value_integer::text
                        WHEN 'float' THEN to_char(new_value_float, 'FM999,999,999,999,990.00')
                        WHEN 'monetary' THEN to_char(new_value_float, 'FM999,999,999,999,990.00')
                        WHEN 'date' THEN to_char(new_value_datetime, 'MM/DD/YYYY')
                        WHEN 'datetime' THEN to_char(new_value_datetime, 'MM/DD/YYYY HH24:MI:SS')
                        WHEN 'text' THEN new_value_text ELSE new_value_char END AS new_disp
      FROM tv
    ), html AS (
      SELECT mail_message_id,
             '<div>' || string_agg(
               etl_html(coalesce(nullif(old_disp, ''), 'None')) || ' → <b>' || etl_html(coalesce(nullif(new_disp, ''), 'None'))
               || '</b> <i>(' || etl_html(label) || ')</i>',
               '<br>' ORDER BY seq, id) || '</div>' AS body
      FROM disp GROUP BY mail_message_id
    )
    UPDATE mail_message m SET
      body = CASE WHEN m.body IS NULL OR m.body IN ('', '<p></p>', '<p><br></p>', '<p><br/></p>') THEN h.body ELSE m.body || h.body END,
      message_type = 'tracking'
    FROM html h WHERE m.id = h.mail_message_id AND m.message_type <> 'tracking'""",
    chunk=("mail_message", 200000))

# a binary field must end up with ONE attachment per (res_model, res_id, res_field).
# Two ways duplicates appear here: the ORM's empty placeholder created with the record
# coexists with the copied 18 file, and the SOURCE itself may hold several uploads of one
# field (several uploads: 18 served the newest, 20 serves nothing).
# Keep the newest row (highest id — source copies keep their relative order at +OFFSET).
BINARY_DEDUP = SqlStep("chatter.binary_dedup", """
    DELETE FROM ir_attachment a USING ir_attachment b
    WHERE a.res_model = b.res_model AND a.res_id = b.res_id AND a.res_field = b.res_field
      AND a.res_field IS NOT NULL AND a.id < b.id""")

SEQ_TABLES = ["ir_attachment", "mail_message", "mail_followers", "mail_tracking_value", "mail_notification",
              "mail_mail", "mail_message_reaction", "sms_sms"]


def _sequences(engine, ctx):
    cr = engine.cr
    for t in SEQ_TABLES:
        cr.execute(f"SELECT setval(pg_get_serial_sequence('{t}', 'id'), GREATEST((SELECT coalesce(max(id), 1) FROM {t}), 1))")
    return dict(tables=len(SEQ_TABLES))


SEQUENCES = FuncStep("chatter.sequences", _sequences)

STEPS = [MAPS, PURGE_ETL_MESSAGES, ATTACHMENTS, FILESTORE, MESSAGES, MESSAGE_PARENTS, RECIPIENTS, FOLLOWERS, FOLLOWER_SUBTYPES,
         TRACKING, MAILS, SMS, NOTIFICATIONS, MSG_ATTACHMENTS, REACTIONS, TRACKING_BODIES, BINARY_DEDUP, SEQUENCES]
