# Revert — Master lists (draft for correction)

Status: draft v0.1 · 2026-11-18 · **for Revert to correct**: strike what is wrong, add what is missing, rename to the words the team uses.
Used by: project onboarding ([phase1_adoption.md](phase1_adoption.md) §5.2). These lists are data in Setup, so they can be changed any time after launch; this draft only decides what is there on day one.

How it was drafted: from the names already used in Revert's own projects (work items such as "Furniture work", "POP work", "CP fittings", "Water proofing"; rooms such as "Consulting room", "Procedure room", "Pantry"), plus usual practice. Items not seen in Revert's data are marked *(assumed)*.

---

## 1. Trades

A trade is a kind of agency. Each project ticks the trades it needs and names the agency for each.

| # | Trade | Covers | Name in Gujarati / Hindi (for the agency app) |
|---|---|---|---|
| 1 | Civil | Demolition, masonry, plaster, punning, water proofing | સિવિલ / सिविल |
| 2 | Tiles and flooring | Floor tiles, wall tiles, grouting, epoxy | ટાઇલ્સ / टाइल्स |
| 3 | Stone (Salat) | Marble, granite, kitchen platform, cladding | સલાટ / पत्थर |
| 4 | Electrical | Conduit, wiring, points, switchboards, fixtures, testing | ઇલેક્ટ્રિક / इलेक्ट्रिक |
| 5 | Plumbing | Concealed lines, drainage, CP fittings, sanitary ware | પ્લમ્બિંગ / प्लंबिंग |
| 6 | POP / false ceiling | Gypsum and POP ceilings, cornices, punning on ceilings | પીઓપી / पीओपी |
| 7 | Carpenter | Furniture made on site and off site, storage, doors, panelling | સુથાર / बढ़ई |
| 8 | Colour / polish | Paint, polish, texture, wallpaper | કલર / रंग |
| 9 | Aluminium and glass | Windows, glass partitions, mirrors, shower enclosures | એલ્યુમિનિયમ-કાચ / एल्युमिनियम-कांच |
| 10 | Fabrication | MS and SS work, railings, grills, structures | ફેબ્રિકેશન / फैब्रिकेशन |
| 11 | AC | Air-conditioning piping, units, ducting | એસી / एसी |
| 12 | AV, network and intercom | AV system, internet, intercom, CCTV | એવી-નેટવર્ક / एवी-नेटवर्क |
| 13 | Supplied furniture | Bought-in loose furniture, chairs, sofas | ફર્નિચર સપ્લાય / फर्नीचर सप्लाई |
| 14 | Soft furnishing *(assumed)* | Curtains, blinds, upholstery, fabric | પડદા-ફેબ્રિક / पर्दे-फैब्रिक |
| 15 | Landscape *(assumed)* | Garden, planters, outdoor work | ગાર્ડન / गार्डन |

Questions: Is "Salat" the stone mason as read here? Are tiles done by the civil agency or by a separate one? Is anything missing (lift, fire, solar, modular kitchen vendor)?

## 2. Entity types and their usual trades

An entity is one room or zone of the site and becomes one task. When an entity is added, the trades below are pre-ticked for it; the user unticks what does not apply.
✓ = usually needed.

| Entity type | Civ | Tile | Stone | Elec | Plumb | POP | Carp | Colour | Alu-glass | Fab | AC | AV-net | Supp. furn. | Soft |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **Home** | | | | | | | | | | | | | | |
| Living room | ✓ | ✓ | | ✓ | | ✓ | ✓ | ✓ | ✓ | | ✓ | ✓ | ✓ | ✓ |
| Dining | | ✓ | | ✓ | | ✓ | ✓ | ✓ | | | ✓ | | ✓ | |
| Kitchen | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | | | | | | |
| Bedroom | | ✓ | | ✓ | | ✓ | ✓ | ✓ | ✓ | | ✓ | | | ✓ |
| Master bedroom | | ✓ | | ✓ | | ✓ | ✓ | ✓ | ✓ | | ✓ | ✓ | | ✓ |
| Toilet / bathroom | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | | | ✓ | | | | | |
| Pooja room | | ✓ | ✓ | ✓ | | ✓ | ✓ | ✓ | | | | | | |
| Balcony / wash area | ✓ | ✓ | | ✓ | ✓ | | | ✓ | | ✓ | | | | |
| Passage / foyer | | ✓ | | ✓ | | ✓ | ✓ | ✓ | | | | | | |
| Staircase | ✓ | | ✓ | ✓ | | | | ✓ | | ✓ | | | | |
| Garden / backyard | ✓ | | | ✓ | ✓ | | | | | ✓ | | | | |
| **Office** | | | | | | | | | | | | | | |
| Cabin | | ✓ | | ✓ | | ✓ | ✓ | ✓ | ✓ | | ✓ | ✓ | ✓ | |
| Conference / board room | | ✓ | | ✓ | | ✓ | ✓ | ✓ | ✓ | | ✓ | ✓ | ✓ | ✓ |
| Workstation area | | ✓ | | ✓ | | ✓ | ✓ | ✓ | | | ✓ | ✓ | ✓ | |
| Reception / waiting | | ✓ | ✓ | ✓ | | ✓ | ✓ | ✓ | ✓ | | ✓ | ✓ | ✓ | |
| Pantry | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | | | | | | |
| Server / store room | | ✓ | | ✓ | | | ✓ | ✓ | | | ✓ | ✓ | | |
| **Clinic / hospital** | | | | | | | | | | | | | | |
| Consulting room | | ✓ | | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | | ✓ | ✓ | ✓ | |
| Procedure room | ✓ | ✓ | | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | | ✓ | | | |
| Lab | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | | | ✓ | | | |
| **Always added** | | | | | | | | | | | | | | |
| Whole site | ✓ | | | ✓ | ✓ | | | ✓ | | | | ✓ | | |

