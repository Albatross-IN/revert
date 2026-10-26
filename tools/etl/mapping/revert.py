"""Phase 'revert' (revert_customizations data) and the activity load.

* mom.meeting (legacy MOM lines) and person.person (responsibilities) through the ORM; the
  site photos are attachments and arrive with the chatter phase.
* mail.activity, SQL lane at +OFFSET (an ORM create would notify assignees and subscribe them):
  every open and closed activity of a migrated record. On a source already at module 1.1+ the MOM
  fields (Related To, visit, sequence, legacy line) are carried; an older source has none.
* the module upgrade: production on 18 runs revert_customizations at whatever version the
  source records (18.0.1.0.0 on the 2026-08-31 backup); the target runs 20.0.1.8.0. Every
  migration script of the module newer than the source version is run on the target, in order,
  exactly as an upgrade on 18 would have run them: 1.1.0 turns each legacy MOM line into a closed
  MOM activity (with its photo), 1.2.0 links, 1.4.0 restores the real creation date, 1.6.0
  numbers the site visits by date, 1.8.0 gives every entry a Visit Date and ranks the visits by
  it. Folders are compared on the module part only (18.0.1.6.0 and 20.0.1.8.0 are 1.6.0 and
  1.8.0), since the scripts written on 20 also have to run against an 18 source. Runs after the
  chatter phase (photos must exist)."""
import importlib.util
import logging
import os

from ..core import OrmStep, FuncStep, TableCopy, IDM
from .. import config

_logger = logging.getLogger("etl.revert")
S = config.SRC_SCHEMA
MODULE = "revert_customizations"

MOM_LINES = OrmStep("mom.meeting", force_fields={"seq"}, keep_ids=True,
                    transform=lambda v, r, c: v if v.get("task_id") else None)
PERSONS = OrmStep("person.person", force_fields={"seq"}, keep_ids=True,
                  transform=lambda v, r, c: v if v.get("task_id") else None)

ACTIVITIES = TableCopy(
    "mail.activity", "mail_activity",
    joins=["LEFT JOIN etl_idmap m ON m.model = s.res_model AND m.old_id = s.res_id",
           "LEFT JOIN ir_model im ON im.model = s.res_model",
           IDM("at", "mail.activity.type", "s.activity_type_id"), IDM("u", "res.users", "s.user_id"),
           IDM("mp", "res.partner", "s.mom_partner_id"), IDM("mm", "mom.meeting", "s.mom_meeting_id"),
           IDM("mt", "project.task", "s.mom_task_id"), IDM("mj", "project.project", "s.mom_project_id")],
    where="(s.res_model IS NULL OR m.new_id IS NOT NULL) AND at.new_id IS NOT NULL",
    overrides={"id": "s.id + {OFF}", "res_model_id": "im.id", "res_id": "m.new_id", "activity_type_id": "at.new_id",
               "user_id": "u.new_id", "mom_partner_id": "mp.new_id", "mom_meeting_id": "mm.new_id",
               "mom_task_id": "mt.new_id", "mom_project_id": "mj.new_id", "activity_plan_id": "NULL",
               "activity_template_id": "NULL", "role_id": "NULL"},
    extra={"technical_usage": "'none'"},
    register=("mail.activity", "mail_activity"), on_conflict="DO NOTHING",
)


def _activity_sequence(engine, ctx):
    engine.cr.execute("SELECT setval(pg_get_serial_sequence('mail_activity', 'id'), "
                      "GREATEST((SELECT coalesce(max(id), 1) FROM mail_activity), 1))")
    return {}


ACTIVITY_SEQ = FuncStep("mail.activity.sequence", _activity_sequence)


def _version_key(v):
    """The module part of a version: 18.0.1.6.0 and 20.0.1.6.0 are both (1, 6, 0)."""
    return tuple(int(x) for x in v.split(".")[-3:])


def _module_upgrade(engine, ctx):
    cr, env = engine.cr, engine.env
    cr.execute(f"SELECT latest_version FROM {S}.ir_module_module WHERE name = %s AND state = 'installed'", (MODULE,))
    row = cr.fetchone()
    if not row or not row[0]:
        return dict(skipped=f"{MODULE} not installed on the source")
    src_version = row[0]
    from odoo.modules.module import get_module_path
    root = os.path.join(get_module_path(MODULE), "migrations")
    ran = []
    for version in sorted(os.listdir(root), key=_version_key):
        if _version_key(version) <= _version_key(src_version):
            continue
        for stage in ("pre-migrate.py", "post-migrate.py", "end-migrate.py"):
            path = os.path.join(root, version, stage)
            if not os.path.exists(path):
                continue
            spec = importlib.util.spec_from_file_location(f"etl_{MODULE}_{version}_{stage[:-3]}", path)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            mod.migrate(cr, src_version)
            env.flush_all()
            env.invalidate_all()
            ran.append(f"{version}/{stage}")
            _logger.info("%s migration %s/%s done", MODULE, version, stage)
    cr.execute("""SELECT count(*), count(a.mom_meeting_id), count(*) FILTER (WHERE a.active)
                  FROM mail_activity a JOIN mail_activity_type t ON t.id = a.activity_type_id WHERE t.is_mom""")
    total, synced, open_ = cr.fetchone()
    return dict(source_version=src_version, ran=ran, mom_entries=total, from_legacy_lines=synced, open=open_)


MODULE_UPGRADE = FuncStep("revert_customizations.upgrade", _module_upgrade)

STEPS = [MOM_LINES, PERSONS]
ACTIVITY_STEPS = [ACTIVITIES, ACTIVITY_SEQ]
POST_CHATTER_STEPS = [MODULE_UPGRADE]
