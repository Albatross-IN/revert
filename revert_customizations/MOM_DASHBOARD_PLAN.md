# Implementation Plan — Project MOM Dashboard

| | |
|---|---|
| **Requirement** | C — MOM viewer action on `project.project` |
| **Module** | `revert_customizations` |
| **Odoo version** | 18.0 |
| **Target version** | 18.0.1.3.0 |
| **Depends on** | Requirements A and B (MOM activity type, `is_mom`, `mom_*` fields) |
| **Status** | Built — all 7 phases delivered |
| **Date** | 31 August 2026 |

A project holds many tasks; each task holds many MOM entries. Today the only way
to read them is to open tasks one at a time. This adds a **MOM Dashboard**: one
screen per project showing every MOM entry across all its tasks, with filters,
totals and charts, reached from a button on the project's kanban card.

---

## 1. What the user gets

1. On the Projects kanban, the card's ⋮ menu gains a **MOM Dashboard** entry under
   *Reporting*, beside *Tasks Analysis* and *Burndown Chart*.
2. Clicking it opens a full-screen dashboard scoped to that project.
3. The dashboard shows, for every MOM entry on every task in the project:
   - a row of totals — entries, open, overdue, closed, contacts involved, photos;
   - a status breakdown and a "top Related To" breakdown as charts;
   - a volume-over-time chart;
   - a filterable table of the entries themselves, with site-photo thumbnails.
4. Clicking any row opens the task it belongs to. Breadcrumb returns to the dashboard.

---

## 2. The problem that has to be solved first

MOM entries are `mail.activity` records. An activity points at its record through
`res_model` (Char) and `res_id` (**Many2oneReference**) — a loose pointer, not a
foreign key. You cannot join it, group by it, or filter through it to a project.

Every part of this dashboard — each filter, each chart, each total — is a grouped
query over MOM entries scoped to a project. None of it can be written against
`res_id`. So the first piece of work is not the screen; it is giving MOM
activities a real link to their task and project.

**Add to `mail.activity`:**

| Field | Definition | Why |
|---|---|---|
| `mom_task_id` | Many2one `project.task`, `compute` + `store=True`, from `res_model` / `res_id` when the entry is a MOM entry | Turns the loose pointer into a real relation |
| `mom_project_id` | Many2one `project.project`, `related='mom_task_id.project_id'`, `store=True`, indexed | The column every dashboard query filters on |

Both are stored computed fields, so the ORM populates them for existing rows during
the upgrade. **No migration script is needed.**

Worth noting what else these two fields unlock at no extra cost: once
`mom_project_id` exists, standard pivot, graph and list views over `mail.activity`
work on MOM data immediately. That is a useful fallback if the custom dashboard is
ever descoped, and a useful cross-check while building it.

---

## 3. Architecture

Three layers, each testable on its own.

```
project.project.action_open_mom_dashboard()      ← button target
        │  returns ir.actions.client (tag: mom_dashboard, context: active_id)
        ▼
OWL client action  static/src/mom_dashboard/
        │  orm.call("project.project", "get_mom_dashboard_data", [id, filters])
        ▼
project.project.get_mom_dashboard_data(filters)  ← one JSON payload per render
        │  _read_group over mail.activity, domain anchored on mom_project_id
        ▼
mail.activity  (mom_project_id, mom_task_id, mom_partner_id, mom_sequence, …)
```

**All aggregation happens in Python.** The client sends a filter state and receives
finished numbers. The alternative — shipping raw records and counting in JavaScript —
breaks the moment a project has a few thousand entries, and would bypass record
rules on the totals.

**Everything runs in the user's environment, never `sudo`.** A user who cannot read
a task must not see its minutes counted in a total.

---

## 4. Screen layout

```
┌────────────────────────────────────────────────────────────────────┐
│  ‹ Mr. Vinod- Hemdeep Society · MOM Dashboard                      │
│  [ All | Open | Overdue | Closed ]   [Period ▾] [Related To ▾]     │
│  [Assignee ▾] [Task ▾] [☐ With photo only]              [Reset]    │
├────────────────────────────────────────────────────────────────────┤
│  ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐            │
│  │  142   │ │   38   │ │   11   │ │  104   │ │   17   │            │
│  │ Entries│ │  Open  │ │Overdue │ │ Closed │ │Contacts│            │
│  └────────┘ └────────┘ └────────┘ └────────┘ └────────┘            │
├──────────────────────────────┬─────────────────────────────────────┤
│  Status split (donut)        │  Top Related To (horizontal bar)    │
├──────────────────────────────┴─────────────────────────────────────┤
│  Entries per month, open vs closed (stacked bars)                  │
├────────────────────────────────────────────────────────────────────┤
│  Sr. │ Task │ Remark │ Related To │ Assigned │ End Date │ 📷 │ ●   │
│  … click a row → the task form                                     │
└────────────────────────────────────────────────────────────────────┘
```

Overdue is the number that should draw the eye — it is the reason someone opens
this screen. It gets the one piece of semantic colour; the rest of the tiles stay
neutral.

---

## 5. Filters

All applied server-side by building a domain in `get_mom_dashboard_data`. The
client holds only the filter state.

| Filter | Control | Domain contribution |
|---|---|---|
| Status | Segmented buttons | `active`/`date_deadline` combinations for open / overdue / closed |
| Period | Preset dropdown (This month, This quarter, This year, Custom) | `date_deadline` between |
| Related To | Multi-select of partners present in the data | `mom_partner_id in [...]` |
| Assignee | Multi-select of users present in the data | `user_id in [...]` |
| Task | Multi-select of tasks in the project | `mom_task_id in [...]` |
| With photo only | Checkbox | `mom_site_photo != False` |

