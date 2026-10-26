# Revert: Odoo 18 → Odoo 20 migration

Code: this repository, branch `20.0` (`revert_customizations` 20.0.1.7.0, `admin_notes_viewer` 20.0.1.0.0).
Data: `tools/etl/` (fresh Odoo 20 database + explicit transformation of the Odoo 18 data).
Runtime directory: `/opt/odoo20/etl_revert` (staged source filestore, logs, QA output).

## 1. Upgrade path

| | |
|---|---|
| Source | Odoo **18.0 Enterprise** (`18.0+e`), self-hosted (147.93.30.85:8020), PostgreSQL 16, 52 modules |
| Target | Odoo **20.0 Enterprise** (`20.0+e`, build of 2026-09-17), PostgreSQL 18, Python 3.12 |
| Subscription | the database records only an expired trial (`database.expiration_reason = trial`, 2025-05-25) |

Options considered:

* **Odoo's upgrade service** (upgrade.odoo.com) is the vendor path for Enterprise databases: it handles
  the intermediate version (18 → 19 → 20) on Odoo's side, but needs a valid Enterprise subscription,
  means sending the production database to Odoo, and does not migrate custom modules or their data
  (`revert_customizations` would still need porting plus its own data migration).
* **OpenUpgrade** (OCA) covers Community modules only, one version at a time; it has nothing for the
  Enterprise modules this database uses (`project_enterprise`, `web_studio`, `web_gantt`, …).
* **Chosen: no conversion of the 18 database at all.** A fresh 20 database is installed with the same
  module set, and the 18 records are loaded into it by `tools/etl`: business records through the
  Odoo 20 ORM (20's own validation applies), history (chatter, attachments, activities) by SQL with
  every 18 → 20 schema difference mapped explicitly. No intermediate 19 hop is needed because nothing
  of the 18 schema is upgraded in place, and the result is proven field by field against the source
  (§4). The production database is only ever read from a backup.

## 2. Replay from a fresh production backup (the cutover procedure)

Take a backup on production (database manager → Backup, "zip" format with filestore; or `pg_dump -Fc`
plus a copy of the filestore). Then, as `om1203` on this machine:

```bash
cd /opt/odoo20/custom/revert_20
tools/etl/restore_src.sh /path/to/revert_<date>.zip      # or: restore_src.sh <dump> <filestore_dir>
/opt/odoo20/odoo20-venv/bin/python tools/etl/gen_target_modules.py
tools/etl/mkdb.sh revert20_etl_final
/opt/odoo20/odoo20-venv/bin/python -m tools.etl.run    --db revert20_etl_final
/opt/odoo20/odoo20-venv/bin/python -m tools.etl.verify --db revert20_etl_final     # must print ALL GREEN
```

About one minute end to end. `restore_src.sh` neutralizes the copy (crons, mail servers, IAP tokens,
push keys off) before anything reads it. Every run builds a NEW target, so there are no duplicates and
no partial states; a failed step is fixed in `tools/etl/mapping/*.py` and the target rebuilt — a target
database is never patched by hand. `run.py --list` prints the 68 steps; `--phase`/`--only` re-run parts.

Production changes made after a backup are picked up by replaying from a newer backup (the whole
pipeline is deterministic and takes a minute); this is preferred over the engine's experimental delta
mode (`--delta-t0`, inherited, not exercised on Revert).

The pipeline adapts to the module version found in the backup:
* `revert_customizations` 18.0.1.0.0 (the 2026-08-31 backup): no MOM activities exist yet; the
  module's own migration scripts 1.1.0 → 1.6.0 are replayed on the target (legacy MOM lines become
  closed MOM activities with their photos, visits numbered by date) — exactly what upgrading production
  would have done. Proven identical to an 18 database that really ran that upgrade (`verify --oracle`).
* 18.0.1.6.0 / 1.7.0 (proven with the local dev copy as a second source): the MOM activities and their
  fields are carried as they are; no migration script is replayed.

## 3. What the ETL does (18 → 20 decisions)

