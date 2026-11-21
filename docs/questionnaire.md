# Revert — Discovery Questionnaire for the Principal Consultant

Status: v0.1 · 2026-10-31 · to be answered in a 90-minute session, or filled in and returned

Tick one box per question, or write under "Other". **Recommended** is the default the documents assume; ticking it changes nothing. Questions marked ★ gate a build phase. Answers are copied into [memory.md](memory.md) §4 and the matching decisions in [architecture.md](architecture.md) flip to Agreed.

---

## A. Business model and money

**★ A1. How does Revert contract a typical project?** (tick all that occur, and mark the most common)
- [ ] Design only: Revert gives drawings; the client hires and pays agencies directly; Revert visits occasionally
- [ ] Design + supervision: Revert designs and coordinates agencies; the **client pays agencies directly** on Revert's recommendation (Recommended as the base case)
- [ ] Turnkey: Revert contracts and pays all agencies and bills the client one amount with margin
- [ ] Mixed within one project (some agencies paid by client, some by Revert)
- [ ] Other: ___

**★ A2. Who issues the work order to an agency?**
- [ ] Revert, in its name, even when the client pays (Recommended)
- [ ] Revert, in the client's name
- [ ] The client directly; Revert only recommends
- [ ] Depends: ___

**★ A3. Fee model for design**
- [ ] ₹ per sq ft of carpet / built-up area (typical ₹___ to ₹___)
- [ ] % of estimated project cost (___%)
- [ ] Lump sum, split by stage
- [ ] Different for architecture vs interiors: ___
- [ ] Other: ___

**A4. Fee payment schedule** (write the % at each stage)
- [ ] On signing ___% · layout approved ___% · concept approved ___% · working drawings released ___% · execution start ___% · handover ___% (Recommended structure)
- [ ] Monthly retainer
- [ ] Other: ___

**A5. When Revert pays an agency and recovers from the client**
- [ ] Rare: only petty site expenses, recovered in the next invoice (Recommended)
- [ ] Common: Revert fronts agency advances and bills the client at cost
- [ ] Revert adds a handling % on recovered amounts: ___%
- [ ] Never

**A6. Agency payment norms**
- [ ] Advance ___% on work order, RA bills on measured work, final ___% on verification, retention ___% for ___ days (Recommended structure)
- [ ] Per-visit or daily labour payments
- [ ] Lump sum on completion
- [ ] Other: ___

**A7. Is TDS deducted on agency payments made by Revert?**
- [ ] Yes, 194C at 1% / 2% depending on entity (Recommended if Revert pays)
- [ ] No, the client pays agencies
- [ ] Not sure, ask the CA

**A8. GST**
- [ ] Revert is GST registered; design fees at 18% (Recommended)
- [ ] Composition / not registered
- [ ] Agencies: mostly unregistered · mostly registered · mixed

**A9. Who may see project money in the app?**
- [ ] Owner only: everything. Accounts: bills and payments. Office: work order values without margin. Client: only their own invoices and payments. Agency: only their own work order and payments (Recommended)
- [ ] Office may also see margin
- [ ] Client may see agency prices
- [ ] Other: ___

## B. Leads and sales

**B1. Lead sources today** (tick all)
- [ ] Referral from old clients · [ ] builders / brokers · [ ] Instagram · [ ] Google / Justdial · [ ] walk-in · [ ] repeat clients · [ ] architects' network · [ ] Other: ___

**B2. Monthly lead volume and conversion**
- [ ] Under 10 leads/month, about ___% convert
- [ ] 10–30 · [ ] more than 30

**B3. What makes a lead "serious"?** (tick all)
- [ ] Referral by an old client (Recommended as the top signal) · [ ] possession date within 3 months · [ ] budget stated · [ ] site visit agreed · [ ] decision maker present · [ ] Other: ___

**B4. Who follows up leads, and how fast must the first response be?**
- [ ] Owner, within 24 h (Recommended) · [ ] Office coordinator · [ ] Within ___ h

