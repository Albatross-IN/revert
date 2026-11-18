# Revert platform: system design

Status: v0.1 · 2026-10-31 · the detailed companion of [architecture.md](architecture.md)
API reference: [api_design.md](api_design.md) · App: [mobile_app_plan.md](mobile_app_plan.md) · Look and tone: [design.md](design.md)

## 0. Assumptions this design is built on (to be confirmed in the questionnaire)
| Area | Assumption | Question |
|---|---|---|
| Engagement | Base case is design + supervision; the client pays agencies on Revert's work orders; turnkey and design-only are flags on the project | A1, A2 |
| Agencies | Fixed panel per trade; owner plus workers; agency with material for most trades | E2, E3, E5 |
| Marking | Carpenter, electrician and plumber mark; supervisor approves from photos | F1 |
| Billing | Measured RA bills against the quote; TDS when Revert pays | F5, A7 |
| Client view | Stage progress, next steps, photos, their approvals and invoices; no agency prices | G4 |
| WhatsApp | Official Meta Cloud API via Odoo `whatsapp` | J2 |
| Languages | gu, hi, en; voice on the phone | G3, J3 |

---

## 1. Components and deployment

```
                ┌────────────────────────── Revert VPS (Ubuntu, India) ───────────────────────────┐
 Flutter app ──►│ nginx :443  <domain>                                                             │
 (agency/client │   /api/rvt/v1/*  → Odoo (rvt_api on OCA fastapi, as in marut_20)                │
  office/owner) │   /websocket     → Odoo gevent (bus doorbell for open apps)                     │
   ▲            │   /office, /my   → Odoo back office (Glass + Identity), portal                   │
   │            │                                                                                  │
   │            │ Odoo 20 EE  revert.service  (127.0.0.1:8169 http, :8172 gevent, db revert)       │
   │            │   crm · project_enterprise · sale_project · purchase · account/l10n_in            │
   │            │   documents · sign · whatsapp · gamification · rvt_* · identity · glass           │
   │            │   queue_job runner (media processing, notification fan-out, nightly scores)      │
   │            └──────────────────────────────────────────────────────────────────────────────────┘
   │
   ├──── FCM push ◄── Firebase project (Revert) ◄── rvt_notify (HTTP v1 API, service account root-only)
   ├──── WhatsApp ◄── Meta Cloud API ◄── Odoo whatsapp (templates per language, webhook back to Odoo)
   └──── SMS (OTP fallback) ◄── Indian DLT-registered gateway (Q J2)
```

| Component | Runs as | Notes |
|---|---|---|
| Odoo 20 + `rvt_*` | `revert.service` | system of record, back office, API |
| `queue_job` | same process, `--load=base,rpc,web,queue_job` | thumbnails, video probes, notification fan-out, score recompute |
| Firebase Cloud Messaging | HTTP v1 | Android + iOS push |
| WhatsApp | Odoo `whatsapp` module | templates approved by Meta; inbound replies land in Discuss and are mirrored to the query thread |
| Backups | systemd timer 19:30 UTC | `pg_dump` + filestore tar → S3 (Marut pattern), no-delete IAM user |

---

## 2. Odoo module responsibilities

See architecture.md §3 for the table. Dependencies form a strict order so each phase installs on its own:

```
rvt_base → rvt_site → rvt_crm
                    → rvt_design
rvt_base → rvt_agency
rvt_site + rvt_agency → rvt_execution → rvt_visit → rvt_mom
rvt_agency + rvt_execution → rvt_finance
rvt_execution + rvt_visit + rvt_design → rvt_game
rvt_base → rvt_notify (used by all through a service, soft dependency via `_name` lookups)
all → rvt_api, rvt_office
```

---

## 3. Data model

