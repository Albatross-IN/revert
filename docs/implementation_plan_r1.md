# Revert — Release 1 implementation plan (phase by phase)

Status: v1.0 · 2026-11-18 · scope approved by the project owner on 2026-11-18
Scope: [phase1_adoption.md](phase1_adoption.md) v0.4 (what and why). This document is **how and in what order**.
For: Om and the Claude session on his machine, working one phase at a time. Each phase is written to be picked up cold: read §1–§3 once, then only the phase in hand.

---

## 1. How we work

1. **One phase at a time, in order.** A phase is finished only when its exit check passes on a database freshly built with `tools/dev_db.sh`. Do not start the next phase with the previous one half done.
2. **Branch:** all Release 1 work is on `20.0-release1`. Branch `20.0` is what production runs and is not touched. Branch `main` is the old Odoo 18 code.
3. **Commits:** small, each one installable. Subject starts with the phase: `[P2] rvt_project: entity tasks and work lines`. Push at least at every phase end.
4. **At the end of every phase**, in the same commit:
   - tick the tasks in [tasks.md](tasks.md);
   - fill the phase's row in §6 "Phase log" below (date, commit, what differs from the plan, what the next phase must know);
   - add any new trap to [memory.md](memory.md) §6.
5. **Read before coding:** [rules.md](rules.md) (naming, licences, Odoo 20 and OWL 3 conventions, tests), [memory.md](memory.md) (decisions and traps), then the phase.
6. **If the plan is wrong, change the plan first.** Edit this file in the same commit as the code that departs from it, with one line saying why. Scope changes (anything not in phase1_adoption.md) go to the project owner before they are built.
7. **Never on production.** Nothing in this plan is installed on `erp.revert.co.in` before phase P11, except what a phase names explicitly. The project owner runs production releases.
8. **Client data:** the dev database is a copy of production. It stays on the developer's machine, out of git, and no WhatsApp message or e-mail is ever sent from it (the copy is neutralised; keep it so).

## 2. Setting up a machine

```bash
git clone https://github.com/Albatross-IN/revert && cd revert
git checkout 20.0-release1
tools/dev_db.sh          # newest nightly production backup → local db revert20, neutralised
tools/dev.sh             # http://localhost:8094  (log in with a production user)
```

The scripts assume Odoo 20 Enterprise under `/opt/erp` (`odoo/`, `sub/` for enterprise, `erp-venv/`). On another layout set these before calling them:

| Variable | Meaning | Default |
|---|---|---|
| `ODOO_PYTHON` | python of the Odoo 20 venv | `/opt/erp/erp-venv/bin/python` |
| `ODOO_BIN` | `odoo-bin` | `/opt/erp/odoo/odoo-bin` |
| `ODOO_ADDONS` | community addons folder | `/opt/erp/odoo/addons` |
| `ERP_ENTERPRISE` | enterprise addons folder | `/opt/erp/sub` |
| `REVERT_DB` / `REVERT_PORT` | database name / port | `revert20` / `8094` |
| `REVERT_SERVER` | where backups are fetched from | `root@147.93.30.85` |

Tests run on a throwaway copy, never on `revert20` itself:
```bash
createdb -T revert20 revert20_test      # revert20 must have no open connection
REVERT_DB=revert20_test tools/dev.sh -u rvt_base --test-enable --test-tags /rvt_base --stop-after-init
dropdb revert20_test
```

## 3. What is there today (verified 2026-11-18 on the restored copy)

- Odoo 20 Enterprise, 94 modules installed, among them `project`, `project_enterprise`, `crm`, `web_studio`, `ai`; ours: `revert_customizations` 20.0.1.8.0, `admin_notes_viewer`, `rvt_website_lead`. The code on production is identical to branch `20.0`.
- 10 staff users, 19 active projects, 1,219 tasks (370 top-level, 849 sub-tasks), 925 MOM entries (151 open) addressed to about 40 people.
- **How staff use it now:** a project per client site. Top-level tasks are rooms ("Consulting room", "Pantry") or a date ("17/11/2025", "MOM master") created only to hang that day's MOM entries on. Sub-tasks are work items ("Furniture work", "Electrical work", "POP work") and steps ("Off site", "On site", "Installation"). MOM entries are `mail.activity` records of a MOM activity type on tasks, with "Related To" (a contact), photo, visit date and number.
- **Users:** Pratik Anavadiya = owner and principal; Parija = owner; Harshal Sharma = coordinator; Hitesh Mevada, Arpita Amin, Harsha Mahawar, Kishan, Ruchit Shah, Akshay Oda = draftsmen.