**B5. Do referrers get anything?**
- [ ] A thank-you message only (Recommended for v1)
- [ ] A gift or fee · [ ] Status updates on the referred project · [ ] Nothing

**B6. What is captured in the first "vision brief"?** (tick all)
- [ ] Property type and size · [ ] location · [ ] possession / target date · [ ] budget band · [ ] style references (photos, Pinterest) · [ ] family / staff size · [ ] must-haves · [ ] scope wanted (design only / with execution) · [ ] Other: ___

## C. Site documentation

**★ C1. Pratik's measurement template: which fields per room?** (we will model the template as data; please attach it)
- [ ] Length, width, slab height, clear height under beam, beam positions and depths, column positions, doors (size, swing, type), windows (size, sill, lintel), existing electrical points, plumbing points, AC points, flooring type, wall condition (Recommended set)
- [ ] Simpler: dimensions, heights, doors, windows only
- [ ] Attached: ___

**C2. Space types to set up on day one** (tick all)
- [ ] Residential: living, dining, kitchen, master bedroom, bedroom, kids' room, bathroom, toilet, balcony, utility, pooja, study, foyer, terrace
- [ ] Office: reception, workstation area, cabin, conference, pantry, server room, washroom, store
- [ ] Hospital: OPD room, ward, OT, ICU, nurse station, pharmacy, reception, waiting, washroom
- [ ] Factory / studio: shop floor, office block, store, utility
- [ ] Other: ___

**C3. Who does the measurement and photography?**
- [ ] A junior from the office with a laser meter and the phone app (Recommended) · [ ] An external surveyor · [ ] The principal joins · [ ] Varies

**C4. Does a measured CAD drawing (as-built) get made from these measurements?**
- [ ] Yes, in the office afterwards; the app holds the raw numbers and photos (Recommended) · [ ] No · [ ] Only for larger projects

**C5. Vastu input**
- [ ] A free-text paragraph by the principal per site (Recommended for v1)
- [ ] A checklist per space (entrance direction, kitchen fire corner, master bedroom, toilets, pooja) plus notes
- [ ] Not for corporate / hospital projects
- [ ] Other: ___

**C6. Video**
- [ ] A walkthrough video per site, under 3 minutes (Recommended) · [ ] Per room · [ ] Not needed

## D. Design and drawings

**D1. Who writes the client brief?**
- [ ] Office, after the meeting; the client confirms it in the app (Recommended) · [ ] The client fills a form · [ ] Both

**★ D2. Drawing types and numbering** (attach the standard list; a draft set is in system_design.md §3.3)
- [ ] Use the draft set and refine (Recommended) · [ ] Attached: ___

**D3. How many layout options and concept rounds are normal?**
- [ ] 2–3 layout options, 1–2 revisions on the chosen one; concept per room, 1 revision (Recommended) · [ ] Other: ___

**D4. How are drawings released today?**
- [ ] PDF on WhatsApp / email (Recommended to replace with app release + PDF) · [ ] Printed sets on site · [ ] DWG to agencies

**D5. Do agencies receive only their trade's drawings?**
- [ ] Yes, trade-wise sets; carpenter also sees furniture layout (Recommended) · [ ] Full set to all · [ ] Decided per project

**D6. Client approval formality**
- [ ] One-tap approval in the app with a time stamp is enough (Recommended) · [ ] E-signature on concept and drawings · [ ] Signed printouts · [ ] Corporate clients need a named approver and a committee: ___

**D7. Query SLA the office can promise**
- [ ] 4 working hours for site-blocking queries, 1 working day otherwise (Recommended) · [ ] Same day · [ ] Other: ___

## E. Agencies

**★ E1. Trades list (confirm and correct)**
- [ ] Civil (mason, demolition) · [ ] Electrician · [ ] Plumber · [ ] POP / false ceiling · [ ] Painter · [ ] Carpenter · [ ] Window (aluminium / UPVC) · [ ] **Salat** = stone mason (marble, granite, kitchen platform) — correct? ___
- [ ] Add: [ ] glass & mirror · [ ] MS/SS fabrication · [ ] tiles / flooring · [ ] modular kitchen vendor · [ ] soft furnishings · [ ] HVAC · [ ] fire / low voltage · [ ] loose furniture · [ ] polish · [ ] Other: ___