### 3.1 Roles and people
```
res.groups (rvt_base)      group_rvt_owner > group_rvt_office_lead > group_rvt_designer | group_rvt_supervisor
                           group_rvt_accounts ; portal: group_rvt_agency_owner, group_rvt_agency_person, group_rvt_client
res.users (inherit)        rvt_role (computed from groups: owner|office_lead|designer|supervisor|accounts|
                           agency_owner|agency_person|client), rvt_lang_pref, rvt_signature (image)
res.partner (inherit)      rvt_is_agency, rvt_agency_id, rvt_is_client, rvt_phone_e164, rvt_lang (gu|hi|en),
                           rvt_referred_by_id, rvt_referral_count
rvt.device                 user_id, platform, app_version, push_token, push_enabled, refresh_jti, last_seen, active
rvt.otp                    target (phone), channel (whatsapp|sms), code_hash, attempts, expires (5 min), consumed
```
Office staff are internal users with one of the office groups. Agency owners, agency persons and clients are **portal users**; every permission check happens in the API and in record rules.

### 3.2 Site and spaces (`rvt_site`)
```
rvt.site                   name, project_id, partner_id (client), address fields, lat, lng, maps_url,
                           property_type (apartment|bungalow|villa|office|hospital|clinic|studio|factory|retail|other),
                           carpet_area, builtup_area, area_unit (sqft|sqm), floors, floor_no, possession_date,
                           north_deg (0-359), vastu_notes (html), vastu_by, vastu_at, access_notes, parking_notes,
                           lift (bool), working_hours_allowed, society_rules,
                           documentation_state (pending|partial|complete|overridden), documentation_pct (computed),
                           summary (computed: "3 BHK · 2 bath · 1 balcony · 1,250 sq ft")
rvt.space.type             name (translate), code, category (residential|office|healthcare|industrial|common),
                           spec_template_id, default_trade_ids, icon, sequence, counts_as_bhk (bool)
rvt.space.spec.template    name, line_ids
rvt.space.spec.line        template_id, key, label (translate), field_type (float|int|text|bool|select|photo),
                           unit, options, required, sequence, help (translate)
rvt.space                  site_id, type_id, name (default from type + number), sequence, floor,
                           length, width, slab_height, clear_height, area (computed), beam_notes, column_notes,
                           spec_json (values keyed by spec line key), photo_ids (attachments, with kind
                           measurement|existing|progress), video_ids, notes,
                           brief (html, client-confirmable), concept_state (none|shared|approved|changes),
                           documentation_pct, work_pct (from packages), client_safe_status
rvt.opening                space_id, kind (door|window|ventilator|opening|shutter), label, width, height,
                           sill_height, lintel_height, swing (left|right|sliding|none), material_existing, keep (bool)
rvt.existing.point         space_id, kind (light|fan|switchboard|socket|ac|water_in|drain|gas|data), x, y, wall, notes
rvt.site.checklist.item    site_id, key (north|vastu|video|per_space_dims|per_space_photo|per_space_clear_h|...),
                           done, done_by, done_at, waived_reason
```
**Site type summary**: `summary` counts spaces whose type has `counts_as_bhk` for the "N BHK" prefix, then bathrooms, balconies and area. For offices and hospitals it lists cabin/ward counts and area.

### 3.3 Design (`rvt_design`)
```
rvt.drawing.type           name (translate), code (e.g. FL, FC, EL, PL, FLR, WE, CD, DW, LT, HV, CV),
                           trade_id, sequence, needs_client_approval (bool), default_due_offset_days
                           draft set: FL furniture layout · DM demolition/civil · FC false ceiling · EL electrical
                           points · SB switchboard · PL plumbing · FLR flooring pattern · WE wall elevations ·
                           CD carpentry details · DW door/window schedule · LT lighting · HV HVAC · ST stone details
rvt.layout.option          project_id, name ("Option A"), file, thumbnail, state (shared|chosen|dropped), client_note
rvt.drawing                project_id, type_id, trade_id (related), space_ids, sheet_no (unique per project),
                           title, revision (0,1,2…), state (planned|in_progress|internal_check|released|approved|
                           changes_requested|superseded), due_date, assignee_id, checker_id, file (attachment, PDF),
                           dwg_file (optional), document_id (documents.document mirror),
                           released_to (none|client|agency|both), released_at, released_by, release_note,
                           approved_by (client partner), approved_at, change_note,
                           blocks_task_ids (work packages that cannot start before release), query_ids,
                           supersedes_id (previous revision), client_visible (bool)
rvt.query                  project_id, drawing_id?, task_id?, space_id?, asked_by (partner), asked_via (app|office),
                           question (text), media_ids, answer (html), answered_by, answered_at,
                           priority (blocking|normal), sla_deadline (computed from priority + office hours),
                           state (open|answered|closed|reopened), satisfaction (thumbs), is_overdue (computed)
```
**Approval**: a drawing of a type with `needs_client_approval` goes `released → approved` on the client's tap; `changes_requested` creates a new revision in `in_progress` and marks the old one `superseded`. Space `concept_state` is set per space from its concept boards (drawings of a "Concept" type, one per space).

