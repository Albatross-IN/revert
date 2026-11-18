# Revert — notes for Claude sessions in this repository

Revert Architects (Ahmedabad) runs Odoo 20 Enterprise in production from this repository. Release 1 of the project platform is being built on branch `20.0-release1`.

Read in this order before doing anything:
1. `docs/implementation_plan_r1.md`: how we work (§1), machine set-up (§2), the phase in hand (§5) and the phase log (§6). Work on **one phase at a time, in order**.
2. `docs/rules.md`: naming (`rvt_`), licences, Odoo 20 / OWL 3 conventions, tests, client-facing wording.
3. `docs/memory.md`: facts, decisions with dates, environment, traps.
4. `docs/phase1_adoption.md`: what Release 1 is and why (the approved scope).

Hard rules:
- Branch `20.0` is production; branch `main` is the old Odoo 18 code. Neither is touched. Work on `20.0-release1`.
- The dev database is a neutralised copy of production with client data. Keep it out of git. Never send WhatsApp or e-mail from it.
- Production is released by the project owner only. Prepare scripts; do not run them on the server.
- Shared modules copied into this repository (theme, identity, WhatsApp connector, fastapi) are not edited here.
- When a phase ends: tick `docs/tasks.md`, fill the phase log, add new traps to `docs/memory.md`, in the same commit.
- The older documents (`prd.md`, `system_design.md`, `api_design.md`, `mobile_app_plan.md`, `architecture.md`) describe the long-term platform. Where they disagree with `phase1_adoption.md` or the implementation plan, the latter two win.

Run: `tools/dev_db.sh` (build the dev database once), `tools/dev.sh` (serve on :8094), `tools/dev.sh shell`.
