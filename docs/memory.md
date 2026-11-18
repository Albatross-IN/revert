# Revert — Project Memory

This is the running context for anyone (human or AI agent) picking up the project. Read it first and keep it current. Append decisions with a date. Do not rewrite history; mark superseded items instead.

## 1. The business (facts supplied by the owner's brief, 2026-10-31)
- **Name:** Revert Architects (referred to as "Revert"), Ahmedabad, Gujarat, India. Architecture and interior design consultancy.
- **Services:** requirement gathering, planning, agency execution coordination, handover. Sectors: corporate offices, residences, hospitals, design studios, manufacturing units (incl. hospital unit architecture).
- **Key people named:** the owner (brief source), the **principal design consultant** (Vastu, site analysis, MOM, approvals), **Pratik** (holds the site measurement template). Team size and roles not yet known (Q H1).
- **Agencies named:** civil, electrician, plumber, POP (false ceiling), colour (painter), carpenter, window (aluminium/UPVC), **Salat work** (read as Gujarati *salaat*, stone mason: marble, granite, kitchen platform; to confirm Q E1).
- **Lifecycle described:** Lead (vision brief; referral = more serious) → qualified → site documentation (room-wise measurement, ceiling and clear height, beam grid, doors, windows, photos, video, site analysis: north, Vastu paragraph by the principal) → client brief → layout → room-wise concept → client OK → working drawings with revisions → agency finalisation (trade clarity before drawings; undecided trade must be highlighted to office, client and owner) → **site marking by the carpenter, approval by the office** → execution with agency coordination → handover.
- **Wanted:** Odoo 20 Enterprise as the engine; everyone aligned through an action-driven mobile app with gamification instead of static dashboards; agencies in Hindi and Gujarati; chatter-style questions with photos; agency money transparency (work given, done, pending, payment requests, expenses); reminders (next visit, arrival confirmation, "did you start?"); scheduling of agency persons across sites; KYC at onboarding with minimal friction; "done" with photo or video; only the committed end date matters; MOM in the app with quick agendas, sticky room, voice-to-text gu/hi/en; pre-scheduled site visits; drawing release and pending-drawing visibility; query dashboards; per-project gamified health; **client journey always positive**; owner-only money view (agency price, paid or not, paid by whom, expenses, company-paid recoverable, probable invoice, compilation).
- **Owner's process ask:** process the brief, find gaps, prepare the questionnaire for the principal consultant, then map to Odoo and derive customisation v1, then refine before execution. Also asked for references or an ERP book on the subject (prd.md §13).

