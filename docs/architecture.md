# Revert — Architecture

Status: draft v0.1 · 2026-10-31 · owner: solution architecture
Companions: [prd.md](prd.md) · [system_design.md](system_design.md) (models, flows, rules in detail) · [api_design.md](api_design.md) · [mobile_app_plan.md](mobile_app_plan.md) · [design.md](design.md) · [rules.md](rules.md) · [memory.md](memory.md) · [tasks.md](tasks.md)

---

## 1. Decision summary

| # | Decision | Choice | Why |
|---|---|---|---|
| A1 | Platform | **Odoo 20 Enterprise** as the single system of record; custom modules prefixed `rvt_` | CRM, Project (with Gantt and dependencies), Purchase, Accounting with Indian localisation, Documents, Sign, WhatsApp, Planning and Gamification are already there. Custom work is the domain layer (spaces, drawings, agencies, work packages, visits, MOM, money view, engagement) |
| A2 | Backbone object | **Space** (room / entity) under a **Site**, owned by a **Project** | The brief says every stage happens per room: measurement, concept, drawings, agency work, MOM points, payments. Making the space a first-class record lets every other object point at it |
| A3 | Project and execution | `project.project` per client project; `project.task` = **work package** (space × trade × agency) with `project_enterprise` Gantt, `planned_date_begin`, `date_deadline`, `depend_on_ids`; `project.milestone` for stage gates | Reuses Odoo's task machinery (stages, assignees, chatter, recurrence, Gantt, dependencies, portal sharing) instead of a parallel model. Field Service (`industry_fsm`) is **not** used: it is absent from this build and is designed for one technician per intervention, not for multi-agency trade sequences |
| A4 | Agencies | `res.partner` (company) + persons; `rvt.agency` profile with trades, KYC, status; portal users; **work orders = `purchase.order`**, bills = vendor bills, payments = `account.payment`, TDS via `l10n_account_withholding_tax` | Money stays in Accounting where the CA expects it. Odoo 20 ships Indian GST (`l10n_in`) and withholding tax |
| A5 | Client fees | `sale.order` with milestone-based invoicing (`sale_project`), invoices and payments in Accounting | Stage-wise fee schedule maps to milestones |
| A6 | Drawings | Custom `rvt.drawing` register with revisions and releases; files as attachments, mirrored into a Documents workspace per project (`documents_project`) | Documents gives folders, sharing and previews; the register gives trade, space, revision, release, approval and query semantics Documents does not have |
| A7 | Visits and reminders | Custom `rvt.visit` + a reminder engine (crons) in `rvt_notify`; `planning` not used for agencies | Planning needs employee or material resources and shift semantics; agency persons are partners, visits are per site with arrival confirmation |
| A8 | MOM and voice | Custom `rvt.mom` / `rvt.mom.item`; speech-to-text **on the phone** (Google / Apple speech, gu-IN, hi-IN, en-IN) with a server fallback through the existing Gemini stack (`aic_ai`, optional) | On-device is free, offline-capable and private; the server fallback handles long audio and mixed-language sentences |
| A8a | Existing MOM (2026-11-17) | `rvt_mom` replaces the MOM of `revert_customizations` (activities on tasks). Existing entries are moved into `rvt.mom` / `rvt.mom.item` by an ETL, shaped by the final requirement; then `revert_customizations` is retired | One MOM in the system; history stays visible in the new screens |
| A9 | Engagement | Own `rvt_game` (XP ledger, levels, badges, reliability score) modelled on `bhr_game`; core `gamification` optional for office badges | Rules must be records, awards must come from verified server events, and scores must stay private per agency; the core module is user-centric and public |
| A10 | Notifications | `rvt_notify` dispatcher: **Firebase push**, **official WhatsApp (Odoo `whatsapp`, Meta Cloud API)**, SMS fallback for OTP, email; templates per language | Revert is a business talking to clients; the official channel is the professional and durable choice. `open_whatsapp_connector` stays available as a fallback (Q J2) |
| A10a | WhatsApp (2026-11-18) | `open_whatsapp_connector` 20.0.95.0.0 with `web_auth_otp_login`, as on the Sudi project, on a dedicated Revert number. Supersedes the official-API recommendation in A10 | Decided by the project owner; no Meta approval lead time; sends PDFs. Unofficial route: caps stay on |
| A11 | Mobile app | **One Flutter app** with role-based homes (agency, client, office, owner) on **FastAPI inside Odoo** (`rvt_api`, the vendored OCA `fastapi` + `endpoint_route_handler` and PyJWT pattern of `marut_api` / `bhr_api`) | Proven in marut_20, sfj_be and bhujrnr_be; typed, documented, JWT per device; one app to publish and maintain |
| A12 | Languages | Odoo `gu_IN`, `hi_IN`, `en_IN` loaded; all `rvt_` fields and master data `translate=True`; app ARB files in three languages; the user's `lang` drives notifications | The brief requires Gujarati and Hindi for agencies |
| A13 | Back office | Odoo web client with the Glass theme and Identity white-label (`web_theme_glass`, `web_glass_workspace`, `identity*` from aic_apps), back office at `/office` | Same look the other Albatross projects ship; office staff still get full Odoo where the app is too small |
| A14 | Hosting (amended 2026-11-17) | The **existing production**: database `erp.revert.co.in` on the shared server `147.93.30.85` (nginx + certbot, Odoo 20 EE, PostgreSQL 18, local daily backups). To add: S3 backups, a staging copy. ~~Dedicated VPS in India with a fresh database~~ | Decided by the project owner: extend what Revert already uses. Consequences: a restart drops Albatross too, and media growth shares the disk |
| A15 | Existing system (2026-11-17) | Build in the existing repo `Albatross-IN/revert`, branch `20.0`, and in the existing database. `revert_customizations` and `admin_notes_viewer` stay installed until `rvt_mom` takes over | Users, projects, tasks and MOM history are already there; no second system, no second migration |

