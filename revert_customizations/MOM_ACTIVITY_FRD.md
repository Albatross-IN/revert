# Functional Requirements — MOM as an Activity Type on Project Tasks

| | |
|---|---|
| **Module** | `revert_customizations` (custom addon path `/opt/odoo18/custom/revert`) |
| **Odoo version** | 18.0 |
| **Target object** | `project.task` |
| **Related module** | `admin_notes_viewer` (same addon path) |
| **Status** | Draft for sign-off |
| **Date** | 31 August 2026 |

**Requirement in one line:** introduce a new activity type **MOM**, available only when
the record is a project task, and give activities of that type three fields the standard
activity does not have — **Related To** (a contact), **Site Photo**, and **Sequence**.

---

## 1. Current implementation (as-built)

This section documents what the code does today. It is the baseline the requirements
below change.

### 1.1 Modules in the addon path

| Module | Depends on | What it does |
|---|---|---|
| `revert_customizations` | `project`, `project_enterprise` | MOM meetings and Responsibilities on project tasks, the MOM PDF, and an "All Tasks & Sub-Tasks" list. |
| `admin_notes_viewer` | `mail`, `base` | A System-Administrator-only "Activity Logs" menu listing every `mail.message` note across all objects, with an *Open Document* button. |

### 1.2 Models

**`mom.meeting`** — `models/mom_meeting.py`, ordered by `task_id, seq`

| Field | Type | Notes |
|---|---|---|
| `task_id` | Many2one `project.task` | Required, `ondelete='cascade'` |
| `seq` | Integer | Read-only; set in `create()` to the highest `seq` on that task + 1 |
| `remarks` | Char | "Remark / Observation / Suggestion / Opinion" in the PDF |
| `related_to` | **Char** | Free text — not linked to a contact |
| `end_date` | Date | |
| `site_photo` | Binary | Plain binary, no image resizing |

**`person.person`** ("Personas", exposed as *Responsibilities*) — same file, same
auto-`seq` pattern

| Field | Type |
|---|---|
| `task_id` | Many2one `project.task`, required, cascade |
| `seq` | Integer, read-only, auto |
| `from_client` / `from_architect` / `from_agency` | Char |

**`project.task`** — `models/project_task.py` adds:

- `mom_meeting_ids` — One2many to `mom.meeting`
- `person_ids` — One2many to `person.person`, labelled *Responsibilities*
- `agenda` — Text, `tracking=True`, labelled *Details*

**`mail.message`** — `admin_notes_viewer/models/mail_message.py` adds
`action_open_related_document()`, which opens the message's source record or shows a
warning notification when the record is gone.

### 1.3 Views, report and security

| Artefact | File | Detail |
|---|---|---|
| Task form page *MOM Meetings* | `views/project_task_views.xml` | Inherits `project.view_task_form2`, inserted after `description_page`. Holds `agenda`, an editable `person_ids` list, and an editable `mom_meeting_ids` list with `site_photo` as a 64×64 image widget. |
| *All Tasks & Sub-Tasks* list, action and menu | same file | Standalone `project.task` list grouped by project and parent, under the Project main menu. |
| MOM PDF template `task_report` | `views/project_task_report.xml` | Heading "MOM", the agenda, a Responsibilities table over `person_ids`, then a minutes table over `mom_meeting_ids` (Sr. No., Remark, Related to, End Date, Site photo). |
| Print actions | same file | The template is bound **twice**: a `<report>` shortcut named *Extract in PDF* and a separate `ir.actions.report` record named *MOM PDF*. |
| Access rights | `security/ir.model.access.csv` | Full CRUD on both `mom.meeting` and `person.person` for `base.group_user`. |

### 1.4 Why this is being changed

The MOM table is inert data. A minute recorded in it:

- cannot be **assigned** to anyone;
- has no **follow-up** — `end_date` is a printed date, not a deadline the system chases;
- never appears in the assignee's *My Activities*, in the task's activity area, or in
  any standard "what is pending" view;
- records *Related To* as free text, so the same contractor is spelled three ways and
  cannot be filtered on;
