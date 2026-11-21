# Revert — Phase 1 for adoption ("Release 1")

Status: **v0.4, approved by the project owner on 2026-11-18** · build order in [implementation_plan_r1.md](implementation_plan_r1.md) · master lists in [masters_draft.md](masters_draft.md)
Based on: the client conversation relayed on 2026-11-17 (§1.1), the project owner's review of v0.1 on 2026-11-18 (§1.2), and the decisions of 2026-11-17 (existing repo, existing database, existing MOM entries moved by ETL).
Companions: [prd.md](prd.md) (full scope, now the long-term backlog) · [system_design.md](system_design.md) · [mobile_app_plan.md](mobile_app_plan.md) · [tasks.md](tasks.md) (Release 1 task list) · [memory.md](memory.md)

Where this document and the v0.1 documents of 2026-10-31 disagree, this one wins for Release 1.

---

## 1. Inputs

### 1.1 Client conversation (2026-11-17)

| # | What the client said | What it means for the design |
|---|---|---|
| 1 | Too much information to the client causes problems. The client app shows **drawing releases** and **the next action pending from the client, raised by the Revert office**. | The client home has two blocks and nothing else. |
| 2 | Agencies must **not demand payment** from the app. **Revert asks** for an invoice or memo at a sensible point; the agency **uploads it**; Revert tracks **paid or not**. | No "Request payment" button. A bill is uploaded only against an invitation. |
| 3 | An invoice may be **against the end customer or against Revert**. | Every bill carries "billed to" and "paid by". |
| 4 | The team has **never used an ERP**. Staff use it fully first, agencies start adopting, micro-level management comes later. | Small releases. Release 1 works even if no agency opens the app. |
| 5 | The first release must let **everyone feel an advantage**. | One clear gain per role for little effort (§4). |
| 6 | Staff need visibility of **agencies' work per site**, of **their own drafting and releases**, and of **whom they coordinate**. | "My work" and "My sites" for staff. |

### 1.2 Review of v0.1 (2026-11-18)

| # | Decision | Effect on this document |
|---|---|---|
| a | Staff work **entirely in the mobile app or the web portal**, through **one dedicated window** as built for SFJ, not by moving between Odoo apps. | New §5.1 "Revert Desk". The app and the web desk offer the same staff functions. |
| b | **MOM is captured live on the mobile app** on site: lines with photos; tapping an agency or person **sends that party's MOM lines as a PDF on WhatsApp immediately**. | MOM moves into Release 1 (§5.4, §6.3). The new MOM replaces the present one and the existing entries are moved over in this release. |
| c | WhatsApp through **open_whatsapp_connector**, as on the Sudi project. | §5.7. The share-button approach of v0.1 is dropped; messages are sent automatically. |
| d | **Project onboarding is the key screen.** Selecting agencies fills in the standard set of required drawings; the user ticks what is needed and can add more later. Onboarding drives tasks, MOM and what each person sees in the app. | New §5.2, and the first flow designed. |
| e | Billed to: **a default on the project, changeable bill by bill**. | §5.6 |
| f | Agencies see **status per bill** only. | §5.6 |
| g | **No advance payments** for now. | §5.6: a payment is always recorded against a bill. |
| h | Release needs the **principal consultant's approval by default**; a setting can turn this off. | §5.3 |
| i | **Several coordinators** per project, set on the project. | §5.2 |
| j | Client access by **installed app and by link**. | §5.8 |
| k | **No signature**; the client's tap with name, date and time is the record. | §5.3 |
| l | The client receives **only drawings the office marks for the client**. | §5.3 |
| m | Pilot projects and agencies: **Excel sheet to follow**. | §9 |
| o | (same day, v0.4) The project must show **the whole picture of execution: progress, blockers, and next actions for Revert staff and for each agency**. | New §5.10 with the rules behind every figure, §6.4 redrawn, §7.1 |
| n | (same day, v0.3) Onboarding also asks the **site configuration** (3 BHK + garden; office with 3 cabins and a pantry). **One task per entity** is created, and **every agency working in that entity is tracked against that task**. | §5.2 step 3, §5.5: the board becomes rooms × trades |

## 2. The idea behind Release 1

**Set the project up once; after that there are two daily acts.**

1. **Onboarding** a project names its people, its trades and agencies, and the drawings it needs. From that moment the system knows who must draw what, who is waiting for what, and who may see what.
2. **Releasing a drawing** is the office's daily act.
3. **Writing a MOM point** is the site's daily act.