---

## 2. System context

```
 Agency persons   Clients   Office / Owner
   (Flutter app, gu/hi/en)   (Flutter app + Odoo back office)
        │               │              │
        ▼               ▼              ▼
 ┌──────────────────────────────────────────────────────────────┐
 │ nginx :443  app.revert… (TLS, rate limits, /websocket)       │
 └───────┬───────────────────────────────────┬──────────────────┘
         │ /api/rvt/v1 (FastAPI in Odoo)      │ /office, /my (Odoo web, portal)
         ▼                                   ▼
 ┌──────────────────────────────────────────────────────────────┐
 │ Odoo 20 Enterprise                                           │
 │  crm · project(+enterprise, gantt) · sale_project · purchase │
 │  account + l10n_in + withholding · documents · sign          │
 │  whatsapp (Meta Cloud API) · gamification · mail/discuss     │
 │  rvt_base rvt_site rvt_crm rvt_design rvt_agency             │
 │  rvt_execution rvt_visit rvt_mom rvt_finance rvt_game        │
 │  rvt_notify rvt_api · identity* · web_theme_glass            │
 │  workers + gevent (bus) + cron + queue_job                   │
 └───────┬──────────────┬──────────────┬───────────────┬────────┘
         ▼              ▼              ▼               ▼
   PostgreSQL     filestore        Firebase FCM    Meta WhatsApp
   (nightly S3)   (photos, video,  (push)          Cloud API
                   drawings, KYC)                  (templates)
                                                   SMS gateway (OTP fallback)
```

## 3. Module map (repo `revert`, all custom modules prefixed `rvt_`)