- leaves no audit trail when the point is settled — it is simply edited or deleted.

Expressing a MOM point as a **scheduled activity** fixes all five with framework
behaviour rather than custom code, and makes closed points visible in the existing
`admin_notes_viewer` log.

---

## 2. Glossary

| Term | Meaning |
|---|---|
| MOM | Minutes of Meeting — one recorded observation, remark, suggestion or action point arising from a site or client meeting. |
| MOM activity | A `mail.activity` record whose activity type is *MOM*, attached to a project task. |
| MOM entry | The user-facing name for a MOM activity, open or closed, as it appears on the task and in the MOM PDF. |
| Related To | The person or company a MOM entry concerns — the client, architect, consultant or contractor answerable for the point. |
| Legacy MOM line | An existing `mom.meeting` record. |

---

## 3. Functional requirements

Numbered for traceability into build and UAT. **Must** is in scope for this release;
**Should** is in scope but may be deferred if it threatens the date.

### FR-01 — A new activity type "MOM" exists · *Must*

The module ships an activity type named **MOM** as installable data, so it is present in
every database where `revert_customizations` is installed and is never created by hand.

It carries a distinguishing icon and decoration so MOM entries are visually separable
from Email, Call, Meeting and To-Do in the activity list.

### FR-02 — MOM is offered only on project tasks · *Must*

The MOM type is restricted to the model `project.task`. Scheduling an activity on a task
offers MOM in the type list; scheduling one on a sale order, invoice, contact or any
other record does not offer it and does not allow it to be selected.

An attempt to attach a MOM activity to a non-task record — by import, automated action
or API call — is rejected with a clear message.

### FR-03 — MOM activities carry three additional fields · *Must*

Beyond the standard activity fields (Activity Type, Summary, Due Date, Assigned to,
Notes), a MOM activity records:

| Label | Type | Required | Behaviour |
|---|---|---|---|
| Related To | Many2one → `res.partner` | Yes (see D-1) | Any contact or company. Defaults to the task's customer when the task has one; the user may change it. Searchable, filterable and groupable. Replaces today's free-text `related_to`. |
| Site Photo | Image | No | One photograph of the site condition being minuted. Uploaded from file or phone camera, shown as a thumbnail, opens full size on click, downscaled on upload so large phone photos do not bloat the database. |
| Sequence | Integer | System-set | The serial number of the entry within its task. Assigned automatically, read-only to the user, printed as "Sr. No." on the MOM PDF. Same numbering intent as today's `mom.meeting.seq`. |

### FR-04 — The three fields appear only for MOM · *Must*

Related To, Site Photo and Sequence are hidden whenever the selected activity type is
anything other than MOM, and appear the moment the user picks MOM — in the *Schedule
Activity* dialog, in the activity edit form, and anywhere else an activity is created or
edited.

The visibility rule keys off a property of the activity **type**, not a hardcoded record
ID, so a second MOM-like type can be added later without touching the views.

### FR-05 — Sequence numbering rules · *Must*

- Numbering starts at `1` and is **per task**: each project task has its own MOM entries
  1, 2, 3… This matches the existing `mom.meeting` behaviour and the "Sr. No." column of
  the current PDF.
- The number is assigned when the MOM activity is created and never changes afterwards,
  so a number quoted in a circulated PDF still identifies the same point later.
- Closed entries keep their number and continue to occupy it; a new entry always takes
  the next number above the highest ever used on that task, closed entries included.
- Deleting an entry leaves a gap. Numbers are never renumbered or reused.
- Sub-tasks number independently of their parent task.

### FR-06 — Closing a MOM entry preserves its data · *Must*

Standard Odoo deletes an activity record when it is marked done, keeping only a chatter
note. That would destroy the Related To, Site Photo and Sequence of every closed MOM
point and make the MOM PDF incomplete the day after a meeting is closed out.

The MOM activity type must therefore be configured to **keep done activities**, so a
completed MOM entry is retained (archived, not deleted) with all three fields intact,
stays visible in the task's activity history, and stays printable.

The closing feedback the user types is retained as the entry's closure remark.