**★ E2. Agency panel**
- [ ] A fixed panel of 2–4 agencies per trade, reused across projects (Recommended) · [ ] New agencies per project · [ ] Client's own agencies sometimes

**E3. Who supplies material?**
- [ ] Agency with material for most trades; some labour-only with client material (Recommended) · [ ] Labour only; client buys material · [ ] Revert procures material

**E4. Quotation granularity** (attach the quotation format)
- [ ] Lines per space and item with unit (sq ft, point, rft, lump sum), quantity and rate (Recommended) · [ ] Lump sum per trade · [ ] Attached: ___

**E5. Agency people**
- [ ] One owner (contractor) plus 1–10 workers; the owner decides who comes (Recommended) · [ ] Revert names the person · [ ] Single-person agencies mostly

**E6. KYC documents at onboarding**
- [ ] PAN, Aadhaar (masked), bank account with cancelled cheque photo, GST if registered, phone, photo (Recommended) · [ ] PAN and bank only · [ ] Nothing formal today

**E7. May an agency start work before KYC is verified?**
- [ ] No (Recommended) · [ ] Yes, but no payment before KYC · [ ] Yes

## F. Execution and scheduling

**★ F1. Site marking: which trades, who approves?**
- [ ] Carpenter marks; electrician and plumber mark their points; the site supervisor approves from photos, the principal for layout changes (Recommended) · [ ] Only carpenter; principal approves on site · [ ] Other: ___

**F2. How is the committed end date set?**
- [ ] Agreed with the agency when the work package is assigned; changes need a reason (Recommended) · [ ] Revert sets it · [ ] Agency proposes

**F3. Scheduling horizon and day structure**
- [ ] Agencies scheduled 1–2 weeks ahead; a worker does 1–2 sites a day; working hours 9–7; weekly off varies (Recommended) · [ ] Day-to-day · [ ] Other: ___

**F4. Who verifies "done"?**
- [ ] Site supervisor from photos, with a site check for carpentry and civil (Recommended) · [ ] Principal only · [ ] Client also confirms

**F5. Billing basis**
- [ ] Measured quantities per RA bill (sq ft, points, rft) checked against the quote (Recommended) · [ ] Percentage of lump sum · [ ] Mixed by trade

**F6. Rework**
- [ ] Rework at agency cost when caused by them; noted on the package; affects their reliability score (Recommended) · [ ] Always paid · [ ] Case by case

**F7. Materials and blockers**
- [ ] Agency flags "material needed" or "blocked" in the app; the office acts (Recommended) · [ ] Phone calls stay

## G. Visits, MOM, client

**G1. Site visit frequency**
- [ ] Supervisor 2–3 times a week per active site; principal weekly or at gates (Recommended) · [ ] Other: ___

**G2. MOM today**
- [ ] WhatsApp message or a notebook, shared the same evening (Recommended to replace) · [ ] Formal document · [ ] None

**G3. Voice capture languages**
- [ ] Gujarati, Hindi and English, mixed in one sentence is common (Recommended) · [ ] English only

**G4. What may the client see?** (tick all)
- [ ] Stage progress and what is next (Recommended) · [ ] Photos of work in progress · [ ] The Gantt · [ ] Agency names · [ ] Agency prices · [ ] MOM items that concern them · [ ] Invoices and payments

**G5. How should a delay be communicated to the client?**
- [ ] "Revised plan: carpentry finishing now completes by 12 Nov because the laminate shade was changed" — reason plus new date, written by the office (Recommended) · [ ] Not shown at all · [ ] Shown as a delay

**G6. Client approvals pending for long**
- [ ] Gentle reminder after 2 days, office nudge after 5 (Recommended) · [ ] No reminders

## H. Office team

