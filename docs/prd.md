# Revert — Product Requirements (PRD)

Status: draft v0.1 · 2026-10-31 · for discussion with the principal consultant before anything is built
Companions: [questionnaire.md](questionnaire.md) (what we must still ask) · [architecture.md](architecture.md) · [system_design.md](system_design.md) · [design.md](design.md) · [mobile_app_plan.md](mobile_app_plan.md) · [api_design.md](api_design.md) · [rules.md](rules.md) · [memory.md](memory.md) · [tasks.md](tasks.md)

> **2026-11-17:** after client feedback the first release is much smaller than the scope below. See [phase1_adoption.md](phase1_adoption.md). §7.4–§7.8 here are now the long-term backlog; agency-started payment requests (§7.7) and the wide client view are withdrawn.

Where this document says "Revert" it means Revert Architects, Ahmedabad. The brief arrived unorganised; §3 is the brief re-ordered into a lifecycle, §12 lists what the brief does not say, and the questionnaire turns those gaps into questions.

---

## 1. The business in one paragraph

Revert is an architecture and interior design consultancy in Ahmedabad. It takes a project from the first conversation with a prospect, through site documentation, client brief, layout, concept and working drawings, to agency (vendor) finalisation, site marking, execution and handover. Its clients are corporate offices, residences, hospitals, design studios and manufacturing units. Execution is done by **third-party agencies** (civil, electrician, plumber, POP, painter, carpenter, window fabricator, stone mason) who are coordinated by Revert's office team and the principal consultant. The owner wants **Odoo 20 Enterprise as the engine**, and a **mobile-first, action-driven experience** for three audiences who today live on phone calls and WhatsApp: the office team, the agencies and the client. Instead of static dashboards, every stakeholder opens the app, sees what is expected of them, acts, and the ERP does the bookkeeping. Engagement is kept up with **professional gamification**: visible progress, reliability, recognition and payment transparency.

## 2. How interior and architecture projects run in India (reference cycle)

The brief assumes this cycle; the questionnaire checks each assumption. Terms in brackets are the local words heard on Gujarat sites.