## 4. Design rules that hold across phases

| Topic | Rule |
|---|---|
| Entities | An entity is a top-level `project.task` with `rvt_kind = 'entity'`. Hand-made tasks stay `rvt_kind = False` and keep working as before ("both ways"). |
| Work lines | A work line is a child `project.task` of an entity with `rvt_kind = 'work'`, a trade and an agency. Its state is `rvt_work_state`; the project's stages are not used for it. Setting Done also closes the task (`state = '1_done'`) so the old task views agree. |
| Agencies | An agency is a `res.partner` (company) with `rvt_is_agency`; its people are child contacts with a mobile number. |
| Points | MOM lines and office-raised items are one model, `rvt.point`; a visit is `rvt.visit`. |
| Access | A person sees a project only through membership: staff by the project's team fields, an agency by its trade line, a client by the project's client contacts. Owners and the principal see all. Enforce with record rules **and** test each role. |
| Money | Bill amounts and totals are visible to the owner group only, at field level as well as on screens. |
| Picture | Progress, blockers and next actions are computed on reading by `project.project.rvt_picture()`; nothing about them is stored (phase1_adoption §7.1). |
| Screens | Staff screens live in `rvt_desk` only. Other modules bring models, logic and plain back-end views for administrators. |
| Messages | Only `rvt_notify` sends. Other modules call `self.env['rvt.notify'].send(event, record, recipients)`. |
| Text | Every string an agency or client can read is translatable; Gujarati and Hindi are filled in the same phase. |
| Tests | Each module has tests for its rules and its access. A phase's exit check lists the minimum. |

## 5. Phases

Estimates are working weeks for one developer and are estimates, not measurements.

### P0 — Ground (this machine, mostly done)
| | |
|---|---|
| Done 2026-11-18 | Repo checkout at `/opt/erp/custom/revert`; website work committed on `20.0`; branch `20.0-release1`; `tools/dev.sh`, `tools/dev_db.sh`; dev database `revert20`; [masters_draft.md](masters_draft.md) |
| Open | **P0.1** Revert corrects masters_draft.md. **P0.2** Clickable screens (R1.0) for onboarding, Today, project picture, MOM capture, release, bill, agency and client homes: needed before P3. **P0.3** Shared modules copied into the repo from their home repositories: `web_theme_glass`, `web_glass_workspace`, `identity` (needed for P3); `open_whatsapp_connector` 20.0.95.0.0, `web_auth_otp_login` (P6); `fastapi`, `endpoint_route_handler` (P7). They are copied whole and not edited here. |

### P1 — `rvt_base`: roles and master lists · 1 week · tasks R1.1a
**Goal:** the lists onboarding needs exist, and each present user has a role.

**Build**
- Groups: `group_rvt_owner` ⊃ `group_rvt_principal` ⊃ `group_rvt_staff`; flags `group_rvt_designer`, `group_rvt_coordinator` (a user may have both); portal-side `group_rvt_agency`, `group_rvt_client`.
- `rvt.trade`: name (translated), code, sequence, active.
- `rvt.entity.type`: name, site kind (home / office / clinic / other), default trades (many2many), sequence.
- `rvt.site.preset` + `rvt.site.preset.line` (entity type, count).
- `rvt.drawing.type`: code, name (translated), trade (empty = general set), for client, needs client approval, default due offset in days, sequence.
- Partner: `rvt_is_agency`, `rvt_trade_ids`; contact people are child contacts.
- Settings (`res.config.settings` → config parameters): release needs approval (on), client points need confirmation (on), day limits for the picture: not opened 2, question 1, bill review 3, stuck 7.
- Data files from masters_draft.md (`noupdate="1"`): trades, entity types, presets, drawing types, with gu / hi names.
- `tools/assign_roles.py` (run through `tools/dev.sh shell`): gives the nine users their groups from a small mapping at the top of the script. Not a data file, because users differ per database.
- Plain list and form views with a "Revert › Configuration" menu, for administrators.