### 3.4 Agencies and work orders (`rvt_agency`)
```
rvt.trade                  name (translate), code (civil|electrical|plumbing|pop|paint|carpentry|window|stone|glass|
                           fabrication|tiles|kitchen|soft|hvac|lv|furniture|polish), sequence (trade order),
                           needs_marking (bool), billing_unit_default (sqft|point|rft|lumpsum|nos|day),
                           predecessor_trade_ids (default dependencies), color
rvt.agency                 partner_id (company), name, trade_ids, owner_partner_id, person_ids (partners with
                           parent = agency partner), languages, service_areas, since,
                           kyc_state (none|pending|verified|rejected), kyc_verified_by/at,
                           pan (masked display), pan_doc, aadhaar_last4, aadhaar_doc (private), gstin?, gst_doc,
                           bank_name, bank_account_masked, bank_ifsc, cheque_doc, upi_id,
                           status (invited|onboarding|active|paused|blacklisted), paused_reason,
                           reliability_score (0-100, nightly), level_id, rating_internal (1-5), notes (internal),
                           allow_work_before_kyc (bool, default from settings)
rvt.agency.invite          agency_id, partner_id (person), code (8 chars), channel (whatsapp|sms), sent_at, expires,
                           used_at
rvt.trade.plan             project_id, trade_id, required (bool), reason_not_required, agency_id, decision_due,
                           state (undecided|quoting|finalised|not_required), finalised_at, finalised_by,
                           client_safe_text (computed: "We are finalising the electrical partner")
rvt.quote.request          project_id, trade_id, agency_ids, due_date, scope (html), drawing_ids, space_ids, state
rvt.quote                  request_id, agency_id, received_at, via (app|email|paper), total, validity, notes,
                           line_ids, state (received|shortlisted|rejected|accepted), attachment
rvt.quote.line             quote_id, space_id, description, unit (sqft|point|rft|lumpsum|nos|day), qty, rate,
                           amount, material_included (bool), remarks
purchase.order (inherit)   rvt_project_id, rvt_agency_id, rvt_trade_id, rvt_quote_id, rvt_paid_by (company|client),
                           rvt_advance_pct, rvt_retention_pct, rvt_retention_days, rvt_ra_billing (bool),
                           committed_end (agreed), state flow unchanged (draft → sent → purchase)
purchase.order.line (inh.) rvt_space_id, rvt_unit, rvt_material_included, rvt_task_ids (work packages created from it)
```
A **work order** is a confirmed `purchase.order` with `rvt_paid_by`. When the client pays directly, the PO is still the contract record; bills against it are marked "paid by client" and never hit Revert's payables, but they count in the project money view.