| Module | Depends on | Responsibility | Licence | Phase |
|---|---|---|---|---|
| `rvt_base` | `base`, `mail`, `contacts`, `project` | Groups and roles (owner, office lead, designer, supervisor, accounts, agency owner, agency person, client), trades (`rvt.trade`) with sequence and marking flag, settings, Gujarati/Hindi language loading, shared mixins (space link, media proof, client-safe text) | LGPL-3 | 1 |
| `rvt_site` | `rvt_base`, `web_map` | Site, space types, spec templates, spaces, door/window records, documentation checklist, Vastu notes, site summary | OEEL-1 (web_map) | 1 |
| `rvt_crm` | `rvt_base`, `crm`, `sale_project`, `utm` | Vision brief on the lead, referral fields and seriousness, qualification checklist, site creation at win, fee quotation template with milestones | LGPL-3 | 1 |
| `rvt_design` | `rvt_site`, `documents_project`, `sign` | Client brief, layout options, concept per space, drawing register and revisions, releases, approvals, queries with SLA, pending-drawings board | OEEL-1 | 2 |
| `rvt_agency` | `rvt_base`, `purchase`, `portal` | Agency profile, trades, persons, invites and OTP onboarding, KYC documents and verification, trade plan per project, quotation requests and comparison, work orders on `purchase.order` | LGPL-3 | 2 |
| `rvt_execution` | `rvt_site`, `rvt_agency`, `project_enterprise` | Work packages on `project.task`, scope lines, trade sequence templates, dependencies, planned/committed/actual dates, marking gate, progress updates with media, verification, Gantt views, blockers | OEEL-1 | 3 |
| `rvt_visit` | `rvt_execution`, `calendar` | Visits for agency persons and staff, conflicts, arrival confirmation with optional GPS, start/stop nudges, visit calendar and map | OEEL-1 | 3 |
| `rvt_mom` | `rvt_visit` | MOM, items with sticky space, voice audio + transcript, classification into tasks/queries/drawing changes/decisions, sharing per audience | LGPL-3 | 4 |
| `rvt_finance` | `rvt_agency`, `rvt_execution`, `account`, `l10n_in`, `l10n_account_withholding_tax`, `hr_expense` | Payment requests, RA bill measurement, approval to vendor bill, site expenses with payer and recoverability, client milestone invoicing, owner money view | LGPL-3 | 4 |
| `rvt_game` | `rvt_execution`, `rvt_visit`, `rvt_design` | XP rules and ledger, levels, badges, reliability score, project health score, recognition | LGPL-3 | 5 |
| `rvt_notify` | `rvt_base`, `whatsapp`, `sms`, `mail` | Dispatcher (push, WhatsApp, SMS, email, in-app), devices and tokens, templates per language, quiet hours, reminder crons, delivery log | OEEL-1 | 1 (skeleton), 3 (reminders) |
| `rvt_api` | all `rvt_*`, `fastapi`, `endpoint_route_handler` | REST `/api/rvt/v1`: routers per area, Pydantic schemas, JWT per device, role dependencies, Swagger (off in prod) | LGPL-3 | 1 onward |
| `rvt_office` | `rvt_*`, `web_glass_workspace` | Back-office home for the office: boards (drawings due, queries, agencies to finalise, verifications, payment requests, visits today), project health | OEEL-1 | 5 |
| Vendored: `fastapi`, `endpoint_route_handler`, `identity`, `identity_enterprise`, `web_theme_glass`, `web_glass_workspace`, `queue_job`, (`open_whatsapp_connector` only if Q J2 says unofficial) | | Copied from marut_20 / aic_apps 20.0; **not edited here** | as upstream | 1 |

**Licence rule:** a module that imports or depends on an Enterprise module (`project_enterprise`, `web_map`, `documents`, `sign`, `whatsapp`, `web_gantt`) is `OEEL-1`. Everything else is `LGPL-3`. Never copy code out of `/opt/erp/sub` into an LGPL module.

### 3.1 Standard Odoo modules used and what for

| Odoo module | Used for |
|---|---|
| `crm`, `utm` | Leads, stages, sources (referral), lost reasons |
| `sale_management`, `sale_project` | Fee quotation, milestone invoicing, project creation from the order |
| `project`, `project_enterprise`, `web_gantt` | Projects, work packages as tasks, stages, dependencies, Gantt, milestones, portal sharing of tasks |
| `purchase` | Work orders to agencies, lines per space/item |
| `account`, `l10n_in`, `l10n_account_withholding_tax`, `account_reports` | Invoices, vendor bills, payments, GST, TDS, analytic account per project |
| `hr_expense` | Office-staff expenses; agency and client-paid expenses use `rvt.expense` and post to vendor bills or re-invoices |
| `documents`, `documents_project` | A Documents workspace per project for drawings, photos, KYC (separate restricted folder) |
| `sign` | Agreement and optional concept sign-off |
| `whatsapp` | Official WhatsApp templates and messaging |
| `sms` | OTP fallback |
| `calendar` | Visits appear in staff calendars |
| `gamification` | Optional badges for office staff (`rvt_game` holds the real rules) |
| `web_map` | Sites and today's visits on a map |
| `knowledge` | Office SOPs (how to measure, how to verify) linked from the app |

