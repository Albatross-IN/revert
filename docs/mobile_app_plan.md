# Revert: mobile app plan (Android + iOS)

Status: plan v0.1 · 2026-10-31 · nothing built · depends on the questionnaire answers marked ★
Repos: backend `Albatross-IN/revert`, branch `20.0` (existing, decided 2026-11-17) · app `AlbatrossHub/revert_fe` (Flutter)
Related: [architecture.md](architecture.md) · [system_design.md](system_design.md) · [api_design.md](api_design.md) · [design.md](design.md)

---

## 1. One app, four homes

| Home | Who | Leads with | Language |
|---|---|---|---|
| **Site** (agency person) | karigar, mistri, helper lead | Today: where, when, what; then start / update / done with camera; questions; my level | gu, hi |
| **Agency** (agency owner) | contractor | People on sites today; work by state; quotes due; money (verified, pending, paid); KYC; score | gu, hi, en |
| **Home** (client) | the client and family / committee | Progress per room, what is next, decisions waiting for me, this week's photos, invoices | en, gu, hi |
| **Office** (staff) and **Owner** | supervisor, designer, accounts, principal, owner | What waits on me today: visits, verifications, drawings due, queries, approvals; owner adds money and health | en |

A person with several roles (owner who is also principal; office staff who is also a client) switches home from the profile. The role comes from the server; the app never decides permissions.

## 2. Requirements as understood (from the brief)

### 2.1 Agency person
- Sees the number of sites assigned, on which date, at which location; opens the map.
- Gets reminders of the next visit; confirms arrival; is reminded to mark "started" if forgotten; is reminded to update at the end of the day.
- Sees assigned, executed and pending work, and payments against it.
- Asks questions with photos against a drawing or a work package; receives answers.
- Marks work done with photo or video; sees verification result.
- Works in Hindi or Gujarati, on a low-end Android, often in sunlight, sometimes offline.

### 2.2 Agency owner
- Onboards with minimal steps (KYC once), invites their people.
- Quotes on requests; accepts work orders; sees the committed dates.
- Requests payments against verified work; adds expenses; sees paid and pending.

### 2.3 Client
- Confirms the brief, chooses a layout, approves concepts per room and drawings.
- Follows execution positively: room progress, photos, what happens next, revised plans with reasons.
- Sees invoices and pays (payment link in v1; in-app payment later).
- Reads MOM items that concern them.

### 2.4 Office and principal
- Documents a site on the phone (spaces, specs, photos, video, Vastu).
- Schedules visits; sees who has not arrived; verifies work from photos; approves marking.
- Runs MOM with voice, sticky space and later classification.
- Releases drawings and answers queries from the phone when needed; sees the pending boards.
- Owner: money per project and overall; project health; recognition.

## 3. Decisions (recommended)

| # | Decision | Recommendation | Why |
|---|---|---|---|
| D1 | Native vs PWA | **Flutter, native** | camera, offline queue, push, speech recognition and background upload behave on ₹8k Android phones only natively |
| D2 | One or many apps | **One app, role homes** | one store listing, one codebase, shared components; roles from the server |
| D3 | Stack | Riverpod, go_router, dio, flutter_secure_storage, drift (offline cache and queue), image_picker + flutter_image_compress, video_compress, speech_to_text, geolocator, firebase_messaging, flutter_localizations + ARB (en, hi, gu), google_fonts (Noto Sans Gujarati, Noto Sans Devanagari, Inter), pdfrx, signature, mobile_scanner (optional) | the SFJ and Bhuj Runners app stack, plus offline, media and speech |
| D4 | Auth | phone + OTP (WhatsApp, SMS fallback) → PIN + biometrics for agency and client; Odoo credentials for office | matches system_design §6 |
| D5 | Offline | today's visits, ready/in-progress packages, their drawings (PDF cached), queued updates and MOM items with media; sync on connectivity with idempotent `client_id` | sites have poor network; the app must never lose a photo |
| D6 | Media | compress on the phone (≤ 1600 px, ≤ 400 KB; video ≤ 60 s), upload in the background with retry; thumbnails from the server | data cost and 3G |
| D7 | Speech | `speech_to_text` with gu-IN / hi-IN / en-IN chosen by a language chip before holding the mic; audio kept; server fallback later | free, offline on many devices, private |
| D8 | Maps | `url_launcher` to Google Maps for navigation; `flutter_map` or google_maps_flutter for the office visit map | navigation belongs to the maps app |
| D9 | Push | Firebase (FCM, APNs through Firebase), deep links `rvt://…` | proven in bhujrnr_fe |
| D10 | Payments by client | payment link (UPI / Razorpay page) from the invoice in v1 | in-app payment is a later phase and needs a gateway decision |
| D11 | Look | design.md tokens: warm paper ground, ink, one terracotta accent, large type, 48 px targets, high contrast for sunlight; glass only on photo headers | professional, readable on site |
| D12 | Store accounts | Albatross developer accounts first; transfer to Revert's accounts when they exist | avoids waiting on the firm's accounts |