### 3.5 Execution (`rvt_execution`)
```
project.project (inherit)  site_id, engagement_model (design|supervision|turnkey), client_partner_ids,
                           principal_id, supervisor_id, designer_ids, stage gates via project.milestone
                           (Documented, Brief confirmed, Layout chosen, Concept approved, Drawings released,
                           Agencies finalised, Marking approved, Execution complete, Handover),
                           health (on_track|attention|stuck; computed, §8.3), health_reasons (json),
                           client_safe_status (text written by office), next_client_action, trade_sequence_template_id,
                           allow_task_dependencies = True, allow_milestones = True
rvt.trade.sequence.template name, line_ids (trade_id, predecessor_trade_ids, lag_days)
project.task (inherit)     = work package when rvt_kind = 'work' (also 'marking', 'snag', 'office')
                           space_id, trade_id, agency_id, work_order_id, work_order_line_ids,
                           scope_line_ids (rvt.scope.line: description, unit, qty, rate, done_qty, verified_qty),
                           needs_marking (from trade), marking_task_id, marking_state (none|pending|photos|approved|rejected),
                           planned_date_begin, date_deadline (planned end), committed_end, committed_set_by/at,
                           committed_history (json: date, reason, by), actual_start, actual_end,
                           progress_pct (last update), last_update_at, silent_days (computed),
                           proof_media_ids, done_requested_at, verify_state (none|pending|passed|rework),
                           verify_by/at, verify_note, rework_reason, rework_count,
                           blocked (bool), blocked_reason (material|drawing|access|other), material_needed (text),
                           billable_amount (sum verified_qty × rate), billed_amount, client_safe_note,
                           depend_on_ids (core), drawing_ids (required drawings), is_ready (computed: deps done,
                           drawings released, marking approved)
rvt.progress.update        task_id, by_partner_id, pct, note, media_ids, material_needed, blocked, blocked_reason,
                           lat, lng, created_at, is_done_claim (bool)
rvt.snag                   project_id, space_id, trade_id, agency_id, description, media, state (open|fixed|verified),
                           raised_by, due
```
**Stages** (`project.task.type` per project template): *Planned → Marking → Ready → In progress → Done (pending verification) → Verified → Billed*, plus *Rework* as a return path. `is_ready` is what the agency sees as "you can start".