Everything else in Release 1 (pending lists, the agency board, client actions, bills) is read from these or hangs on them.

Two working rules the owner sets:
- **A drawing is released only through the system.** A PDF forwarded on personal WhatsApp does not count.
- **A point agreed on site is a MOM point in the app.** If it is not there, it was not agreed.

## 3. Adoption ladder

| Step | Who starts using it | What they do | Not asked of them yet |
|---|---|---|---|
| **Release 1** (this document) | Staff fully · agencies and clients as receivers | Staff: onboard projects, release drawings, capture MOM on site, keep the agency board, ask for and record bills. Agencies: receive drawings and MOM points, upload a bill when asked. Clients: see their drawings, close their pending items. | Agencies do not report progress. No KYC, quotes, visit scheduling, Gantt. |
| Release 2 "Agencies report" | Agencies as contributors | Mark a MOM point done with a photo, start / done on work, questions by voice note, visit confirmation, reminders. | |
| Release 3 "Site in detail" | Staff at micro level | Measured rooms from Pratik's template, site marking approval, order of trades and planned dates per room (Gantt). | |
| Release 4 "Money and commitment" | Owner and office | Quotes and work orders, committed dates with history, expenses and recoverables, advances, full owner money view. | |
| Release 5 "Recognition" | Everyone | Reliability scores, recognition, project health scoring. | |

Releases 2–5 are a direction. Their order follows what users ask for after Release 1 (§10).

## 4. What each person gives and gets

| Role | Gives | Gets |
|---|---|---|
| **Designer / draftsman** | Uploads the PDF and sends it for release. | One list of what to draw and by when, with who is waiting. Proof of release and of who opened it. |
| **Coordinator** | Writes MOM points on the phone at site; keeps the agency board. | The agency gets its points on WhatsApp before the coordinator leaves the room. One screen per site with agencies, pending drawings and pending client items. |
| **Principal consultant** | Approves releases (one tap). Captures MOM on the phone instead of paper. | Nothing reaches a client or agency unchecked. Open points from the last visit are in hand at the next one. |
| **Owner** | Sets the two rules. Runs the weekly review from the desk. | What is stuck and why, per project; what each agency billed, to whom, and what is paid by whom. |
| **Agency** | Nothing new at first: messages arrive on WhatsApp. Later, opens the app. | Its own points and the latest drawing, in Gujarati or Hindi. Bills on record with a visible status. |
| **Client** | Opens a link or the app. | The drawings meant for them, and a short list of what Revert needs from them. |

## 5. Scope of Release 1

### 5.1 Revert Desk: one window for staff
- **One menu entry, "Revert"**, in the browser and the same sections in the app. Staff do not open Project, Contacts, Documents or any other Odoo app; those menus are hidden for them, as on SFJ. Administrators keep them.
- Built as on SFJ's admin panel: list on the left, the selected record on the right, actions on the screen that shows the facts, every count opens the list behind it. Glass look, back office at `/office`.

| Section | Question it answers | Who |
|---|---|---|
| **Today** | What do I do now? (my drawings to make or approve, my open points, questions for me, bills to review) | every staff member |
| **Projects** | Everything about one project in one panel. It opens on the **project picture** (§5.10): progress, blockers, next actions. Tabs behind it: Work · Drawings · MOM · Client · Bills · earlier tasks | staff on that project |
| **Drawings** | All drawings across projects: to draw, awaiting approval, released, not opened | designers, principal |
| **MOM** | Visits and points across projects: open, due, by agency, by person; PDF | coordinators, principal |
| **Bills** | Asked, to review, unpaid | office, owner |
| **Review** | The weekly board: per project, drawings overdue, agencies undecided or waiting, client items open, bills unpaid | owner, principal |
| **Setup** | Trades, standard drawing sets, agencies and their people, staff, settings | administrator, owner |

- **Earlier tasks and hand-made tasks**: both ways stay (decided 2026-11-18). Staff can keep creating tasks by hand; they show in the project panel and in Today. On an existing project, "Project configuration" adds the entity tasks and work lines beside what is there; an existing room task can be marked as an entity instead of creating a second one.

### 5.2 Project onboarding
One guided screen, in the browser and in the app, for new projects and to complete the 12+ existing ones.

