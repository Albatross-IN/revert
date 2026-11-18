# Revert — Tasks

Tick boxes in the same commit as the work. IDs are stable; never renumber.
Legend: 🧑 owner / principal input needed · ⛔ blocked · ⏳ in progress

## Phase 0 — Discovery & setup
- [x] T0.1 Brief processed into a lifecycle, gaps listed (prd.md §3, §12) — 2026-10-31
- [x] T0.2 Docs: prd, questionnaire, architecture, system_design, api_design, mobile_app_plan, design, rules, memory, tasks, deployment_plan, deployment — 2026-10-31
- [ ] T0.3 🧑 Questionnaire session with the principal consultant; answers into memory.md §4; ★ items closed
- [ ] T0.4 🧑 Attachments: measurement template (Pratik), quotation formats, sample MOM, one drawing set, fee proposal, agency list, brand assets
- [ ] T0.5 Refine docs v0.2 from answers (the "refine before execution" round the owner asked for)
- [ ] T0.6 (checkout, branch `20.0-release1`, website work committed, `CLAUDE.md`, `tools/dev.sh`, `tools/dev_db.sh` done 2026-11-18; pre-commit still open) Repo: work in `Albatross-IN/revert` branch `20.0` (decided 2026-11-17). Bring these documents into that branch, make `/opt/erp/custom/revert` a checkout of it, commit the pending website work (`rvt_website_lead`, `website/`, nginx configs), add `CLAUDE.md` → docs/rules.md + memory.md, pre-commit (ruff, pylint-odoo, prettier for XML)
- [x] T0.7 Dev DB `revert20` on :8094 = **neutralised restore of production** (decided 2026-11-17), then add `l10n_in`, `crm`, `sale_project`, `project_enterprise`, `purchase`, `documents_project`, `sign`, `whatsapp`, `gamification`, `hr_expense`, `l10n_account_withholding_tax`; languages en_IN, hi_IN, gu_IN; `tools/dev.sh`, `tools/setup_company.py` — 2026-11-18: restored from the nightly backup, neutralised; the listed extra modules are installed by the phases that need them
- [ ] T0.8 (identity, web_theme_glass, web_glass_workspace copied 2026-11-19 from aic_apps 20.0-glass @ 53b6989; the WhatsApp and API modules follow with P6 / P7) Vendor `fastapi`, `endpoint_route_handler`, `queue_job` (marut_20), `identity*`, `web_theme_glass`, `web_glass_workspace` (aic_apps 20.0); record commits in README
- [ ] T0.9 Demo seed `tools/seed_demo.py` (fake client, site with 8 spaces, 4 agencies, drawings, packages; no real data)
- [ ] T0.10 Inventory of the live system for the refinement round: what `revert_customizations` MOM holds (fields, counts per project, photos), the two Studio items, users and groups; map each to the new design