## 1a. What Revert already runs (recorded 2026-11-17; the 2026-10-31 documents missed it)
- **Production Odoo 20 Enterprise** at `https://erp.revert.co.in` (database `erp.revert.co.in`) on the server `147.93.30.85`, shared with Albatross: one Odoo service, one database per host name. Migrated from Odoo 18 on 2026-10-27; 10 users, 12 projects with MOM history. Moved to this domain on 2026-11-16.
- **Code:** GitHub `Albatross-IN/revert`, branch `20.0`: `revert_customizations` 20.0.1.8.0 (MOM as activities on project tasks, Sr. No., Related To, site photo, Visit Date and Visit No#, per-project MOM dashboard, MOM PDF), `admin_notes_viewer`, `tools/etl` (18 → 20), `tools/deploy`, and the runbooks `docs/deploy_production.md` and `docs/migration_18_to_20.md`. Branch `main` is the Odoo 18 code.
- **Website** `https://revert.co.in` (static page); its enquiry form creates a CRM lead through `rvt_website_lead` 20.0.1.0.0. CRM is installed on production for this. Not committed yet (worktree `/opt/odoo18/custom/revert-20`).

## 2. Brand
- No logo, colours or fonts received. design.md uses a placeholder palette ("Studio Paper": paper, ink, terracotta). Replace when assets arrive (design.md §9).

## 3. Decisions log
| Date | Decision | Ref |
|---|---|---|
| 2026-10-31 | Odoo 20 Enterprise is the single system of record; custom modules prefixed `rvt_`; Space is the backbone object under Site under Project | architecture A1–A2 |
| 2026-10-31 | Work packages are `project.task` (space × trade × agency) with `project_enterprise` Gantt and dependencies; Field Service and Planning are not used (absent / wrong fit) | A3, A7, §7 |
| 2026-10-31 | Agencies are partners with an `rvt.agency` profile; work orders are `purchase.order`; bills, payments and TDS live in Accounting; the owner money view is analytic sums plus `paid_by` | A4, system_design §3.7 |
| 2026-10-31 | Drawings get their own register (`rvt.drawing`) mirrored into Documents; queries are a model with SLA | A6 |
| 2026-10-31 | Visits, MOM and reminders are custom models with a cron-based reminder engine; voice-to-text on the phone first | A7, A8 |
| 2026-10-31 | Engagement engine is our own `rvt_game` (as `bhr_game`), rules as records, scores private per agency, verified events only | A9, system_design §8 |
| 2026-10-31 | Notifications through one dispatcher; **official WhatsApp (Odoo `whatsapp`, Meta Cloud API) recommended**, unofficial connector only as fallback; decision pending Q J2 | A10 |
| 2026-10-31 | One Flutter app with four role homes on FastAPI inside Odoo (`rvt_api`), the marut_20 / bhujrnr_be pattern | A11 |
| 2026-10-31 | Languages gu, hi, en everywhere; Noto Sans Gujarati / Devanagari + Inter bundled | A12, design §2.4 |
| 2026-10-31 | Client UI never shows delay words; office writes `client_safe_status`; a lint enforces it | rules §6.1 |
| 2026-10-31 | Dev DB `revert20` on port **8094** (8095–8099 are taken by Slate, Bhuj Runners, SFJ, Alps, Sudi). *Amended 2026-11-17: `revert20` is a neutralised restore of production, not a fresh database* | architecture §8 |
| 2026-10-31 | Backups to S3 from day one on prod (unlike the Bhuj Runners decision). *Still wanted; production today has local daily backups only (14 days)* | A14 |
| 2026-11-17 | **Repo:** the platform is built in the existing repo `Albatross-IN/revert`, branch `20.0`, next to `revert_customizations`. Supersedes the proposed new remote `AlbatrossHub/revert` | A15, rules §1.1 |
| 2026-11-17 | **Database:** the platform extends the existing production database `erp.revert.co.in` on the shared server. Supersedes "fresh database on a dedicated VPS" (A14, deployment_plan Phases A–B) | A14, A15 |
| 2026-11-17 | **MOM:** the new `rvt_mom` replaces the MOM of `revert_customizations`. Existing MOM entries are moved into the new models by an ETL written once the new requirement is final; `revert_customizations` is retired after that | A8, system_design §3.6, task 6.6 |

| 2026-11-17 | **Release 1 scope** (proposal, awaiting review): drawings register and release, office-raised actions, agencies-per-site board kept by staff, bills asked by Revert and uploaded by agencies. Client app = drawings + pending actions only. Agency-started payment requests withdrawn. Existing MOM unchanged in Release 1; its replacement and ETL move to Release 3. Points and scores deferred to Release 5 | phase1_adoption.md |

| 2026-11-18 | **Release 1 re-cut (v0.2):** single-window `rvt_desk` for staff (web and app, same functions); project onboarding as the source of drawings, board and access; **MOM in Release 1** with live mobile capture and per-party PDF on WhatsApp; the new MOM and the ETL of existing entries move from Release 3 into Release 1 | phase1_adoption.md v0.2 |
| 2026-11-18 | **WhatsApp:** `open_whatsapp_connector` 20.0.95.0.0 + `web_auth_otp_login`, vendored from `/opt/erp/custom/sudi_20`. Supersedes "official WhatsApp recommended" (A10) and the share-button idea of v0.1 | A10, phase1_adoption §5.7 |
| 2026-11-18 | **Points:** MOM lines and office-raised "pending from you" items are one record type; client points are confirmed by the office before the client sees them (assumption, open item 5) | phase1_adoption §5.4 |

| 2026-11-18 | **Entities:** onboarding asks the site configuration; one `project.task` per entity (room, zone, "Whole site"); under it one work line per trade with its agency and its own state; entity state computed; shown as an entity × trade grid. Sequence, planned dates and Gantt wait for Release 3 | phase1_adoption v0.3 §5.2, §5.5 |

| 2026-11-18 | **Project picture:** first screen of a project = progress (4 counts), blockers (10 fixed rules, each with owner and age), next actions grouped by Revert staff / agency / client, status word with reasons. Computed on read by one method that also feeds Today and Review; "Waiting" on a work line must name its cause | phase1_adoption v0.4 §5.10, §7.1 |

| 2026-11-18 | **Modelling:** entity = top-level `project.task` with `rvt_kind=entity`; work line = child task with `rvt_kind=work`, trade, agency and its own `rvt_work_state`; hand-made tasks untouched. Onboarding is a model method (`rvt_onboard`) used by desk and API alike | implementation_plan_r1 §4, P2 |
| 2026-11-18 | **Branches:** `20.0` = production (website work committed there, cbe59e5); `20.0-release1` = Release 1 | implementation_plan_r1 §1 |

## 4. Answers from the principal consultant
**2026-11-17, from a conversation with the client, relayed by the project owner** (not yet the written questionnaire answers):
- Client app: too much information to the client causes problems. Show only drawing releases and the next action pending from the client, raised by the Revert office.
- Agencies must not demand payment through the app. Revert asks for an invoice or memo at a sensible point; the agency uploads it in the app; paid or not is tracked.
- A bill may be against the end customer or against Revert; this must be clear on each bill (rule still to be confirmed).
- The team has never used an ERP. Adoption is gradual: staff use it fully first, agencies start adopting, micro-level management later. The first release must make every role feel an advantage.
- Staff must see agencies' work per site, their own drafting and drawing releases, and whom they coordinate.
→ Worked into [phase1_adoption.md](phase1_adoption.md) (Release 1). Its §9 lists 11 follow-up questions.

**2026-11-18, project owner's review of phase1_adoption.md v0.1** (worked into v0.2):
- Staff work entirely in the mobile app or the web portal through one dedicated window, as on SFJ (`sfj_admin`).
- MOM is captured live on the phone on site (lines + photo); tapping an agency or person sends that party's MOM lines as a PDF on WhatsApp at once.
- WhatsApp through `open_whatsapp_connector` as on the Sudi Odoo 20 project.
- Project onboarding is the key screen: selecting agencies fills the standard drawing set, the user ticks what is needed and adds more later; it drives tasks, MOM and what each person sees (access).
- Billed to: default on the project, changeable per bill. Agencies see status per bill only. No advance payments for now.
- Release needs the principal consultant's approval by default (setting). Several coordinators per project. Client access by app and by link. No signature. Client receives only drawings marked for the client. Pilot list to follow as Excel.

**2026-11-18, project owner, go-ahead:**
- phase1_adoption.md v0.4 approved to build.
- Hand-made tasks and configured entity tasks both stay; an existing project gets its entity tasks through project configuration.
- Roles: Pratik Anavadiya owner and principal consultant; Parija owner; Harshal Sharma coordinator; the other six users draftsmen.
- Master lists drafted by us ([masters_draft.md](masters_draft.md)) and sent to Revert for correction.
- Repo: this folder is a checkout; new work on its own branch. Om works on this scope from his machine, phase by phase ([implementation_plan_r1.md](implementation_plan_r1.md)).

Written questionnaire answers: none yet (expected back as an md file). Copy answers here from questionnaire.md with the date; flip the matching architecture decisions to Agreed.

## 5. Environment
- Dev Odoo 20: `/opt/erp/odoo` (community) + `/opt/erp/sub` (enterprise), venv `/opt/erp/erp-venv`, Python 3.14.
- Repo: `Albatross-IN/revert`. `/opt/erp/custom/revert` is a checkout since 2026-11-18, on branch `20.0-release1` (Release 1 work); `20.0` is production. The older worktree `/opt/odoo18/custom/revert-20` still exists with the same website files untracked; it is no longer the working copy.
- Dev DB `revert20` on port **8094**: a neutralised restore of production, built 2026-11-18 from the nightly backup of 2026-11-17 20:32 UTC with `tools/dev_db.sh`; run with `tools/dev.sh`. The backup files are in `/opt/erp/backups/revert-prod` (not in git). Production runs Python 3.12 and PostgreSQL 18; this box runs Python 3.14.
- Run command (once modules exist):
  ```
  /opt/erp/erp-venv/bin/python /opt/erp/odoo/odoo-bin \
    --addons-path=/opt/erp/odoo/addons,/opt/erp/sub,/opt/erp/custom/revert \
    -d revert20 --http-port=8094 --db-filter='^revert20$' --load=base,rpc,web,queue_job
  ```
- Modules verified present in this build (2026-10-31): `project`, `project_enterprise`, `web_gantt`, `web_map`, `worksheet`, `planning`, `documents`, `documents_project`, `sign`, `whatsapp`, `gamification`, `purchase`, `project_purchase`, `sale_project`, `hr_expense`, `l10n_in`, `l10n_account_withholding_tax`, `knowledge`, `approvals`, `voip`. **Absent:** `industry_fsm`. Translations `gu.po` and `hi.po` exist in core modules.
- Vendor sources: `fastapi` + `endpoint_route_handler` from `/opt/erp/custom/marut_20`; `identity*`, `web_theme_glass`, `web_glass_workspace`, `open_whatsapp_connector` from `/opt/projects/aic_apps-20.0`; `queue_job` from marut_20 (with the Py3.14 stack-leak fix 1896eda).

### Om's laptop (2026-11-19)
- Odoo 20 at `/opt/odoo20/odoo20`, enterprise `/opt/odoo20/ent`, venv `/opt/odoo20/odoo20-venv` (Python 3.12), repo at `/opt/odoo20/custom/revert_20`, app repo at `/opt/odoo20/custom/revert_fe`. `source /opt/odoo20/tools/revert_env.sh` sets the variables of implementation_plan_r1 §2 and gives `rv` = `tools/dev.sh` with the data folder `/opt/odoo20/revert-dev-data`.
- `revert20` on this laptop is a neutralised clone of the local production copy of **23 Oct 2026** (`revert20_oct_dev`: 18 projects, 1,202 tasks, 741 MOM entries), not the 17 Nov backup of §3, because the nightly backup cannot be fetched from this machine. Counts in exit checks are therefore those of this copy. Its admin password is reset to a local one for browser tests.
- Tests: `createdb -T revert20 revert20_test`, copy the filestore folder too, then `REVERT_DB=revert20_test REVERT_PORT=8194 rv -u <module> --test-enable --test-tags /<module> --stop-after-init`.

## 6. Build status (2026-10-31)
- Documents only: prd, questionnaire, architecture, system_design, api_design, mobile_app_plan, design, rules, memory, tasks, deployment_plan, deployment (dev as-built). No module, no database, no app.
- Waiting on the owner / principal consultant: questionnaire answers (★ A1, A2, A3, C1, D2, E1, E2, F1, J2, K4 gate the build), attachments (measurement template, quotation formats, sample MOM and drawing set, agency list, brand).

### Gotchas carried over from sibling Odoo 20 projects
- `request.env.website` (no `request.website`); XML file fields `type="bytes"`; `blog.post.published_date`.
- Transient models need `ir.access.csv` rows in Odoo 20.
- OWL 3: `proxy()` not `reactive`; `this.` in templates; no static props.
- SCSS: no variable interpolation inside `url()`; libsass `@extend` across files breaks.
- `queue_job` runner needs `--load=base,rpc,web,queue_job`; on Python 3.14 use the patched copy (stack leak).
- Run the dev server through a `tools/dev.sh` that finds the real PID (setsid forks).
- Binary fields exposed through FastAPI need `BinaryBytes` handling (Sudi lesson).

### How Revert uses the present system (seen in the local June 2026 copy of their Odoo 18 data)
- A project per client site (34 then). Tasks are rooms or zones ("Chairman Cabin", "Board / conference Room") with work items under them ("Furniture work", "Electrical Work", "Paint Work"), and drafting to-dos ("electrical of all toilets"). Stages New / In Progress / Completed / Revision.
- MOM entries are pending points addressed to a person by name: an agency's man, "Ar. Pratik", "Client scope", "Vendor", with a photo and a date. This is the habit Release 1 builds on.

### Update 2026-11-17
- Still documents only for the platform. No questionnaire answers yet; the customer is returning feedback as an md file.
- Decided by the project owner: existing repo, existing database, existing MOM entries moved by ETL (decisions log).
- Documents amended for these three decisions: architecture (A8, A14, A15, §8), rules §1.1, tasks (T0.6, T0.7, 6.6, 9.1), deployment_plan (notice), deployment (§3), system_design §3.6. The rest of each document is still v0.1.

### Update 2026-11-18
- Release 1 approved; build plan in implementation_plan_r1.md (P0–P11). No `rvt_*` platform module exists yet; P1 is next.
- Production code was compared with branch `20.0` file by file: identical. The server's `REVISION` file names commit `f3c3d9f`, which is not in the repository (an old hash); correct it at the next release.
- Live figures (copy of 2026-11-17): 10 staff users, 19 active projects, 1,219 tasks, 925 MOM entries of which 151 open, about 40 "Related To" people with some duplicate spellings.
- Staff create top-level tasks named by date ("17/11/2025", "MOM master") only to hang MOM entries on; the new visit model removes that need.

### Update 2026-11-19
- Preview v4 approved by the project owner; development started. Phase log in implementation_plan_r1.md §6; additions of the day in its §8.
- P1 `rvt_base`, P2 `rvt_project`, P3 `rvt_desk`, P4 `rvt_drawing`, P5 `rvt_mom`, P6 `rvt_notify` and P7 `rvt_api` done (the earlier MOM is moved on the dev copy; its screens are still on). Local test logins on the dev copy (never on production): `meera` (coordinator), plus local passwords on two existing users for browser checks.

### Traps found while building Release 1
- Odoo 20: an `ir.actions.act_window` has no `target="inline"` any more (current / new / fullscreen / main).
- A `.po` file must not repeat a `msgid`: when two records share a source word ("AC" as name and as short name), list both `#:` references on one entry.
- Boolean settings that default to on: `set_bool(key, False)` stores "False", so `get_bool(key, True)` reads the choice back correctly; read them through `rvt.config` only.

- Odoo 20: `res.partner.is_company` is computed (own commercial entity **and** a VAT number), so an agency without GST is not a "company"; its people are still its child contacts and `commercial_partner_id` still points at the firm.
- Odoo 20: outside (portal) users read only whitelisted fields of `project.task`; extend the `TASK_PORTAL_READABLE_FIELDS` property for every `rvt_` field an agency must read.
- A search under an access rule that reads a **stored computed** field does not recompute that field when it is still pending in the same transaction (seen with `project.rvt_agency_ids`). After changing what it depends on, call `flush_recordset([field])` (see `_rvt_flush_agency_access`).
- Access rules are evaluated once per user and cached: in tests, give a user its partner at creation, do not swap it afterwards.
- Never type a `pkill -f <pattern>` whose pattern also appears in the command line that runs it: it kills its own shell.
- Tasks created in code take the current user as assignee unless `user_ids` is passed as False.

- Odoo 20: `/web/session/logout` accepts POST only, with the security token. A page of our own logs out by posting a form.
- `HttpCase.browser_js(ready=...)`: the expression must give `true`, not an element (`!!document.querySelector(...)`).
- A private to-do ("Welcome <name>!") is created for every new internal user; it has no project and even the administrator cannot read it. Pick test tasks with `project_id` set.
- With `identity` installed the standard back office is at `/app` by default; `/office` needs `identity_web_prefix = office` in the server config file. Build links from `rvt.desk._web_prefix()`, never from a literal `/odoo`.
- The preview's screen code hard-codes a few invented ids (`s1` as principal, `s4` as designer). `_num('s1')` is 1, the system user: the adapter must replace such defaults (see `obStart` in live.js) and the server must refuse non-staff on a team (`_rvt_onboard_project_vals`).
- Dates: use `env['rvt.config'].today()`, not `fields.Date.context_today`: people outside the office have no time zone set, and UTC is yesterday until 05:30 in India.

- Odoo test framework: `assertRaises` rolls the transaction back to a savepoint, so everything done inside the `with` block (also the steps that succeeded before the error) is undone.
- Stored moments are UTC. `released_on.date()` is yesterday's date until 05:30 in India: compare local dates (`rvt.config.to_date`).
- `odoo.http.content_disposition` is gone: `from odoo.http.stream import content_disposition` (it takes "inline").
- An access rule for outside users must not hang on a state that changes while they still need the record (a released drawing goes back to "in progress" when revision 2 is started): key it on what they received (`released_revision_id`, `receiver_ids`).
- Reading a Binary attachment field loads the file. Use the file name (or `bin_size=True`) to know whether a file is there.
- Browser file pickers need a real click: in headless checks use `Input.dispatchMouseEvent` with `Page.setInterceptFileChooserDialog`, not a dispatched event.

- Tests run on a copy of real data: never assert on totals of the whole database or on names that the client also uses ("Rahul bhai", "Jitu Bhai" exist for real). Use invented, unmistakable names and compare only your own records.
- In a test run a QWeb PDF is rendered as HTML (no PDF engine): assert on the text, check the real PDF by hand.
- Report templates: the loop variable must not be called `doc` or `o` when it is not a record (`web.basic_layout` reads `doc._name`).
- A new MOM activity must name a person ("Related To" is required), but 346 earlier entries have none; to make such a row in a test, null the column with SQL after creating it.
- `html2plaintext` turns bold into asterisks; strip tags yourself when the plain words are wanted.
- Parsing a party key: `'all'.startswith('a')` is true. Test the literal first.

- A contact created under a firm starts in the database's default language. For messages take Gujarati or Hindi from the person, else from the firm (`rvt.notify._lang`).
- A keyword argument named like a method's own parameter (`partner=` passed through `**values` into `render(event, record, partner, ...)`) raises "multiple values": keep pass-through values in one dict.
- The WhatsApp connector's own copy in sudi_20 carries Sudi's template data; the clean copy of the same version is in synapse_be.

- Never name a model method `_register` (the framework keeps a class attribute of that name: "'bool' object is not callable"); prefix helpers with `_rvt_`.
- Tests that count rows (message log, sign-in codes, agencies by name) must ignore what the copy already holds: take a floor id in `setUp`, or select by id.
- The dev server does not compress answers; nginx does on the server. The staff snapshot is about 120 KB plain on this copy.
- **API: make the caller the transaction's user.** A FastAPI request starts as the public user. After the token is checked, `deps.caller` sets `env.transaction.default_env` to the caller's environment (what `request.update_env` does after a web sign-in). Without it, an x2many command towards `res.partner` or `res.users` (models with `_allow_sudo_commands = False`) is checked against the public user and refused ("Failed to write field ... Public user").
- **Never ask a person's groups under their own rights.** `user.has_group()` on a non-sudo record of a portal-type user reads `all_group_ids` as that user, gets nothing, and the framework's groups cache keeps "no groups" for that user until the next restart, for every later check. `env.user` is safe (it is a sudo record); a browsed user is not: `user.sudo().has_group(...)`. Test: `test_a_token_after_a_restart_keeps_the_role`.
- `env.transaction.invalidate_ormcache()` is how a test drops the ormcache in this version (`registry.clear_cache()` is gone).
- **The app must send a stated `Content-Length`.** Dart's `HttpClient` sends a chunked body when the length is not set; the server behind a plain WSGI gateway reads it as empty ("The request is not complete").
- **A web view keeps the app's own files.** The screens are served with `no-store` and each build has its own address for `app.js` and `styles.css` (`?v=`), or an updated app shows old screens for minutes.
- Android's web view follows the phone's font-size setting (text zoom): fixed at 100 in the shell; the app's own "Large" text size scales the whole layout instead.
- The system's fingerprint prompt cannot be screenshotted (`adb screencap` comes back empty): check for its window with `dumpsys window` instead.
- Hand tests on the dev copy used the fixtures' sample people and numbers. The API tests now take those numbers over inside the test (`ApiCase._own_the_numbers`), so they pass on any copy.
- The web view of a debug build can be driven over USB: `adb forward tcp:9555 localabstract:webview_devtools_remote_<pid>` and the Chrome DevTools protocol.

## 7. Glossary
| Term | Meaning |
|---|---|
| BHK | Bedroom-hall-kitchen count of a flat ("3 BHK") |
| Clear height | Floor to beam bottom (vs slab height: floor to slab) |
| Beam grid | Positions and depths of beams and columns in a room; the brief wrote "BIM GRID" |
| POP | Plaster of Paris; the false-ceiling trade (gypsum boards too) |
| Colour kaam | Painting |
| Salaat (સલાટ) | Stone mason: marble, granite, kitchen platform, cladding ("Salat work" in the brief) |
| Karigar / mistri | Skilled worker / craftsman-foreman of an agency |
| GFC | Good-for-construction (working) drawing |
| RA bill | Running-account bill: a part bill on measured work during execution |
| Retention | A percentage withheld from agency bills until the defect period ends |
| Site marking | Chalk/laser marking of the layout on floor and walls before execution |
| MOM | Minutes of meeting from a site visit |
| Vastu | Traditional Indian orientation principles the principal consultant comments on per site |
| Griha pravesh / muhurat | Housewarming / auspicious date, often the real deadline |
| TDS 194C | Indian withholding tax on payments to contractors |
| Trade plan | Which trades a project needs and which agency is finalised for each |
| Work package | One space × one trade × one agency unit of execution (`project.task`) |
| Committed end | The end date agreed with the agency; the only date the brief says matters |
| Client-safe | Text or media the client is allowed to see |

## 8. Open threads
See questionnaire.md (all) and prd.md §12. Update this section when answers arrive.