| Step | What is entered | What it produces |
|---|---|---|
| **1 Project** | Name, client and client contacts, site address, type (3 BHK, office, clinic …), **billed-to default** (client or Revert) | The project; client access when invited |
| **2 Team** | Principal, designers, **coordinators (one or more)** | Who sees the project; who approves releases |
| **3 Site configuration** | Pick a preset ("3 BHK", "Clinic", "Office") and adjust: 3 bedrooms, 3 toilets, living, kitchen, + garden; or 3 cabins, 1 pantry, reception. Rename freely. A "Whole site" entity is always added for work that belongs to no single room | **One task per entity.** The entity list is also the pick-list for MOM points and drawings. No measurements in Release 1 |
| **4 Trades and agencies** | Tick the trades involved. For each: the agency (or "undecided" with a decide-by date) and its contact people. Then a grid of entities × trades opens, pre-ticked from each entity type's usual trades (a toilet: plumber, civil, electrician; a bedroom: electrician, POP, carpenter, colour); untick what does not apply | **Under each entity task, one work line per ticked trade**, carrying that trade's agency. Who receives MOM points and drawings |
| **5 Drawings** | For every ticked trade the **standard drawing set** appears, plus the general set (layouts, elevations). Tick what this project needs; set designer and due date; mark "for client" and "needs client approval" | One drawing task per ticked drawing on the designer's list |
| **6 Review and start** | Summary; choose whom to invite now | Access for each person by role; WhatsApp invitations |

- **Changeable later**: adding a trade offers its standard drawings again; any drawing can be added by hand; an agency can be changed; coordinators added.
- **Standard sets** are kept in Setup per trade and per project type, so they improve with every project.
- **This is where access comes from.** A person sees a project only if onboarding (or a later edit) put them on it: staff by team, an agency by its trade line, a client by the client contacts.

### 5.3 Drawings
- **Register per project**, created by onboarding: sheet number, title, type, trade, area, designer, due date, state.
- **States**: To draw → In progress → Awaiting approval → Released → Superseded. A change request from the client returns it to In progress as a new revision.
- **Approval before release**: the designer sends the PDF for release; the **principal consultant approves**; then it goes out. A setting "release needs approval" (default on) can be turned off, and then the designer releases directly.
- **Release**: receivers are proposed from the drawing's trade (that trade's agency) and its "for client" mark; the user can add other trades of the project. Receivers get a WhatsApp message with the PDF or a secure link, and a push in the app.
- **Opened**: the system records when each receiver first opened it.
- **Revisions**: receivers only ever see the current revision, stamped.
- **Client approval** (only where marked): the client taps Approve, or Ask for a change with a note. The record is the client's name, date and time. No signature.
- **Questions on a drawing**: typed or with a photo, from an agency or client, or logged by staff from a phone call. They stay on the designer's list until answered.

### 5.4 MOM and points
A **point** is one line: what is needed, from whom, by when, with an optional photo, area and drawing. A **MOM** is the set of points written during one site visit. An office-raised "pending from you" item is the same record without a visit. One record type serves the MOM, the agency's to-do and the client's pending list.

- **Capture on the phone, live**, in a flow built for standing on site (§6.3): under ten seconds a point.
- **For whom**: an agency of the project (and optionally one of its people), the client, a vendor, or a staff member. The choice stays selected until changed.
- **Send**: tapping an agency or person sends **that party's points of this visit as a PDF on WhatsApp at once**, with photos. Points added afterwards are sent again on the next tap, marked "new".
- **Client points** are not sent on the spot by default: they appear for the client after the office confirms them, in line with §1.1 (1). A setting can make them immediate.
- **Without network**: points and photos are saved on the phone and go out when the signal returns. The screen shows what is still waiting.
- **Follow-up**: a point stays open until closed with a note or photo. Starting the next visit shows each party's open points first, to tick off on site.
- **Numbers**: visit number by date within the project and a serial number per point, as today.
- **In the desk**: the MOM section and the project's MOM tab carry the present dashboard (counts, by person, by month, filters) and the PDFs (whole visit, per party, open points of a project).
- **Existing entries are moved over**: every present MOM entry becomes a point with its text, "Related To" person, photo, visit date and number, serial number, due date, open or closed state, closing note and author. Entries stay linked to the task they were written on. After the check the present MOM screens are switched off.