## Release 1 — adoption launch (approved 2026-11-18; scope [phase1_adoption.md](phase1_adoption.md), build order [implementation_plan_r1.md](implementation_plan_r1.md), whose phases P1–P11 name these task ids)
Release 1 replaces Phases D and 1–9 below as the first thing built. Those phases stay as the long-term backlog and are re-cut into Releases 2–5 after Release 1 is reviewed. The v0.1 list of 2026-11-17 (R1.1a–R1.4) was re-cut on 2026-11-18 before any work started; the ids below are the stable ones.
- [x] R1.A Review of phase1_adoption.md v0.1 by the project owner; answers to its 11 questions — 2026-11-18
- [x] R1.B v0.4 approved by the project owner — 2026-11-18
- [ ] R1.C 🧑 Revert corrects [masters_draft.md](masters_draft.md); pilot sheet and the person → trade / agency / number sheet; WhatsApp SIM
- [ ] R1.0 (prototype built 2026-11-18 in `prototype/index.html`; sign-off by Revert open) Design: clickable screens for onboarding, Today, project panel, MOM capture, release, bill, agency and client homes; en/gu/hi wording; sign-off
- [x] R1.1a (2026-11-19) `rvt_base`: roles (owner, principal, designer, coordinator, agency, client), trades, settings ("release needs approval", "client points need confirmation")
- [x] R1.1b (2026-11-19; the drawings step lands with P4) `rvt_project`: onboarding (project, team with several coordinators, site configuration from presets, trades and agencies, entity × trade grid, drawings from standard sets), one `project.task` per entity with one work line per trade (state on the line, entity state computed), grid view, access from project membership; standard drawing sets per trade and project type
- [x] R1.1c (2026-11-19; served at `/rvt/desk`, see the phase log) `rvt_desk`: single window (Today, Projects panel, Setup), Glass + Identity at `/office`, other menus hidden for staff (sfj_admin pattern)
- [ ] R1.1d Exit: two pilot projects and the running projects onboarded by staff in the browser
- [x] R1.1e (2026-11-19) Project picture v1 (phase1_adoption §5.10, §7.1): computed method on the project (progress, blockers B1/B5/B6, next actions, status), project Overview, Review rows, Today from the same items; "Waiting" cause on work lines; settings for day limits
- [ ] R1.2a `rvt_drawing`: register, revisions, approval by the principal (setting), release with receivers, opened tracking, questions, client approval / change request
- [ ] R1.2b Desk: Drawings and Review sections; picture rules B2, B3, B8, B9 and drawing progress
- [ ] R1.2c Exit: staff of the pilot projects release every drawing through the system for two weeks
- [ ] R1.3a `rvt_mom`: points and visits (one record type for MOM points and office-raised items), numbering, close with note/photo, PDFs (visit, per party, open points)
- [ ] R1.3b Desk: MOM section and project MOM tab with the present dashboard's figures; picture rule B7 and points progress; "Remind on WhatsApp" per item with R1.4
- [ ] R1.3c ETL of existing MOM entries (`revert_customizations` activities) into points, with a verification report (counts, photos, visit numbers per project); dry run on `revert20`; present MOM screens off; supersedes task 6.6
- [ ] R1.4a Vendor `open_whatsapp_connector` 20.0.95.0.0 and `web_auth_otp_login` from sudi_20; sidecar service on production; dedicated number paired (🧑)
- [ ] R1.4b `rvt_notify`: message texts en/gu/hi, MOM PDF and drawing sends, caps, delivery log, push (FCM)
- [ ] R1.5a `rvt_api`: staff login, phone + WhatsApp code, every desk function incl. `GET /projects/{id}/picture`, secure links
- [ ] R1.5b Flutter app, staff: Today, Projects, onboarding, drawings, MOM capture with offline queue and per-party send, bills
- [ ] R1.5c Flutter app, agency and client homes; client browser link; gu/hi/en
- [ ] R1.5d Exit: a MOM is captured on site and an agency receives its PDF on WhatsApp within a minute; a pilot client closes an item
- [ ] R1.6 `rvt_bill`: ask, upload, review, payments against bills (no advances), billed-to default from project, agency status list, owner money view
- [ ] R1.7 Rollout: store listing, privacy page, onboarding material gu/hi, production release, waves 0–5

## Phase D — Design
- [ ] D.1 Screen canvas: agency Today + Work detail, agency owner Money, client Project + Approval, office MOM + Verification, owner Money (360 px, en/hi/gu)
- [ ] D.2 🧑 Direction chosen (A "Studio Paper" recommended) and tokens frozen; brand assets applied
- [ ] D.3 Copy deck: client-safe status patterns, agency nudges, gamification names in en/hi/gu; native-speaker review
- [ ] D.4 Design sign-off (P0 exit)

## Phase 1 — Foundations (`rvt_base`, `rvt_api`, `rvt_notify`, app scaffold)
- [ ] 1.1 `rvt_base`: groups and roles, `rvt.trade` with sequence/marking/billing unit, settings, mixins (space link, media proof, client-safe text), language loading
- [ ] 1.2 `rvt_api`: endpoint record `/api/rvt/v1`, JWT (access/refresh per device), errors, role dependencies, `/health`, `/auth/staff-login`, `/me`, Swagger off in prod
- [ ] 1.3 `rvt_notify`: dispatcher service, `rvt.device`, `rvt.template` per language, push (FCM HTTP v1), WhatsApp via Odoo `whatsapp`, SMS fallback, email, in-app inbox, delivery log, dev dummy dispatcher
- [ ] 1.4 🧑 Firebase project; 🧑 WhatsApp Business number + Meta verification; first templates submitted (invite, OTP, visit reminder) in en/hi/gu
- [ ] 1.5 Flutter scaffold `revert_fe`: stack (D3), theme tokens, l10n ARB en/hi/gu, offline core (drift + outbox), media core (compress + upload queue), speech spike gu/hi on two phones, push, staff login, Today placeholder
- [ ] 1.6 Tests: JWT, roles, record-rule scaffolding; CI (Android APK + iOS cloud build)