**Exit check**
- Module installs on a fresh `revert20`; tests pass.
- After `assign_roles.py`: Pratik is owner + principal, Parija owner, Harshal coordinator, six designers.
- An administrator can add a trade, an entity type with default trades, a preset and a drawing type.

### P2 — `rvt_project`: onboarding data, entities, work lines · 1.5 weeks · R1.1b
**Goal:** a project can be set up completely from the back end, and its entity × trade grid is correct.

**Build**
- `project.project`: `rvt_client_id`, `rvt_client_contact_ids`, `rvt_site_address`, `rvt_site_kind`, `rvt_site_label` ("3 BHK + garden"), `rvt_billed_to_default` (client / revert), `rvt_principal_id`, `rvt_designer_ids`, `rvt_coordinator_ids`, `rvt_onboarded` (bool), `rvt_onboarded_on`.
- `rvt.project.trade` (the trade plan): project, trade, agency (partner, empty = undecided), contact people (many2many partners), decide-by date, note; unique (project, trade). Computed `is_undecided_late`.
- `project.task`: `rvt_kind` (entity / work), `rvt_entity_type_id`; for work lines `rvt_trade_id`, `rvt_agency_id` (default from the trade plan, can be overridden), `rvt_work_state` (not_started / waiting / working / done), `rvt_wait_cause` (drawing / client / trade / material / other), `rvt_wait_trade_id`, `rvt_wait_note`, `rvt_wait_since`, `rvt_expected_finish`. (`rvt_wait_drawing_id` and `rvt_wait_point_id` arrive with P4 and P5.) Entity: computed `rvt_entity_state` and counts from its work lines.
- Constraints: one work line per (entity, trade); a work line's parent must be an entity; Waiting requires a cause.
- **Onboarding as a service**, not a screen: `project.project.rvt_onboard(vals)` takes the whole payload (project data, team, entities with types and names, trades with agencies, the entity × trade ticks, drawings in P4) and applies it in one transaction; callable again later to add entities, trades or ticks without duplicating. A helper returns the proposal for a preset: entities and pre-ticked trades. The desk (P3) and the API (P7) both call these two methods.
- Existing projects: onboarding **adds** entity tasks; it does not convert or touch hand-made tasks. An existing top-level task can be marked as an entity from its form (sets `rvt_kind`), for staff who want to keep their room task.
- Grid data method: `project.project.rvt_grid()` → entities, trades, cells (state, wait cause, open point count later).
- Changing the agency on a trade plan line updates work lines that still carry the old default.
- Record rules: staff see projects where they are on the team; owner and principal all. The same for tasks through the project. **Check that existing behaviour for the nine users does not narrow before they are put on teams**: until a project is onboarded (`rvt_onboarded = False`), it stays visible as today.
- Back-end views: project form tab "Revert" (team, trade plan), a wizard-free "Onboard" server action for testing.

**Exit check**
- Tests: preset proposal; onboard a new 3 BHK (entities, lines, plan created; second call adds a room without duplicates); undecided-late; entity state from lines; Waiting needs a cause; agency change propagates; access for owner, principal, designer on team, designer not on team.
- On `revert20`: one existing project onboarded by the server action; its old tasks and MOM entries are unchanged.

### P3 — `rvt_desk`: the single window, onboarding screen, project picture v1 · 2.5 weeks · R1.1c, R1.1d, R1.1e
**Needs:** P0.2 screens, P0.3 theme modules.

**Goal:** staff work in one "Revert" window in the browser: Today, Projects with the picture and the grid, Review, Setup; they can onboard a project there.