## 4. Data model (summary; detail in system_design.md §3)

```
crm.lead (inherit)            vision brief, referral_partner_id, seriousness, site_visit_date, scope_wanted
project.project (inherit)     site_id, engagement_model (design|supervision|turnkey), client_contact_ids,
                              stage gates (milestones), health, client_safe_status, money view (owner)
rvt.site                      project_id, address, lat/lng, property_type, area, floors, north_deg, vastu_notes,
                              access_notes, documentation_state, summary (computed: "3 BHK + 2 bath")
rvt.space.type                name (translatable), category, spec_template_id, default trades
rvt.space.spec.template       lines: field key, label (translatable), type, unit, required
rvt.space                     site_id, type_id, name, sequence, dims, slab_h, clear_h, beams, spec json, photos,
                              video, brief, concept_state, documentation %, work % (computed from packages)
rvt.opening                   space_id, kind (door|window|ventilator|opening), w, h, sill, swing, notes
rvt.drawing                   project_id, type_id (trade), space_ids, sheet_no, revision, state, due, assignee,
                              file, released_to, released_at, approved_by/at, query_ids, blocks_task_ids
rvt.query                     project_id, drawing_id?, task_id?, space_id?, asked_by, question, media, answer,
                              answered_by/at, sla_deadline, state
rvt.agency                    partner_id, trade_ids, persons (partner children with users), kyc docs, kyc_state,
                              status, reliability_score, service_area, bank (masked), notes
rvt.trade.plan                project_id, trade_id, required, agency_id, decision_due, state (undecided|quoting|final)
rvt.quote.request / rvt.quote / rvt.quote.line → purchase.order (work order) per agency per project
project.task (inherit)        = work package: space_id, trade_id, agency_id, work_order_line_ids, scope lines,
                              needs_marking, marking_state, committed_end, actual_start/end, progress %,
                              proof media, verify_state, billable_amount, blocker, client_safe_note
rvt.progress.update           task_id, by, pct, note, media, material_needed, blocked, created_at
rvt.visit                     project_id, site_id, person_id (agency or staff), date, window, purpose,
                              state (planned|confirmed|arrived|started|done|missed), arrival_at, gps_distance
rvt.mom / rvt.mom.item        visit_id?, project_id, items: space_id (sticky), text, audio, transcript,
                              kind (todo|task|query|drawing_change|decision|client_action), assignee, due,
                              audience (internal|client|agency), converted_to (model, id)
rvt.payment.request           agency_id, project_id, work_order_id, type (advance|ra|final), lines
                              (task_id, qty, unit, rate), amount, media, state, bill_id
rvt.expense                   project_id, space_id?, payer (company|client|agency), partner_id, amount,
                              receipt, recoverable, reimbursed, bill/invoice links
rvt.xp.rule / rvt.xp.entry / rvt.level / rvt.badge / rvt.badge.award / rvt.reliability.snapshot
rvt.device / rvt.notification / rvt.template (per language) / rvt.reminder.rule
```

## 5. Key flows (short; full sequences in system_design.md §4)

1. **Lead → project.** Lead with vision brief → site visit scheduled → documentation done on the phone → fee quotation sent → won → project + site + client portal invite created; milestones from the fee schedule.
2. **Design.** Brief confirmed → layout options → client picks → concept per space → client OKs each space → drawings per trade with revisions → release to client/agency → queries answered within SLA.
3. **Agencies.** Trade plan from space types and the engagement model → quotation requests → quotes compared → work order → agency persons invited → KYC verified.
4. **Marking and execution.** Carpenter marking visit → photos → office approval → work packages unlocked in trade sequence → progress updates with media → done → verification → billable.
5. **Visits and MOM.** Office schedules visits → reminders → arrival confirmation → MOM items by space → converted to tasks, queries and drawing changes → shared to the right audience.
6. **Money.** Payment request from the app → approval → vendor bill (TDS if applicable) → payment → agency sees paid; expenses with payer and recoverability → client re-invoice; owner money view per project.
7. **Engagement.** Verified events award XP; reliability recomputed nightly; project health from signals; recognition monthly.