## 4. Screens

### 4.1 Shared
Splash (brand) · Language picker · Invite code · OTP · PIN set / unlock (biometric) · Profile · Notifications inbox · Media viewer (photo, video, PDF) · Query thread (question, photos, answer, follow-up) · Space picker (sticky) · Offline banner and sync status.

### 4.2 Site home (agency person)
1. **Today**: a card per visit: site name, area, time window, "Open map", tasks for this visit; big buttons **I will come** → **I have arrived** → **Start** → **Update** → **Done**.
2. **My work**: chips Ready · In progress · Waiting check · Rework · Done; cards with space, trade, committed date, drawings.
3. **Work detail**: scope lines, drawings (open PDF), what blocks it (in words: "marking not approved yet"), updates timeline, **Update** (percent slider, note, camera), **Done** (camera required, scope quantities), **Ask** (question with photo), **Need material** / **Blocked**.
4. **Questions**: mine, with answered / waiting.
5. **Me**: level, points this month, badges, streak, language, devices.

### 4.3 Agency home (owner)
1. **Today**: people and their sites with state dots (not confirmed, confirmed, arrived, started, done); tap to call or re-assign.
2. **Work**: all packages by project and state; committed dates; "Needs my attention" (rework, blocked, silent).
3. **Quotes**: requests due with scope and drawings; quote editor (lines per space, unit, qty, rate, material included).
4. **Money**: per project: work order, verified, billed, paid, pending; **Request payment** (type, prefilled verified quantities, photos) ; requests by state; paid with date and reference.
5. **People**: list, add person (name, phone, language) → invite; deactivate.
6. **Agency**: KYC steps, status, reliability score with "what raises it", badges.

### 4.4 Client home
1. **Projects** (usually one): hero photo, stage stepper, `client_safe_status`, **Next for you** (approve brief / choose layout / approve kitchen concept / approve EL-01 / pay invoice).
2. **Rooms**: cards with progress ring, concept thumbnail, state; room detail: concept, drawings shared with me, this room's photos, "what happens next here".
3. **Approvals**: one list; detail with preview, **Looks good** / **I'd like changes** (note).
4. **Updates**: weekly photo strip, gates reached, MOM items for me.
5. **Payments**: schedule, invoices, receipts, pay link.
6. **Help**: message the office (lands as a query of kind client), call.

### 4.5 Office home (staff, principal)
1. **Today**: my visits, visits not arrived (call / WhatsApp), verifications waiting (with photos, pass / rework), approvals from clients pending.
2. **Boards**: drawings due and overdue; queries past SLA; trades undecided; payment requests; silent packages; blocked.
3. **Project**: stages, spaces, Gantt (read on phone), trade plan, drawings, queries, visits, MOM list, health reasons.
4. **Site documentation**: add space → spec form from the template (numbers, selects, photo fields), openings, photos, video; checklist ring; north compass input; Vastu (principal).
5. **MOM**: start from visit or ad hoc; big mic button with language chips; sticky space header with **Change location**; items list; later: classify, assign, due, audience; share.
6. **Schedule**: calendar per agency person; create visit; conflicts shown.
7. **Drawings**: release from the phone (pick to, note); answer a query with a photo.

### 4.6 Owner (extra tabs)
1. **Money**: overview across projects; project money view; drill to agency and expense lines.
2. **Health**: projects by health with reasons; tap to act.
3. **Approvals**: quotes to accept, agencies to activate, expenses over a limit.
4. **Recognition**: this month's top agencies, persons and staff; feature one.

## 5. Flutter project structure (proposed)
```
lib/
  app/           router (go_router), theme, l10n (ARB en/hi/gu), role switch
  core/          api client (dio, JWT refresh, ETag), offline (drift tables + outbox), media (compress, upload queue),
                 speech, location, push, formatting (₹, dates, Indian numbering)
  features/
    auth/        invite, otp, pin, biometric
    home/        role homes
    visits/      today, visit detail, arrival
    work/        packages, updates, done, marking
    queries/
    design/      brief, layouts, drawings, approvals
    site/        spaces, spec forms, openings, media, checklist
    mom/
    money/       agency money, payment requests, expenses, client invoices, owner money
    agency/      kyc, people
    game/
    office/      boards, schedule, verifications
  widgets/       progress ring, stage stepper, work card, big action button, media grid, language chips, space header
```