**Build**
- Install `web_theme_glass`, `web_glass_workspace`, `identity`; Revert tokens; back office at `/office`. Follow `sfj_admin` in the SFJ repository (client actions per workspace, list-left / detail-right, data methods on the models, other app menus hidden for the staff group through a data file; administrators keep them).
- Client actions: `rvt_desk.today`, `rvt_desk.projects`, `rvt_desk.review`, `rvt_desk.setup`. Drawings, MOM and Bills sections are added by P4, P5, P10.
- **Onboarding screen** (six steps of phase1_adoption §5.2, step 5 arrives with P4): calls the P2 proposal and `rvt_onboard`. Also opens on an existing project as "Project configuration".
- **Grid component**: entities × trades, tap a cell → state, and for Waiting the cause in the same popover.
- **`project.project.rvt_picture()`** v1: progress (agencies decided, work), blockers B1, B5, B6, next actions for Revert and per agency, status word; plus `rvt_picture_summary()` for Review rows and a user-filtered variant for Today. Each blocker rule is one small method returning `{rule, record, holds, actor, since}`; register them in a list so later phases append.
- Project panel: picture first, tabs Work (grid) · earlier tasks (the standard task list of the project, embedded).
- Review: one row per project (status, counts, blocker count). Today: my next actions across projects, plus my hand-made tasks.