### 5.5 Entities and agencies (the board)
- **One task per entity** (room, zone, garden, "Whole site"), created by onboarding. This is how the team already works: today's tasks are rooms with work items under them, made by hand and by copying.
- **Under each entity, one work line per trade that works there.** The agency is chosen once per trade for the project and applies to every entity; it can be overridden on one line (a second carpenter for the kitchen).
- **State lives on the work line**, because several agencies work in one room at different times: Not started · Waiting · Working · Done. Optional expected finish and note.
- **"Waiting" always names its cause**, picked in the same tap: a drawing (choose it), the client (choose or raise the item), another trade (choose it), material, or other with a note. This is what lets the project picture say who must act to unblock it.
- **The entity's own state is read from its lines**: not started, in progress (3 of 5 trades done), done. Nobody sets it by hand.
- **Seen as a grid**: entities down, trades across, one coloured cell per line. One tap changes a cell. The same data is listed per agency ("Mahadev: 6 rooms, 2 working, 1 waiting") and per room.
- **Signals**: a trade still "undecided" past its date is highlighted to coordinators and the owner. A cell "waiting for a drawing" points at the drawing, so the designer sees who is waiting. Open MOM points show on their cell.
- **Light by design**: a 3 BHK gives about 10 entities × 6 trades, of which perhaps 40 cells apply. Nobody is asked to keep 40 statuses current every day. Cells start at "Not started" and are changed when something changes, usually during the site visit; closing the last MOM point of a cell offers "mark done".
- Kept by staff. An agency sees its own lines but does not edit them in Release 1.
- **Not yet**: order of trades within a room, dates per line as a plan, Gantt, measurements. These come with Release 3.

### 5.6 Bills
- **Ask for a bill**: the office picks project, agency and trade, says what the bill is for and optionally up to what amount. The agency is told on WhatsApp and in the app.
- **Upload**: the agency photographs or attaches the invoice or memo and enters the amount. Staff can upload on its behalf.
- **Billed to**: taken from the project's default, changeable on each bill.
- **Review**: Accept, or Return with a reason.
- **Payment**: recorded against a bill only (date, amount, paid by client or by Revert, mode, optional proof). A bill can be paid in parts. **No advances** without a bill in Release 1.
- **Agency view**: its bills with a status each (Asked · Submitted · Returned · Accepted · Part paid · Paid). No totals, no balance, no way to start a request.
- **Owner view** (owner only): per project and per agency: billed, billed to whom, paid, paid by whom, unpaid, and "paid by Revert on a bill addressed to the client" as an amount to recover.
- A register only. Nothing is posted to accounts.

### 5.7 WhatsApp
- **open_whatsapp_connector**, the full Odoo 20 version running on Sudi (20.0.95.0.0, which sends documents), with its companion for sign-in codes on WhatsApp. Both are copied from the Sudi project unchanged.
- **Sent automatically**: MOM PDF to a party, drawing released, client item raised, bill asked / returned / paid, invitation, sign-in code.
- **It needs**: one dedicated phone number for Revert (a new SIM, paired once by scanning a code), and the connector's helper service installed on the production server next to Odoo.
- **Limits to know**: this route is unofficial; WhatsApp can block a number that sends in bulk or gets reported. The connector's per-minute and per-day caps stay on, messages go only to people on a project, and the dedicated number keeps any block away from staff's own numbers.

### 5.8 Access and languages
- **Staff**: their Odoo login, in the browser or the app. The app covers every staff function of the desk, including onboarding.
- **Agencies and clients**: phone number and a code on WhatsApp, invited from onboarding. No KYC in Release 1.
- **Client**: the installed app, or the same screens from a secure link in the browser.
- **Languages**: agency screens and messages in Gujarati, Hindi and English. Client in English and Gujarati. Staff in English.

| Role | Sees |
|---|---|
| Owner | Everything, including money |
| Principal | All projects; approves releases; no money totals unless the owner allows |
| Designer, coordinator | Projects they are on; bills as far as asking and reviewing |
| Agency | Its own board line, drawings released to its trade, its MOM points, its bills |
| Client | Drawings marked for the client, its own pending items |

### 5.9 Not in Release 1
Measured rooms and Pratik's template · site marking gate · quotes, work orders · Gantt and dependencies · agency progress updates · visit scheduling, arrival and reminders · KYC · built-in voice-to-text (the phone keyboard's own Gujarati / Hindi dictation works in every text box) · advances and expenses · accounting, GST, TDS · points, levels, scores · leads beyond the website enquiry that already works.

