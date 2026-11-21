# Identity — Odoo 20 debranding

`identity` white-labels an Odoo 20 instance (Community or Enterprise): brand
name, logos, favicon, PWA metadata, texts, e-mail footers, vendor links, the
chat bot, and a complete redesigned application icon set.

Ported from the Odoo 19 version (`19.0` line); the technical name stays
`identity`, so databases upgraded from 19 keep their configuration.

## What it changes

| Surface | Result |
|---|---|
| Browser tab title | `<Action> - <Brand>` (fallback `<Brand>` instead of `Odoo`) |
| Favicon, apple-touch icon, PWA manifest (name, icons, theme colour), offline page | brand icon / colour |
| Login page, portal & website footers, e-mail layouts | `Powered by <Brand>` (linked to your site) or nothing; the login card shows the company logo, else the brand logo (Odoo 20 would show none) |
| `/web/binary/company_logo` fallback (no DB / default company logo) | brand logo |
| Database manager / selector | branded from the config file or built-in defaults |
| User menu | `Help` → your support URL (hidden if empty); `My Odoo.com Account` removed |
| Settings → About | brand + platform version, no vendor links |
| Documentation links in Settings (relative paths and absolute odoo.com documentation URLs) | your documentation base URL, or hidden; third-party documentation links are kept |
| Community "Upgrade to Enterprise" dialog | opens your website instead of odoo.com |
| Enterprise "Promote Studio" systray | removed |
| Every `Odoo` in client-side text (`_t()` + OWL templates) | brand name (`OdooBot` → bot name) |
| Every `Odoo` in server-rendered pages, reports, e-mails, view labels / help | brand name |
| Stock Odoo image URLs in rendered pages (`logo.png`, `odoo_logo_tiny.png`, `favicon.ico`, `odoo-icon-*.png`, the login page's OpenGraph `og_image.png`) | brand images |
| Website favicon while it still holds the stock one | brand favicon |
| Apps list (`ir.module.module`) | Identity icons, debranded summaries, no `Learn More` → odoo.com |
| OdooBot | renamed (default *Assistant*), brand avatar, onboarding messages debranded |
| Application icons: home menu, navbar, Apps, Settings sidebar, PWA shortcuts | the Identity icon set (89 minimal neumorphic SVG tiles, Community + Enterprise) |
| Web-client URL prefix `/odoo/...` | `/app/...` (configurable); `/odoo/...` becomes a permanent redirect; login-page link previews (OpenGraph) work with the new prefix |

Everything is reversible: uninstalling restores the stock icons, bot name and
avatar.

## Configuration

**Settings → Identity** (system administrators):

* **Brand** — name (defaults to the company name), website, theme colour, bot name
* **Logo and icon** — wordmark (login / footers) and square icon (favicon / PWA / bot avatar)
* **Links** — support URL (`Help` entry), documentation base URL, `Powered by` toggle
* **Behaviour** — text replacement, Identity icons (+ *Refresh app icons*), hide vendor links

Brand values are per company; behaviour switches are global.

Pages served without a database (database manager) use built-in defaults.
Override them in the server config file:

```ini
[options]
identity_name = Acme
identity_url = https://www.acme.example
```

(Odoo logs an "unknown option" warning for these keys at start-up; that is expected.)

### Web-client URL prefix

Stock Odoo 20 serves the backend under `/odoo` (e.g. `/odoo/users/res.users/8`).
Identity serves it under `/app` by default and redirects every `/odoo/...` URL
permanently to the new prefix, so bookmarks, e-mail links and modules that
still build `/odoo` links keep working. Rendered pages, the PWA manifest, the
service worker and the JavaScript router all use the new prefix.

Routes are registered at start-up, so the prefix comes from the server config
file and needs a restart to change:

```ini
[options]
identity_web_prefix = app
```

Allowed: lower-case letters, digits, `_` and `-`; `web`, `my`, `mail`,
`website`, `shop`, `scoped_app` and `identity` are reserved. Set it to `odoo`
to keep the stock prefix. The active value is shown in Settings → Identity.

## Icon set

Minimal neumorphic tiles ("Pill" style): a pastel ground of the app's own
hue carrying a raised circular button with a small one-colour glyph. Metaphors are literal so apps are recognisable at 24 px
(calculator = Accounting, factory = Manufacturing, headset = Helpdesk, ID
badge = Employees, cart = eCommerce…). The design sheet with every icon at
Odoo's real sizes is `static/description/icons.html`.

`static/src/img/apps/<key>.svg` — one 512×512 tile per application. The key
is the module name (`crm.svg`), or `<module>__<basename>` for modules that
ship several icons (`base__settings.svg`, `base__modules.svg`). Any module
without a tile keeps its own icon. PNG rasters in `apps/png/` back the Safari
PWA icon route.

To change or extend the set, edit `tools/icon_catalog.py` (glyphs are drawn in
a 100×100 box with tone tokens `T:base / T:dark / T:light / T:white`; one hue
per app) and run:

```bash
python3 tools/build_icons.py
```

This regenerates the SVGs, the brand mark, the PNGs (headless Chrome +
Pillow) and the design sheet `static/description/icons.html`.

Four tile styles share the same glyphs: `pill` (default), `mono` (Mono
Raised), `carved` (Carved Grey) and `soft` (multi-tone). Preview them with
`python3 tools/build_icons.py --previews` (writes
`static/description/preview_<style>.html`) and switch the module's set with
`python3 tools/build_icons.py --style=carved`, then *Settings → Identity →
Refresh app icons*.

## How it works (for maintainers)

* `models/identity_brand.py` — single source of truth for the brand dict
  (`identity.brand.get()`), text replacement and icon lookup.
* `ir.http.session_info` / `get_frontend_session_info` expose `session.identity`
  to the client; `static/src/js/debrand_text.js` patches
  `LazyTranslatedString.translate()`, the one place every `_t()` string and
  every OWL template text node (`appTranslateFn`) passes through in Odoo 20.
* `ir.qweb._render` post-processes server-rendered output (skipped in the
  website editor so user content is never rewritten); `Base.get_view` /
  `get_views` debrand view archs and field labels and point Settings app
  logos at the tiles.
* `ir.ui.menu._read_image` and `ir.module.module._get_icon_image` /
  `_read_format` serve the tiles; `post_init_hook` recomputes the cached
  `web_icon_data` attachments.
* Controllers: `/identity/image/<logo|icon|apple|favicon>`, `/favicon.ico`,
  overrides of `company_logo`, the web manifest / offline / scoped-app /
  service-worker routes, and a wrapper around the module-level
  `web.controllers.database._render_template` (the database manager is no
  longer rendered by a controller method in Odoo 20).
* URL prefix: `controllers/home.py` registers `/<prefix>` and redirects
  `/odoo`; the JS router (`web/static/src/core/browser/router.js`) and
  `menu_helpers.js` are swapped for prefix-aware copies through the
  `('replace', …)` asset directives (`static/src/replace/`, aliased to the
  original module names); `web_prefix_patch.js` patches the navbar,
  many2one links, the service-worker scope and the PWA start URL.
* The two replaced files are **generated** from the Odoo sources: after
  updating Odoo, run `python3 tools/sync_web_overrides.py <odoo>/addons/web`
  and review the diff (the script stops if one of its anchors moved).
* The browser tab title ("<action> - <brand>") comes from a patch of
  `TitlePlugin.setParts` (`webclient_patch.js`).

## Porting notes (19.0 → 20.0)

* Binary fields hold `BinaryValue` objects (raw bytes) instead of base64:
  `_read_image`, `icon_image` and the bot avatar use `BinaryBytes`; values
  are compared by content (`checksum` differs between attachment-backed and
  in-memory values).
* `ir.config_parameter` is typed (`get_bool` / `get_str`); settings booleans
  are stored with `set_bool`, so the behaviour switches can now be turned off
  (in 19.0 an unticked switch read back as ticked).
* `odoo.http` is a package: `Stream` / `STATIC_CACHE` come from
  `odoo.http.stream`; `registry.clear_cache()` became
  `env.transaction.invalidate_ormcache()`.
* Server QWeb dropped `t-esc` (`t-out` only); OWL 3 templates resolve names
  on the context, so component attributes are written `this.x`; components
  declare props with `useProps` (a `static props` now raises).
* `mail.bot._get_answer(channel, body, message, command)` may return a list.
* The stock bot avatar is `odoobot.webp` (older `mail` builds: `odoobot.png`).
* New Odoo 20 applications got tiles (`ai_agentic`, `obox`,
  `planning_field_service`, `delivery_shipstation`); the tiles of the
  removed `ai_app` and `industry_fsm` were dropped.

## Tests

```bash
odoo-bin server --addons-path=<odoo>/addons,<path>/identity_20 -d <db> \
    -i identity --test-tags /identity --stop-after-init
```

Python, HTTP and one browser test (`test_webclient`, needs Chrome and the
`websocket-client` Python package).

## Limitations

* Replacement is case-sensitive on `Odoo`; `odoo.com` URLs inside stored
  user data (e.g. old e-mails) are not touched.
* Stored record data is not rewritten, except module summaries (on read) and
  the bot's own messages.
* Native mobile apps and PDF fonts/branding embedded in third-party modules
  are out of scope.
* A few buttons whose click is handled in JavaScript (the home-menu toggle)
  keep a static `href="/odoo"` in the stock templates: it only shows on hover,
  and following it lands on the permanent redirect.

## App icons (symbol set, 2026-09-27)

`tools/build_icons.py` (style `symbol`, the default) writes two files per application from the
Material Symbols Outlined sources cached in `tools/symbols/`: the tile (`static/src/img/apps/<key>.svg`,
what the menus' `web_icon_data` and the Apps kanban show) and the glyph alone
(`static/src/img/apps/glyph/<key>.svg`). The session lists the available glyph keys
(`identity_glyphs`); `static/src/js/icons.js` turns a menu's `web_icon` into the pair of CSS custom
properties a `.o_identity_icon` element carries, and `identity_enterprise` (auto-installed with
web_enterprise) renders the home menu tiles and the navbar's current app that way. Without a theme
the element shows the tile file; a theme may draw tile and glyph in its own colours
(`web_theme_slate` does). `tools/solve_icon_filters.py` documents the filter chains a theme can use
on the plain images.