## Phase 2 — Site & leads (`rvt_site`, `rvt_crm`)
- [ ] 2.1 `rvt_site`: site, space types + spec templates (from Pratik's sheet), spaces, openings, existing points, checklist, summary, Vastu, map
- [ ] 2.2 `rvt_crm`: vision brief fields, referral + seriousness + SLA, qualification stages, site creation from lead, fee quotation templates (per sq ft / % / lump sum) with milestone schedule, won → project + site + client invite
- [ ] 2.3 API: `/leads`, `/sites`, `/spaces`, `/space-types`, `/media`
- [ ] 2.4 App (office): leads, site documentation flow (spaces, spec forms, openings, photos, video, checklist ring, north, Vastu)
- [ ] 2.5 Back office: site form with spaces kanban, checklist, project form Spaces tab
- [ ] 2.6 Exit: a real site documented on the phone end to end; project created from a won lead

## Phase 3 — Agencies (`rvt_agency`)
- [ ] 3.1 Agency profile, persons, invites with codes (WhatsApp/SMS), OTP login, PIN, language at first login
- [ ] 3.2 KYC: documents, masking, consent version, verify/reject, `allow_work_before_kyc`
- [ ] 3.3 Trade plan per project with defaults from space types + engagement model; undecided-past-due alerts (office, owner, client-safe text)
- [ ] 3.4 Quote requests, quotes with lines per space/unit, comparison view, accept → `purchase.order` work order (`paid_by`, advance, retention, committed end)
- [ ] 3.5 API: `/auth/invite/*`, `/auth/otp/*`, `/agencies/*`, `/trade-plan`, `/quote-requests`, `/quotes`, `/work-orders`
- [ ] 3.6 App: agency owner home (people, KYC, quotes), person onboarding; office agency screens
- [ ] 3.7 Record-rule tests: agency isolation (rules §8.3)
- [ ] 3.8 Exit: a real agency owner onboards, invites two people, quotes; office accepts into a work order

## Phase 4 — Design & approvals (`rvt_design`)
- [ ] 4.1 Brief (project, space) + client confirm; layout options + choose
- [ ] 4.2 Drawing types (draft set, 🧑 confirm), drawing register, revisions, internal check, release (to client/agency, notifications in language), Documents mirror
- [ ] 4.3 Client approvals (drawing, room concept), change requests → new revision; optional `sign` on agreement
- [ ] 4.4 Queries with SLA (office hours), boards: drawings due, queries open
- [ ] 4.5 API: `/design/*`, `/drawings/*`, `/queries/*`, `/projects/{id}/approvals/pending`
- [ ] 4.6 App: client home (project, rooms, approvals, updates), designer phone flows (release, answer query)
- [ ] 4.7 Client-tone lint (rules §6.1) in templates and `client_safe_*` validation
- [ ] 4.8 Exit: client approves brief, layout, a room concept and a drawing in the app; an agency query is answered within SLA with alerts

## Phase 5 — Execution & visits (`rvt_execution`, `rvt_visit`)
- [ ] 5.1 Work packages on `project.task`: fields, stages, scope lines, generation from work orders, trade sequence template → dependencies and planned dates
- [ ] 5.2 Marking gate (tasks, photos, approve/reject), `is_ready` with reasons
- [ ] 5.3 Progress updates with media, done with media, verification pass/rework, verified quantities → billable
- [ ] 5.4 Committed end with reason history; Gantt views (plan / committed / actual; group by space or agency)
- [ ] 5.5 Visits: model, conflicts, calendar + map, arrival with optional GPS, start/end, missed
- [ ] 5.6 Reminder engine: T-1 evening, morning, arrival alert, start nudge, EOD nudge, pending digest; quiet hours
- [ ] 5.7 Blockers and material-needed; snags
- [ ] 5.8 API: `/tasks/*`, `/visits/*`, `/execution/boards/*`
- [ ] 5.9 App: agency person Today + Work + Done flow (offline queue), agency owner Work and Today, office verifications and schedule, client room progress and photo strip
- [ ] 5.10 Exit: pilot project runs two trades through marking → execution → verification with reminders; Gantt shows plan vs committed vs actual

## Phase 6 — MOM & voice (`rvt_mom`)
- [ ] 6.1 MOM, items with sticky space, audio + transcript, classify, convert (task / query / drawing change / decision / client action), audience
- [ ] 6.2 Share per audience: PDFs (client, each agency, internal) + notifications
- [ ] 6.3 App: MOM capture (mic, language chips, change location), later classification screen
- [ ] 6.4 Optional server transcription fallback via the Gemini stack behind a setting
- [ ] 6.6 (moved to Release 1 as R1.3c on 2026-11-18) ETL of existing MOM entries (`revert_customizations` activities: Sr. No., Related To, photo, Visit Date, remark, closing note) into `rvt.mom` / `rvt.mom.item`; verify counts and photos per project; dry run on `revert20`; then retire `revert_customizations`
- [ ] 6.5 Exit: principal runs a site MOM by voice; items become tasks and queries; client and agencies receive their parts

## Phase 7 — Money (`rvt_finance`)
- [ ] 7.1 Payment requests (advance / RA / final / retention release) from verified quantities; approve/return; → vendor bill with TDS; paid by company / client with proof
- [ ] 7.2 Expenses with payer, category, receipt, recoverable → client re-invoice line; reimbursement
- [ ] 7.3 Client milestone invoices from the fee schedule; receipts; pay link
- [ ] 7.4 Owner money view per project + overview (analytic sums, `paid_by` split, probable invoice, margin for turnkey)
- [ ] 7.5 API: `/payment-requests/*`, `/expenses/*`, `/invoices/*`, `/projects/{id}/money`, `/money/*`
- [ ] 7.6 App: agency Money + Request payment, office approvals, client Payments, owner Money
- [ ] 7.7 🧑 CA review of GST/TDS configuration; reconciliation test against accounts
- [ ] 7.8 Exit: an RA bill flows from request to paid; the owner's project view matches accounts

## Phase 8 — Engagement & office home (`rvt_game`, `rvt_office`)
- [ ] 8.1 XP rules, ledger, levels, badges, awards from verified server events; caps
- [ ] 8.2 Reliability score (nightly), components, hints; project health with reasons; health log
- [ ] 8.3 Recognition (monthly), feature partner of the month; weekly digests
- [ ] 8.4 `rvt_office`: back-office home boards, project health list, Glass tokens for Revert
- [ ] 8.5 API: `/game/*`, `/office/*`, `/me/game`, role `GET /me/home` payloads complete
- [ ] 8.6 App: Me/level screens, agency score with hints, owner Health and Recognition
- [ ] 8.7 Exit: scores from real pilot data; owner edits a rule; health reasons match reality

## Phase 9 — Rollout
- [ ] 9.1 Production = the existing database `erp.revert.co.in` on the shared server (decided 2026-11-17): release `rvt_*` per the repo's `docs/deploy_production.md`, restarts announced to Albatross; add S3 backups + restore drill; staging with neutralisation
- [ ] 9.2 🧑 Enterprise subscription registered before trial day 30
- [ ] 9.3 Store listings (Play, App Store), privacy policy (en/hi/gu), data-safety forms, screenshots; review fixes
- [ ] 9.4 Onboard all panel agencies (office-assisted first week); add running projects (🧑 K4)
- [ ] 9.5 Admin training (2 h) + short office guide in Knowledge; agency one-page guide in gu/hi
- [ ] 9.6 Post-pilot tuning: notification counts, SLA defaults, XP caps, client copy

## Later (not scheduled)
- [ ] L.1 Materials procurement for turnkey (`purchase` + `stock` to site)
- [ ] L.2 BOQ / quantity take-off per space from spec templates
- [ ] L.3 In-app client payments (gateway decision)
- [ ] L.4 Worksheet templates for trade verification checklists
- [ ] L.5 AI assistance (query drafting, MOM classification, photo progress hints) via the Gemini stack
- [ ] L.6 Referrer portal