### 5.10 Project picture: progress, blockers, next actions
The first screen of every project, in the desk and in the app. It answers three questions without anyone preparing a report. Every figure is computed from records that already exist; nothing on this screen is typed in.

**Progress** (four measures, each a count, never an estimated percentage)

| Measure | Counted as | Broken down by |
|---|---|---|
| Agencies decided | trades with an agency ÷ trades needed | — |
| Drawings | released ÷ required | trade, designer |
| Work | work lines done ÷ lines that apply; lines working shown apart | entity, trade / agency |
| Points | closed ÷ raised; open and overdue shown apart | party |

Plus "this week": drawings released, lines started and finished, points closed in the last 7 days, so movement is visible even when the totals barely change.

**Blockers** (a fixed list of rules; each blocker shows what is held, who must act, and for how long)

| # | A blocker exists when | Who must act | What it holds |
|---|---|---|---|
| B1 | a trade is undecided past its decide-by date | coordinators | every work line of that trade |
| B2 | a work line waits for a drawing | the designer; the principal if it awaits approval | that line |
| B3 | a required drawing is past its due date and not released | the designer / the principal | lines of its trade (and entity, if set) |
| B4 | a client item is open past its date (approval, choice, information) | the client; the coordinator chases | the drawing or line it is linked to |
| B5 | a work line waits for another trade | that trade's agency | that line |
| B6 | a work line waits for material or another cause | named on the line | that line |
| B7 | a MOM point is past its due date | the party it is for | its entity and trade |
| B8 | a released drawing is not opened by an agency after 2 days | the coordinator chases | that agency's lines |
| B9 | a question on a drawing is unanswered after 1 working day | the designer | the asker's line |
| B10 | a bill is submitted and not reviewed after 3 days | the office | — |

Day limits are settings. Also shown, without being a blocker: a work line marked Working whose trade has no released drawing yet ("working without a drawing").

**Next actions** (the blockers and the due items, turned round and grouped by who acts)

| Group | Lines look like | Button on the line |
|---|---|---|
| **Revert**, per staff member | "Riya: release Electrical layout (Jay Electric waiting 3 days)" · "Principal: approve Wardrobe details" · "Coordinator: decide the plumber" · "Review Mahadev's bill" | Open · Release · Approve · Assign |
| **Each agency** | "Mahadev: 2 open points (1 overdue), Master bedroom wardrobe due Fri, Kitchen not started" · "Jay Electric: has not opened Electrical layout rev 2" | Remind on WhatsApp · Close point · Change state |
| **Client** | "Approve furniture layout rev 2 (2 days)" · "Choose kitchen platform stone (by Fri)" | Remind on WhatsApp · Mark received |

"Remind" sends a short WhatsApp message for that one item, on the staff member's tap. Nothing is chased automatically in Release 1.

**Status of the project** (one word with its reasons, no score)
- **Stuck**: any blocker older than 7 days, or B1.
- **Needs attention**: any other blocker.
- **On track**: none.
The reasons are the blockers themselves, listed.

**One source, three views.** The same computed items feed three screens, so they can never disagree:
- **Project picture**: all items of one project.
- **Today**: the items where I must act, across my projects.
- **Review**: one row per project with its status, four progress counts and blocker count; the owner's weekly meeting.

**What others see.** An agency sees only its own slice: its work lines, its points, its drawings. It does not see blockers, other agencies or the client's items. The client sees none of this (§1.1).

## 6. UX flows

Three rules shape every screen:
1. **The home is a to-do, not a dashboard.** A short list that can reach zero.
2. **One tap from the list to the act.**
3. **Each role sees only its own slice.**

### 6.1 Onboarding, step 5 (the step that saves the most typing)
```
New project · Shah Residence            5 of 6
───────────────────────────────────────────────
Drawings needed            14 ticked of 22
GENERAL
 ☑ Furniture layout        Riya   20 Nov  client ✓
 ☑ Wall elevations         Riya   27 Nov  client ✓
ELECTRICIAN · Jay Electric
 ☑ Electrical layout       Amit   24 Nov
 ☑ Switchboard details     Amit   26 Nov
 ☐ Lighting layout
CARPENTER · Mahadev Furniture
 ☑ Wardrobe details        Riya   1 Dec   client ✓
 ☑ Kitchen details         Riya   3 Dec   client ✓
PLUMBER · undecided
 ☑ Plumbing layout         Amit   25 Nov
 + Add a drawing
───────────────────────────────────────────────
[ Back ]                          [ Review ▸ ]
```
Designer and due date are pre-filled from the standard set and the team, so most rows need only the tick.

