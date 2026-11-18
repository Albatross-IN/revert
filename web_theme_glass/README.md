# Glass — Glassmorphic Backend Theme (Odoo 20)

Frosted-glass restyling of the Odoo 20 backend: translucent panes with a bright hairline edge over a
soft colour field. Pure CSS, zero JavaScript, Odoo's own colour tokens for inks, states and the one
indigo accent; supports Community, Enterprise, Enterprise dark mode and a dark mode of its own for
Community.

## Install
1. Copy `web_theme_glass` into your addons path.
2. Update the apps list and install **Glass - Glassmorphic Backend Theme**.
3. Reload the browser. Done.

Disable/enable without uninstalling: *Settings → General Settings → Glass Theme*
(stored in `ir.config_parameter` key `web_theme_glass.enabled`; reload the page after changing).

## The material

`tokens.scss` defines the field and the glass:

| Token | Light | Dark | Meaning |
|---|---|---|---|
| `--gl-ground` + `--gl-field` | `#EDF0F6` + indigo / sky / violet blobs | `#12161E` + the same hues, dimmer | the colour field, fixed to the viewport (`body` background) |
| `--nm-surface` | white 52 % | white 8 % | a pane, a key, a field — one translucent white; nested panes stack whiter |
| `--nm-surface-high` | white 86 % | `#1A1F29` 90 % | floating objects (dropdowns, dialogs): nearly opaque, so text stays legible over anything |
| `--gl-well` | white 22 % | white 3.5 % | a kanban lane, the settings rail, the search panel: the faintest layer |
| `--gl-edge`, `--gl-edge-top` | white 78 % / 95 % | white 10 % / 14 % | the hairline ring and the 1 px light along a pane's top |
| `--gl-hair` | ink 10 % | white 10 % | a seated field's edge, dividers |
| `--gl-cast`, `--gl-cast-strong` | ink 10 % / 18 % | black 45 % / 60 % | the soft cast under a pane / an overlay |
| `--gl-blur`, `--gl-blur-sm` | 18 px / 10 px | | the frost (`gl-blur` mixin) |

The token *names* keep the `--nm-*` prefix of the soft-UI family this theme descends from, so every
component rule reads the same across Slate, Tiles and Glass; only the values are glass:
`--nm-raised*` = cast + edge ring + top light, `--nm-inset*` = hairline ring + 1 px inner shade,
`--nm-well` = the faintest ring. Anything in the family that reads a raise token gets the glass edge
for free.

**Blur budget.** `backdrop-filter` makes a compositing layer per element, so it is applied
deliberately, never through the generic raise mixin: the navbar, the form panes, the kanban lanes,
the chatter, the list header strip and every overlay blur; list rows and kanban cards are tint-only.

## The pane grammar

`static/src/scss/glass.scss` applies the grammar to the three main views (desktop and tablet, ≥ 768 px;
the phone layout in `mobile.scss` is untouched):

* **Form** (`.o_action_manager .o_form_view`): the sheet dissolves; the status bar, the title block
  (or the header wrapper Odoo 20 uses for contacts / employees / products), each `.o_inner_group`
  of a `.o_group.row` (turned into a 12-column grid with a real gap, `col-lg-N` → `span N`), a bare
  field at the sheet root and the notebook each become a pane; the chatter beside the sheet is a
  pane too. Empty groups and empty properties widgets are hidden. Dialog forms keep the plain sheet.
* **List** (`.o_view_controller.o_list_view`): `border-spacing: 0 6px`, transparent cells, and a
  `::after` pseudo-element on each `<tr>` (rows, group rows, totals, the header) that carries the
  pane's fill, corners and edge — so a row is one object, not per-cell seams.
* **Kanban**: lanes are `--gl-well` glass with a light blur, cards are panes (radius 14), a dragged
  card lifts, tilts and turns opaque.

## How it works (performance-oriented)
| Piece | What it does | Cost |
|---|---|---|
| `static/src/scss/tokens.scss` | The field, the glass and every token above, as CSS custom properties on `.o_theme_glass`. Because `web.assets_web_dark` recompiles the backend bundle with the dark variables, the same file produces the dark palette. | compile‑time only |
| `static/src/scss/theme.scss` | Component rules targeting Odoo's structural classes (`.btn`, `.o_input`, `.o_main_navbar`, `.o_kanban_record`, `.o_control_panel`, `.o_home_menu`, `.fc-*`, gantt/grid/cohort…), all scoped under `.o_theme_glass`. Never touches layout or DOM. | one stylesheet in the backend bundle |
| `static/src/scss/form_view.scss` | Form-view UX pass (flat notebook tabs, calm x2many edit rows, aligned labels, mobile card rows, the chatter aside). | part of the same bundle |
| `static/src/scss/glass.scss` | The pane grammar above. Loaded after `form_view.scss` so it wins ties. | part of the same bundle |
| `static/src/scss/discuss.scss` | Discuss, chat windows and the messaging menu. | part of the same bundle |
| `static/src/scss/backlight.scss` | App map kept for `--nm-app` consumers; paints nothing by default. | part of the same bundle |
| `static/src/scss/typography.scss` | Inter (self-hosted, variable) with a seven-step scale and three weights. | two woff2 files |
| `static/src/scss/mobile.scss` | Phone adaptation (< 768 px). | part of the same bundle |
| `static/src/scss/community.scss`, `community_dark.scss` | Community-only readability rules and a dark palette for Community. | Community only |
| `static/src/scss/pos.scss` | Point of Sale UI (`/pos/ui`), a separate bundle with its own soft-clay tokens (not yet glass). | POS bundle only |
| `models/ir_http.py` | Adds one boolean (`glass_theme_enabled`) to the webclient bootstrap qcontext; registers the Community dark assets. | one `get_param` per page load |
| `views/webclient_templates.xml` | Inherits `web.webclient_bootstrap` to add `o_theme_glass` to `<body>` when enabled. | none |
| `models/res_config_settings.py` + view | The Settings toggle. | none at runtime |

## Customising
Change the field (`$gl-ground`, `$gl-blob-*`), the glass (`$nm-surface`, `$gl-edge`), the blur
(`--gl-blur`) or the pane grammar's `--gl-tile-gap`, `--gl-tile-radius`, `--gl-row-radius`,
`--gl-tile-pad` (`glass.scss`). A small module that depends on `web_theme_glass` and sets a few
custom properties after this bundle is all it takes for the runtime tokens.

## Compatibility
Odoo 20.0 Community and Enterprise. Chrome, Edge, Safari, Firefox 103+ (`backdrop-filter`); older
browsers get the same panes without the frost. The list-row panes need `position: relative` on
`<tr>` (every current browser).

## License
OPL-1 (Odoo Proprietary License v1.0). © Hardik Anavadia.
