# Revert — Design

Status: v0.1 · 2026-10-31 · direction proposed, not yet chosen · brand assets not received (placeholder palette)
Scope: the mobile app (four role homes), notification copy, and the back office (Glass theme with Revert tokens)

## 1. What the design must do
1. **Make the next action obvious** on a ₹8k Android in sunlight, for a person who may read Gujarati better than English and would rather talk than type. One big button per state: *I will come → I have arrived → Start → Update → Done*.
2. **Keep the client calm and informed.** Progress, next steps and decisions waiting on them, in positive language. The client never sees scores, raw agency notes or red flags.
3. **Give the office a worklist, not a dashboard.** What waits on me today, then the boards. Numbers only where they change what someone does.
4. **Feel like a studio, not a factory app.** Revert sells design; its own tools must look designed. Calm paper ground, generous type, one accent, real photos of the work.
5. **Stay one system** across app, WhatsApp messages, PDFs (MOM, drawings release note, invoices) and the back office.

## 2. Language and tone

### 2.1 Client copy (the "always positive" rule, FR-C1)
| Never | Instead |
|---|---|
| Delayed, late, overdue, stuck, pending from your side | "Revised plan", "now completes by", "waiting for your go-ahead on" |
| "Electrician not finalised" | "We are finalising your electrical partner" |
| "Carpenter did not come" | "Carpentry continues on Thursday" (office writes the client-safe status) |
| "Rework" | "We are refining the finish on the kitchen shutters" |
| Percentages below 10% shown as failure | "Started" state with the next milestone |

Pattern for a revised plan: **what** + **new date** + **reason in one clause**. Example: "Kitchen carpentry now completes by 12 Nov because the laminate shade was changed to the one you chose on Monday."

### 2.2 Agency copy (plain, respectful, specific)
- Address the person by name; use the polite form (આપ / आप).
- One sentence per message, the site name and time first: "કાલે 10:00 · શાહ રેસિડન્સ, બોડકદેવ · સુથારી ફિનિશિંગ" / "कल 10:00 · शाह रेसिडेंस, बोडकदेव · कारपेंट्री फिनिशिंग".
- Nudges ask, they don't scold: "શું કામ શરૂ થયું? એક ફોટો મોકલો" ("Has work started? Send one photo").
- Money words are exact: verified, billed, approved, paid, with dates and references.

### 2.3 Gamification copy
Professional nouns: **reliability**, **on time**, **documented**, **verified**, **partner level**. No "you lost points". Level-ups and badges are celebrated privately with a short card; monthly recognition is a message from Revert, not a leaderboard.

### 2.4 Script and fonts
Gujarati and Devanagari need fonts with full conjuncts and matching weights to the Latin face: **Noto Sans Gujarati**, **Noto Sans Devanagari**, **Inter** (Latin), bundled in the app and the back office (rules.md §7). Numerals stay Latin (0–9) in all languages for amounts and dates.

## 3. Direction options

### Option A — "Studio Paper" ✅ recommended
Warm off-white paper ground, ink text, one **terracotta** accent (brick, the material most sites start from), olive for verified/positive, amber for attention (office only). Photos of real work carry the colour. Cards with soft shadows, no glass except on photo headers. Reads outdoors.
- Pros: calm, professional, high contrast, cheap to render on low-end phones, matches an architecture studio's print collateral.
- Cons: needs good site photography to avoid looking plain.

### Option B — "Blueprint"
Deep indigo ground with white line-work, cyan accents, grid textures from drawing sheets.
- Pros: unmistakably architectural; striking.
- Cons: dark-only is poor in sunlight and for older clients; blue text on blue photos fails contrast; feels technical for clients.
- Verdict: dark mode of Option A, and the look of the drawings module in the back office.

### Option C — "Glass"
The Glass theme already used in the Albatross back office carried into the app.
- Pros: continuity with the office tools.
- Cons: `backdrop-filter` is costly on budget Android; translucency hurts readability on site.
- Verdict: back office only (where it is already the standard), with Revert tokens.

## 4. Design tokens (placeholder until the brand arrives)