### 6.2 Staff "Today"
```
Today · Riya                        Wed 18 Nov
───────────────────────────────────────────────
TO DRAW                                      4
 Electrical layout   Shah Res.   due today
   ⚠ Jay Electric waiting · 3 days
 Wardrobe details    Shah Res.   due Thu
CHANGE ASKED                                 1
 Furniture layout    Patel Res.  client note
QUESTIONS                                    2
 Wardrobe details "Loft depth 18 or 24?" · photo
MY OPEN POINTS                               3
 Send revised kitchen elevation · Mehta Off.
───────────────────────────────────────────────
Released this week 6 · opened 5 · not opened 1
```
The principal's Today starts with "To approve"; a coordinator's with "My sites" and open points per agency.

### 6.3 MOM capture on site
```
MOM · Shah Residence · Visit 7 · 18 Nov   ● saved
───────────────────────────────────────────────
OPEN FROM EARLIER            Mahadev 2 · Jay 1
───────────────────────────────────────────────
 12  Mahadev  Wardrobe loft depth 24"     📷  Fri
 13  Mahadev  Shift TV unit 4" left           Mon
 14  Jay      Add 2 points near study     📷  Thu
───────────────────────────────────────────────
For:  [Mahadev ✓] [Jay] [Shree POP] [Client] [+]
Area: [Master bedroom ✓]                  change
┌─────────────────────────────────────────────┐
│ Type or speak the point…                    │
└─────────────────────────────────────────────┘
 📷 Photo    Due: [Today][Tmrw][Fri ✓][Pick]  [Add]
───────────────────────────────────────────────
Send:  Mahadev (2) ➤     Jay (1) ➤     All ➤
```
1. **Start**: open the project, tap "Start MOM". The visit number and date are set. Open points from earlier visits are listed first per party; tap to close with a note or photo.
2. **Write**: choose "For" once; it stays. Type or dictate, add a photo if useful, pick a due chip, Add. The composer clears and is ready for the next point for the same party and area.
3. **Move on**: change "For" or "Area" when walking to the next agency or room.
4. **Send**: tap "Mahadev (2) ➤". Mahadev's contact people receive a PDF of those points with photos on WhatsApp within seconds. The points show a sent tick. Points added later raise the count again.
5. **Finish**: "All ➤" sends each party its own PDF and files the full MOM for the office. Client points wait for office confirmation.

### 6.4 Project picture (first screen of a project)
```
Shah Residence · 3 BHK + garden · Bopal        ● NEEDS ATTENTION
──────────────────────────────────────────────────────────────────
PROGRESS
 Agencies  5 of 6 decided     Drawings  9 of 14 released
 Work      11 of 38 done · 9 working      Points  41 of 52 closed
 This week: 3 drawings released · 4 lines done · 9 points closed
──────────────────────────────────────────────────────────────────
BLOCKERS                                                        4
 ⚠ Plumber undecided · 6 days late      holds 5 lines   Coordinator
 ⏸ Electrical layout not released       holds 3 lines   Amit · 3 d
 ⏸ Client: approve furniture layout     holds Wardrobe  Client · 2 d
 ⏸ Mahadev: loft depth point overdue    Master bedroom  Mahadev · 1 d
──────────────────────────────────────────────────────────────────
NEXT ACTIONS      [ Revert ]   Agencies   Client
 Amit       Release Electrical layout              [ Open ]
 Principal  Approve Wardrobe details               [ Approve ]
 Meera      Decide the plumber                     [ Assign ]
 Meera      Review Mahadev's bill                  [ Open ]
──────────────────────────────────────────────────────────────────
WORK              Civ  Elec  Plmb  POP  Carp  Col
 Living           ✓    ◐     ·    ◐    ○     ○
 Kitchen          ✓    ◐     ⚠    ·    ○     ○
 Master bedroom   ✓    ⏸     ·    ◐    ○2    ○
 Toilet 1         ◐    ○     ⚠    ·    ·     ·
 Garden           ○    ○     ⚠    ·    ·     ·
 ✓ done ◐ working ⏸ waiting ○ not started ⚠ undecided · 2 = open points
──────────────────────────────────────────────────────────────────
[ Start MOM ]   [ Raise point ]   [ Ask for bill ]
```
The "Agencies" tab of Next actions:
```
 Mahadev Furniture   2 points (1 overdue) · 6 rooms: 0 done, 1 working
                     next: Master bedroom wardrobe, due Fri    [ Remind ]
 Jay Electric        1 point · waiting for Electrical layout
                     has not opened Switchboard details rev 1  [ Remind ]
 Shree POP           0 points · 2 working, finish 28 Nov
```
On the phone the same blocks stack: status and progress, blockers, next actions, then the grid scrolls sideways.