> ⚠ **Highest-risk requirement.** If FR-06 is missed the feature demos perfectly and
> loses data silently in production. It is the first item on the UAT script.

### FR-07 — MOM entries are visible on the task · *Must*

A user opening a project task can see all MOM entries for that task — open and closed —
in one place, ordered by Sequence, showing at minimum: Sr. No., Summary, Related To,
Assigned to, Due Date, Site Photo thumbnail, and status (planned / today / overdue /
done).

This is added **below** the existing `mom_meeting_ids` list, which stays in place.
The *Details* (agenda) field and the *Responsibilities* list are also unchanged.
Nothing that worked before is removed — the MOM activity work is additive.

Open MOM entries also continue to appear in the standard chatter activity area and in the
assignee's *Activities* views alongside every other activity type.

### FR-08 — The MOM PDF prints activity-based entries · *Must*

The existing minutes table keeps printing `mom_meeting_ids` exactly as before. A
**second** table is appended for MOM activities, printed only when the task has any, so a
task using only legacy lines produces exactly the PDF it produced before.

The MOM activity table prints per row: Sr. No. (Sequence), Remark (Summary), Related to
(contact name), End Date (Due Date), Site photo — in Sequence order, closed entries
included and visibly marked. The heading, the agenda paragraph and the Responsibilities
table are unchanged.

Photos print correctly whatever format was uploaded — JPEG from a phone included — rather
than assuming PNG.

### FR-09 — Search, filter and reporting · *Should*

MOM entries can be filtered by Related To, assignee, due date and open/closed state, and
grouped by Related To, so a user can answer "every open point against this contractor,
across all tasks" — impossible today because Related To is free text.

### FR-10 — Legacy MOM data · *Should*

Existing `mom.meeting` records are migrated to MOM activities on the same task,
preserving:

| Legacy field | Becomes |
|---|---|
| `seq` | Sequence |
| `remarks` | Summary / notes |
| `related_to` (Char) | Related To (`res.partner`) where the text matches a contact exactly; otherwise carried into the notes and flagged for manual correction |
| `end_date` | Due Date |
| `site_photo` | Site Photo |
| `task_id` | The activity's record |

Migrated entries are created in the closed-but-retained state so they do not flood users'
activity queues with historic points. No legacy line is dropped, including ones whose
Related To cannot be matched. **The legacy lines and their list on the task form are kept
indefinitely** — copying them into activities does not remove them.

### FR-11 — Access rights · *Must*

Any user who can read a project task can see its MOM entries. Any user who can schedule
an activity on that task can create one. Editing and closing follow standard activity
rules — the assignee and users with write access on the task. No new security group is
introduced, and the existing `base.group_user` access on `mom.meeting` and
`person.person` is left in place for the legacy data.

### FR-12 — Photo handling constraints · *Should*

Site photos are stored so a task with fifty MOM entries stays usable: images are
downscaled on upload, thumbnails are used in list views and the PDF, and the full
resolution image is fetched only when opened. Today's `site_photo` is a raw Binary with
no limit.

### FR-13 — Closed MOM points appear in the Activity Logs · *Should*

Because closing an activity posts a chatter message, closed MOM points appear in the
existing *Activity Logs → All Logged Notes* view from `admin_notes_viewer`, and its *Open
Document* button opens the task. No change to that module is required; this requirement
exists so it is verified rather than assumed.

### FR-14 — Nothing else on the task changes · *Must*

The *Details* (agenda) field, the *Responsibilities* list, the *All Tasks & Sub-Tasks*
view and menu, and both existing print actions remain available and behave as they do
today.

---

## 4. Business rules and validation

| Rule | Condition | System response |
|---|---|---|
| BR-1 | Type MOM selected, Related To empty, user saves | Save blocked, message names the missing field. |
| BR-2 | Type MOM forced onto a record that is not a project task | Rejected on save with a clear message. |
| BR-3 | User tries to edit Sequence | Not possible — read-only in every view. |
| BR-4 | Type changed **from** MOM to another type after values were entered | MOM fields hide and their stored values are cleared, so no orphan data prints. |
| BR-5 | Type changed **to** MOM on an existing activity | MOM fields appear; a Sequence is assigned on save. |
| BR-6 | MOM entry marked done | Entry retained with all fields, chatter note posted, entry still prints on the MOM PDF. |
| BR-7 | Task duplicated | MOM entries are **not** copied — minutes belong to the meeting that produced them. |
| BR-8 | Task deleted | Its MOM entries go with it, matching today's `ondelete='cascade'` on `mom.meeting`. |

