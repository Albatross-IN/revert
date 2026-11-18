# Revert — Odoo 20 project platform

Architecture and interior project execution for **Revert Architects, Ahmedabad**: Odoo 20 Enterprise as the engine, one Flutter app with role homes for agencies, clients and the office, in Gujarati, Hindi and English.

Status: **discovery and design, 2026-10-31; amended 2026-11-17**. No platform module or app exists yet. Revert already runs Odoo 20 in production (`erp.revert.co.in`, repo `Albatross-IN/revert` branch `20.0`); the platform will be built in that repo and that database (docs/memory.md §1a and decisions log). Start with the documents.

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