### 6.5 Agency
```
નમસ્તે, Mahadev Furniture
───────────────────────────────────────────────
તમારા મુદ્દા · YOUR POINTS                    2
 Wardrobe loft depth 24"   Shah Res. · Fri  📷
 Shift TV unit 4" left     Shah Res. · Mon
નવું · NEW DRAWINGS                           1
 Wardrobe details  rev 1   Shah Res.
REVERT ASKS
 Upload your bill · Mehta Office · carpentry
───────────────────────────────────────────────
My sites (3)       Drawings       Bills
```
An agency that never opens the app still receives all of this on WhatsApp.

### 6.6 Client
```
Shah Residence
───────────────────────────────────────────────
WAITING FOR YOU                              2
 Approve the furniture layout
 Choose the kitchen platform stone
───────────────────────────────────────────────
YOUR DRAWINGS
 Furniture layout      rev 2   new
 Wall elevations       rev 1
```
When nothing is pending: "Nothing needed from you right now". Wording stays positive (rules.md §6.1).

### 6.7 Engagement without points
The list that empties, "opened" ticks on released drawings, "sent" ticks on MOM points and a weekly "released / closed" line are the feedback in Release 1. Points, levels and scores wait for Release 5, when there is real data to score.

## 7. Build breakdown

Built in `Albatross-IN/revert` branch `20.0`, installed on the existing database.

| Part | Contents | Usable after this part | Estimate |
|---|---|---|---|
| **R1.0 Design** | Clickable screens for onboarding, Today, project panel, MOM capture, release, bill; agency and client homes; en / gu / hi wording; sign-off | — | 1.5–2 wk |
| **R1.1 Desk and onboarding** | Roles and access; trades, site presets and entity types, standard drawing sets, agencies; onboarding; entity tasks with work lines and the grid; Revert Desk shell with Today and Projects; Glass look; other menus hidden | Staff onboard projects in the browser | 3–3.5 wk |
| **R1.2 Drawings** | Register, revisions, approval, release, opened tracking, questions, client approval; Drawings and Review sections | Staff release drawings in the browser | 2 wk |
| **R1.3 MOM in the desk** | Points and visits, MOM section, dashboard, PDFs; move of existing entries with a verification report; present MOM screens off | Staff see all MOM, old and new, in one place | 1.5–2 wk |
| **R1.4 WhatsApp** | Connector and sign-in codes from Sudi; message texts in three languages; helper service on the server; dedicated number paired | Drawings and PDFs go out on WhatsApp | 1 wk |
| **R1.5 App** | API; staff app with every desk function, MOM capture with offline queue and send; agency home; client home and browser link; push | Everyone, on the phone | 4.5–5 wk |
| **R1.6 Bills** | Ask, upload, review, payments, agency list, owner money view; desk and app | Office, agencies, owner | 1.5 wk |
| **R1.7 Rollout** | Store listing, privacy page, onboarding material in Gujarati and Hindi, production release | — | 1 wk |

About **17–19 weeks** in sequence (one week for the project picture, spread over R1.1–R1.3). These are my estimates from the SFJ, Sudi and Bhuj Runners builds, not measured figures. Compared with v0.1 (9–10 weeks) the growth comes from MOM with the move of existing entries, the single-window desk, and full staff function in the app. R1.5 can run alongside R1.2–R1.4 if a second developer takes the app, which brings the calendar to about 10–11 weeks. Staff start using the desk after R1.1, about five weeks in.