## 6. Non-functional requirements

| Concern | Target / approach |
|---|---|
| Devices | Android 10+ on ₹8k phones; iOS 15+; 360 px wide; sunlight-readable contrast; 48 px tap targets |
| Network | Site 3G or patchy 4G. Photos compressed on the phone (≤ 1600 px, ≤ 400 KB); video ≤ 60 s, ≤ 25 MB, uploaded in the background with resume; the app works offline for today's visits, assigned work and queued updates |
| Volume (assumed, Q K3) | 20–40 active projects, 10–40 spaces each, 50–150 drawings each, 60 agencies, 300 agency persons, 10–15 office users. A 4 vCPU / 8 GB VPS with `workers=6` is ample |
| Availability | 99.5%; nightly `pg_dump` + filestore to S3, 30-day retention, monthly restore drill; staging restored nightly and neutralised |
| Security | JWT per device (12 h access, 30 d refresh, revocable); roles enforced server-side; record rules so an agency sees only its projects, packages, queries and money; clients see only their project; KYC files private, Aadhaar masked; secrets in the server config |
| Privacy (DPDP Act 2023) | Consent text at onboarding (en/hi/gu); purpose-limited KYC; retention rule (Q K2); export and deletion on request |
| Performance | App home in one API call under 300 ms server time; lists paginated by cursor; Gantt per project rendered by Odoo's own view |
| Observability | Odoo logs to journald; uptime check; notification delivery log with failures surfaced on the office home; WhatsApp template rejections alerted |
| Audit | Every state change on drawings, work packages, payment requests, committed dates and approvals is tracked in chatter with who and when |

## 7. Why not …

| Alternative | Why not (for v1) |
|---|---|
| Odoo Field Service (`industry_fsm`) | Not in this build; one-technician intervention model; worksheets could be useful later for verification checklists (`worksheet` is available and can be attached to tasks in phase 3 if wanted) |
| Odoo Planning for agency schedules | Resources must be employees or materials; no arrival confirmation; shifts not visits |
| Odoo Documents alone for drawings | No trade, space, revision, release-to, approval or query semantics |
| Core `gamification` as the engine | Public, user-centric, goal definitions in Python domains; hard to keep scores private per agency and to feed from verified events |
| Separate apps per role | Three store listings, three codebases; one app with role homes is cheaper and lets a person who is both client and referrer, or both office and owner, switch |
| PWA instead of Flutter | Push, camera, offline and speech work far better natively on low-end Android |

## 8. Environments

| Env | Where | DB | Port | Notes |
|---|---|---|---|---|
| dev | this box, `/opt/erp` (Odoo 20 + `sub/`, `erp-venv`) | `revert20` | 8094 | a neutralised restore of production (amended 2026-11-17); `tools/dev.sh`; 8095–8099 are used by other projects |
| staging | shared server `147.93.30.85` (to build) | named after its host | — | nightly restore from prod, neutralised (no WhatsApp, no push, no email) |
| prod | shared server `147.93.30.85` (live) | `erp.revert.co.in` | 8069 / 8072 | `https://erp.revert.co.in`; service `erp-odoo20` shared with Albatross (amended 2026-11-17) |

Enterprise licence: build on dev under the developer licence; create prod about 2 weeks before go-live on the 30-day trial and register Revert's subscription code before day 30. Portal users (agencies, clients) are free; licences are needed for office staff and the owner only.

## 9. Future scalability

- **Materials procurement** (turnkey): `purchase` + `stock` for Revert-bought materials with delivery to site; the data model already carries the project and space on purchase lines.
- **Quantity take-off**: BOQ lines per space from spec templates and drawings; `rvt.quote.line` is already per space and item.
- **Multiple studios / branches**: multi-company or a `studio_id` on project; record rules extend.
- **Client marketplace or referrals**: referrer portal with status of referred projects.
- **AI assistance**: query drafting, MOM classification, photo-based progress estimates, through the existing Gemini stack (`aic_ai`), behind a setting.
- **Worksheets**: `worksheet` templates attached to work packages for trade-specific verification checklists.