The Related To / Assignee / Task option lists are returned by the same call that
returns the data, computed from the project's own entries — so the dropdowns never
offer a value that would yield an empty screen.

Closed entries are included by default. They are the record of what was settled,
and hiding them would make the totals disagree with the MOM PDF.

---

## 6. Build phases

Each phase leaves the module installable and the previous phase working.

### Phase 1 — Data link *(the enabler; nothing visible yet)*
- `models/mail_activity.py`: add `mom_task_id`, `mom_project_id` and their compute.
- Verify against a standard pivot view on `mail.activity` grouped by
  `mom_project_id` before writing any JavaScript.
- Bump to `18.0.1.3.0`.

### Phase 2 — Backend aggregation
- `models/project_project.py` (new):
  - `_get_mom_domain(filters)` — the single place a domain is built.
  - `get_mom_dashboard_data(filters)` — returns `{kpis, by_status, by_partner, by_task, by_period, entries, filter_options}`.
  - `action_open_mom_dashboard()` — returns the `ir.actions.client`.
- Testable from the shell before any UI exists.

### Phase 3 — Client action shell
- ~~`data/mom_dashboard_action.xml`~~ — **not needed.** `action_open_mom_dashboard()` returns the client action dict directly, so there is no `ir.actions.client` record to keep in sync. Add one only if the dashboard ever needs its own menu item.
- `static/src/mom_dashboard/mom_dashboard.js` — OWL component, registered as
  `mom_dashboard` in `registry.category("actions")`.
- `mom_dashboard.xml` — the OWL template.
- `mom_dashboard.scss` — styles.
- `__manifest__.py`: an `assets` entry adding the three files to `web.assets_backend`.
- At the end of this phase the screen renders the KPI tiles from real data.

### Phase 4 — Filters
- Filter bar component, filter state in a `useState`, refetch on change.
- Debounce refetch so dragging a date range does not fire a call per keystroke.

### Phase 5 — Charts
- `onWillStart: await loadBundle("web.chartjs_lib")` — in Odoo 18 Chart.js is a
  **lazy** bundle, not part of `assets_backend`. Rendering a chart without this
  fails with `Chart is not defined`. This is the single most common way a custom
  Odoo dashboard breaks.
- Three charts, each a small component wrapping one canvas, destroyed on unmount.

### Phase 6 — Entries table and drill-through
- Paginated table, site-photo thumbnails served through `/web/image`.
- Row click → `action.doAction` opening the task form, so the breadcrumb returns
  to the dashboard.

### Phase 7 — Entry points
- `views/project_project_views.xml` (new): xpath into `project.view_project_kanban`,
  adding a *MOM Dashboard* item to the card menu's Reporting column.
- A smart button on the project form showing the MOM entry count.

---

## 7. Files

| File | Status |
|---|---|
| `models/mail_activity.py` | edit — two fields |
| `models/project_project.py` | new — aggregation + action |
| `models/__init__.py` | edit |
| `views/project_project_views.xml` | new — kanban menu item, form smart button |
| `static/src/mom_dashboard/mom_dashboard.js` | new |
| `static/src/mom_dashboard/mom_dashboard.xml` | new |
| `static/src/mom_dashboard/mom_dashboard.scss` | new |
| `__manifest__.py` | edit — version, data, assets |

No new model, no new access rights: the dashboard reads `mail.activity`, which
users can already read.

---

## 8. Things that will bite, and the answer

| Risk | Handling |
|---|---|
| Chart.js undefined | `loadBundle("web.chartjs_lib")` in `onWillStart` (Phase 5) |
| A client action has no standard search bar, no favourites, no export | Accepted — it is the cost of a custom screen. The pivot/graph views that Phase 1 enables cover ad-hoc analysis and export |
| Site photos are large; a table of 200 thumbnails is heavy | Serve via `/web/image/mail.activity/<id>/mom_site_photo/64x64`, never inline base64 in the payload |
| Charts leak between renders | Keep the Chart instance in a ref and `destroy()` it in `onWillUnmount` |
| `mom_project_id` goes stale if a task moves project | It is a stored related field — the ORM recomputes it on the task's `project_id` write |
| A project with 5,000 entries | Aggregates come from `_read_group`; only the entries table is paginated. No unbounded `search()` |
| Sub-task entries | Included — a sub-task belongs to the project, and its minutes are the project's minutes |

---

## 9. Decisions to confirm before Phase 1

| # | Decision | Recommendation |
|---|---|---|
| C-1 | Should the dashboard cover one project, or allow comparing several? | One project. It is opened from a project card; a cross-project view is a different screen with a different question behind it |
| C-2 | Closed entries in the totals by default? | Yes, with a status filter to exclude them |
| C-3 | Is a photo gallery mode needed (site photos as a grid)? | Not in this scope. Cheap to add later as a table/gallery toggle if users ask |
| C-4 | Should the dashboard offer "Print MOM" for the whole project? | Out of scope. The existing PDF is per task; a project-level MOM is a separate requirement with its own layout questions |

---

## 10. Sequencing

Phases 1–2 are the substance and carry the risk; they are backend-only and
verifiable from the shell. Phases 3–7 are UI assembly on top of a payload that is
already known to be correct.

Recommended first delivery: **Phases 1 and 2**, plus a temporary pivot view on
`mail.activity` grouped by project and status. That answers the underlying
question — "what is outstanding across this project?" — before a line of
JavaScript exists, and proves the data layer against real records.

---

*Plan · 31 August 2026 · `revert_customizations` 18.0 · awaiting sign-off on C-1 to C-4*
