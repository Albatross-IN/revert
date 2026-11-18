# Revert — Odoo 20 project platform

Architecture and interior project execution for **Revert Architects, Ahmedabad**: Odoo 20 Enterprise as the engine, one Flutter app with role homes for agencies, clients and the office, in Gujarati, Hindi and English.

Status: **Release 1 is being built on branch `20.0-release1`** (started 2026-11-19; phase log in docs/implementation_plan_r1.md §6). Production (`erp.revert.co.in`) runs branch `20.0` and is not touched until phase P11.

## Release 1 modules

| Module | What it is |
|---|---|
| `rvt_base` | Roles, trades, entity types, site presets, standard drawing sets, settings |
| `rvt_project` | Onboarding service, one task per room, one work line per trade, team access, the project picture |
| `rvt_drawing` | Drawing register, revisions, approval, release with receivers, opened tracking by link, questions, the client's approval |
| `rvt_mom` | Site visits and points (one record for MOM lines, office-raised items and client items), per-party PDFs, the move of the earlier MOM entries (`tools/etl_mom.py`) |
| `rvt_notify` | The one sender: message texts in English, Gujarati and Hindi, delivery log, reminders, invitations; never sends from a test copy |
| `rvt_api` | The app's back end at `/api/rvt/v1` (FastAPI): sign-in for staff, agencies and clients, the staff snapshot and operations, agency and client homes, files, preferences, push |
| `rvt_desk` | The single window for staff at `/rvt/desk`, and the log-in page. It runs the screen code of the approved preview (`revert_fe/design`) on live data: see `rvt_desk/tools/sync_from_preview.py` |

## Shared modules copied in (not edited here)

| Module | Version | Copied from | Why |
|---|---|---|---|
| `identity` | 20.0.2.0.0 | aic_apps `20.0-glass` @ 53b6989 | Own brand in the standard back office; its address prefix comes from the server setting `identity_web_prefix` (set it to `office` on production) |
| `web_theme_glass` | 20.0.1.1.0 | aic_apps `20.0-glass` @ 53b6989 (`identity_enterprise/`) | Glass look of the standard back office |
| `web_glass_workspace` | 20.0.1.0.0 | aic_apps `20.0-glass` @ 53b6989 (`marut_loader/`) | Split view and left pane of the standard back office |

| `open_whatsapp_connector` | 20.0.95.0.0 | synapse_be @ 85705e5 (the tracked files; the helper service's `node_modules` are installed on the server by `sidecar/setup.sh`) | WhatsApp through a paired number |
| `fastapi`, `endpoint_route_handler` | 20.0.1.1.0, 20.0.1.2.0 | sudi_20 @ 818c723 (the in-house port of the OCA modules to version 20) | The API framework |

Fix these in their home repository and copy again; record the new commit here. Python packages they need: `requirements.txt`.

| Document | For |
|---|---|
| [docs/prd.md](docs/prd.md) | The business, the brief processed into a lifecycle, scope v1, gaps, references |
| [docs/phase1_adoption.md](docs/phase1_adoption.md) | **Release 1**: what is built first and how it is rolled out (2026-11-17, after client feedback) |
| [docs/implementation_plan_r1.md](docs/implementation_plan_r1.md) | **Release 1 build plan**, phase by phase (start here to build) |
| [prototype/index.html](prototype/index.html) | Clickable screens of Release 1 (open in a browser) |
| [docs/masters_draft.md](docs/masters_draft.md) | Draft trades, room types, site presets and standard drawing sets, for Revert to correct |
| [docs/questionnaire.md](docs/questionnaire.md) | Questions for the principal consultant; ★ items gate the build |
| [docs/architecture.md](docs/architecture.md) | Decisions, module map, Odoo mapping, environments |
| [docs/system_design.md](docs/system_design.md) | Models, state machines, flows, security, notifications, gamification rules |
| [docs/api_design.md](docs/api_design.md) | `/api/rvt/v1` for the app |
| [docs/mobile_app_plan.md](docs/mobile_app_plan.md) | The app: homes, screens, stack, phases |
| [docs/design.md](docs/design.md) | Tone rules, tokens, components, screen sketches |
| [docs/rules.md](docs/rules.md) | How we work (read before contributing) |
| [docs/memory.md](docs/memory.md) | Facts, decisions log, environment, glossary |
| [docs/tasks.md](docs/tasks.md) | Phase plan with stable task ids |
| [docs/deployment_plan.md](docs/deployment_plan.md) · [docs/deployment.md](docs/deployment.md) | How prod will be built · what exists today |

Planned modules (all `rvt_*`): `rvt_base`, `rvt_site`, `rvt_crm`, `rvt_design`, `rvt_agency`, `rvt_execution`, `rvt_visit`, `rvt_mom`, `rvt_finance`, `rvt_game`, `rvt_notify`, `rvt_office`, `rvt_api`, plus vendored `fastapi`, `endpoint_route_handler`, `queue_job`, `identity*`, `web_theme_glass`, `web_glass_workspace`.
