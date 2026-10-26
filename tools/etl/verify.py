#!/usr/bin/env python3
"""Verify a loaded Revert target against its Odoo 18 source, with numbers (exit 1 on any FAIL).

    cd /opt/odoo20/custom/revert_20 && /opt/odoo20/odoo20-venv/bin/python -m tools.etl.verify --db revert20_etl_dry1
        [--oracle revert]   # an 18 DB that really ran the revert_customizations upgrade on the same data:
                            # the MOM entries the replayed upgrade produced are compared with it

The source is read live through the foreign schema inside the target (src18), so the check is
always against the exact snapshot the run loaded. Sections: refusals, record parity, field-level
comparison of every business record, users and access, Studio, activities, MOM upgrade,
chatter, attachments + filestore bytes, dry-run safety."""
import argparse
import hashlib
import os
import sys

import psycopg2

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from tools.etl import config  # noqa: E402

S = config.SRC_SCHEMA
OFF = config.OFFSET
failures = []


def check(name, ok, detail=""):
    print(f"[{'PASS' if ok else 'FAIL'}] {name}" + (f"  {detail}" if detail else ""))
    if not ok:
        failures.append(name)


# refusals that are EXPLAINED (step, reason prefix) -> allowed distinct count; anything else fails
EXPLAINED_REFUSALS = {}