> **Confirm before build** — BR-4 and BR-7 are judgement calls made on your behalf. If
> the business would rather keep MOM values when the type changes, or carry minutes into a
> duplicated task, say so now; both flip cheaply before build and awkwardly after.

---

## 5. Acceptance criteria

The UAT script. Each maps to the requirements above.

**AC-1 · FR-01, FR-02**
- *Given* I am on a project task
- *When* I click Activities and open the type list
- *Then* MOM is offered; and on a contact or an invoice, it is not.

**AC-2 · FR-03, FR-04**
- *Given* the Schedule Activity dialog is open on a task
- *When* I select type MOM
- *Then* Related To, Site Photo and Sequence appear; selecting To-Do instead hides all three.

**AC-3 · FR-05**
- *Given* a task with no MOM entries
- *When* I create three MOM entries, delete the second, then create a fourth
- *Then* the numbers read 1, 3, 4 — never reused, never renumbered.

**AC-4 · FR-06**
- *Given* an open MOM entry with a Related To contact and a site photo
- *When* I mark it done with feedback
- *Then* the entry still exists with its number, contact and photo; the chatter shows it
  was closed; and it still prints on the MOM PDF.

**AC-5 · FR-08**
- *Given* a task with four MOM entries, two closed, photos uploaded as JPEG
- *When* I print the MOM PDF
- *Then* all four rows print in serial order, every photo renders, closed rows are marked
  as closed, and the agenda and Responsibilities table are unchanged.

**AC-6 · FR-10**
- *Given* a database with existing `mom.meeting` lines
- *When* the module is upgraded
- *Then* every legacy line appears as a retained MOM entry on the same task with its
  number, remark, date and photo intact, and unmatched Related To values are visible in
  the notes rather than lost.

**AC-7 · FR-11**
- *Given* a project user who is not the assignee
- *When* they open the task
- *Then* they can read every MOM entry and add a new one, with no error and no missing field.

**AC-8 · FR-13**
- *Given* a MOM entry closed in AC-4
- *When* an administrator opens Activity Logs → All Logged Notes
- *Then* the closure appears, and *Open Document* opens the task.

---

## 6. Scope boundary

**In scope**

- MOM activity type, restricted to project tasks
- Related To, Site Photo, Sequence on MOM activities
- Conditional display in all activity dialogs and forms
- Retention of closed entries
- MOM entry list on the task form, **in addition to** the `mom_meeting_ids` list
- MOM PDF minutes table driven by activities
- One-off migration of existing `mom.meeting` lines (copy, not move)

**Out of scope**

- Any change to *Responsibilities* (`person.person`), the agenda field, or the legacy MOM list
- Emailing the MOM PDF to attendees on close
- Portal or customer-facing view of MOM entries
- Multiple photos or attachments per entry
- Digital sign-off or approval of minutes
- Changes to `admin_notes_viewer` or to the *All Tasks & Sub-Tasks* view
- Mobile app-specific screens

---

## 7. Open decisions

Four points need a business answer. The assumed default is in force unless you say
otherwise; none of them blocks the start of build.

| # | Decision | Assumed default |
|---|---|---|
| D-1 | Is Related To mandatory on every MOM entry? | Yes — a point with nobody answerable for it is not a minute. |
| D-2 | Does Sequence run per task, or continuously per project? | Per task, matching `mom.meeting.seq` and the current PDF. |
| D-3 | Does the legacy MOM list stay on the form? | **Yes — decided 31 Aug 2026. Existing behaviour is kept as it is; all MOM activity work is additive.** Reverses the earlier recommendation. |
| D-4 | Does the PDF print open entries only, or open and closed? | Both, with closed rows marked — a circulated MOM normally shows what was resolved. |

