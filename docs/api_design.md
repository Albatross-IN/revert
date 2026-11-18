# Revert API v1

Status: v0.1 design · 2026-10-31 · see [system_design.md](system_design.md)
Base URL: `https://<domain>/api/rvt/v1` · OpenAPI and Swagger UI at `/api/rvt/v1/docs`, served only when *Public API docs* is ticked on the endpoint record (off in production)

**Implementation: the same FastAPI layer as marut_20 and bhujrnr_be** (`marut_api`, `bhr_api`):
- the OCA `fastapi` module (ACSONE port 20.0.1.1.0) + `endpoint_route_handler`, vendored from marut_20
- one `fastapi.endpoint` record ("Revert API", `root_path=/api/rvt/v1`, a dedicated runner user in `fastapi.group_fastapi_endpoint_runner`), `_get_fastapi_routers()` returning one APIRouter per area below
- `schemas.py` (Pydantic), `errors.py` (one JSON error shape), `dependencies.py` (current user from JWT, role checks, record scoping), `jwt_tokens.py` (PyJWT, access 12 h / refresh 30 d per device), `hooks.py` (endpoint sync on install)

## 1. Conventions
| Topic | Rule |
|---|---|
| Format | JSON (UTF-8). Uploads are `multipart/form-data`. Dates are ISO-8601 UTC; the business time zone is Asia/Kolkata and the app renders local time |
| Language | `Accept-Language: gu|hi|en` (defaults to the user's `rvt_lang`); translatable names and all server-composed texts come back in that language |
| Auth | `Authorization: Bearer <access JWT>`; renew with the refresh JWT (rotated, bound to the device); none for `/public`; HMAC for `/webhooks` |
| Roles | `agency_person` · `agency_owner` · `client` · `supervisor` · `designer` · `accounts` · `office_lead` · `owner`. `office` means any of supervisor, designer, accounts, office_lead, owner. Each endpoint lists the minimum role; records are scoped server-side |
| IDs | integers; `client_id` (UUID) on writes the app may retry (updates, MOM items, check-ins, expenses) gives idempotency |
| Pagination | cursor: `?limit=30&after=<cursor>`; responses include `next_cursor` |
| Errors | `{"error": {"code": "marking_not_approved", "message": "…in the user's language…", "details": {…}}}` with 400/401/403/404/409/422/429 |
| Caching | `ETag` on GET; `GET /me/home` is never cached |
| Rate limits | OTP: 3 per 15 min per phone, 10 per hour per IP. Writes: 60/min per token. Uploads: 30/min per token. Every 429 includes `Retry-After` |
| Media | `POST /media` first (returns `media_id`, server compresses and thumbnails through queue_job), then reference ids in the write. Images ≤ 8 MB, video ≤ 60 s / 25 MB, audio ≤ 2 min |
| Versioning | path `/api/rvt/v1`; additive changes only; breaking changes go to `/api/rvt/v2` |
| Push payload | `{type, id, title, body, deep_link}` with deep links such as `rvt://visits/123`, `rvt://tasks/45`, `rvt://drawings/9`, `rvt://approvals/3`, `rvt://payments/7` |

### Common objects (abridged)
```jsonc
Space      { "id": 12, "name": "Kitchen", "type": {"code": "kitchen", "name": "રસોડું"}, "floor": 0,
             "documentation_pct": 100, "work_pct": 60, "concept_state": "approved", "photo": "…" }
ProjectCard{ "id": 7, "name": "Shah Residence", "site": {"id": 3, "summary": "3 BHK · 2 bath · 1,250 sq ft", "lat": 23.03, "lng": 72.51, "maps_url": "…"},
             "stage": "execution", "stage_label": "…", "health": "attention" /* office only */,
             "client_safe_status": "…", "next_client_action": {...} /* client */, "progress_pct": 54 }
WorkCard   { "id": 45, "project": {...}, "space": Space, "trade": {"code": "carpentry", "name": "સુથારી કામ"},
             "agency": {"id": 5, "name": "…"}, "state": "ready|in_progress|pending_verification|verified|rework|planned|billed",
             "is_ready": true, "blocked": false, "planned_start": "…", "planned_end": "…", "committed_end": "…",
             "actual_start": null, "progress_pct": 0, "last_update_at": null, "scope_lines": [...],
             "drawings": [{"id": 9, "sheet_no": "CD-03", "revision": 1, "url": "…"}], "proof_media": [...] }
Drawing    { "id": 9, "sheet_no": "EL-01", "title": "…", "type": {"code": "EL", "name": "…"}, "trade": {...},
             "spaces": [Space], "revision": 2, "state": "released", "due": "…", "released_at": "…", "file_url": "…",
             "needs_my_approval": false, "open_queries": 1 }
Query      { "id": 31, "drawing": {...}, "task": {...}, "space": Space, "question": "…", "media": [...], "priority": "blocking",
             "asked_by": {...}, "asked_at": "…", "answer": "…", "answered_at": null, "sla_deadline": "…", "state": "open" }
Visit      { "id": 123, "project": {...}, "site": {...}, "date": "2026-11-12", "window": ["10:00","13:00"], "purpose": "work",
             "tasks": [WorkCard], "state": "planned|confirmed|arrived|started|done|missed", "arrived_at": null }
Money      { "work_order_total": 450000, "billed": 180000, "paid": 150000, "pending_approval": 30000, "pending_payment": 30000,
             "verified_unbilled": 60000, "currency": "INR" }
Media      { "id": 5, "kind": "image|video|audio|file", "url": "…signed…", "thumb": "…", "w": 1600, "h": 1200, "duration_ms": 0 }
```

---

## 2. Auth and devices (`/auth`)
| Method | Path | Role | Purpose |
|---|---|---|---|
| POST | `/auth/invite/check` | none | `{code}` → `{valid, first_name, phone_masked, role, agency_name?, project_name?}` |
| POST | `/auth/otp/send` | none | `{purpose: invite|login, channel: whatsapp|sms, invite_code? | phone?}` → `{otp_id, sent_to, expires_in, resend_in}`; 503 `otp_undeliverable` offers the other channel |
| POST | `/auth/otp/verify` | none | `{otp_id, code, device{name, platform, app_version, push_token?}, lang}` → token pair + `user{role, lang, onboarding_steps}`; first invite sign-in creates or links the portal user and spends the code |
| POST | `/auth/pin` · `/auth/login` | user / none | set PIN (6 digits, trivial refused) · `{phone, pin, device}` → token pair; 5 wrong → `pin_locked` 15 min |
| POST | `/auth/staff-login` | none | office: `{login, password, totp?, device}` → token pair |
| POST | `/auth/refresh` · `/auth/logout` | refresh / user | rotate pair (reuse signs the device out) · sign this device out |
| GET · DELETE | `/auth/devices` · `/auth/devices/{id}` | user | list / sign out devices |
| GET | `/auth/ws-session` | user | short Odoo session cookie for `/websocket` only |

## 3. Me (`/me`)
| Method | Path | Role | Purpose |
|---|---|---|---|
| GET | `/me` | user | profile, role, lang, agency or client link, level, xp, reliability (agency owner), counters |
| PATCH | `/me` | user | `name, photo_media_id, lang, pin reset request` |
| GET | `/me/home` | user | **one call for the role home** (§13): agency person, agency owner, client, office, owner variants |
| GET | `/me/notifications` · POST `/me/notifications/read` | user | inbox with deep links · mark read |
| POST | `/me/push-token` | user | `{token, platform}` |
| GET | `/me/game` | agency_person, agency_owner, office | xp, level, next level, badges, streaks, reliability components (own only) |
| POST | `/me/export` · `/me/delete-request` | user | data rights |

## 4. Agencies and onboarding (`/agencies`)
| Method | Path | Role | Purpose |
|---|---|---|---|
| GET | `/agencies/me` | agency_owner | my agency: trades, persons, kyc_state, status, score |
| PATCH | `/agencies/me` | agency_owner | languages, service areas, UPI id |
| GET · POST | `/agencies/me/kyc` | agency_owner | kyc state and docs · `{pan_media_id, aadhaar_media_id, aadhaar_last4, gstin?, gst_media_id?, bank{name, account, ifsc}, cheque_media_id}`; consent text version recorded |
| GET · POST | `/agencies/me/persons` | agency_owner | list · add `{name, phone, lang}` → invite sent (WhatsApp/SMS) |
| PATCH · DELETE | `/agencies/me/persons/{id}` | agency_owner | edit · deactivate (signs their devices out) |
| POST | `/agencies/me/persons/{id}/reinvite` | agency_owner | resend code |
| GET | `/agencies` · `/agencies/{id}` | office | list with trades, score, status · detail incl. KYC (masked unless accounts/owner) |
| POST | `/agencies` | office | create agency + owner person → invite |
| POST | `/agencies/{id}/kyc/verify` · `/kyc/reject` | accounts, office_lead | `{note}` |
| POST | `/agencies/{id}/status` | office_lead | `{status: active|paused|blacklisted, reason}` |

## 5. Projects, sites, spaces (`/projects`, `/sites`, `/spaces`)
| Method | Path | Role | Purpose |
|---|---|---|---|
| GET | `/projects?state=&mine=` | user | cards scoped by role (agency: projects with my work orders; client: mine; office: all) |
| GET | `/projects/{id}` | user | detail by role: stages and gates, spaces with progress, team (office), partners (client sees names only if Q G4), money (owner), health (office) |
| GET | `/projects/{id}/timeline` | client, office | gates reached with dates, upcoming, photo strip |
| GET | `/projects/{id}/gantt?view=plan|committed|actual` | office, client (if allowed) | packages grouped by space or trade with dates and dependencies |
| PATCH | `/projects/{id}/client-status` | supervisor | `{client_safe_status, next_client_action}` (the only client-facing free text) |
| GET | `/sites/{id}` | user | site detail with checklist, spaces, map |
| PATCH | `/sites/{id}` | supervisor, designer | north, vastu (principal only for vastu), access notes |
| GET · POST | `/sites/{id}/spaces` | user / supervisor | list · add `{type_id, name?, floor}` → spec fields from template |
| GET · PATCH | `/spaces/{id}` | user / supervisor | detail · dims, heights, spec values, notes |
| POST · DELETE | `/spaces/{id}/openings` · `/openings/{id}` | supervisor | doors and windows |
| POST | `/spaces/{id}/media` | supervisor, agency_person | `{media_ids, kind: measurement|existing|progress, client_visible?}` |
| GET | `/sites/{id}/checklist` · POST `/sites/{id}/checklist/{key}/waive` | supervisor / office_lead | documentation checklist · waive with reason |
| GET | `/space-types` · `/spec-templates/{id}` | user | master data in the user's language |

## 6. Leads (`/leads`) — office
| Method | Path | Role | Purpose |
|---|---|---|---|
| GET · POST | `/leads` | office | pipeline · create `{name, phone, property_type, size, location, target_date, budget_band, scope, referral_partner_id?, notes, voice_media_id?}` |
| GET · PATCH | `/leads/{id}` | office | detail · brief fields, stage, next action |
| POST | `/leads/{id}/site-visit` | office | `{date, window, person_id}` → creates the site (if none) and a measurement visit |
| POST | `/leads/{id}/quotation` | office_lead, owner | `{fee_model, area?, rate?, lumpsum?, schedule[{milestone, pct}]}` → sale order + PDF |
| POST | `/leads/{id}/won` · `/lost` | office_lead | `{}` → project + site + client invite · `{reason}` |

## 7. Design: brief, layouts, drawings, approvals, queries (`/design`)
| Method | Path | Role | Purpose |
|---|---|---|---|
| GET · PATCH | `/projects/{id}/brief` · `/spaces/{id}/brief` | user / designer | brief text · edit |
| POST | `/projects/{id}/brief/confirm` | client | `{note?}` → gate |
| GET · POST | `/projects/{id}/layouts` | user / designer | options · add `{name, media_id}` |
| POST | `/layouts/{id}/choose` | client | choose (others dropped) |
| GET | `/projects/{id}/drawings?trade=&state=&space=&mine=` | user | register scoped by role (agency: released, own trade; client: client_visible) |
| POST | `/projects/{id}/drawings` | designer | `{type_id, space_ids, title, due, assignee_id}` |
| GET · PATCH | `/drawings/{id}` | user / designer | detail with revisions and queries · metadata |
| POST | `/drawings/{id}/file` | designer | multipart PDF (and optional DWG) for the current revision |
| POST | `/drawings/{id}/check` · `/release` | designer, office_lead | → internal_check · `{to: client|agency|both, note}` → released + notifications |
| POST | `/drawings/{id}/approve` · `/request-changes` | client | one tap · `{note}` → changes_requested, new revision created |
| POST | `/spaces/{id}/concept/approve` · `/request-changes` | client | per-room concept gate |
| GET | `/projects/{id}/approvals/pending` | client | everything waiting on the client, one list |
| GET · POST | `/queries?project=&state=&mine=` · `/queries` | user | list scoped · `{project_id, drawing_id?, task_id?, space_id?, question, media_ids, priority}` |
| POST | `/queries/{id}/answer` · `/close` · `/reopen` | designer, supervisor / asker | `{answer, media_ids?}` · `{thumbs?}` · `{note}` |
| GET | `/design/boards/drawings-due` · `/design/boards/queries-open` | office | the two office boards (due, overdue, unassigned; queries by SLA state) |

## 8. Trade plan, quotes, work orders (`/trade-plan`, `/quotes`, `/work-orders`)
| Method | Path | Role | Purpose |
|---|---|---|---|
| GET · PATCH | `/projects/{id}/trade-plan` · `/trade-plan/{id}` | office / supervisor | rows · `{required, agency_id?, decision_due, state}` |
| POST | `/trade-plan/{id}/quote-request` | supervisor | `{agency_ids, due, scope, drawing_ids, space_ids}` → agencies notified |
| GET | `/quote-requests?mine=` · `/quote-requests/{id}` | agency_owner, office | my requests · detail with scope and drawings |
| POST | `/quote-requests/{id}/quote` | agency_owner, office (on behalf) | `{lines[{space_id, description, unit, qty, rate, material_included}], validity, notes, attachment_media_id?}` |
| GET | `/quote-requests/{id}/compare` | office | side-by-side totals and per-space lines |
| POST | `/quotes/{id}/accept` | office_lead, owner | `{paid_by: company|client, advance_pct, retention_pct, retention_days, committed_end}` → work order + packages |
| GET | `/work-orders?mine=` · `/work-orders/{id}` | agency_owner, office, owner | list · detail with lines, packages, money |

## 9. Work packages and execution (`/tasks`)
| Method | Path | Role | Purpose |
|---|---|---|---|
| GET | `/tasks?project=&space=&trade=&agency=&state=&date=&mine=` | user | scoped list; `mine` = my agency (owner) or my scheduled sites today (person) |
| GET | `/tasks/{id}` | user | WorkCard with scope lines, drawings, updates, proof, dependencies |
| POST | `/tasks/{id}/start` | agency_person, agency_owner | → in_progress (409 `not_ready` with reasons: marking, drawing, dependency) |
| POST | `/tasks/{id}/updates` | agency_person, agency_owner | `{client_id, pct, note, media_ids, material_needed?, blocked?, blocked_reason?, lat?, lng?}` |
| POST | `/tasks/{id}/done` | agency_person, agency_owner | `{client_id, note, media_ids (≥1), scope_done[{line_id, qty}]}` → pending_verification (422 `media_required`) |
| POST | `/tasks/{id}/verify` | supervisor | `{result: pass|rework, note, verified_qty[{line_id, qty}], client_visible_media_ids}` |
| POST | `/tasks/{id}/commit` | supervisor, agency_owner | `{committed_end, reason}` (reason required after the first) |
| PATCH | `/tasks/{id}/plan` | supervisor | planned dates, dependencies, assignee agency, needs_marking |
| POST | `/tasks/{id}/marking/photos` · `/marking/approve` · `/marking/reject` | agency_person / supervisor | marking gate |
| POST | `/tasks/{id}/unblock` | supervisor | `{note}` |
| GET · POST | `/projects/{id}/snags` · `/snags/{id}/fix` · `/snags/{id}/verify` | office, agency / agency / supervisor | snag list |
| GET | `/execution/boards/verifications` · `/execution/boards/blocked` · `/execution/boards/silent` | office | pending verifications · blocked packages · silent > N days |

## 10. Visits and MOM (`/visits`, `/moms`)
| Method | Path | Role | Purpose |
|---|---|---|---|
| GET | `/visits?from=&to=&person=&project=&mine=` | user | calendar scoped (person: own; owner: agency; office: all); includes conflicts |
| POST | `/visits` | supervisor, agency_owner (own persons) | `{project_id, person_partner_id, date, window_start, window_end, purpose, task_ids}` → reminders scheduled |
| PATCH · DELETE | `/visits/{id}` | creator, supervisor | reschedule `{date, window, reason}` · cancel |
| POST | `/visits/{id}/confirm` · `/arrive` · `/start` · `/end` | agency_person, staff | `{}` · `{lat?, lng?, client_id}` · `{}` · `{}` |
| POST | `/visits/{id}/missed` | supervisor, person | `{reason}` |
| GET | `/visits/today/map` | office | pins of today's visits with states |
| GET · POST | `/moms?project=` · `/moms` | office, client (shared) / principal, supervisor | list · `{project_id, visit_id?, attendees}` |
| POST | `/moms/{id}/items` | principal, supervisor | `{client_id, space_id?, text?, audio_media_id?, transcript_lang?}` → item (server stores; transcript is from the phone) |
| PATCH | `/moms/{id}/items/{item_id}` | principal, supervisor | `{space_id, text, kind, audience, assignee_partner_id, agency_id, due}` |
| POST | `/moms/{id}/items/{item_id}/convert` | supervisor | `{to: task|query|drawing_change|decision|client_action, payload}` → linked record |
| POST | `/moms/{id}/share` | supervisor | `{audiences: [client, agency, internal]}` → PDF per audience + notifications |
| GET | `/moms/{id}` | user | items filtered by audience |

## 11. Money (`/payments`, `/expenses`, `/invoices`)
| Method | Path | Role | Purpose |
|---|---|---|---|
| GET | `/money/agency` | agency_owner | Money object per project and overall; recent requests |
| GET · POST | `/payment-requests?mine=` · `/payment-requests` | agency_owner, office | list · `{work_order_id, type, lines[{task_id, qty_claimed}], note, media_ids}` (lines prefilled from verified_qty by `GET /work-orders/{id}/billable`) |
| GET | `/work-orders/{id}/billable` | agency_owner, office | verified, unbilled quantities and amounts per package |
| POST | `/payment-requests/{id}/submit` · `/approve` · `/return` · `/reject` | agency_owner / accounts, office_lead / same / same | `{}` · `{amount_approved, lines[{line_id, qty_approved}], note}` · `{note}` · `{note}` |
| POST | `/payment-requests/{id}/mark-paid-by-client` | office | `{proof_media_id, date, ref}` |
| GET · POST | `/expenses?project=&payer=` · `/expenses` | office, agency_owner (own) | list · `{client_id, project_id, space_id?, task_id?, payer, amount, gst_amount?, category, receipt_media_id, note, recoverable}` |
| POST | `/expenses/{id}/approve` · `/reject` · `/settle` | accounts, office_lead | `{}` · `{note}` · `{payment_ref}` |
| GET | `/invoices?mine=` · `/invoices/{id}/pdf` | client, office | client invoices and receipts |
| GET | `/projects/{id}/money` | owner | the owner money view (system_design.md §3.7) |
| GET | `/money/overview` | owner | all active projects: contract, received, pending, recoverable, margin |

## 12. Engagement (`/game`) and office boards (`/office`)
| Method | Path | Role | Purpose |
|---|---|---|---|
| GET | `/game/levels` · `/game/badges` | user | master data in language |
| GET | `/game/agency/{id}` | office | an agency's score components, trend, badges |
| GET | `/office/home` | office | boards: drawings due, queries past SLA, trades undecided, verifications waiting, payment requests waiting, visits today (with unarrived), silent packages, approvals waiting on clients, project health list |
| GET | `/office/recognition?month=` | office_lead, owner | monthly top performers (agencies, persons, staff) for recognition |
| POST | `/office/recognition/{partner_id}/feature` | owner | mark "partner of the month" → notification and badge |

## 13. `GET /me/home` payloads
| Role | Content |
|---|---|
| agency_person | today's visits (site, time, map, tasks), ready-to-start packages, in-progress packages needing an update, open queries I asked, my level and streak, unread notifications |
| agency_owner | persons' visits today with states, packages by state across projects, quote requests due, payment summary (verified unbilled, pending approval, pending payment, paid this month), KYC state, reliability score with hint |
| client | project cards with stage, client_safe_status, next action; approvals waiting; this week's photo strip; invoices due; MOM items for me |
| office | the boards of `/office/home` reduced to counts with deep links, plus my own items (drawings assigned, queries assigned, visits, verifications) |
| owner | money overview, project health list, approvals needed from the owner (quotes to accept, agencies to activate), recognition pending |

## 14. Media (`/media`)
| Method | Path | Role | Purpose |
|---|---|---|---|
| POST | `/media` | user | multipart `file` + `{kind, client_id}` → `Media` (processing async; `thumb` arrives via refetch) |
| GET | `/media/{id}` | user | signed URL refresh (access checked against the owning record) |

## 15. Webhooks and public (`/webhooks`, `/public`)
| Method | Path | Auth | Purpose |
|---|---|---|---|
| POST | `/webhooks/whatsapp` | Meta signature | handled by Odoo `whatsapp` module; mirrored here only for delivery states if needed |
| POST | `/webhooks/sms` | HMAC | delivery reports from the SMS gateway |
| GET | `/public/verify/{code}` | none | verifies a shared MOM or handover document code |
| GET | `/health` | none | `{status, version}` |

## 16. Error codes (selection)
`invalid_code` · `otp_expired` · `otp_undeliverable` · `pin_locked` · `token_reused` · `kyc_required` · `not_ready` (details: `missing: [marking, drawing:EL-01, dependency:45]`) · `media_required` · `already_done` · `verification_pending` · `committed_reason_required` · `not_billable` · `visit_conflict` · `quiet_hours` (for manual sends) · `client_safe_text_required` · `forbidden_scope`