**H1. Team size and roles**
- [ ] Principal ___ · designers / draftsmen ___ · 3D ___ · site supervisors ___ · accounts ___ · admin ___

**H2. Who answers agency queries on drawings?**
- [ ] The drawing's assignee, with the supervisor as backup (Recommended) · [ ] Principal · [ ] Supervisor

**H3. Who releases drawings?**
- [ ] Designer prepares, principal or lead approves, then release (Recommended) · [ ] Designer releases directly

**H4. Office hours and holidays (for SLAs and reminders)**
- [ ] Mon–Sat 10–7, Sunday off, Gujarat public holidays (Recommended) · [ ] Other: ___

## I. Gamification

**I1. Rewards for agencies**
- [ ] Recognition and faster payment processing for high reliability; no cash bonus (Recommended) · [ ] Cash or rate bonus · [ ] Recognition only

**I2. May agencies see each other's scores?**
- [ ] No; each sees their own score and level, the office sees all (Recommended) · [ ] Yes, a leaderboard per trade

**I3. Office team gamification**
- [ ] Yes: on-time drawings, answered queries, verified work; monthly recognition (Recommended) · [ ] No

**I4. What should an agency's home screen lead with?**
- [ ] Today's site and time, then my pending work, then my money (Recommended) · [ ] Money first · [ ] Work list first

**I5. Negative signals**
- [ ] Shown only to the agency themselves and the office, never to the client or other agencies (Recommended) · [ ] Other: ___

## J. Technology

**J1. Agency phones**
- [ ] Mostly Android, ₹8k–₹15k, Gujarati or Hindi keyboard, sometimes shared (Recommended assumption) · [ ] Some iPhones · [ ] Feature phones exist: ___

**★ J2. WhatsApp channel**
- [ ] Official WhatsApp Business (Meta Cloud API) on a new Revert number through Odoo; templates approved by Meta; most reliable, small per-message cost (Recommended) · [ ] Unofficial connector on an existing number (ban risk, no cost) · [ ] SMS only · [ ] Push notifications only

**J3. Voice to text**
- [ ] On-device speech recognition (Google / Apple) in gu, hi, en, with a cloud fallback (Recommended) · [ ] Not needed in v1

**J4. Email**
- [ ] Google Workspace at revert's domain (for client documents) · [ ] Other: ___

**J5. Existing software and data to migrate**
- [ ] Tally for accounts (keep Tally, Odoo for operations; decide later) · [ ] Excel project trackers · [ ] AutoCAD / SketchUp files on Drive · [ ] Nothing to migrate

**J6. Hosting**
- [ ] A dedicated VPS in India, Revert's name, nightly S3 backups (Recommended) · [ ] Odoo.sh · [ ] Odoo Online (no custom modules possible: not viable)

## K. Data, legal, go-live

**K1. Legal entity**
- [ ] Proprietorship · [ ] Partnership / LLP · [ ] Private limited; name, GSTIN and PAN: ___

**K2. KYC data retention and access**
- [ ] Aadhaar stored masked (last 4) with the image private; visible to owner and accounts only; deleted 3 years after the agency's last payment (Recommended) · [ ] Other: ___

**K3. Volume (for sizing)**
- [ ] Active projects at a time ___ · spaces per project ___ · drawings per project ___ · agencies ___ · agency persons ___ · office users ___

**★ K4. Pilot and go-live**
- [ ] One new residential project as pilot, office + 3 agencies, within 8 weeks of design sign-off; running projects added after (Recommended) · [ ] All new projects from day one · [ ] Migrate running projects too · [ ] Target date: ___

**K5. Brand**
- [ ] Logo (vector), colours and fonts to be shared · [ ] Use the neutral palette in design.md until then (Recommended)

---

## Attachments requested
1. Pratik's measurement / spec template
2. Quotation format(s) by trade
3. A sample MOM, a sample working-drawing set (one trade) and a sample fee proposal
4. Agency list (trade, name, phone, language)
5. Logo and brand assets