| Area | Rule |
|---|---|
| Users | logins, password hashes and TOTP secrets copied (prod credentials work), group memberships by xmlid, admin's partner (time zone!) and signature, login history |
| Partners | `mobile` no longer exists on 20 → becomes `phone` (or a note if both are set) |
| Projects | prod's stages only (20 would add four default stages per project); favourites, alias, last update |
| Task stages | project stages owned by nobody; personal stages (Inbox, Today, …) land on the ones 20 creates per user |
| Tasks | private to-dos created one by one (20 applies a parent's project to a whole create batch); 20's create-time stamps (assignment / stage / end dates, allocated hours, default stage) reset to prod's values |
| Studio | `x_studio_responsible_person`, the two Studio views, the empty `x_mom.rec` model — recreated with their `studio_customization` xmlids |
| Activities | all 118 at +10,000,000 ids; web_studio's "Grant Approval" type recreated as a plain type (20 dropped it) |
| Chatter | messages, followers, notifications, reactions, tracked values (module `mail_tracking` added; their bodies rendered because 20 shows tracking from the body) |
| Attachments | byte-identical files hard-linked into the 20 filestore; 18's compiled JS/CSS asset bundles are not carried (20 builds its own) |
| Discuss | 19 conversations and their members; direct chats get 20's member index |
| Settings | config parameters the user set, report font/colours/paper format, quarterly digest + subscribers |
| Not carried | language flags/menu icons/asset bundles (rebuilt by 20), the `iap.account` record and its one message, 18's "Default User Template" user, the `project_todo.group_onboarding_todo` group (gone on 20) |

## 4. Verification

`python -m tools.etl.verify --db <target> [--oracle <18 db that ran the module upgrade>]` — 84 checks:
every source record mapped once; **field-by-field comparison** of every task (23 fields incl. assignees,
tags, Studio value), project, stage, update, MOM line, responsibility, partner, user (password hash,
TOTP, signature) and activity; group memberships (no right lost, none gained); menu visibility; Studio
fields and views; MOM upgrade replay vs the oracle (task, Sr. No., visit, remark, note, end date,
assignee, Related To, created, closed, photo checksum); chatter per model; attachments by checksum and
size; **every file in the 20 filestore re-hashed (sha1) against its checksum**; channel members;
no active cron, no outgoing mail server, no queued e-mail.

Functional QA (on a throwaway clone, never on a database people use):

```bash
tools/etl/qa/browser_qa.py --base http://localhost:8174 --db <clone> --menus /dev/null --out /opt/odoo20/etl_revert/qa
```

15 browser checks (Chrome headless): every visible menu in normal and debug mode opens without a JS
error; the MOM dashboard of every project matches the database (KPIs, charts, rows) and its filters
work; "Print entries" PDF; task MOM tab (closed entries included); Studio field; chatter with tracked
changes; attachment downloads byte-identical; "Create MOM" (Related To, photo, next Sr. No., visit
No#); mark done with a closing note; task MOM PDF; Discuss; Gantt; a non-admin project user.
The MOM dashboard payload of all 12 projects was also compared between the 18 code on an 18 database
and the 20 code on the migrated one: identical.

## 5. Code port notes (18 → 20)

* security: `ir.model.access.csv` → `ir.access.csv`; server action `groups_id` → `group_ids`.
* MOM activity type: `keep_done` removed (20 archives every completed activity); icons are Material
  Symbols names (FontAwesome is not bundled any more).
* views rebuilt for 20's activity dialog layout; MOM button on the project card view; reports
  `t-esc` → `t-out`, `report_file` removed.
* `mom_activity_ids` needs `context={'active_test': False}` on 20, else closed MOM entries vanish from
  the task form and the MOM PDF.
* "Create MOM": 20 creates the activity under `clean_context()` (drops `default_*`), so the MOM values
  travel on `mom_schedule_values`.
* MOM dashboard: OWL 3 (`useProps`, `proxy`, `signal.ref`, core `useChart`, `this.`-scoped templates).
* **Bug fixed (also present on production 18):** the "Create MOM" dialog always offered Visit No# 1
  because the wizard field had `default=1`, which wins over its compute; it now offers today's visit or
  the project's last visit + 1, as its help text says.

## 6. Behaviour to know (same as production, not migration issues)

* The first report printed asks to "Configure your document layout": production's company has no
  document layout yet (18 asks the same).
* Legacy MOM lines whose "Related To" text matches no contact keep it in the entry's note (most of
  them on this data): set Related To by hand where needed — same as the 18 upgrade.