### 3.6 Visits and MOM (`rvt_visit`, `rvt_mom`)
```
rvt.visit                  project_id, site_id, person_partner_id (agency person or staff user partner),
                           agency_id?, task_ids (what they come for), date, window_start, window_end,
                           purpose (work|marking|measurement|mom|verification|client_meeting|handover),
                           created_by, source (office|agency_owner|auto),
                           state (planned|confirmed|arrived|started|done|missed|cancelled),
                           reminded_evening_at, reminded_morning_at, confirmed_at, arrived_at, arrival_lat/lng,
                           arrival_distance_m, started_at, ended_at, missed_reason, conflict_ids (same person, overlapping),
                           calendar_event_id (for staff)
rvt.mom                    project_id, visit_id?, date, attendees (partners), by_user_id, state (draft|shared),
                           shared_client_at, shared_agency_at, pdf
rvt.mom.item               mom_id, sequence, space_id (sticky at capture), text, audio (attachment), transcript_lang,
                           kind (todo|task|query|drawing_change|decision|client_action|note),
                           audience (internal|client|agency|all), assignee_partner_id, agency_id, due,
                           converted_model, converted_res_id, state (open|converted|done)
```
**Existing MOM (decided 2026-11-17).** Production already holds MOM entries as activities on project tasks (`revert_customizations`: Sr. No., Related To, site photo, Visit Date, Visit No#, remark, closing note, open/closed). `rvt_mom` replaces that. An ETL (task 6.6) turns each project + Visit Date into one `rvt.mom` and each entry into an `rvt.mom.item`, keeping the photo, the task link and the closed state. The exact mapping is fixed after the questionnaire answers; fields the new model lacks (Sr. No., Related To) are added to it or kept in the item text, to be decided then.

### 3.7 Money (`rvt_finance`)
```
rvt.payment.request        agency_id, project_id, work_order_id, type (advance|ra|final|retention_release),
                           line_ids (task_id, description, unit, qty_claimed, qty_verified, rate, amount),
                           amount_claimed, amount_approved, media_ids, note, requested_by, requested_at,
                           state (draft|submitted|returned|approved|billed|paid|rejected), returned_note,
                           approved_by/at, bill_id (account.move), paid_by (company|client), paid_at, payment_ref,
                           client_payment_proof (when the client pays directly, uploaded by office or client)
rvt.expense                project_id, space_id?, task_id?, date, payer (company|client|agency|staff),
                           payer_partner_id, category (hardware|cartage|labour|petty|food|fuel|permission|other),
                           amount, gst_amount, receipt (attachment), note,
                           recoverable_from_client (bool), recovered_invoice_line_id, reimbursed (bool),
                           reimbursed_payment_id, state (draft|approved|rejected|settled), approved_by
sale.order (inherit)       rvt_project_id, rvt_fee_model (per_sqft|pct|lumpsum|turnkey), rvt_area, rvt_rate,
                           milestone lines (sale_project) = fee schedule
project.project (money view, owner group only; computed from the analytic account)
                           contract_value, invoiced, received, outstanding,
                           agency_committed (Σ work orders), agency_billed, agency_paid_company, agency_paid_client,
                           agency_pending, expenses_total, expenses_company, expenses_recoverable, expenses_recovered,
                           probable_invoice (contract + recoverable + approved extras), margin (turnkey only)
```
Every PO, bill, expense and invoice carries the project's analytic account (`project.project.account_id`), so the view is a set of analytic sums plus the `paid_by` split.

### 3.8 Engagement (`rvt_game`)
```
rvt.xp.rule                code, name (translate), points, daily_cap, audience (agency_person|agency|office), active
rvt.xp.entry               partner_id, rule_id, points, date, source_model, source_id   (append-only)
rvt.level                  audience, sequence, name (translate), min_xp, icon
rvt.badge                  code, name (translate), description (translate), audience, criteria_type
                           (count|streak|first|manual), threshold, icon, secret
rvt.badge.award            partner_id, badge_id, awarded_at, source
rvt.reliability.snapshot   agency_id, date, score, components (json: on_time_arrival, update_cadence, proof_rate,
                           query_response, rework_rate, commitment_adherence)
rvt.project.health.log     project_id, date, health, reasons (json)
```

### 3.9 Notifications (`rvt_notify`)
```
rvt.template               code, channel (push|whatsapp|sms|email|inapp), lang, subject, body (jinja-like fields),
                           whatsapp_template_id (approved Meta template), deep_link pattern
rvt.notification           partner_id, code, channel, payload, deep_link, state (queued|sent|delivered|failed|read),
                           sent_at, read_at, error
rvt.reminder.rule          code (visit_evening|visit_morning|arrival_check|start_nudge|eod_update|pending_digest|
                           drawing_due|query_sla|trade_undecided|approval_pending|payment_waiting),
                           offset, channel order, audience, quiet_hours_respect, active
```

---

## 4. State machines and stage gates

### 4.1 Project stages and exit conditions
| Stage | Owner | Exit condition (auto unless overridden) | Client sees |
|---|---|---|---|
| Lead | Owner | Fee quotation accepted (`sale.order` confirmed) | — |
| Documenting | Supervisor | Site checklist complete (FR-S2) | "We are measuring and studying your site" |
| Brief | Designer | Brief confirmed by client (tap) | "Tell us how you live / work" (confirm brief) |
| Layout | Designer | A layout option is `chosen` | "Choose your layout" |
| Concept | Designer | All spaces `concept_state = approved` | "Approve the look of each room" |
| Drawings | Designer | All drawing types marked required for the project are `released` | "Your drawings are being prepared" (count released / total) |
| Agencies | Supervisor | All required trade plans `finalised` | "We are finalising your execution partners" |
| Marking | Supervisor | Marking tasks approved for trades that need it | "Layout is being marked on site" |
| Execution | Supervisor | All work packages `verified` and snags `verified` | Progress per room, photos, what is next |
| Handover | Principal | Handover milestone reached, final invoice issued | "Handover on <date>" |
| Closed | Owner | Money view reconciled (pending = 0) | "Thank you" + referral ask |

Stages can overlap in reality (drawings for the kitchen while the living room is in concept). The project stage is the **lowest incomplete gate**; the per-space view shows each room's own position, which is what the client sees most.

### 4.2 Work package
```
Planned ──(deps done, drawings released, marking approved or not needed)──► Ready
Ready ──(agency taps Start, or first progress update)──► In progress
In progress ──(agency taps Done with media)──► Done, pending verification
Pending verification ──(supervisor Pass)──► Verified ──(payment request billed)──► Billed
Pending verification ──(supervisor Rework + reason)──► Rework ──(agency Start)──► In progress
any ──(office)──► Cancelled (reason)
```

### 4.3 Drawing
```
Planned → In progress → Internal check → Released ──(client tap)──► Approved
                                              └──(change request)──► Changes requested → (new revision) In progress ; old → Superseded
```

### 4.4 Visit
```
Planned ──(T-1 evening reminder, T morning reminder)──► Confirmed (tap "I will come")
Confirmed/Planned ──(tap "I have arrived" ± GPS)──► Arrived ──(tap Start or first update)──► Started ──► Done
Planned/Confirmed ──(no arrival 60 min after window start)──► office alert; ──(end of day)──► Missed (reason asked)
```

### 4.5 Payment request
```
Draft → Submitted ──(office)──► Approved → Billed (vendor bill, TDS) → Paid (company) | Paid by client (proof)
Submitted ──(office)──► Returned (note) → Draft
```

---

## 5. Key flows

### 5.1 Lead to project
```
Office app ─ New lead {name, phone, type, size, location, dates, budget band, scope, referral, voice note}
  → referral? seriousness=high, SLA 24 h, "thank you" WhatsApp to referrer (if opted)
Office ─ Schedule site visit → rvt.visit(purpose=measurement) for a junior → reminders
Junior app ─ Site → Add spaces from types → fill spec (template) → photos, video → north, Vastu by principal
  → documentation_pct 100 → lead stage Documented
Office ─ Fee quotation (sale.order template per fee model, milestones from schedule) → send PDF (email/WhatsApp)
Client ─ Accepts (sign optional) → order confirmed → project created (sale_project), site linked, milestones created,
  client portal user invited (WhatsApp code), lead won
```

### 5.2 Design and approvals
```
Designer ─ Brief per project/space → client app "Confirm brief" (edit suggestions as a note)
Designer ─ Layout options (files) → client app "Choose" → chosen → others dropped
Designer ─ Concept per space (drawing type Concept) → release → client app per-room "Looks good" / "Change"
Designer ─ Drawings per type/trade with due dates (defaults from type offsets) → internal check → release
  → notification to client (if type needs approval) and to agencies of that trade (their persons, in their language)
Agency person ─ Query on drawing with photo → designer notified → answer → asker notified; SLA timer; overdue → office home
```

### 5.3 Agency finalisation and work orders
```
Project created → trade plan rows from space types' default trades + engagement model → decision_due defaults
Supervisor ─ Quote request per trade to 2-3 panel agencies (scope, drawings, spaces) → agencies get it in app
Agency owner ─ Quote lines in app (or office types from paper) → comparison view → shortlist → accept
Accept → purchase.order (work order) with paid_by, advance %, retention → work packages generated per
  space × scope line (or per space) with planned dates from the trade sequence template → trade plan finalised
Agency owner ─ invites persons (name, phone, language) → codes → persons onboard; KYC docs uploaded once per agency
Office ─ KYC verify → agency active
```

### 5.4 Marking, execution, verification
```
Supervisor ─ schedule marking visit (carpenter) → carpenter app: visit → arrived → marking task → photos → "Marking done"
Supervisor ─ approve from photos (or on site) → marking_state approved → dependent packages become Ready
Agency person ─ Today: site, time, packages ready → Start → progress updates (pct, note, photos, material needed)
  → EOD nudge if silent → Done with media → supervisor verifies → Verified → billable_amount grows
Client ─ sees room progress, curated photos (client_visible), "next: painter from Monday"
```

### 5.5 Visit day
```
19:00 T-1  push + WhatsApp "Tomorrow 10:00 · Shah residence, Bodakdev · carpentry finishing" → tap "I will come"
07:30 T    push "Today 10:00 …" with map link
10:00      window start; no "arrived" by 11:00 → office home alert + WhatsApp to agency owner
on arrive  tap → GPS distance stored (if permitted); 30 min later, no update → "Have you started?" nudge
18:30      no update since start → "Share today's progress with a photo"
```

### 5.6 MOM
```
Principal app ─ Visit → "Start MOM" → current space = first space (or none)
  item: type or hold-to-talk → on-device STT (gu/hi/en) → editable text + audio kept
  "Change location" → pick space → following items carry it
Office (same evening) ─ classify items: task (→ project.task in the space/trade, assignee, due), query, drawing change
  (→ new revision planned), decision, client action; set audience
Share → client PDF/app (client + all items), each agency (their items), internal (everything)
```

### 5.7 Money
```
Agency owner app ─ Payment request: type RA → pick verified packages → qty claimed (prefilled with verified) → media → submit
Office ─ compare claimed vs verified vs quote → approve amount (or return) → vendor bill created on the PO
  (TDS line if applicable, paid_by) → accounts pays → bill paid → agency app shows Paid with date and UTR
Client pays directly → office marks bill "paid by client" with proof → counts in project view, not in payables
Expense ─ anyone with rights: payer, amount, receipt, recoverable → approve → if recoverable: added to next client invoice
Owner app ─ Project money: contract / invoiced / received / agency committed / billed / paid (company vs client) / expenses / recoverable / probable invoice / margin
```

---

## 6. Security and access

| Topic | Rule |
|---|---|
| App auth | JWT (HS256, PyJWT) as in `marut_api`: access 12 h, refresh 30 d bound to `rvt.device`, rotated on refresh, revocable. Agency and client login by phone + OTP (WhatsApp, SMS fallback), then an optional 6-digit PIN with biometric unlock. Office staff log in with Odoo credentials (TOTP if enabled) |
| Roles | Every endpoint declares its minimum role. Record rules: agency sees its own agency, projects where it has a trade plan or work order, its packages, queries, visits, payment requests; agency person sees only their own visits and the packages of their agency on sites they are scheduled for; client sees their projects, client-visible drawings and photos, their approvals, invoices and MOM items with audience client/all |
| Money | Owner group only for the project money view and margins; accounts group for bills and payments; office sees work order values without margin (Q A9) |
| KYC | Aadhaar stored as last 4 digits plus a private attachment readable by owner and accounts; PAN masked in lists; bank account masked; files never public |
| Media | Attachments are private; served through the API with an access check and a short-lived signed URL for the app's image cache |
| Client-safe text | Fields marked client-safe are the only free text the client ever sees; agency notes, rework reasons and scores never cross |
| Secrets | JWT secret, FCM service account, WhatsApp tokens, S3 keys: server config or root-only files |
| Audit | `tracking=True` on states, committed dates, approvals, amounts; chatter messages on every gate |

---

## 7. Notifications matrix

| Event | Push | WhatsApp | SMS | Email | In-app | Who |
|---|---|---|---|---|---|---|
| Invite code | – | ✓ | fallback | – | – | agency person, client |
| OTP | – | ✓ | fallback | – | – | requester |
| Visit reminder T-1 evening | ✓ | ✓ | – | – | ✓ | person |
| Visit reminder morning | ✓ | – | – | – | ✓ | person |
| No arrival 60 min after window | ✓ | ✓ | – | – | ✓ | agency owner, supervisor |
| Start nudge / EOD update nudge | ✓ | – | – | – | ✓ | person |
| Package ready to start | ✓ | ✓ | – | – | ✓ | agency owner, person |
| Drawing released | ✓ | ✓ (agency) | – | ✓ (client) | ✓ | per release_to |
| Approval waiting (client) | ✓ | ✓ after 2 d | – | ✓ | ✓ | client |
| Query asked / answered | ✓ | – | – | – | ✓ | assignee / asker |
| Query past SLA | ✓ | – | – | – | ✓ | assignee, office lead |
| Trade undecided past due | ✓ | – | – | – | ✓ | supervisor, owner |
| Done claimed / verification result | ✓ | – | – | – | ✓ | supervisor / agency |
| Payment request submitted / approved / paid | ✓ | ✓ (paid) | – | – | ✓ | office / agency owner |
| Client invoice / receipt | – | ✓ | – | ✓ | ✓ | client |
| MOM shared | ✓ | ✓ (link) | – | ✓ (client) | ✓ | per audience |
| Level up / badge / monthly recognition | ✓ | – | – | – | ✓ | person |
| Weekly project digest | – | – | – | ✓ | ✓ | client, owner |

Quiet hours 21:00–07:30 IST except arrival alerts to the office. Every send is logged with delivery state; failures over 24 h surface on the office home.

---

## 8. Engagement and gamification (professional)

### 8.1 Principles
1. **Only verified events earn points**: confirmed arrival inside the window, a progress update with media, a done claim that passes verification, an answered query inside the SLA, a drawing released on or before its due date.
2. **Scores are private**: an agency sees its own score, level and badges; the office sees all; clients and other agencies see none (Q I2).
3. **Nothing punitive in public**: low scores change what the office does (follow-up, choice of agency), never what the person sees from others.
4. **Rules are records** (`rvt.xp.rule`, caps, levels, badges), editable by the owner, with an audit trail.

### 8.2 Rules (defaults)
| Audience | Event | XP | Cap |
|---|---|---|---|
| Agency person | Arrival confirmed within the window | +20 | 2/day |
| Agency person | Progress update with photo | +10 | 3/day |
| Agency person | Done claim verified first time | +40 | – |
| Agency person | Rework | 0 (reliability component only) | – |
| Agency owner | Payment request with complete measurements, approved without return | +30 | – |
| Agency owner | Quote submitted before due | +20 | – |
| Agency owner | Committed end met | +50 per package | – |
| Office designer | Drawing released on or before due | +30 | – |
| Office designer | Query answered within SLA | +10 | 10/day |
| Office supervisor | Verification within 24 h of claim | +10 | 10/day |
| Office supervisor | Visit scheduled 48 h ahead | +5 | 5/day |

**Levels (agency)**: Naya Sathi (0) · Bharosemand (300) · Ustad (900) · Karigar Shiromani (2,000) · Revert Partner (4,000). Names to be confirmed with the owner (Q I1); shown in the user's language.

**Badges**: First Site, 10 / 50 / 200 verified packages, 4-week on-time streak, Zero Rework Month, Early Bird (10 confirmed arrivals before 09:30), Clear Communicator (20 updates with photos), Fast Answer (designer: 50 queries in SLA), Release Train (designer: 20 drawings on time).

**Reliability score** (agency, 0–100, nightly over the last 90 days): on-time arrival 25 · update cadence 15 · proof rate 15 · query response 10 · rework rate 20 · commitment adherence 15. Shown to the agency as a number with a one-line hint on what raises it.

### 8.3 Project health (office and owner only)
`stuck` if any: a blocking query past SLA by > 1 day, a required drawing overdue > 3 days with a dependent package Ready-blocked, a trade undecided past due, a package silent > 3 working days while In progress, a committed end slipped twice.
`attention` if any: a drawing due in 2 days unassigned, a client approval waiting > 5 days, a payment request submitted > 3 days, a visit missed this week.
`on_track` otherwise. Reasons are listed so the office can act; the client sees `client_safe_status` only.

### 8.4 Client momentum (what the client gets instead of scores)
Room progress rings, "this week on your site" photo strip, "what happens next" with dates, decisions waiting on them, a timeline of gates reached. Delay copy is written by the office in `client_safe_status` using the pattern in design.md §2.

---

## 9. Languages and voice

- Odoo languages `en_IN`, `hi_IN`, `gu_IN` activated; `rvt_` modules ship `i18n/hi.po` and `i18n/gu.po`; master data fields are `translate=True`.
- The app ships ARB files for `en`, `hi`, `gu`; the user picks a language at first login; `res.partner.rvt_lang` drives templates.
- Notifications pick the template in the recipient's language, falling back to English.
- **Voice**: Flutter `speech_to_text` with locale `gu-IN`, `hi-IN` or `en-IN` as chosen by the speaker before holding the mic; the audio is saved with the item; a server fallback (optional, phase 4) sends the audio to the Gemini stack for transcription of mixed-language sentences, behind a setting and consent text.
- Numbers, dates and currency use Indian formatting (₹1,25,000; 12 Nov 2026) in all three languages.

---

## 10. Configuration (back office: Revert › Configuration)
| Setting | Default |
|---|---|
| Office hours and holidays (for SLAs, reminders) | Mon–Sat 10:00–19:00, Gujarat holidays |
| Query SLA | blocking 4 working hours, normal 1 working day |
| Visit reminders | T-1 19:00 and T 07:30; arrival alert at window start + 60 min |
| Start nudge / EOD nudge | 30 min after arrival; 18:30 if no update since start |
| Client approval reminder | 2 days (app + WhatsApp), 5 days (office nudge) |
| Trade decision due | project start + 14 days (per trade override) |
| Allow work before KYC | off |
| Done requires media | on (photos ≥ 1) |
| Verification target | 24 h |
| Client sees photos | curated only (`client_visible` on media) |
| Quiet hours | 21:00–07:30 |
| XP rules, levels, badges, reliability weights | records (§8) |
| Trade list, sequence template, drawing types, space types, spec templates | records |
| WhatsApp templates per language | records linked to approved Meta templates |