```scss
// Ground (Option A)
--rvt-paper:        #F6F2EC;   // app background
--rvt-card:         #FFFFFF;
--rvt-line:         #E4DCD1;   // dividers
--rvt-ink:          #1F1B17;   // text (≈15:1 on paper)
--rvt-ink-muted:    #6B625A;   // secondary (≥4.5:1 on paper)
// Brand accent
--rvt-terracotta:   #B9512E;   // primary actions, progress (≈5.6:1 on paper)
--rvt-terracotta-700: #93401F;
// Semantic (office and agency only; the client sees terracotta + olive)
--rvt-olive:        #3E6B3A;   // verified, done, on track
--rvt-amber:        #B57A14;   // attention (office), waiting check (agency)
--rvt-slate:        #4C5B6B;   // planned, info
--rvt-rose:         #9E3B3B;   // office-only: stuck, rework (never in client UI)
// Dark (Option B as dark mode)
--rvt-dark-ground:  #14202E;
--rvt-dark-card:    #1C2B3C;
--rvt-dark-ink:     #EEF2F6;
--rvt-dark-accent:  #E07A52;
// Type
--rvt-font-latin:   "Inter";
--rvt-font-gu:      "Noto Sans Gujarati";
--rvt-font-hi:      "Noto Sans Devanagari";
// Scale (phone)
--rvt-text-xs: 12px; --rvt-text-sm: 14px; --rvt-text-md: 16px; --rvt-text-lg: 20px; --rvt-text-xl: 26px; --rvt-display: 34px;
// Shape and space
--rvt-radius: 14px; --rvt-radius-pill: 999px; --rvt-gap: 12px; --rvt-gutter: 16px; --rvt-tap: 48px;
```
Indic scripts render taller than Latin at the same size: line height 1.5 for gu/hi, 1.35 for Latin; body text never below 16 px for agency screens.

## 5. Components

| Component | Where | Behaviour |
|---|---|---|
| **Big action button** | agency work and visit screens | full-width, 56 px, one per state; disabled state explains why in words ("Marking not approved yet") |
| **Stage stepper** | client project, office project | horizontal pills; current stage highlighted; past stages ticked; future stages muted; tap for dates |
| **Progress ring** | room cards, project card | terracotta arc on paper track; percent inside; never red |
| **Work card** | agency, office | space · trade · state chip · committed date · drawings count · last update ago; swipe to update |
| **Visit card** | agency today | time window, site name and area, map button, tasks list, state buttons |
| **Drawing card** | all | sheet no · title · revision badge · state · open PDF · queries count; approval buttons for the client |
| **Query thread** | all | question bubble with photos, answer bubble, SLA chip (office only), follow-up |
| **Approval sheet** | client | preview, two buttons: *Looks good* / *I'd like changes* (note required) |
| **Money ledger card** | agency owner, owner | rows verified · billed · approved · paid · pending with dates; totals pinned |
| **Space header (sticky)** | MOM, site documentation | current space name with *Change location*; stays while scrolling |
| **Mic button** | MOM, lead notes, query | hold to talk; language chips gu · hi · en above; waveform; text appears editable; audio kept |
| **Spec form** | site documentation | fields from the template: numeric pads with unit, selects as chips, photo fields with camera |
| **Health pill** (office only) | project list | on track · attention · stuck with reasons on tap |
| **Recognition card** | agency, office | monthly card with name, badge, one line from Revert; shareable image |
| **Offline banner** | all | "Saved on phone · will send when online" with count |

## 6. Screen sketches (phone, 360 px)

### 6.1 Agency person: Today
```
┌──────────────────────────────────────┐
│ નમસ્તે, રમેશભાઈ          ◉ Level 3   │
│ આજે · 2 સાઇટ                         │
├──────────────────────────────────────┤
│ 10:00–13:00                          │
│ શાહ રેસિડન્સ · બોડકદેવ        [નકશો] │
│ • રસોડું · સુથારી ફિનિશિંગ            │
│ • લિવિંગ · TV યુનિટ                   │
│ ┌──────────────────────────────────┐ │
│ │        હું પહોંચી ગયો છું          │ │  ← big action (state-driven)
│ └──────────────────────────────────┘ │
├──────────────────────────────────────┤
│ 15:00–18:00                          │
│ ઓફિસ · પ્રહલાદનગર            [નકશો] │
│ • કેબિન 2 · પાર્ટિશન                 │
│ [ હું આવીશ ]                          │
├──────────────────────────────────────┤
│ મારું કામ   ·  પ્રશ્નો (1)  ·  હું     │
└──────────────────────────────────────┘
```