| # | Stage | What usually happens | Common Indian specifics |
|---|---|---|---|
| 1 | Enquiry / lead | Walk-in, referral from an old client or a builder, Instagram, Justdial, Houzz. First call: property type and size (2/3/4 BHK, office floor plate in sq ft, hospital beds), location, possession date, budget band, scope wanted | Referral leads convert far better and are treated as serious. Dates matter: possession, *muhurat*, *griha pravesh*, Diwali deadlines |
| 2 | First meeting, fee proposal | Site visit or office meeting; scope decided: **design only**, **design + supervision (PMC)** or **turnkey** (Revert executes and bills everything) | Fee models: ₹ per sq ft for interiors, % of project cost for architecture, lump sum per stage, or turnkey margin. Advance (retainer) on signing |
| 3 | Agreement + advance | Letter of engagement, stage-wise payment schedule | GST 18% on design fees (SAC 9983); Council of Architecture conditions of engagement are the usual reference for architects |
| 4 | Site documentation | Measured survey: room-wise dimensions, slab and clear (beam-bottom) heights, beam and column grid, door and window schedule, existing electrical and plumbing points, north, photos and video | Done by a junior with a laser meter and a template (Pratik's). Vastu reading by the principal consultant |
| 5 | Client brief | Family or business needs, lifestyle, storage, style references, must-haves, budget per area | Often written by the office after the meeting, not by the client |
| 6 | Layout | Furniture ("object") layout options and zoning; client picks one | Usually 2–3 options, revisions on the chosen one |
| 7 | Concept | Room-wise concept: mood boards, materials, 3D views or renders | Client approval ("OK") per room is the gate to drawings |
| 8 | Working drawings (GFC) | Civil and demolition, furniture layout, false-ceiling, electrical points and switchboards, plumbing, flooring pattern, wall elevations, carpentry details, door/window schedule, lighting, HVAC | Revisions R0, R1, R2…; each trade needs its own sheet set; a pending electrical drawing blocks conduiting |
| 9 | Estimate, quotations, agency finalisation | BOQ by trade; quotations from 2–3 agencies on Revert's format; comparison; negotiation; work order | Agencies quote per sq ft (carpentry, painting, POP), per point (electrical), per running foot (stone platform), lump sum (civil). Many are unregistered or under GST composition; TDS 194C applies when Revert pays them |
| 10 | Site marking and approval | Carpenter marks the layout on floor and walls per drawing; office checks on site or from photos and approves | The last cheap moment to catch a layout error |
| 11 | Execution | Trade sequence with dependencies: civil/demolition → plumbing + electrical conduiting → POP/false ceiling → carpentry framework → flooring/stone → carpentry finishing → primer → electrical fittings → final paint → polish → loose furniture and soft furnishings | Agency coordination is the real job: the electrician must finish before the ceiling closes; the painter waits for the carpenter. Daily site WhatsApp groups, photos, "material not reached" calls |
| 12 | Bills and payments | Agency RA (running account) bills on measured quantities; advance %, retention; client pays agencies directly, or Revert pays and recovers | Petty site expenses (hardware, cartage) are paid by whoever is on site and reconciled later, badly |
| 13 | Handover | Snag list, deep cleaning, final bills, warranty cards, as-built drawings, handover photos | *Griha pravesh* or office opening date is the real deadline |
| 14 | After handover | Defect liability period, referrals | The referral loop feeds stage 1 |

Trade names from the brief, mapped: **civil** (mason, demolition, masonry), **electrician**, **plumber**, **POP** (plaster-of-Paris / gypsum false ceiling), **color** (painter, *colour kaam*), **carpenter**, **window** (aluminium / UPVC section fabricator), **Salat work** (*salaat*, Gujarati for stone mason: marble, granite, kitchen platform, stone cladding; to confirm, Q E1). Agencies not in the brief but usual on such sites: glass and mirror, fabrication (MS/SS), flooring and tiles (if not the mason), modular kitchen vendor, soft furnishings, HVAC, fire and low-voltage (hospitals, offices), loose furniture vendors.

## 3. The brief, processed

The owner's brief, re-ordered into the lifecycle above. "Said" is the brief; "Read as" is the requirement we take from it; "Gap" points into the questionnaire.

| Lifecycle | Said | Read as | Gap |
|---|---|---|---|
| Lead | Prospect gives an initial brief about their vision; documented against the lead. Referral of old client = higher seriousness | CRM lead with a structured **vision brief** (type, size, location, dates, budget band, scope, references) plus free notes and voice notes. Referral source and referring client are fields; referral leads get a higher priority and a tighter follow-up SLA | A1–A4, B1–B5 |
| Qualification → site documentation | Measurement room-wise (ceiling height, clear height, beam grid, doors, windows), photography, videography, site analysis; "get template from Pratik" | A **site** (property) with **spaces** (rooms) created on the phone; each space has a spec sheet from a template, photos and video; a documentation checklist with completion % | C1–C6 |
| Site analysis | North, Vastu paragraph by the principal consultant | Site-level fields: north angle, Vastu notes (rich text, author, date), constraints | C5 |
| Client brief | From the client or written by an internal person | Brief per project and per space; who wrote it; client can read and confirm it in the app | D1 |
| Layout → concept → OK → working drawings, revisions | Layout, room-wise concept, client okays, team prepares working drawings, revisions | **Drawing register** with types, sheets, revisions, release to client/agency, client approval per drawing (and per space concept), queries against a drawing | D2–D6 |
| Agency finalisation | Agencies known before working drawings; may change later; undecided agency must be highlighted to internal, client and owner | **Trade plan** per project: which trades are needed, which agency is finalised, by when; an undecided trade past its date becomes a visible alert for office, client (softened) and owner | E1–E7 |
| Quotation | "Get quotation format" | Quotation request → agency quote lines (per space and item, unit, rate) → comparison → work order. The format is a data model, not a document | E4 |
| Property spec | At measurement "add room, add kitchen… add specifications"; project shows "3 BHK" and each entity goes through agency work | **Space** is the backbone: every drawing, task, MOM point, photo and payment line can point at a space. Project summary = site type + space count by type | C2 |
| Execution visibility | Gantt of plan vs actual; real-time tracking of agency work | **Work packages** = space × trade (× agency) with planned and actual dates, dependencies, Gantt; status from agency updates with photo or video | F1–F6 |
| Agency app | Hindi and Gujarati; ask questions in chatter with photos; share updates; gamification: assigned, executed, pending, payment; request payment, add expenses | Agency app in **gu / hi / en**, role-based home: my sites today, my work, my questions, my money. Questions are threaded on the work package or drawing. XP, reliability score and badges for verified actions | I1–I5, J1–J3 |
| Reminders and scheduling | Office sets reminders; automated next-visit reminders; confirm arrival; "did you start?"; number of sites per date and location; office schedules agencies; more than one person per agency; KYC on onboarding; minimal onboarding | **Visit schedule** per agency person with date, site, time window; arrival confirmation (one tap, GPS optional); start/stop nudges; KYC with Aadhaar/PAN/bank once per agency, persons added by the agency owner; invite by WhatsApp with a code | E5–E7, F3 |
| Pending tasks and proof | Keep reminding; "work is done" documented by photo or video | Done needs **proof media**; office **verifies**; verified work is what earns XP and unlocks the bill | F4, I2 |
| Commitments | Only the committed or mutually decided end date matters | Each work package has a **committed end date** agreed with the agency; plan vs committed vs actual shown; reschedules are recorded with a reason | F2 |
| Site visit and MOM | Principal consultant and staff visit; MOM in the app; quick agenda/TODOs, segregate later per space; "change location" asks for the next space; voice-to-text gu/hi/en; visits pre-scheduled | **Site visit** (scheduled) → **MOM** with items captured fast (text or voice), each item tagged to a space (current space sticky), later converted to tasks, queries or drawing changes, and shared | G1–G3, J3 |
| Internal team | Follow up agencies; clear doubts on drawings; release drawings; pending drawings highlighted; queries dashboard; per-project gamified dashboard: stuck / on track / off plan | Office home: drawings due, queries open past SLA, agencies to finalise, visits today, verifications waiting, payment requests waiting. Project health indicators | H1–H4 |
| Client journey | Always positive even if the backend is not; design language accordingly | Client app shows progress, what is next, decisions waiting on them, photos and payments; delays are shown as **revised plan with reasons**, never red flags (see design.md §2) | G4–G6 |
| Owner finance | Agency finalised price, paid or not, paid by whom, total expenses, company-paid expenses to recover from client, probable invoice value, compilation of expenses | **Project money view**, owner-only: contract value, invoiced, received; per agency: work order value, billed, paid, paid by company or client; expenses by payer and recoverability; margin | A5–A9 |
| Site marking | Carpenter marks, office approves, before execution | A **gate** between drawings and execution: marking task (carpenter) → photos → office approval → execution unlocked | F1 |

## 4. Who uses it

| Persona | What they do | Device | Language | Odoo user type |
|---|---|---|---|---|
| **Owner / principal design consultant** | Approves concept directions, signs off agencies and payments, visits sites, writes Vastu and MOM points, reads money and health | Phone, tablet, desktop | en | Internal |
| **Office staff: design (draftsman, 3D)** | Drawings, revisions, releases, answers drawing queries | Desktop, phone for queries | en | Internal |
| **Office staff: site supervisor / coordinator** | Schedules agencies, verifies work and marking, runs MOM, chases drawings and agencies | Phone first | en, gu, hi | Internal |
| **Office staff: accounts** | Client invoices, agency bills, payments, expenses, GST and TDS | Desktop | en | Internal |
| **Agency owner** (contractor) | Accepts work, quotes, assigns people, sees money, requests payment | Phone | gu, hi | Portal |
| **Agency person** (karigar, mistri) | Sees today's site, confirms arrival, posts progress and done with photos, asks questions | Phone, low-end Android, sunlight | gu, hi | Portal |
| **Client** | Confirms brief, approves layout/concept/drawings, follows progress, pays, raises requests | Phone | en, gu, hi | Portal |
| **Referrer / old client** | Receives thanks and status of their referral (optional) | Phone | — | Not a user in v1 |

Portal users are free in Odoo Enterprise; only office staff and the owner consume licences.

## 5. The journey

```
Lead → Qualify → Document site → Brief → Layout → Concept OK → Drawings → Agencies → Mark & approve → Execute → Handover → Close
 CRM   referral  spaces+specs  per space  options   per space   register  trade plan   gate         work pkgs   snags     money
       visit     photos/video  confirm              approvals   releases  quotes       photos       visits      proof     margin
                 vastu                              in app      queries   work orders  approval     MOM         sign-off  referral
```

Each stage has an **owner**, an **exit condition** and **what the client sees** (system_design.md §4). The project **stage** changes automatically when the exit condition is met, or manually by the office with a reason.

## 6. Goals and measures

| # | Goal | Measure (6 months after go-live) |
|---|---|---|
| G1 | Nothing waits silently | 90% of agency questions answered within the SLA (default 4 working hours); zero drawings past due without an owner-visible flag |
| G2 | Execution is documented | 95% of work packages closed with proof media and office verification |
| G3 | Agencies run on the app | 80% of active agency persons confirm arrival in the app; payment requests come only through the app |
| G4 | Clients feel informed | Client opens the app at least weekly on active projects; approvals happen in the app within 3 days median |
| G5 | Money is known per project | Owner can read contract, billed, paid, recoverable and margin per project without asking accounts |
| G6 | Plan vs actual exists | Every active project has a Gantt with committed dates; slippage is visible per trade |

**Non-goals for v1:** 3D/BIM model viewing, CAD file editing, quantity take-off from drawings, a public website, e-commerce for materials, payroll for agency workers, procurement of materials by Revert (unless the turnkey answer in Q A1 changes this), a client-facing marketplace of agencies.

## 7. Scope v1 by area

### 7.1 Leads and qualification (`rvt_crm`)
1. Lead with vision brief fields, referral source and referring client, seriousness score, next action.
2. Lead stages: New → Contacted → Site visit scheduled → Documented → Proposal sent → Won / Lost, with reasons.
3. Fee proposal as a quotation (`sale.order`) with stage-wise payment schedule; won lead creates the project and the site.
4. Voice notes and photos on the lead from the phone.

### 7.2 Site and spaces (`rvt_site`)
1. Site: address, map pin, property type (apartment, bungalow, office, hospital, studio, factory), size, floors, north angle, Vastu notes, access notes, documentation checklist.
2. Space types (living, kitchen, bedroom, bathroom, balcony, cabin, conference, ward, OT, shop floor…) with **spec templates** (Pratik's sheet) that decide which fields appear.
3. Space: dimensions, slab height, clear height, beam positions, door and window records, existing points, photos, video, notes.
4. Project summary line computed from spaces ("3 BHK + 2 bath + balcony", "Office 4,200 sq ft, 12 cabins").

### 7.3 Design and drawings (`rvt_design`)
1. Client brief per project and per space, author, client confirmation.
2. Drawing register: drawing types by trade, sheet number, space(s), revision, status (planned → in progress → internal check → released → approved → superseded), due date, assignee, released-to (client, agency, both).
3. Client approvals: layout option, concept per space, drawings; one-tap approve or "change request" with a note; optional e-signature on the agreement and concept sign-off (`sign`).
4. Queries on a drawing or a space: question with photo, answer, resolution; SLA timers; open-query board.
5. Pending drawings board: by trade, by due date, blocking which work package.

### 7.4 Agencies (`rvt_agency`)
1. Agency = partner company with trades, service area, rating, KYC (PAN, Aadhaar masked, GST if any, bank account, cancelled cheque photo), status (invited → KYC pending → active → paused → blacklisted).
2. Persons under an agency, added by the agency owner or the office, each with a phone (login) and language.
3. Invite by WhatsApp or SMS with a code; first login = OTP + language choice + photo; KYC documents uploaded in the app and verified by the office.
4. Trade plan per project: required trades, chosen agency, decision due date, status; **undecided past due** alert.
5. Quotation request → quote lines per space/item → comparison → **work order** (`purchase.order`) with payment terms (advance %, RA bills, retention %).

### 7.5 Execution (`rvt_execution`)
1. Work package (`project.task`) = space × trade × agency, with scope lines, planned start/end, **committed end**, actual start/end, dependencies, state (planned → marking → approved for execution → in progress → done, pending verification → verified → billed).
2. Gantt per project (plan, committed, actual) and per agency; dependencies drawn from the trade sequence template and editable.
3. Progress updates from the agency: percent, note, photos, video, materials needed; "done" requires media.
4. Verification by office with pass / rework; rework reopens with a reason.
5. Site marking gate: marking task, photos, approval, unlock.
6. Materials-needed and blocker flags that the office can act on.

### 7.6 Visits, reminders and MOM (`rvt_visit`, `rvt_mom`)
1. Visit: who (agency person or staff), which site, date, time window, purpose, created by office or by the agency owner; conflicts shown (same person, two sites).
2. Reminders: day-before and morning-of; **arrival confirmation** (tap, optional GPS distance check); "work started?" nudge after N minutes; end-of-day "update your progress" if silent; pending-task digest.
3. MOM: start from a scheduled visit or ad hoc; items captured as text or voice (gu/hi/en) with the **current space sticky**; "change location" switches space; items later classified (task, drawing change, query, decision, client action), assigned, due-dated; MOM shared to client (client-safe items only) and agencies (their items only).

### 7.7 Money (`rvt_finance`)
1. Client side: fee quotation with payment schedule, milestone invoices, receipts; turnkey items if applicable.
2. Agency side: work orders, payment requests from the app (advance, RA bill, final) with measured quantities and media, office approval, vendor bill, payment, TDS if applicable.
3. Expenses: who paid (company, client direct, agency), what, for which project and space, receipt photo, recoverable from client or not, reimbursed or not.
4. Owner money view per project: contract, invoiced, received, outstanding; per agency committed, billed, paid (by whom), pending; expenses by payer; recoverable; probable final invoice; margin. Owner-only access.
5. Agency money view in the app: work given, done, verified, billed, paid, pending, in their language, with dates.

### 7.8 Engagement (`rvt_game`)
Professional, verifiable, never punitive in public (full rules in system_design.md §8):
1. Agency reliability score from arrival on time, updates with media, questions answered, rework rate, committed-date adherence. Shown to the agency as their own score and to the office when choosing agencies.
2. XP and levels for agency persons and office staff; badges for streaks and firsts; monthly recognition.
3. Project health for office and owner: on track, needs attention, stuck, from measurable signals (overdue drawings, unanswered queries, undecided trades, silent work packages, slipped commitments).
4. Client sees progress and momentum, never scores.

### 7.9 Notifications and languages (`rvt_notify`)
1. One dispatcher: push (Firebase), WhatsApp (official Meta Cloud API via Odoo `whatsapp`, decision Q J2), SMS fallback for OTP, email for office and client documents.
2. Templates in en, hi, gu; the recipient's language decides; quiet hours.
3. In-app inbox with actions.

### 7.10 Mobile app (`rvt_api` + Flutter)
One app, four role homes (agency, client, office, owner); details in mobile_app_plan.md.

## 8. Functional requirements (selected, testable)

| ID | Requirement |
|---|---|
| FR-L1 | A lead stores property type, approximate size, location, target dates, budget band, scope wanted, referral source and referring client. A referral lead gets priority "high" and a 24 h first-response SLA by default (configurable). |
| FR-L2 | Winning a lead creates a project, a site, the client contact as a portal user invite, and copies the vision brief. |
| FR-S1 | A space is created from a space type; the type's spec template decides the fields shown. Templates are records editable by the office. |
| FR-S2 | The site documentation checklist is complete only when every space has dimensions, clear height, at least one photo, and the site has north and Vastu notes. The project stage cannot pass "Documented" without it, except by an office override with a reason. |
| FR-D1 | A drawing has a type, trade, spaces, revision number, status, due date and assignee. Releasing a drawing records who released it, to whom and when, and notifies the recipients in their language. |
| FR-D2 | A client approval is one tap in the app and is logged with time and user. A "change request" needs a note and reopens the drawing to "in progress" with a new revision. |
| FR-D3 | A query on a drawing has an SLA. Past the SLA it appears on the office home and the assignee's home until answered. |
| FR-A1 | A trade in the trade plan with no finalised agency and a decision date in the past is flagged to the office and the owner, and shown to the client as "we are finalising the <trade> partner". |
| FR-A2 | An agency person can log in only after the agency's KYC is verified or the office has explicitly allowed "work before KYC" (configurable, default off). |
| FR-E1 | A work package cannot move to "in progress" before its site marking is approved, where the trade requires marking (per trade setting). |
| FR-E2 | "Done" requires at least one photo or video. The office verifies within a configurable time; verified work updates the agency's billable amount. |
| FR-E3 | The Gantt shows planned, committed and actual dates per work package; a change of committed date needs a reason and is logged. |
| FR-V1 | A scheduled visit sends a reminder the evening before and the morning of (configurable). Arrival confirmation is one tap; if GPS is on, the distance to the site is stored. No confirmation by 60 min after the window start notifies the office. |
| FR-M1 | A MOM item carries the space it was captured in; "change location" switches the sticky space. Items can be converted to tasks, queries or drawing changes without retyping. |
| FR-M2 | Voice capture produces editable text in the speaker's language (gu, hi, en). Audio is kept with the item. |
| FR-P1 | A payment request from an agency references a work order and verified work packages, states the amount and type (advance, RA, final), and carries media. It is approved or returned by the office with a note. Approval creates the vendor bill. |
| FR-P2 | An expense records payer (company, client direct, agency), amount, project, space, receipt photo, recoverable flag and reimbursement status. |
| FR-O1 | The owner money view is readable only by the owner group and is computed from sale orders, invoices, payments, purchase orders, vendor bills, bill payments and expenses of the project's analytic account. |
| FR-G1 | XP is awarded only by server-side events (verified work, confirmed arrival within window, answered query, released drawing on time). Rules, points and caps are records. |
| FR-C1 | The client app never shows the words delayed, late, overdue or stuck. It shows the revised plan and the reason, as written by the office in a client-safe field. |
| FR-I1 | Every user-facing string in the app and in notifications exists in en, hi and gu. Master data (trades, space types, checklist items, drawing types) is translatable. |

## 9. Non-functional requirements

See architecture.md §6. Headlines: works on a ₹8k Android in sunlight on a 3G site; photos compressed client-side; app usable offline for today's visits and updates (queued); Aadhaar numbers masked at rest; DPDP-style consent for KYC data; 99.5% availability; nightly backups to S3 from day one.

## 10. Content and configuration the business must provide

| Item | Owner | Status |
|---|---|---|
| Measurement / spec template (Pratik) | Office | pending |
| Quotation format(s) by trade | Office | pending |
| Drawing type list by trade and standard sheet numbering | Design team | pending |
| Trade sequence and dependency rules | Principal consultant | pending |
| Fee model and payment schedule templates | Owner | pending |
| Agency list with trades, phones, languages | Office | pending |
| Client-facing tone examples and the brand (logo, colours, fonts) | Owner | pending |
| WhatsApp business number and Meta Business verification | Owner | pending |
| Legal entity, GST, TDS applicability, bank | Accounts / CA | pending |

## 11. Risks

| Risk | Mitigation |
|---|---|
| Agencies do not adopt the app | Payment transparency and payment requests only through the app; onboarding in 3 taps; Gujarati and Hindi first; voice and photo over typing; site supervisor helps the first week |
| Office keeps using WhatsApp groups in parallel | Every WhatsApp-worthy event has an app action; office home shows what waits; WhatsApp used as a notification channel into the app, not a parallel system |
| Business model mixes design-only and turnkey | Model it explicitly per project (Q A1); the money view handles both |
| Gamification feels childish to professionals | Scores framed as reliability and recognition; no leaderboards across agencies in public; see design.md §3 |
| Unofficial WhatsApp sending gets the number banned | Prefer the official Meta Cloud API (Odoo `whatsapp`); unofficial connector only as a fallback for internal notices |
| Personal data (Aadhaar, bank) | Masking, private attachments, owner/accounts-only access, retention rule |

## 12. Gaps found in the brief

These are the questions the questionnaire asks. Starred items gate the build.

1. ★ **Business model per project**: design-only, design + supervision, or turnkey? Who contracts the agencies, who pays them, who holds the GST and TDS exposure? The money view and the purchase flow depend on it.
2. ★ **Fee model** and payment schedule; when invoices are raised; advance.
3. **Lead sources and volume**; how referrals are rewarded; how many leads per month; who follows up.
4. ★ **Scope of "site documentation"**: fields in Pratik's template; whether CAD measured drawings come later from the measurements; who takes photos; is a laser meter or any measuring app used.
5. **Vastu**: free text only, or a checklist per space (entrance, kitchen fire, master bedroom direction)?
6. **Drawing types and numbering**; whether drawings are released as PDF only; whether agencies get full sets or only their trade; how revisions are communicated today.
7. ★ **Agency relationship**: fixed panel or per project; exclusivity; how many agencies per trade; advance and retention norms; who supplies materials (agency with material, or labour only with Revert/client material).
8. **Quotation granularity**: per space, per item, per sq ft; whether a BOQ is prepared by Revert first.
9. **Site marking**: which trades need it; who approves (site supervisor or principal); photo approval acceptable?
10. **Scheduling**: how far ahead agencies are scheduled; how many sites a person works per day; working hours and holidays; whether the agency owner or Revert decides who comes.
11. **Verification**: who verifies "done"; measurement-based billing or lump sum per package; how rework is handled and paid.
12. **Expenses**: who pays petty expenses today; how they are recovered; limits.
13. **Client approvals**: formal sign-off needed (e-sign) or a tap; who at the client side approves (corporate projects have committees).
14. **Client visibility**: should the client see agency names, prices, the Gantt, photos of raw stages?
15. **Office team**: size, roles, who answers queries, SLAs they can promise.
16. **Gamification appetite**: rewards tied to money (bonus, faster payment) or recognition only; whether agencies may see each other's rankings.
17. **Languages**: Gujarati script or transliterated Gujarati; Hindi; English for clients; voice typing expectation.
18. **WhatsApp**: official business number (Meta verification) or the existing personal numbers; templates approval lead time.
19. **Devices**: agency phones (Android share), office laptops; tablets on site.
20. **Data and legal**: entity, GST, TDS, KYC data retention, consent text, who may see Aadhaar.
21. **Volume**: active projects at a time, spaces per project, drawings per project, agencies and persons; needed to size the plan and the server.
22. **Go-live**: which projects start on the system (new only, or migrate running ones); pilot project; target date.

## 13. References and prior art

Asked: is there an ERP book on this subject? There is no single ERP book for interior project execution in India. The useful references are:

- **Council of Architecture (India), Architects (Professional Conduct) Regulations and Conditions of Engagement and Scale of Charges**: the stage list (concept, design development, working drawings, tender, construction, completion) and stage-wise fee percentages that Indian architects follow. Our stage model matches it.
- **RIBA Plan of Work 2020** (stages 0–7): the clearest published lifecycle for design and construction; our gates (concept OK, drawings released, marking approved, handover) map to stages 2, 4, 5 and 6.
- **Christine Piotrowski, *Professional Practice for Interior Designers*** and **Mary Knackstedt, *The Interior Design Business Handbook***: the standard texts on interior practice management: client agreements, fee models, vendor management, change orders.
- **PMI PMBOK / Construction Extension**: dependencies, baselines (planned vs committed vs actual), change control.
- **National Building Code of India 2016**, **IS 962** (architectural drawing conventions) and **CPWD DSR** (schedule of rates) for drawing standards and quantity/rate structures used in BOQs.
- **Software prior art**: Monograph, BQE Core and Deltek Vantagepoint (architecture practice management: phases, fee by phase, timesheets); Buildertrend, Procore and Fieldwire (site execution: daily logs, photo proof, punch lists, RFIs); Interior Design Management from Houzz Pro (client approvals, selections). Our design borrows the RFI (query) model from Procore and Fieldwire, the client approval flow from Houzz Pro, and phase-based fees from Monograph.
- **Odoo**: *Odoo 17 Development Essentials* (Daniel Reis) and the Odoo 20 developer documentation for the framework; Odoo's own Project, Purchase, Documents, Sign and WhatsApp modules carry most of the standard behaviour we need.