**Exit check**
- A coordinator-role user logs in, sees only the Revert menu, onboards a new project from a preset in under five minutes, changes cells, and the picture changes accordingly.
- Review shows all onboarded projects for the owner; a designer not on a project does not see it.
- Tests for `rvt_picture()` (each rule) and a browser tour for onboarding.
- **Staff can start using it after this phase** (rollout wave 1, by the project owner's decision).

### P4 — `rvt_drawing`: register, approval, release · 2 weeks · R1.2a–c
**Goal:** drawings are planned at onboarding, approved by the principal, released to the right people, and the picture knows what is late and who waits.

**Build**
- `rvt.drawing`: project, type, trade, entity (optional), sheet number (code + running number per project), title, designer, due date, for client, needs client approval, state (to_draw / in_progress / awaiting_approval / released / superseded is on the revision), current revision.
- `rvt.drawing.revision`: drawing, number, PDF (attachment), note, state (draft / awaiting_approval / released / superseded), sent for approval by / on, approved by / on, released by / on, client decision (pending / approved / change asked), client decided by / on, change note.
- `rvt.drawing.receipt`: revision, partner, kind (agency / client), sent on, opened on.
- `rvt.drawing.question`: drawing, asked by (partner), via (app / office), text, photo, answer, answered by / on, state.
- Flow methods: `action_send_for_approval`, `action_approve`, `action_release(receivers)`; with the setting off, the designer releases directly. Releasing revision n supersedes n−1. Receivers proposed from the trade plan and the "for client" mark.
- Opened tracking through a tokenised controller `/rvt/d/<token>` that records the first opening and serves the PDF (also the link later sent on WhatsApp).
- Onboarding step 5: proposal of drawings from `rvt.drawing.type` for the ticked trades; `rvt_onboard` creates the `rvt.drawing` rows.
- Work lines: `rvt_wait_drawing_id`.
- Picture: drawing progress; B2, B3, B8, B9; "working without a drawing"; next actions Release / Approve.
- Desk: Drawings section (to draw, awaiting approval, released, not opened), project tab Drawings, release dialog, question thread.
- Notification calls go to `rvt.notify` events (`drawing_released`, `drawing_approval_needed`, `drawing_question`); until P6 a stub model logs them.

**Exit check**
- Tests: numbering, the approval setting both ways, supersede, receivers, opened tracking, change request → new revision, access (a designer cannot approve; an agency partner sees only drawings released to its trade).
- On `revert20`: a designer sends a PDF, the principal approves from Today, the receipt link opens and marks "opened", the picture shows and clears B2 / B3.

### P5 — `rvt_mom`: points, visits, PDFs, move of existing entries · 2 weeks · R1.3a–c
**Goal:** all MOM, old and new, lives in the new model and the desk; the present MOM screens are off.

**Build**
- `rvt.visit`: project, date, number (rank of the date within the project, as today), started by, attendees, state (open / finished).
- `rvt.point`: project, visit (empty = raised from the office), serial number, text, for-kind (agency / client / vendor / staff), partner, user (for staff), trade, entity, drawing, photos, due date, state (open / closed), closed by / on, closing note and photo, client confirmed (bool, default from the setting), sent on (per send), raised by, legacy activity id, legacy task id.
- Reports: visit PDF (all), per-party PDF for one visit (points with photos, "new" mark for points added since the last send), open points of a project. Start from the layout of the present MOM PDF.
- Desk: MOM section (visits and points across projects, the present dashboard's figures: counts, by person, by month, filters), project tab MOM, quick add of a point with sticky "for" and entity, close with note or photo.
- Work lines: `rvt_wait_point_id`; open point count per grid cell; closing the last open point of a cell offers "mark done".
- Picture: points progress, B4, B7; next actions per agency and client.
- **Move of existing entries** (`tools/etl_mom.py`, run through the shell; dry-run by default, `APPLY=1` to write):
  - each MOM activity (active or archived) → one `rvt.point`: summary and note → text, `mom_partner_id` → partner, photo, `mom_visit_date` and number → `rvt.visit`, `mom_sequence` → serial, due date, done state and feedback → closed + closing note, author and dates kept, `legacy_activity_id` set so a second run does nothing;
  - the point's entity stays empty; `legacy_task_id` keeps the task link;
  - for-kind from a mapping sheet (person → trade, agency, number) supplied by Revert (masters_draft §6); unmapped people are kept as vendor-kind contacts and listed in the report;
  - duplicate contacts ("rahul bhai" / "Rahul bhai") are merged only through the mapping sheet, never by guessing;
  - verification report per project: entries, open, closed, photos (by checksum), visits and numbers, before and after. It must match exactly.
- After the check: hide the MOM activity type from the schedule menu, remove the MOM button and dashboard action from the staff menu (keep the module installed and the data untouched until Release 2).

**Exit check**
- ETL dry run and apply on `revert20`: report all equal for 925 entries; second apply creates nothing.
- Tests: numbering, per-party PDF content, close flow, client confirmation setting, access (an agency partner reads only its own points).
- The owner compares three projects' MOM in the old dashboard and the new section and signs off before the old screens are hidden.

### P6 — WhatsApp and `rvt_notify` · 1 week · R1.4a–b
**Needs:** P0.3 connector modules; a dedicated SIM from Revert for production (a test number for development).

**Build**
- Install `open_whatsapp_connector` and `web_auth_otp_login` unchanged; sidecar set up for development as in the Sudi repository's notes.
- `rvt.notify` (replaces the stub): `send(event, record, recipients)`; `rvt.notify.template` per event and language (en / gu / hi) with a text and an optional document; delivery log `rvt.notify.log`; language from the partner's `lang`; respects the connector's caps; a hard switch "sending on" that is **off** in any neutralised database.
- Events: `mom_party_pdf`, `drawing_released`, `drawing_approval_needed` (staff, in-app only), `client_item`, `bill_asked`, `bill_returned`, `bill_paid`, `invite`, `remind` (one item, on a staff tap).
- Push (FCM) transport is added in P7 behind the same `send`.
- Desk: "Send to party" on a visit, "Remind" on next-action lines, a log view for administrators.

**Exit check**
- With a test number paired on a development copy: a visit's per-party PDF arrives on a real phone within a minute; a released drawing arrives with its link; opening the link marks "opened".
- With "sending on" off, nothing leaves and the log says "held".
- Tests with the connector mocked: template choice by language, recipients from the trade plan's contact people, log rows.

### P7 — `rvt_api`: the app's back end · 1.5 weeks · R1.5a
**Needs:** P0.3 `fastapi`, `endpoint_route_handler`.

**Build**
- FastAPI app at `/api/rvt/v1` as in `sfj_api` / `sudi_api`: JWT access and refresh per device, error format, Swagger off in production.
- Sign-in: staff with login and password; agencies and clients with phone number + code on WhatsApp; invitations create the portal user.
- Endpoints, each a thin layer over the model methods already used by the desk: `/me`, `/me/today`, `/projects`, `/projects/{id}/picture`, `/grid`, `/onboarding/proposal`, `/onboarding`, `/work-lines/{id}/state`, `/drawings` (+ send for approval, approve, release, open, questions, client decision), `/visits`, `/points` (create in batches with client-generated ids for offline replay, close, send to party), `/media` (photo and PDF upload), `/masters`, `/devices` (push tokens).
- Client browser link: the same endpoints behind a signed link that opens the web build of the app without sign-in for that project.
- FCM push transport in `rvt.notify`.
- Role tests run through HTTP for owner, principal, designer, coordinator, agency, client: each endpoint's allowed and forbidden cases.

**Exit check**
- The role test suite passes with `--workers=0`.
- An agency token cannot read another agency's point, drawing or line, nor any bill amount of another; a client token gets only marked drawings and its own points.
- Replaying the same batch of points twice creates them once.

### P8 — Flutter app, staff · 3 weeks · R1.5b
Repository `revert_fe` (new). Stack and structure as in [mobile_app_plan.md](mobile_app_plan.md) §3 and §5, cut down to Release 1.

**Build**
- Scaffold: theme tokens, en / gu / hi, sign-in, role home switch, push, media capture and compression, an outbox for offline writes.
- Staff: Today · Projects → picture, grid (cell change with cause), drawings (send for approval, approve, release), onboarding (six steps) · **MOM capture** exactly as phase1_adoption §6.3: sticky "for" and entity, composer always ready, photo, due chips, open points from earlier visits first, per-party send, works without network and shows what is waiting to go.

**Exit check**
- On two Android phones and one iPhone: a MOM of ten points with four photos is captured in flight mode, then syncs and sends per party when the network returns, without duplicates.
- The principal approves a drawing from the phone; a coordinator onboards a project from the phone.

### P9 — Flutter app, agency and client; client link · 1.5 weeks · R1.5c–d
**Build**
- Agency home: your points, new drawings, "Revert asks", My sites, Drawings (full-screen viewer, revision stamp, ask a question), Bills list (P10 fills it). Gujarati and Hindi checked by a native speaker.
- Client home: Waiting for you, Your drawings; approve / ask for a change. The same screens as a web build behind the signed link.
- Invitation flow from the desk and the staff app.

**Exit check**
- A pilot-style agency user signs in with a WhatsApp code in Gujarati and opens a released drawing; "opened" shows in the desk.
- A client approves a drawing from the link without installing anything; the record shows name, date and time.

### P10 — `rvt_bill`: bills and payments, in desk, API and app · 1.5 weeks · R1.6
**Build**
- `rvt.bill`: project, agency, trade, asked by / on, what for, up-to amount (optional), document, bill number and date, amount, billed to (default from the project), state (asked / submitted / returned / accepted / part_paid / paid), return reason.
- `rvt.bill.payment`: bill (required: no advances), date, amount, paid by (client / revert), mode, proof.
- Amount fields restricted to the owner group; staff who ask and review see the document and state; the agency sees its own bills and states.
- Desk: Bills section, project tab Bills, owner money view per project and per agency (billed, to whom, paid, by whom, unpaid, to recover). Picture: B10.
- API: `/bills` (ask, upload, review, pay, list), agency "Revert asks". App: agency upload, staff ask and review, owner money tab.

**Exit check**
- Tests: no payment without a bill, part payments, state changes, billed-to default and override, field access per role through the API.
- An agency uploads a photographed bill from the phone; the office accepts; the owner records two part payments; the agency sees "Part paid" then "Paid" and no totals.

### P11 — Rollout · 1 week · R1.7
- Production: modules released per `docs/deploy_production.md` (restart announced to Albatross); connector sidecar as a service; dedicated number paired; "sending on" switched on; S3 backup added.
- `assign_roles.py` and the MOM move run on production in a maintenance window, from a fresh backup, with the verification report kept.
- Store listings, privacy page, one-page guides in Gujarati and Hindi.
- Waves 0–5 of phase1_adoption §8.

## 6. Phase log

| Phase | Finished | Commit | Differences from the plan · notes for the next phase |
|---|---|---|---|
| P0 | partly, 2026-11-18 | see git log | P0.1–P0.3 open |
| P1 | | | |
| P2 | | | |
| P3 | | | |
| P4 | | | |
| P5 | | | |
| P6 | | | |
| P7 | | | |
| P8 | | | |
| P9 | | | |
| P10 | | | |
| P11 | | | |

## 7. Order and time

P1 → P2 → P3 → P4 → P5 → P6 → P7 → P8 → P9 → P10 → P11, about 18.5 working weeks in a single stream. P1 and P2 need nothing but the corrected master lists and can start now. The screens (P0.2) are needed before P3. If a second person is free, P0.2 can run beside P1–P2, and P8–P9 can start as soon as P7's sign-in and the first endpoints exist.