---

## 8. Implementation notes

Not requirements — the mapping onto Odoo 18 that shows each requirement is achievable
with framework behaviour rather than custom machinery.

| Requirement | Odoo 18 mechanism |
|---|---|
| FR-01 | An `ir.model.data`-backed `mail.activity.type` record in a new `data/` file, added to the manifest. |
| FR-02 | `mail.activity.type.res_model` set to `project.task`. Core already filters the type list by model (`mail/models/mail_activity_type.py`) and validates it on write, so both halves of FR-02 come free. |
| FR-03 | Fields added to `mail.activity` by inheritance; Site Photo as `fields.Image` with a max dimension, satisfying FR-12 at the same time. |
| FR-04 | A boolean on `mail.activity.type`, mirrored as a related field onto **both** `mail.activity` and the `mail.activity.schedule` wizard, driving `invisible` in `mail.mail_activity_view_form_popup` (editing an activity) and `mail.mail_activity_schedule_view_form` (the chatter's Schedule Activity dialog, which is a wizard, not a `mail.activity` form). No XML ID hardcoded in a view. |
| FR-05 | Sequence computed on create from the highest value among activities of that type on the same `res_id`, **including archived ones**, so FR-05's no-reuse rule survives FR-06. |
| FR-06 | `keep_done = True` on the MOM activity type. Core then archives the activity on completion instead of unlinking it (`mail/models/mail_activity.py`, `_action_done`). |
| FR-07 | A One2many on `project.task` filtered to MOM activities with `active_test=False`, rendered on the existing *MOM Meetings* page. |
| FR-08 | The second table of `task_report` iterates that field instead of `mom_meeting_ids`; the photo `<img>` uses the record's own mimetype rather than the hardcoded `data:image/png;base64` in place today. |
| FR-10 | A migration script under `migrations/18.0.x/` reading `mom.meeting` and creating archived MOM activities. |

**Files touched:** `models/mail_activity.py`, `models/mail_activity_type.py` and `models/mail_activity_schedule.py` (new),
`models/project_task.py`, `data/mail_activity_type_data.xml` (new),
`views/mail_activity_views.xml` (new), `views/project_task_views.xml`,
`views/project_task_report.xml`, `__manifest__.py`, plus a migration script.
`admin_notes_viewer` is not modified.

---

## 9. Observations from the code read

Found while reading the existing module. None of these block the MOM work; listed so the
decision to fix or leave them is deliberate.

| # | Observation | Impact |
|---|---|---|
| O-1 | `views/project_task_report.xml` registered the same template twice — a `<report>` shortcut named *Extract in PDF* and an `ir.actions.report` named *MOM PDF*. **The `<report>` element is not valid in Odoo 18** (`odoo/import_xml.rng` allows only `record`, `menuitem`, `template`, `asset`, `delete`, `function`), so the file failed RelaxNG validation and the module could not load. | Fatal, not cosmetic. Fixed: the shortcut was removed and its `print_report_name` folded into the `ir.actions.report` record, leaving one Print entry. |
| O-2 | The report renders photos as `data:image/png;base64` regardless of the real format. | Fragile for JPEG site photos; addressed by FR-08. |
| O-3 | `mom.meeting.related_to` is free text. | The reason FR-03 makes it a `res.partner` link. |
| O-4 | `project.task.agenda` is declared with a `placeholder` argument on the field. Placeholder is a view attribute, not a field attribute; the view already sets it correctly. | Cosmetic — the field-level argument does nothing. |
| O-5 | `revert_customizations/__manifest__.py` declares no `license` key, unlike `admin_notes_viewer` which declares LGPL-3. | Odoo assumes LGPL-3 and logs a warning. |
| O-6 | The manifest depends on `project_enterprise`, but only the Gantt view mode in the *All Tasks & Sub-Tasks* action needs it. | The module cannot install on Community. Intentional if the deployment is Enterprise. |

---

*Draft · 31 August 2026 · `revert_customizations` 18.0 · awaiting sign-off on D-1 to D-4*