### 6.2 Client: Project
```
┌──────────────────────────────────────┐
│ [hero photo of the living room]      │
│ Shah Residence                       │
│ Brief ✓ Layout ✓ Concept ✓ Drawings ● Agencies ○ Execution ○ │
├──────────────────────────────────────┤
│ This week                            │
│ Electrical and plumbing drawings are │
│ being prepared. Kitchen concept is   │
│ approved. Carpentry partner starts   │
│ marking on 12 Nov.                   │
├──────────────────────────────────────┤
│ Next for you                         │
│ ▸ Approve the master bedroom concept │
│ ▸ Pay invoice 2 (due 10 Nov)         │
├──────────────────────────────────────┤
│ Rooms                                │
│ (◔ 30%) Kitchen   (◑ 55%) Living     │
│ (○ 0%) Master BR  (○ 0%) Kids        │
└──────────────────────────────────────┘
```

### 6.3 Office: MOM capture
```
┌──────────────────────────────────────┐
│ MOM · Shah Residence · 31 Oct        │
│ ┌ Kitchen ─────────── Change location ┐│  ← sticky space header
├──────────────────────────────────────┤
│ 1 · Kitchen · Shift the chimney 6"   │
│     left; check with EL-02.          │
│ 2 · Kitchen · Granite sample to be   │
│     shown Thursday.         ▶ 0:07   │
│ 3 · Living · TV unit depth 18".      │
├──────────────────────────────────────┤
│  gu   hi   en                        │
│        ┌──────────┐                  │
│        │   🎤 hold │                  │
│        └──────────┘                  │
│ [ type instead ]            [ Share ] │
└──────────────────────────────────────┘
```

### 6.4 Owner: Project money
```
┌──────────────────────────────────────┐
│ Shah Residence · Money               │
│ Contract 12,50,000  Invoiced 7,50,000│
│ Received 6,00,000   Outstanding 1,50,000 │
├──────────────────────────────────────┤
│ Agencies           Committed  Billed  Paid │
│ Carpentry (Patel)  4,50,000  1,80,000 1,50,000 (client) │
│ Electrical (Shaikh)1,20,000    60,000   60,000 (company) │
│ …                                     │
├──────────────────────────────────────┤
│ Expenses 38,400 · by company 22,000 · recoverable 18,500 · recovered 10,000 │
│ Probable final invoice 12,68,500 · Margin (turnkey only) — │
└──────────────────────────────────────┘
```

## 7. Back office (Odoo)
- Glass theme (`web_theme_glass`) with Revert tokens: paper ground, terracotta primary, Inter + Noto fonts bundled; Identity white-label with the Revert logo and `/office` prefix.
- **Revert app** menu: Home (office boards) · Projects · Sites · Drawings · Queries · Agencies · Visits · MOM · Money (owner, accounts) · Engagement · Configuration.
- Views that matter: project form with a **Spaces** tab (kanban of rooms with progress), **Gantt** on work packages (group by space or agency; plan, committed and actual as three bars), **Drawing register** list with revision and state colours, **Queries** kanban by SLA state, **Visits** calendar and map, **Trade plan** list with undecided-past-due highlighted, **Payment requests** kanban.
- Dashboards use Odoo spreadsheets or `rvt_office` tiles; charts follow the dataviz palette derived from the tokens (terracotta, olive, slate, amber; rose only for office-only states).

## 8. Accessibility and performance
- WCAG 2.2 AA contrast; 48 px targets; visible focus; `prefers-reduced-motion` honoured; haptics on state changes.
- Works at 360 px with no horizontal scroll; large-type setting raises the scale one step.
- Photos lazy-loaded with thumbnails; lists virtualised; no blur effects on agency screens.
- Every icon has a label; states are never colour-only (chip text in the user's language).

## 9. Assets still needed
Logo (vector), brand colours and fonts if any, 20–30 photographs of completed Revert work for heroes and empty states, Gujarati and Hindi copy review by a native speaker from the office, the client-safe status examples the principal is comfortable with.