# attachments deliberately not carried: rebuilt by 20 itself or bound to records that are not data
ATTACHMENT_EXCLUSIONS = """(
       coalesce(s.res_model, '') IN ('ir.ui.menu', 'ir.module.module', 'mail.compose.message', 'iap.account',
                                     'ir.ui.view')
    OR coalesce(s.name, '') LIKE '/web/assets/%%' OR coalesce(s.url, '') LIKE '/web/assets/%%')"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", required=True)
    ap.add_argument("--oracle", default=None, help="18 DB that ran the module upgrade on the same data")
    a = ap.parse_args()
    conn = psycopg2.connect(dbname=a.db)
    cr = conn.cursor()

    def q1(sql, args=()):
        cr.execute(sql, args)
        return cr.fetchone()[0]

    def qall(sql, args=()):
        cr.execute(sql, args)
        return cr.fetchall()

    # ------------------------------------------------------------------ refusals
    print("== refusals ==")
    rows = qall("SELECT step, left(reason, 70), count(DISTINCT old_id) FROM etl_refusal GROUP BY 1, 2 ORDER BY 3 DESC")
    for step, reason, n in rows:
        allowed = next((v for (s_, r_), v in EXPLAINED_REFUSALS.items() if s_ == step and reason.startswith(r_)), None)
        check(f"refusal {step}: {reason}", allowed == n, f"n={n}")
    if not rows:
        check("no refused record", True)

    # ------------------------------------------------------------------ record parity
    print("\n== record parity (every source record mapped, no duplicates on the target) ==")
    for model, table, src_where in (
        ("project.project", "project_project", "true"),
        ("project.task", "project_task", "true"),
        ("project.task.type", "project_task_type", "true"),
        ("project.tags", "project_tags", "true"),
        ("project.project.stage", "project_project_stage", "true"),
        ("project.update", "project_update", "true"),
        ("mom.meeting", "mom_meeting", "true"),
        ("person.person", "person_person", "true"),
        ("mail.activity.type", "mail_activity_type", "true"),
        ("res.users", "res_users", f"id NOT IN (SELECT res_id FROM {S}.ir_model_data WHERE model='res.users' AND module='base' AND name='default_user')"),
        ("res.partner", "res_partner", f"id NOT IN (SELECT u.partner_id FROM {S}.res_users u JOIN {S}.ir_model_data d ON d.model='res.users' AND d.res_id=u.id AND d.module='base' AND d.name='default_user')"),
        ("discuss.channel", "discuss_channel", "true"),
    ):
        want = q1(f"SELECT count(*) FROM {S}.{table} WHERE {src_where}")
        got = q1(f"SELECT count(*) FROM {S}.{table} s JOIN etl_idmap m ON m.model = %s AND m.old_id = s.id WHERE {src_where}",
                 (model,))
        check(f"mapped {model}", got == want, f"{got}/{want}")
    for table in ("project_project", "project_task", "project_tags", "project_update", "mom_meeting", "person_person",
                  "project_project_stage", "discuss_channel"):
        want, got = q1(f"SELECT count(*) FROM {S}.{table}"), q1(f"SELECT count(*) FROM {table}")
        check(f"total rows {table}", got == want, f"{got}/{want}")
    # relation tables: same pairs, through the id map
    for table, a_col, a_model, b_col, b_model in (
        ("project_task_user_rel", "task_id", "project.task", "user_id", "res.users"),
        ("project_tags_project_task_rel", "project_task_id", "project.task", "project_tags_id", "project.tags"),
        ("project_task_type_rel", "type_id", "project.task.type", "project_id", "project.project"),
        ("project_favorite_user_rel", "project_id", "project.project", "user_id", "res.users"),
    ):
        want = q1(f"SELECT count(*) FROM {S}.{table}")
        got = q1(f"""SELECT count(*) FROM {S}.{table} s
                     JOIN etl_idmap a ON a.model = %s AND a.old_id = s.{a_col}
                     JOIN etl_idmap b ON b.model = %s AND b.old_id = s.{b_col}
                     JOIN {table} t ON t.{a_col} = a.new_id AND t.{b_col} = b.new_id""", (a_model, b_model))
        check(f"links {table}", got == want, f"{got}/{want}")

    # ------------------------------------------------------------------ production ids
    print("\n== production ids preserved (URLs, bookmarks, links inside messages) ==")
    # system users mapped by xmlid (public, portal template) and their partners exist on both sides
    system = f"""(SELECT res_id FROM {S}.ir_model_data WHERE model = 'res.users' AND module = 'base')"""
    for model, except_sql in (
        ("res.users", f"old_id IN {system}"),
        ("res.partner", f"old_id IN (SELECT partner_id FROM {S}.res_users WHERE id IN {system})"),
        ("project.project", "false"), ("project.task", "false"), ("project.tags", "false"),
        ("project.update", "false"), ("mom.meeting", "false"), ("person.person", "false"),
    ):
        moved = qall(f"SELECT old_id, new_id FROM etl_idmap WHERE model = %s AND old_id <> new_id AND NOT ({except_sql}) ORDER BY 1",
                     (model,))
        total = q1("SELECT count(*) FROM etl_idmap WHERE model = %s", (model,))
        check(f"ids {model}", not moved, f"{total - len(moved)}/{total} same id as prod" + (f"; moved: {moved[:5]}" if moved else ""))
    names = {"res.partner": "name", "project.project": "name->>'en_US'", "project.task": "name"}
    links = qall(f"""SELECT DISTINCT m[1], m[2]::int FROM {S}.mail_message s,
                     regexp_matches(s.body::text, '/odoo/(res\\.partner|project\\.task)/([0-9]+)', 'g') m
                     UNION SELECT DISTINCT 'project.project', m[1]::int FROM {S}.mail_message s,
                     regexp_matches(s.body::text, '/odoo/project/([0-9]+)', 'g') m
                     UNION SELECT DISTINCT 'project.task', m[1]::int FROM {S}.mail_message s,
                     regexp_matches(s.body::text, '/odoo/project/[0-9]+/tasks/([0-9]+)', 'g') m""")
    wrong = []
    for model, rid in links:
        table, col = model.replace(".", "_"), names[model]
        a_ = qall(f"SELECT {col} FROM {S}.{table} WHERE id = %s", (rid,))
        b_ = qall(f"SELECT {col} FROM {table} WHERE id = %s", (rid,))
        if a_ != b_:
            wrong.append((model, rid, a_[:1], b_[:1]))
    check("record links inside messages open the same record on 20", not wrong,
          f"{len(links)} distinct links" + (f"; wrong: {wrong[:4]}" if wrong else ""))

    # ------------------------------------------------------------------ every column, every row
    print("\n== every common column of the id-preserved tables, row by row (prod ids) ==")
    # (table, column) -> why a difference is expected; anything else must be identical
    EXPECTED = {
        ("project_task", "stage_id"): "stage ids are not kept (20 creates personal stages per user); compared by name above",
        ("project_task", "task_properties"): "NULL on 18 vs {} on 20, both mean no property value",
        ("project_project", "alias_id"): "alias records are 20's own; alias names compared in the link step",
        ("res_partner", "commercial_company_name"): "display value 20 computes (18 left it empty)",
        ("res_partner", "tz"): "legacy alias Asia/Calcutta is spelled Asia/Kolkata on 20",
        ("res_partner", "phone_sanitized"): "normalised form 20 computes from phone",
        ("res_partner", "signup_type"): "portal sign-up token type, regenerated by 20",
        ("res_users", "odoobot_state"): "deliberately not copied: OdooBot would restart its onboarding chat",
        ("res_users", "odoobot_failed"): "OdooBot onboarding flag, not copied with odoobot_state",
    }
    sys_users = f"(SELECT res_id FROM {S}.ir_model_data WHERE model = 'res.users' AND module = 'base')"
    skip_ids = {"res_users": sys_users, "res_partner": f"(SELECT partner_id FROM {S}.res_users WHERE id IN {sys_users})"}
    unexplained = []
    for table in ("project_task", "project_project", "project_tags", "project_update", "mom_meeting", "person_person",
                  "res_partner", "res_users"):
        cols = [c for (c,) in qall("""SELECT s.column_name FROM information_schema.columns s
                    JOIN information_schema.columns g ON g.table_schema = 'public' AND g.table_name = s.table_name
                         AND g.column_name = s.column_name
                    WHERE s.table_schema = %s AND s.table_name = %s ORDER BY 1""", (S, table))
                if c not in ("id", "write_date", "write_uid")]
        excl = f"AND s.id NOT IN {skip_ids[table]}" if table in skip_ids else ""
        for c in cols:
            n = q1(f"""SELECT count(*) FROM {S}.{table} s JOIN {table} g ON g.id = s.id
                       WHERE s."{c}"::text IS DISTINCT FROM g."{c}"::text {excl}""")
            if n and (table, c) not in EXPECTED:
                unexplained.append(f"{table}.{c}: {n}")
    check(f"no unexplained column difference ({len(EXPECTED)} explained: " + ", ".join(f"{t}.{c}" for t, c in EXPECTED) + ")",
          not unexplained, "; ".join(unexplained[:10]))
    langs = qall(f"""SELECT s.code FROM {S}.res_lang s JOIN res_lang t ON t.code = s.code WHERE s.active AND
                     (s.date_format, s.time_format, s.decimal_point, s.thousands_sep, s.grouping, s.week_start)
                     IS DISTINCT FROM (t.date_format, t.time_format, t.decimal_point, t.thousands_sep, t.grouping, t.week_start)""")
    check("date / time / number formats of the languages = prod's", not langs, f"differ: {langs}" if langs else "")
    stale = q1("""SELECT count(*) FROM project_task t WHERE (t.duration_tracking->>'d')::timestamp
                  > coalesce(t.date_last_stage_update, t.create_date) + interval '1 minute'""")
    check("time in stage counts from prod's history (not from the migration day)", stale == 0, f"{stale} tasks counting from the migration")

    # ------------------------------------------------------------------ field-level comparison
    print("\n== field-level comparison (every record, source vs target, through the id map) ==")
    def compare(name, model, table, exprs_src, exprs_tgt, joins_src="", joins_tgt=""):
        """exprs: SQL expressions on alias s (source row) / t (target row); compared as text."""
        es = " || '|' || ".join(f"coalesce(({e})::text, '∅')" for e in exprs_src)
        et = " || '|' || ".join(f"coalesce(({e})::text, '∅')" for e in exprs_tgt)
        diff = qall(f"""SELECT s.id, {es}, {et} FROM {S}.{table} s
                        JOIN etl_idmap m ON m.model = %s AND m.old_id = s.id
                        JOIN {table} t ON t.id = m.new_id {joins_src} {joins_tgt}
                        WHERE ({es}) IS DISTINCT FROM ({et})""", (model,))
        total = q1(f"SELECT count(*) FROM {S}.{table}")
        detail = ""
        if diff:
            by_field = {}
            for _id, a_, b_ in diff:
                for i, (x, y) in enumerate(zip(a_.split("|"), b_.split("|"))):
                    if x != y:
                        by_field.setdefault(exprs_tgt[i] if i < len(exprs_tgt) else i, []).append((_id, x[:60], y[:60]))
            detail = f"{len(diff)} differ; " + "; ".join(f"{f}: {len(v)} (e.g. #{v[0][0]} {v[0][1]!r} -> {v[0][2]!r})"
                                                       for f, v in by_field.items())
        check(f"{name}: {len(exprs_src)} fields on {total} records", not diff, detail)

    tr = lambda col: f"{col}->>'en_US'"  # noqa: E731
    # the source tz, as 20 spells it (legacy IANA aliases normalised, config.TZ_ALIASES)
    TZ_SRC = "CASE s.tz " + " ".join(f"WHEN '{k}' THEN '{v}'" for k, v in config.TZ_ALIASES.items()) + " ELSE s.tz END"
    compare("tasks", "project.task", "project_task",
            ["s.name", "pm.new_id", "ppm.new_id", tr("sst.name"), "s.state", "s.active", "s.priority", "s.sequence",
             "s.date_deadline", "s.planned_date_begin", "s.date_end", "s.date_assign", "s.date_last_stage_update",
             "md5(coalesce(s.description, ''))", "s.x_studio_responsible_person", "s.agenda", "pa.new_id",
             "coalesce(s.allocated_hours, 0)", "s.color", "s.create_date", "cu.new_id",
             f"(SELECT string_agg(um.new_id::text, ',' ORDER BY um.new_id) FROM {S}.project_task_user_rel r JOIN etl_idmap um ON um.model='res.users' AND um.old_id=r.user_id WHERE r.task_id = s.id)",
             f"(SELECT string_agg(tg.name->>'en_US', ',' ORDER BY tg.name->>'en_US') FROM {S}.project_tags_project_task_rel r JOIN {S}.project_tags tg ON tg.id = r.project_tags_id WHERE r.project_task_id = s.id)"],
            ["t.name", "t.project_id", "t.parent_id", tr("tst.name"), "t.state", "t.active", "t.priority", "t.sequence",
             "t.date_deadline", "t.planned_date_begin", "t.date_end", "t.date_assign", "t.date_last_stage_update",
             "md5(coalesce(t.description, ''))", "t.x_studio_responsible_person", "t.agenda", "t.partner_id",
             "coalesce(t.allocated_hours, 0)", "t.color", "t.create_date", "t.create_uid",
             "(SELECT string_agg(r.user_id::text, ',' ORDER BY r.user_id) FROM project_task_user_rel r WHERE r.task_id = t.id)",
             "(SELECT string_agg(tg.name->>'en_US', ',' ORDER BY tg.name->>'en_US') FROM project_tags_project_task_rel r JOIN project_tags tg ON tg.id = r.project_tags_id WHERE r.project_task_id = t.id)"],
            joins_src=f"""LEFT JOIN etl_idmap pm ON pm.model='project.project' AND pm.old_id = s.project_id
                          LEFT JOIN etl_idmap ppm ON ppm.model='project.task' AND ppm.old_id = s.parent_id
                          LEFT JOIN {S}.project_task_type sst ON sst.id = s.stage_id
                          LEFT JOIN etl_idmap pa ON pa.model='res.partner' AND pa.old_id = s.partner_id
                          LEFT JOIN etl_idmap cu ON cu.model='res.users' AND cu.old_id = s.create_uid""",
            joins_tgt="LEFT JOIN project_task_type tst ON tst.id = t.stage_id")
    # personal stage of each assignee
    want = q1(f"SELECT count(*) FROM {S}.project_task_user_rel")
    got = q1(f"""SELECT count(*) FROM {S}.project_task_user_rel s
                 JOIN etl_idmap tm ON tm.model='project.task' AND tm.old_id = s.task_id
                 JOIN etl_idmap um ON um.model='res.users' AND um.old_id = s.user_id
                 JOIN {S}.project_task_type ss ON ss.id = s.stage_id
                 JOIN project_task_user_rel r ON r.task_id = tm.new_id AND r.user_id = um.new_id
                 JOIN project_task_type ts ON ts.id = r.stage_id
                 WHERE ts.name->>'en_US' = ss.name->>'en_US' AND ts.user_id = um.new_id""")
    check("personal stage of every assignee (My Tasks columns)", got == want, f"{got}/{want}")
    compare("projects", "project.project", "project_project",
            ["s.name->>'en_US'", "s.active", "um.new_id", tr("sps.name"), "s.date_start", "s.date", "s.privacy_visibility",
             "md5(coalesce(s.description, ''))", "s.last_update_status", "s.sequence", "s.color", "s.label_tasks->>'en_US'",
             "s.allow_task_dependencies", "s.allow_milestones", "s.create_date",
             f"(SELECT string_agg(tt.name->>'en_US', ',' ORDER BY tt.sequence, tt.id) FROM {S}.project_task_type_rel r JOIN {S}.project_task_type tt ON tt.id = r.type_id WHERE r.project_id = s.id)"],
            ["t.name->>'en_US'", "t.active", "t.user_id", tr("tps.name"), "t.date_start", "t.date", "t.privacy_visibility",
             "md5(coalesce(t.description, ''))", "t.last_update_status", "t.sequence", "t.color", "t.label_tasks->>'en_US'",
             "t.allow_task_dependencies", "t.allow_milestones", "t.create_date",
             "(SELECT string_agg(tt.name->>'en_US', ',' ORDER BY tt.sequence, tt.id) FROM project_task_type_rel r JOIN project_task_type tt ON tt.id = r.type_id WHERE r.project_id = t.id)"],
            joins_src=f"""LEFT JOIN etl_idmap um ON um.model='res.users' AND um.old_id = s.user_id
                          LEFT JOIN {S}.project_project_stage sps ON sps.id = s.stage_id""",
            joins_tgt="LEFT JOIN project_project_stage tps ON tps.id = t.stage_id")
    compare("project updates", "project.update", "project_update",
            ["s.name", "s.status", "s.progress", "s.date", "md5(coalesce(s.description, ''))", "pm.new_id", "um.new_id", "s.create_date"],
            ["t.name", "t.status", "t.progress", "t.date", "md5(coalesce(t.description, ''))", "t.project_id", "t.user_id", "t.create_date"],
            joins_src="""LEFT JOIN etl_idmap pm ON pm.model='project.project' AND pm.old_id = s.project_id
                         LEFT JOIN etl_idmap um ON um.model='res.users' AND um.old_id = s.user_id""")
    compare("task stages", "project.task.type", "project_task_type",
            ["s.name->>'en_US'", "s.sequence", "s.fold", "s.active", "um.new_id"],
            ["t.name->>'en_US'", "t.sequence", "t.fold", "t.active", "t.user_id"],
            joins_src="LEFT JOIN etl_idmap um ON um.model='res.users' AND um.old_id = s.user_id")
    compare("legacy MOM lines", "mom.meeting", "mom_meeting",
            ["tm.new_id", "s.seq", "s.remarks", "s.related_to", "s.end_date", "s.create_date", "cu.new_id"],
            ["t.task_id", "t.seq", "t.remarks", "t.related_to", "t.end_date", "t.create_date", "t.create_uid"],
            joins_src="""LEFT JOIN etl_idmap tm ON tm.model='project.task' AND tm.old_id = s.task_id
                         LEFT JOIN etl_idmap cu ON cu.model='res.users' AND cu.old_id = s.create_uid""")
    compare("responsibilities", "person.person", "person_person",
            ["tm.new_id", "s.seq", "s.from_client", "s.from_architect", "s.from_agency"],
            ["t.task_id", "t.seq", "t.from_client", "t.from_architect", "t.from_agency"],
            joins_src="LEFT JOIN etl_idmap tm ON tm.model='project.task' AND tm.old_id = s.task_id")
    compare("partners", "res.partner", "res_partner",
            ["s.name", "s.email", "coalesce(nullif(s.phone, ''), nullif(s.mobile, ''))", "s.street", "s.street2", "s.city",
             "s.zip", "s.vat", "s.website", "s.is_company", "s.active", "s.function", "s.lang", TZ_SRC],
            ["t.name", "t.email", "nullif(t.phone, '')", "t.street", "t.street2", "t.city",
             "t.zip", "t.vat", "t.website", "t.is_company", "t.active", "t.function", "t.lang", "t.tz"])

    # ------------------------------------------------------------------ users and access
    print("\n== users and access ==")
    compare("users", "res.users", "res_users",
            ["s.login", "s.active", "s.share", "s.password", "s.totp_secret", "s.notification_type", "s.signature"],
            ["t.login", "t.active", "t.share", "t.password", "t.totp_secret", "t.notification_type",
             "CASE WHEN coalesce(s.signature, '') = '' THEN s.signature ELSE t.signature END"])   # 20 fills an empty signature
    # effective groups on 20 = explicit memberships + everything they imply (transitively).
    # uid 1 (__system__) is the superuser: on 20 it holds no group at all, by design.
    missing = qall(f"""WITH RECURSIVE eff(uid, gid) AS (
                           SELECT uid, gid FROM res_groups_users_rel
                           UNION SELECT e.uid, i.hid FROM eff e JOIN res_groups_implied_rel i ON i.gid = e.gid)
                       SELECT us.login, sd.module || '.' || sd.name FROM {S}.res_groups_users_rel r
                       JOIN {S}.res_users us ON us.id = r.uid
                       JOIN etl_idmap um ON um.model = 'res.users' AND um.old_id = r.uid
                       JOIN {S}.ir_model_data sd ON sd.model = 'res.groups' AND sd.res_id = r.gid
                       JOIN ir_model_data td ON td.model = 'res.groups' AND td.module = sd.module AND td.name = sd.name
                       WHERE r.uid <> 1 AND NOT EXISTS (SELECT 1 FROM eff e WHERE e.uid = um.new_id AND e.gid = td.res_id)""")
    check("every 18 group membership that exists on 20 is held on 20 (explicit or implied)", not missing,
          f"missing: {missing[:5]}" if missing else "")
    extra = qall(f"""WITH RECURSIVE eff18(uid, gid) AS (
                         SELECT uid, gid FROM {S}.res_groups_users_rel
                         UNION SELECT e.uid, i.hid FROM eff18 e JOIN {S}.res_groups_implied_rel i ON i.gid = e.gid)
                     SELECT u.login, td.module || '.' || td.name FROM res_groups_users_rel r
                     JOIN res_users u ON u.id = r.uid
                     JOIN etl_idmap um ON um.model = 'res.users' AND um.new_id = r.uid
                     JOIN ir_model_data td ON td.model = 'res.groups' AND td.res_id = r.gid
                     JOIN {S}.ir_model_data sd ON sd.model = 'res.groups' AND sd.module = td.module AND sd.name = td.name
                     WHERE r.uid > 2 AND NOT EXISTS (SELECT 1 FROM eff18 e WHERE e.uid = um.old_id AND e.gid = sd.res_id)""")
    check("no user gained a right 18 did not give (groups that exist on both)", not extra,
          f"extra: {extra[:5]}" if extra else "")
    gone = qall(f"""SELECT DISTINCT sd.module || '.' || sd.name FROM {S}.res_groups_users_rel r
                    JOIN etl_idmap um ON um.model = 'res.users' AND um.old_id = r.uid
                    JOIN {S}.ir_model_data sd ON sd.model = 'res.groups' AND sd.res_id = r.gid
                    WHERE NOT EXISTS (SELECT 1 FROM ir_model_data td WHERE td.model = 'res.groups'
                                      AND td.module = sd.module AND td.name = sd.name)""")
    print(f"       info: 18 groups with no 20 counterpart (dropped by design): {[g[0] for g in gone]}")
    check("menu visibility deltas carried", q1(f"""SELECT count(*) FROM {S}.ir_ui_menu_group_rel r
            JOIN {S}.ir_model_data smd ON smd.model='ir.ui.menu' AND smd.res_id=r.menu_id
            JOIN ir_model_data tm ON tm.model='ir.ui.menu' AND tm.module=smd.module AND tm.name=smd.name
            JOIN {S}.ir_model_data sgd ON sgd.model='res.groups' AND sgd.res_id=r.gid
            JOIN ir_model_data tg ON tg.model='res.groups' AND tg.module=sgd.module AND tg.name=sgd.name
            WHERE NOT EXISTS (SELECT 1 FROM ir_ui_menu_group_rel e WHERE e.menu_id=tm.res_id AND e.gid=tg.res_id)""") == 0)

    # ------------------------------------------------------------------ studio
    print("\n== Studio customizations ==")
    for model, name in qall(f"SELECT model, name FROM {S}.ir_model_fields WHERE state = 'manual' ORDER BY model, name"):
        check(f"field {model}.{name}", q1("SELECT count(*) FROM ir_model_fields WHERE model=%s AND name=%s AND state='manual'",
                                          (model, name)) == 1)
    for xname, in qall(f"SELECT name FROM {S}.ir_model_data WHERE module='studio_customization' AND model='ir.ui.view'"):
        check(f"view studio_customization.{xname}",
              q1("""SELECT count(*) FROM ir_model_data d JOIN ir_ui_view v ON v.id = d.res_id
                    WHERE d.module='studio_customization' AND d.name=%s AND v.active""", (xname,)) == 1)

    # ------------------------------------------------------------------ activities + MOM upgrade
    print("\n== activities ==")
    compare("activities (every source activity)", "mail.activity", "mail_activity",
            ["s.res_model", "rm.new_id", "atm.new_id", "um.new_id", "s.date_deadline", "s.summary",
             "md5(coalesce(s.note, ''))", "s.active", "s.date_done", "s.create_date"],
            ["t.res_model", "t.res_id", "t.activity_type_id", "t.user_id", "t.date_deadline", "t.summary",
             "md5(coalesce(t.note, ''))", "t.active", "t.date_done", "t.create_date"],
            joins_src=f"""LEFT JOIN etl_idmap rm ON rm.model = s.res_model AND rm.old_id = s.res_id
                          LEFT JOIN etl_idmap atm ON atm.model = 'mail.activity.type' AND atm.old_id = s.activity_type_id
                          LEFT JOIN etl_idmap um ON um.model='res.users' AND um.old_id = s.user_id""",
            )
    src_mom_col = q1(f"""SELECT count(*) FROM information_schema.columns WHERE table_schema='{S}'
                         AND table_name='mail_activity' AND column_name='mom_meeting_id'""")
    src_visit_date = q1(f"""SELECT count(*) FROM information_schema.columns WHERE table_schema='{S}'
                            AND table_name='mail_activity' AND column_name='mom_visit_date'""")
    if src_mom_col:
        # a source already at module 1.1+: its MOM entries were carried, field by field (and their
        # visit dates from 1.8.0 on; an older source gets them from the replayed 1.8.0 script)
        date_cols = (["s.mom_visit_date"], ["t.mom_visit_date"]) if src_visit_date else ([], [])
        compare("MOM fields of carried entries", "mail.activity", "mail_activity",
                ["s.mom_sequence", "s.mom_visit_no", "pm.new_id", "mm.new_id", "tm.new_id", "jm.new_id"] + date_cols[0],
                ["t.mom_sequence", "t.mom_visit_no", "t.mom_partner_id", "t.mom_meeting_id", "t.mom_task_id",
                 "t.mom_project_id"] + date_cols[1],
                joins_src="""LEFT JOIN etl_idmap pm ON pm.model='res.partner' AND pm.old_id = s.mom_partner_id
                             LEFT JOIN etl_idmap mm ON mm.model='mom.meeting' AND mm.old_id = s.mom_meeting_id
                             LEFT JOIN etl_idmap tm ON tm.model='project.task' AND tm.old_id = s.mom_task_id
                             LEFT JOIN etl_idmap jm ON jm.model='project.project' AND jm.old_id = s.mom_project_id""")
    lines = q1("SELECT count(*) FROM mom_meeting")
    one_each = q1("""SELECT count(*) FROM mom_meeting l WHERE
                     (SELECT count(*) FROM mail_activity a WHERE a.mom_meeting_id = l.id) = 1""")
    check("every legacy MOM line has exactly one MOM entry", one_each == lines, f"{one_each}/{lines}")
    check("MOM entries numbered without gaps per task (Sr. No. unique)",
          q1("""SELECT count(*) FROM (SELECT res_id, mom_sequence FROM mail_activity a JOIN mail_activity_type t
                ON t.id = a.activity_type_id WHERE t.is_mom GROUP BY 1, 2 HAVING count(*) > 1) d""") == 0)
    check("MOM entries carry their task + project (dashboard relations)",
          q1("""SELECT count(*) FROM mail_activity a JOIN mail_activity_type t ON t.id = a.activity_type_id
                WHERE t.is_mom AND (a.mom_task_id IS NULL OR a.mom_project_id IS NULL)""") == 0)
    check("every MOM entry has a Visit Date",
          q1("""SELECT count(*) FROM mail_activity a JOIN mail_activity_type t ON t.id = a.activity_type_id
                WHERE t.is_mom AND a.mom_visit_date IS NULL""") == 0)
    off_rank = q1("""SELECT count(*) FROM (
                         SELECT a.mom_visit_no, dense_rank() OVER (PARTITION BY a.mom_project_id ORDER BY a.mom_visit_date) AS rnk
                         FROM mail_activity a JOIN mail_activity_type t ON t.id = a.activity_type_id
                         WHERE t.is_mom AND a.mom_project_id IS NOT NULL) r WHERE r.mom_visit_no <> r.rnk""")
    check("Visit No# is the rank of the Visit Date in its project (1.8.0 rule)", off_rank == 0, f"{off_rank} off")
    photos_lines = q1(f"SELECT count(*) FROM {S}.ir_attachment WHERE res_model='mom.meeting' AND res_field='site_photo'")
    photos_acts = q1("""SELECT count(*) FROM ir_attachment a JOIN mail_activity m ON m.id = a.res_id
                        WHERE a.res_model='mail.activity' AND a.res_field='mom_site_photo' AND m.mom_meeting_id IS NOT NULL""")
    check("every legacy site photo is on its MOM entry", photos_acts == photos_lines, f"{photos_acts}/{photos_lines}")
    if a.oracle:
        print(f"   oracle: {a.oracle} (an 18 DB that ran the real upgrade on this data)")
        oc = psycopg2.connect(dbname=a.oracle).cursor()
        sel = """SELECT pj.name->>'en_US', t.name, t.create_date, a.mom_sequence, a.mom_visit_no, a.mom_visit_date, a.summary,
                        md5(coalesce(a.note, '')), a.date_deadline,
                        u.login, p.name, a.create_date, a.active, coalesce(ph.checksum, '-')
                 FROM mail_activity a JOIN project_task t ON t.id = a.res_id LEFT JOIN project_project pj ON pj.id = t.project_id
                 LEFT JOIN res_users u ON u.id = a.user_id LEFT JOIN res_partner p ON p.id = a.mom_partner_id
                 LEFT JOIN ir_attachment ph ON ph.res_model='mail.activity' AND ph.res_field='mom_site_photo' AND ph.res_id = a.id
                 WHERE a.mom_meeting_id IS NOT NULL ORDER BY 1, 2, 3, 4"""
        oc.execute(sel)
        want_rows = sorted(oc.fetchall(), key=lambda r: tuple(map(str, r)))
        got_rows = sorted(qall(sel), key=lambda r: tuple(map(str, r)))
        diff = [(w, g) for w, g in zip(want_rows, got_rows) if w != g]
        check("MOM upgrade replay == oracle (task, Sr. No., visit, visit date, remark, note, end date, assignee, Related To, "
              "created, closed, photo checksum)", len(want_rows) == len(got_rows) and not diff,
              f"{len(got_rows)}/{len(want_rows)} entries" + (f"; first diff {diff[0]}" if diff else ""))
    elif not src_mom_col:
        print("   (no --oracle given: replayed upgrade checked structurally only)")

    # ------------------------------------------------------------------ chatter
    print("\n== chatter ==")
    for model, in qall(f"SELECT DISTINCT model FROM {S}.mail_message WHERE model IS NOT NULL ORDER BY 1"):
        want = q1(f"""SELECT count(*) FROM {S}.mail_message s JOIN etl_idmap m ON m.model = s.model AND m.old_id = s.res_id
                      WHERE s.model = %s""", (model,))
        allsrc = q1(f"SELECT count(*) FROM {S}.mail_message WHERE model = %s", (model,))
        got = q1(f"""SELECT count(*) FROM {S}.mail_message s JOIN etl_idmap m ON m.model = s.model AND m.old_id = s.res_id
                     JOIN mail_message t ON t.id = s.id + {OFF} AND t.res_id = m.new_id AND t.model = s.model
                     WHERE s.model = %s""", (model,))
        note = "" if want == allsrc else f" ({allsrc - want} on records that are not migrated)"
        check(f"messages {model}", got == want, f"{got}/{want}{note}")
    compare("message content", "mail.message", "mail_message",
            ["s.message_type <> 'tracking' AND s.body IS NOT NULL AND s.body NOT IN ('', '<p></p>')", "s.subject",
             "pa.new_id", "s.date", "s.subtype_id IS NOT NULL", "s.is_internal"],
            ["t.message_type <> 'tracking' AND t.body IS NOT NULL AND t.body NOT IN ('', '<p></p>')", "t.subject",
             "t.author_id", "t.date", "t.subtype_id IS NOT NULL", "t.is_internal"],
            joins_src="LEFT JOIN etl_idmap pa ON pa.model='res.partner' AND pa.old_id = s.author_id")
    for table, cond in (("mail_tracking_value", "true"), ("mail_notification", "true"), ("mail_message_reaction", "true"),
                        ("mail_mail", "true")):
        want = q1(f"""SELECT count(*) FROM {S}.{table} s WHERE EXISTS (SELECT 1 FROM mail_message t WHERE t.id =
                      s.{'message_id' if table == 'mail_message_reaction' else 'mail_message_id'} + {OFF})""")
        got = q1(f"SELECT count(*) FROM {table} WHERE id > {OFF}")
        check(f"rows {table}", got == want, f"{got}/{want}")
    want = q1(f"""SELECT count(*) FROM {S}.mail_followers s JOIN etl_idmap m ON m.model = s.res_model AND m.old_id = s.res_id""")
    got = q1(f"SELECT count(*) FROM mail_followers WHERE id > {OFF}")
    check("followers", got == want, f"{got}/{want}")
    want = q1(f"SELECT count(*) FROM {S}.message_attachment_rel r WHERE EXISTS (SELECT 1 FROM mail_message t WHERE t.id = r.message_id + {OFF})")
    got = q1(f"SELECT count(*) FROM message_attachment_rel WHERE message_id > {OFF}")
    check("attachments posted in chatter", got == want, f"{got}/{want}")
    check("tracked changes visible (rendered body on 20)",
          q1(f"""SELECT count(*) FROM mail_message m WHERE m.id > {OFF} AND EXISTS (SELECT 1 FROM mail_tracking_value v
                 WHERE v.mail_message_id = m.id) AND (m.body IS NULL OR m.body = '')""") == 0)
    check("no ETL-born message on migrated records",
          q1(f"""SELECT count(*) FROM mail_message m WHERE m.id < {OFF} AND m.model IS NOT NULL AND m.model <> 'discuss.channel'
                 AND EXISTS (SELECT 1 FROM etl_idmap x WHERE x.model = m.model AND x.new_id = m.res_id)""") == 0)

    # ------------------------------------------------------------------ attachments + filestore
    print("\n== attachments and filestore ==")
    want = q1(f"""SELECT count(*) FROM {S}.ir_attachment s
                  LEFT JOIN etl_idmap m ON m.model = s.res_model AND m.old_id = s.res_id
                  WHERE NOT {ATTACHMENT_EXCLUSIONS} AND (s.res_model IS NULL OR s.res_id IS NULL OR s.res_id = 0 OR m.new_id IS NOT NULL)""")
    got = q1(f"""SELECT count(*) FROM {S}.ir_attachment s JOIN ir_attachment t ON t.id = s.id + {OFF}
                 WHERE t.checksum IS NOT DISTINCT FROM s.checksum AND t.file_size IS NOT DISTINCT FROM s.file_size""")
    dedup = q1(f"""SELECT count(*) FROM {S}.ir_attachment s WHERE s.res_field IS NOT NULL AND EXISTS (
                   SELECT 1 FROM {S}.ir_attachment b WHERE b.res_model = s.res_model AND b.res_id = s.res_id
                   AND b.res_field = s.res_field AND b.id > s.id)""")
    check("attachments carried byte-identical (checksum + size)", got == want - dedup,
          f"{got}/{want - dedup}" + (f" ({dedup} superseded uploads of one binary field, newest kept)" if dedup else ""))
    excluded = qall(f"SELECT coalesce(s.res_model, '(none)'), count(*) FROM {S}.ir_attachment s WHERE {ATTACHMENT_EXCLUSIONS} GROUP BY 1")
    print(f"       info: not carried by design (rebuilt by 20 / not data): {dict(excluded)}")
    for model, field, n in qall(f"""SELECT res_model, res_field, count(*) FROM {S}.ir_attachment
                                    WHERE res_field IS NOT NULL AND res_model NOT IN ('ir.ui.menu','res.lang') GROUP BY 1, 2 ORDER BY 1, 2"""):
        got = q1(f"""SELECT count(*) FROM ir_attachment t JOIN {S}.ir_attachment s ON t.id = s.id + {OFF}
                     WHERE s.res_model = %s AND s.res_field = %s AND t.res_field = s.res_field""", (model, field))
        check(f"binary field {model}.{field}", got == n, f"{got}/{n}")
    fs = os.path.join(config.ETL_DIR, "data20", "filestore", a.db)
    rows = qall(f"SELECT id, store_fname, checksum FROM ir_attachment WHERE store_fname IS NOT NULL AND id > {OFF}")
    missing = bad = 0
    for _id, fname, checksum in rows:
        path = os.path.join(fs, fname)
        if not os.path.exists(path):
            missing += 1; continue
        with open(path, "rb") as f:
            if hashlib.sha1(f.read()).hexdigest() != checksum:
                bad += 1
    check("every migrated file present in the 20 filestore", missing == 0, f"{len(rows) - missing}/{len(rows)} in {fs}")
    check("every file's bytes match its checksum (sha1)", bad == 0, f"{bad} corrupt" if bad else f"{len(rows)} verified")
    broken = q1("SELECT count(*) FROM ir_attachment WHERE type = 'binary' AND store_fname IS NULL AND db_datas IS NULL AND coalesce(file_size, 0) > 0")
    check("no binary attachment without content", broken == 0, f"{broken}")

    # the company logo as the web client serves it (stored caches of the partner image)
    src_logo = q1(f"""SELECT count(*) FROM {S}.ir_attachment WHERE res_model = 'res.partner' AND res_field = 'image_1920'
                      AND res_id = (SELECT partner_id FROM {S}.res_company ORDER BY id LIMIT 1)""")
    default_logo = q1("SELECT uses_default_logo FROM res_company ORDER BY id LIMIT 1")
    # logo_web is rewritten in place when recomputed: a cache never rewritten since the empty target was
    # created still holds 20's "Your logo" placeholder
    web_logo_fresh = q1("""SELECT count(*) FROM ir_attachment w JOIN res_company c ON w.res_model = 'res.company'
                           AND w.res_id = c.id AND w.res_field = 'logo_web' WHERE w.write_date > w.create_date""")
    check("company logo served by the web client is prod's (logo_web recomputed)",
          not src_logo or (default_logo is False and web_logo_fresh == 1),
          f"prod logo: {bool(src_logo)}, uses_default_logo={default_logo}, logo_web recomputed: {bool(web_logo_fresh)}")

    # ------------------------------------------------------------------ discuss
    print("\n== discuss ==")
    want = q1(f"SELECT count(*) FROM {S}.discuss_channel_member WHERE guest_id IS NULL")
    got = q1(f"""SELECT count(*) FROM {S}.discuss_channel_member s JOIN etl_idmap c ON c.model='discuss.channel' AND c.old_id=s.channel_id
                 JOIN etl_idmap p ON p.model='res.partner' AND p.old_id=s.partner_id
                 JOIN discuss_channel_member t ON t.channel_id = c.new_id AND t.partner_id = p.new_id""")
    check("channel members", got == want, f"{got}/{want}")
    check("direct chats are 1:1 chats on 20", q1("SELECT count(*) FROM discuss_channel WHERE channel_type='chat' AND member_indices IS NULL") == 0)

    # ------------------------------------------------------------------ safety
    print("\n== dry-run safety (this is a test copy) ==")
    if not config.PRODUCTION:
        check("no active cron", q1("SELECT count(*) FROM ir_cron WHERE active") == 0)
        check("no active outgoing mail server", q1("SELECT count(*) FROM ir_mail_server WHERE active") == 0)
    check("no queued outgoing e-mail", q1("SELECT count(*) FROM mail_mail WHERE state = 'outgoing'") == 0)

    print(f"\n{'ALL GREEN' if not failures else f'{len(failures)} FAILURE(S)'}")
    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    main()
