# Glass Workspace

Companion module to **Glass** (`web_theme_glass`). It adds the interactions the pure-CSS
theme cannot do on its own. Everything is a **per-user preference** (My Preferences →
*Glass Workspace*, or the avatar menu) and every default is stock Odoo behaviour, so
installing the module changes nothing until a user opts in.

## Features

### Split Form View
When enabled, clicking a record in a **list** or **kanban** opens its form in a panel beside
the list instead of navigating away — the Backmate/Spiffy "split view" pattern, on Glass's
design.

* The panel embeds Odoo's **own form view** (`View` component, as `FormViewDialog` does), so
  the header buttons, statusbar, sheet, tabs and chatter all behave exactly as normal.
* The list/kanban is unchanged; the selected record is highlighted.
* Panel header: record title, ‹ › to move between records, ⤢ to open the full form, ✕ to close.
* A teal edge tab collapses/​restores the list so the form can take the full width.
* Draggable divider (position remembered per browser); form on the right or below.
* Off by default → stock Odoo (records open on their own page). Never active on phones or
  inside embedded x2many lists.

### Left pane (optional)
The stock Odoo top bar always stays exactly as it is. A **☰ button** at its left shows/hides
an application pane:

* *Open, full* — apps with icons + names, the current app's sections listed under it.
* *Open, icons* — a 60 px icon rail that expands on hover.
* The pane sits under the top bar and shifts only the action area.

### v3 (2026-09-27): collapsed pane 72 px

The collapsed pane is 72 px (was 60): 12 px + the 40 px key + a gutter + the scrollbar column,
which `scrollbar-gutter: stable` reserves so the keys never move and the bar never overlaps them.
Pane icons take the theme's mono filter at rest; the hovered, open (fly-out) and active app carry
the accent. The scrollbar itself follows the theme's hover-only rule.

### Phones (below 768px)
Glass keeps what Odoo does not have and restyles what it does (the theme draws Odoo's own phone UI in clay).
v2 (2026-09-27): while the shell is on screen the tab bar is the one navigator — Odoo's ☰ in the top bar is hidden
(the Apps and Menu tabs open the same drawers); tab labels are 11 px in the muted ink; the theme's bottom action bar
on record forms sits above the tab bar; the stage button no longer covers the last card's keys.
* **Tab bar** — Apps · Menu · Activity · Account at the bottom of the screen. The tabs open Odoo's OWN phone
  navigation: the app drawer with all apps (Enterprise: the home menu), the drawer with the current app's menus,
  the activity menu, and the burger menu (user, companies, preferences, *Install app*, log out — plus Glass's
  *Theme preferences*, Community's *Dark mode* and a *Developer mode* switch for phones / installed apps).
  Optionally hidden while a record's form is open (Theme preferences › Phone).
* **Stage picker** — on a grouped kanban a floating key opens the list of stages (real server totals); picking one
  filters the kanban on it (a real search domain).
* **Show more** — the theme stacks kanban stages top to bottom; each shows its first four cards and a *Show more*.
* **Calendar** — previous / next keys and a tap on the period title to jump to any month.
* **Gantt** — a vertical gantt (time runs down, one column per row) instead of the sideways timeline.
* **Chatter** — a chatter key on every kanban card, list row and form opens the record's chatter in a small
  window, full screen or a bubble.
* Forms, the breadcrumb, the settings' section picker and PWA install are Odoo 20's own (restyled).

## How it is wired (no template surgery on the core views)
* `res.users` gains `glass_nav`, `glass_split`, `glass_split_side` (self-readable/writable),
  delivered to the web client in `session_info`.
* `glass_prefs` service holds the reactive preferences (+ per-browser panel width / pane state).
* The split panel is injected through **`web.Layout`** (patched), which every view — including
  app-specific list/kanban subclasses — renders through.
* The left pane is a **main_components** overlay; the ☰ button is prepended to the navbar.

## Requirements
`web`, `mail`, `web_theme_glass`. Odoo 20.0, Community and Enterprise (the phone gantt only where `web_gantt`
is installed).

## Odoo 20 notes
* Odoo 20 runs **OWL 3**: every component declares its props with `useProps`, keeps state in `proxy` / `signal`,
  reads refs as `signal.ref()`, and templates write `this.…` explicitly. Nothing relies on the Owl 2
  compatibility layer except `useSubEnv` / `render` from `@web/owl2/utils`, which Odoo's own views still use.
* Shared requests (does this model have a chatter? how many messages?) go through the global ORM service:
  Odoo 20 leaves the calls of a destroyed component pending for ever, and a grouped kanban builds its cards twice.
* `res.users` preference fields are `user_writeable=True` (Odoo 20 replaced `SELF_WRITEABLE_FIELDS`).
* Phones use Odoo 20's native form (outlined fields, restyled by the theme), app drawer, burger menu, breadcrumb
  and settings section picker; the 19 module's own phone form, launcher sheets and install prompt are gone.