"Whole site" carries work that belongs to no single room: main electrical board, main water and drainage lines, external civil work, final cleaning.

## 3. Site presets

A preset fills the entity list in one tap; the user then changes counts, renames and adds.

| Preset | Entities created |
|---|---|
| 2 BHK | Living room, Kitchen, Master bedroom, Bedroom, Toilet × 2, Balcony / wash area, Passage / foyer, Whole site |
| 3 BHK | Living room, Dining, Kitchen, Master bedroom, Bedroom × 2, Toilet × 3, Pooja room, Balcony / wash area, Passage / foyer, Whole site |
| 4 BHK / bungalow | 3 BHK + Bedroom, Toilet, Staircase, Garden / backyard |
| Office, small | Cabin × 2, Workstation area, Reception / waiting, Pantry, Toilet, Whole site |
| Office, corporate | Cabin × 3, Conference / board room, Workstation area, Reception / waiting, Pantry, Server / store room, Toilet × 2, Whole site |
| Clinic | Consulting room × 2, Procedure room × 2, Lab, Reception / waiting, Pantry, Toilet × 2, Whole site |
| Empty | Whole site only; add entities by hand |

Extras offered as one-tap additions: Garden / backyard, Terrace, Home theatre, Study, Guest room, Store, Parking, Lift.

## 4. Standard drawing sets

When a trade is ticked on a project, its drawings below are proposed; the user ticks what this project needs. "Client" = normally shown to the client. "Approval" = the client must approve it.

### 4.1 General set (every project)

| Code | Drawing | Client | Approval |
|---|---|---|---|
| ML | Measurement / existing layout | | |
| FL | Furniture layout | ✓ | ✓ |
| WE | Wall elevations (per room) | ✓ | ✓ |
| 3D | Views / concept (per room) | ✓ | ✓ |
| DS | Door and window schedule | | |

### 4.2 Per trade

| Trade | Code | Drawing | Client | Approval |
|---|---|---|---|---|
| Civil | DM | Demolition and new wall layout | ✓ | |
| Civil | WP | Water-proofing areas | | |
| Tiles and flooring | FLR | Flooring layout and pattern | ✓ | ✓ |
| Tiles and flooring | WT | Wall tile layout (toilets, kitchen) | ✓ | ✓ |
| Stone (Salat) | ST | Stone details (platform, cladding, thresholds) | | |
| Electrical | EL | Electrical layout (points) | ✓ | |
| Electrical | SB | Switchboard details | | |
| Electrical | LT | Lighting layout | ✓ | |
| Electrical | LC | Looping / circuit layout | | |
| Plumbing | PL | Plumbing layout (water and drainage) | | |
| Plumbing | TE | Toilet elevations with fitting heights | ✓ | ✓ |
| POP / false ceiling | FC | False ceiling layout | ✓ | ✓ |
| POP / false ceiling | FCS | Ceiling sections and details | | |
| Carpenter | CD | Furniture details (one per piece or room: wardrobe, bed, TV unit, storage) | ✓ | ✓ |
| Carpenter | KD | Kitchen details | ✓ | ✓ |
| Carpenter | DD | Door details | | |
| Colour / polish | CS | Colour and finish schedule | ✓ | ✓ |
| Aluminium and glass | GL | Glass partition and window details | | |
| Fabrication | FB | Fabrication details | | |
| AC | AC | AC layout (units, piping, drain) | ✓ | |
| AV, network and intercom | AV | AV, data and intercom point layout | | |
| Supplied furniture | SF | Loose furniture selection sheet | ✓ | ✓ |
| Soft furnishing | SFN | Curtain and fabric schedule | ✓ | ✓ |
| Landscape | LS | Landscape layout | ✓ | ✓ |

Sheet numbers are the code plus a running number per project (EL-01, EL-02). Questions: Does Revert already use codes or a numbering scheme? Which of these does the office never make? Which drawings does the client normally not receive?

## 5. Roles of the present users (as told on 2026-11-18)

| Person | Role in the system |
|---|---|
| Pratik Anavadiya | Owner and principal consultant (approves drawing releases) |
| Parija | Owner |
| Harshal Sharma | Coordinator |
| Hitesh Mevada, Arpita Amin, Harsha Mahawar, Kishan, Ruchit Shah, Akshay Oda | Draftsman / designer |

Question: do any of the draftsmen also coordinate agencies on site? (A person can hold both roles.)

## 6. People in today's MOM entries (to be matched to agencies)

Today's MOM entries name about 40 people, for example Bherusingh, Rahul bhai, Sanjay Bhai, Jitu Bhai, Munna Bhai, Hanuman Bhai, Om Prakash Bhai, Rajkumar Bhai, Pravin Bhai, Pradip Bhai, Bhavesh Bhai, Vishal Bhai. Several appear twice with different spellings. For the move of existing MOM entries we need, for each person: **trade, agency (firm) name, WhatsApp number**. The full list will be sent as a sheet to fill in, together with the pilot project sheet.