## 6. Phases (sequential; each starts when the previous one's exit criteria are met)

| # | Phase | Scope | Exit criteria | Effort |
|---|---|---|---|---|
| **P0** | Design sign-off | questionnaire answered, screen canvas (role homes, work detail, MOM, client approvals), tokens, tone copy in en/hi/gu | owner approves screens and API; ★ questions closed | 1–2 wk |
| **P1** | Foundations | vendor `fastapi`, `endpoint_route_handler`, `identity*`, glass theme; `rvt_base`, `rvt_api` skeleton (JWT, errors, roles, Swagger); `rvt_notify` skeleton (push, WhatsApp via Odoo module, SMS, templates); Firebase; Flutter scaffold (stack, theme, l10n, offline core, media core, speech spike in gu/hi) | `/health` live; a staff login works; a test push and WhatsApp arrive; gu/hi speech spike proves on-device recognition on two phones | 2 wk |
| **P2** | Site and spaces | `rvt_site`, `rvt_crm`; office app: leads, site documentation (spaces, specs from template, openings, photos, video, checklist, north, Vastu); lead → quotation → won → project | a real site is documented on the phone end to end; the project is created from the won lead | 2 wk |
| **P3** | Agencies and onboarding | `rvt_agency`: agencies, persons, invites, OTP login, PIN, KYC upload and verification, trade plan, quote requests and quotes, work orders; agency home (people, KYC, quotes) | a real agency owner onboards, invites two people, submits a quote; office accepts into a work order | 2 wk |
| **P4** | Design and approvals | `rvt_design`: brief, layouts, drawings, releases, approvals, queries, boards; client home (projects, rooms, approvals, updates); designer phone flows | client approves a brief, layout, a room concept and a drawing in the app; a query from an agency is answered within SLA with alerts | 2–3 wk |
| **P5** | Execution and visits | `rvt_execution`, `rvt_visit`: packages from work orders, sequence template, marking gate, start/update/done with media, verification, Gantt; visits, reminders, arrival, nudges; site home for agency persons; office verifications and schedule; offline queue | pilot project runs two trades through marking → execution → verification with reminders; Gantt shows plan vs committed vs actual | 3 wk |
| **P6** | MOM and voice | `rvt_mom`: capture with sticky space, voice in gu/hi/en, classify, convert, share per audience | a principal runs a site MOM by voice, items become tasks and queries, client and agencies receive their parts | 2 wk |
| **P7** | Money | `rvt_finance`: payment requests, approval → vendor bill (TDS), paid by company / client, expenses with payer and recoverability, client milestone invoices, owner money view and overview | an RA bill flows from the agency's request to a paid bill; the owner reads the project money view and it matches accounts | 2–3 wk |
| **P8** | Engagement and boards | `rvt_game`, `rvt_office`: XP, levels, badges, reliability, project health, recognition; office back-office home; weekly digests | scores computed from real pilot data; owner edits a rule; health reasons match reality | 2 wk |
| **P9** | Store release and rollout | listings, privacy policy, data-safety forms, screenshots, review fixes; onboarding of all panel agencies; running projects added | app live on Play Store and App Store; three projects running on the system | 1–2 wk |

Total: about 20–23 weeks of build after design sign-off, pilot from the end of P5. P4 and P5 can overlap once the API contract is fixed.

## 7. Risks
| Risk | Mitigation |
|---|---|
| Agency persons share one phone or change numbers | Login is per person by phone; the agency owner can re-invite; a device can be signed out remotely |
| Gujarati speech recognition quality | Spike in P1 on real phones; language chips; audio always kept so the office can correct text; server fallback later |
| Photo upload failures on site | Outbox with retry and visible sync state; photos stored locally until acknowledged |
| Too many notifications → ignored | One reminder per event, quiet hours, digests for non-urgent items; counts tuned after the pilot |
| Client approvals stall | Gentle reminders, office nudge at 5 days, approvals in one list |
| iOS build and Apple account | Cloud macOS CI; Albatross account first |
| WhatsApp template approvals take days | Submit templates in P1; use push and SMS until approved |

## 8. Questions for this plan
See questionnaire.md: ★ A1, A2 (money flows in the app), ★ E1, E2 (agency model), ★ F1 (marking), G4 (what the client sees), ★ J2 (WhatsApp channel), J1 (devices), I2 (score visibility), ★ K4 (pilot).
