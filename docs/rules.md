# Revert — Engineering & Content Rules

These rules apply to every contributor, human or AI agent. If a rule blocks you, raise it. Do not work around it.

## 1. Repository & modules
1. The repo is `Albatross-IN/revert`, branch `20.0` (decided 2026-11-17; it already holds `revert_customizations`, `admin_notes_viewer`, `tools/etl` and `tools/deploy`). Odoo addons live at the repo root (`rvt_*/`). Docs live in `docs/`. The Flutter app lives in a separate repo (`revert_fe`). Branch `main` is the Odoo 18 code and is not touched.
2. Target **Odoo 20 only**. Module versions are `20.0.x.y.z`. Bump the version on every change to data or a model.
3. Name custom modules `rvt_<area>`, custom fields on inherited models `rvt_<name>`, own models `rvt.<thing>`, XML ids `rvt_<area>.<thing>`.
4. **Licences:** a module that depends on an Enterprise module (`project_enterprise`, `web_gantt`, `web_map`, `documents`, `sign`, `whatsapp`, `planning`) is `OEEL-1`. All other modules are `LGPL-3`. Never copy code out of `/opt/erp/sub` into an LGPL module.
5. One concern per module (architecture.md §3). No execution logic in `rvt_site`, no API code outside `rvt_api`, no notification sending outside `rvt_notify`'s service.
6. Every model needs `ir.access.csv` rows (Odoo 20 format: `id,name,model_id,group_id/id,operation,domain`) and record rules where data is scoped to an agency, a client or the owner. Transient models need access rows too.
7. **Vendored modules** (`fastapi`, `endpoint_route_handler`, `identity*`, `web_theme_glass`, `web_glass_workspace`, `queue_job`, `open_whatsapp_connector` if used) are not edited here. Fix them in AlbatrossHub/aic_apps or marut_20, copy again, and note the commit in README.md.
8. Dependencies follow system_design.md §2 strictly so each phase installs alone. `rvt_notify` is reached through `self.env["rvt.notify"]` lookups, never imported.

## 2. Odoo 20 / OWL 3 conventions
1. OWL 3: `proxy()` not `reactive`, `this.` in templates, no static props; `hasclass` for class checks, `t-attf-class` for composed classes.
2. `request.env.website` (no `request.website`); XML file fields use `type="bytes"`.
3. SCSS: never interpolate a variable inside `url()`; avoid `@extend` across files; use mixins. Bundle fonts locally.
4. Do not run `--dev=all` on staging or prod. Clear asset caches after theme changes.
5. Use `tracking=True` on every state, date commitment, approval and amount field named in system_design.md §6.
6. Computations that cross records (progress, health, money view) are stored and recomputed by targeted `@api.depends` or a nightly job, never by SQL in views.
7. Long work (media processing, notification fan-out, score recompute, PDF per audience) goes through `queue_job`, never in the request.

## 3. Data & privacy (non-negotiable)
1. **KYC data is private.** Aadhaar is stored as last 4 digits plus a private attachment; PAN and bank account are masked in lists and APIs; files are never `public=True`. Only `group_rvt_owner` and `group_rvt_accounts` read them.
2. Consent text (en/hi/gu) is shown and its version recorded before KYC upload. Retention follows the owner's answer to Q K2; the purge is a cron with a dry-run log.
3. Clients see only `client_visible` media, drawings released to them, their invoices, MOM items with audience `client` or `all`, and `client_safe_*` texts. Record rules enforce it; the API re-checks it.
4. An agency sees only its own agency, projects it works on, its own packages, queries, visits, quotes, work orders and money. Never another agency's prices, scores or people.
5. Scores, reliability components and rework reasons are never exposed to clients or to other agencies.
6. Never put real client, agency or KYC data into fixtures, demo data, screenshots or test dumps. Use the demo seed.
7. GPS is optional, asked at arrival, used only for the arrival distance; it is never tracked in the background.

## 4. Money
1. Every PO, bill, expense and invoice carries the project's analytic account. The owner money view is a sum over that account plus `paid_by`; there is no second ledger.
2. A payment request becomes a vendor bill only on office approval; a bill is "paid by client" only with a proof upload; nothing is marked paid from the app's client side.
3. TDS and GST follow the CA's configuration; code never hard-codes rates.
4. Amounts are INR, stored as Monetary, shown with Indian grouping (₹1,25,000) in every language.
5. Prices, fee schedules, advance and retention percentages are records, never constants.

## 5. Messaging
1. Never send real WhatsApp, SMS, push or email from dev or staging. Staging neutralises mail servers, WhatsApp accounts, SMS gateway keys and push on restore; dev uses a dummy dispatcher that logs.
2. One notification per event per channel; respect quiet hours (except arrival alerts to the office); every send is logged with delivery state.
3. Templates exist in en, hi and gu before a code path can send them; missing languages fall back to English and log a warning.
4. WhatsApp templates are the official Meta Cloud API templates through Odoo `whatsapp` unless Q J2 says otherwise; submit them early, they take days to approve.

## 6. Content & tone
1. **Client-facing text obeys design.md §2.1.** The words delayed, late, overdue, stuck and pending-from-your-side never appear in client UI, notifications or PDFs. A lint test in `rvt_design` and `rvt_notify` fails on them in client templates.
2. The only client-facing free text is `client_safe_status`, `next_client_action`, `client_safe_note` and MOM items with client audience; everything else the client reads is generated from state.
3. Agency copy is polite, specific and short (design.md §2.2). Nudges ask; they do not scold.
4. Gamification copy uses reliability, on time, documented, verified, partner level. No negative scoring language anywhere.
5. Every user-facing string is translatable (`_()` in Python, `translate=True` on master data, ARB in the app). No string concatenation to build sentences; use placeholders.
6. Do not invent progress. Percentages come from updates and verified quantities; a room shows "Started" until data exists.

## 7. Design
1. Use the tokens from `design.md`. No ad-hoc hex values in app code or templates. Rose is office-only.
2. WCAG 2.2 AA: contrast ≥ 4.5:1, tap targets ≥ 48 px, visible focus, `prefers-reduced-motion` respected. Agency screens: body text ≥ 16 px, line height 1.5 for gu/hi.
3. Mobile first at 360 px; no horizontal scroll; no blur effects on agency screens.
4. Bundle Inter, Noto Sans Gujarati and Noto Sans Devanagari; never load fonts from a CDN.
5. States are never colour-only; every state has a chip with text in the user's language.

## 8. Quality gates (each PR / phase)
1. `odoo-bin -d revert20 -i <module> --test-enable --stop-after-init` passes for every touched module; API tests run with `--workers=0`.
2. Fresh install and upgrade both pass on a copy of the dev DB.
3. Record-rule tests: an agency user cannot read another agency's work order, score or person; a client cannot read a non-client-visible attachment or an agency price. These tests exist before the module ships.
4. Client-tone lint passes (rule 6.1). Translation completeness check: every `rvt_` term has hi and gu entries or is listed in a known-gaps file.
5. App: `flutter analyze` clean; golden tests for the four homes in en/hi/gu at 360 px; an offline test that queues an update with a photo and syncs it.
6. Commit message: imperative summary, a body that says why, and `docs/tasks.md` checkboxes updated in the same commit.
7. Deploy to prod only by the documented script. The project owner runs prod deploys.