### 7.1 How the project picture is built
- **Computed on reading, not stored.** One method on the project returns progress, blockers and next actions from the live records (work lines, drawings, points, bills). There is no second table to keep in step, so the picture cannot go stale.
- **The same method serves the desk, the app (`GET /projects/{id}/picture`), Today (filtered to the user) and Review (summary per project).** Access rules decide what a caller gets: staff the whole picture, an agency only its slice.
- **Each blocker rule is a small function** returning: rule, record, what it holds, who must act, since when. Adding a rule later does not touch the screens.
- **It fills in as the parts land:** agencies and work after R1.1; drawings (B2, B3, B8, B9) after R1.2; points (B7) after R1.3; reminders after R1.4; bills (B10) after R1.6.
- **Inputs it depends on**, all captured in the normal flow: decide-by date per trade (onboarding), due date per drawing (onboarding), cause of "Waiting" (one tap on the cell), due date per point (MOM chips).

Modules: `rvt_base` (roles, trades, settings), `rvt_project` (onboarding, team, areas, agency board), `rvt_drawing`, `rvt_mom` (points, visits, PDFs, migration of existing entries), `rvt_bill`, `rvt_notify` (WhatsApp and push messages), `rvt_api`, `rvt_desk` (the single window). Copied in unchanged: `open_whatsapp_connector` and `web_auth_otp_login` from the Sudi project, `web_theme_glass`, `web_glass_workspace`, `identity`, `fastapi`, `endpoint_route_handler`.

## 8. Rollout plan

| Wave | When | Who | What happens | It worked if |
|---|---|---|---|---|
| 0 Prepare | before R1.1 goes live | Albatross + one Revert person | Standard drawing sets, trades, agencies with phone numbers loaded. Two pilot projects onboarded together. One-hour session for staff. | Both pilots show their real team, agencies and drawing list |
| 1 Staff, desk | from R1.1 | All staff | Running projects onboarded. Release rule starts with R1.2. Weekly review run from the desk. | 90% of drawings released through the system |
| 2 MOM | from R1.3–R1.5 | Principal, coordinators | MOM in the desk first; on the phone at site when the app is out. MOM rule starts. | Every site visit of a pilot project has its MOM in the system the same day |
| 3 Agencies | with R1.4–R1.5 | Carpenter and electrician of the pilot sites first | They first receive on WhatsApp only; the coordinator signs them into the app on site. | 70% of released drawings opened within a day |
| 4 Clients | after wave 3 | Clients of the pilot projects | Invited with a short message from the principal. | Client items closed in days, not weeks |
| 5 Bills | with R1.6, at the next sensible billing point | Office, agencies | First bills asked, uploaded, payments recorded. | No bill of a pilot site sits outside the system |

## 9. Still open

| # | Question | Needed by |
|---|---|---|
| 1 | **Standard drawing set per trade and per project type** (the list onboarding fills in). A first draft exists in system_design.md §3.3. | R1.1 |
| 2 | **Pilot projects and agencies** (Excel sheet to follow), with agency contact numbers. | Wave 0 |
| 3 | **Dedicated WhatsApp number** for Revert: who arranges the SIM and keeps the phone. | R1.4 |
| 4 | **An agency with several people**: do MOM PDFs go to the owner, the person on site, or both? Assumed: the contact people ticked on the project's trade line. | R1.0 |
| 5 | **Client MOM points**: confirmed by the office before the client sees them (assumed), or immediate? | R1.0 |
| 6 | **Site presets and usual trades per entity type** (what a "3 BHK" or "clinic" contains, and which trades a toilet, bedroom, cabin or garden usually needs). A first draft will be proposed for Revert to correct. | R1.1 |
| 7 | **Principal and money**: does the principal see bill amounts and totals, or the owner only? Assumed: owner only. | R1.6 |
| 8 | **Production server**: the WhatsApp helper service and the photo and PDF volume land on the server shared with Albatross. Confirm this is acceptable, or plan a move. | R1.4 |

## 10. What comes next, by demand

| What users are likely to ask after Release 1 | It leads to |
|---|---|
| Agency: "let me mark the point done and send a photo" | Release 2 |
| Coordinator: "remind the agency about tomorrow's visit" | Release 2 |
| Principal: "plan my site visits for the week" | Release 2 |
| Designer: "let the carpenter ask by voice" | Release 2 |
| Coordinator: "track by room, with measurements" | Release 3 |
| Owner: "show quoted price against billed and paid, and advances" | Release 4 |
| Owner: "who are my reliable agencies?" | Release 5 |
