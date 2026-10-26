#!/usr/bin/env python3
"""ETL orchestrator (Revert 18→20). Run as om1203:

    cd /opt/odoo20/custom/revert_20 && /opt/odoo20/odoo20-venv/bin/python -m tools.etl.run --db revert20_etl_dry1 [options]

Options: --phase base,product  (default: all phases in order)   --only step1,step2   --force (redo done steps)
         --setup-only (create fdw/idmap tables and exit)      --list (show steps)
         --delta-t0 '2026-10-04 18:00:00' --golive '2026-10-05 09:00:00'   (delta pass after cut-over, plan §4.1:
         new 18 rows are loaded, modified rows overwrite the 20 copy unless it changed after go-live -> etl_conflict)
Every step is resumable: rows already in etl_idmap are skipped, finished steps are skipped unless --force.
"""
import argparse
import logging
import os
import sys
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from tools.etl import config  # noqa: E402
from tools.etl.bootstrap import open_env  # noqa: E402
from tools.etl.core import Engine  # noqa: E402
from tools.etl import refs  # noqa: E402,F401  (registers natural keys)
from tools.etl.mapping import steps_for, ORDER  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", required=True)
    ap.add_argument("--phase", default=None)
    ap.add_argument("--only", default=None)
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--setup-only", action="store_true")
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--production", action="store_true", help="the real cut-over run: keep IAP tokens, do not deactivate crons/mail servers")
    ap.add_argument("--delta-t0", default=None, help="delta pass (plan §4.1): only 18 rows created/modified after this UTC timestamp")
    ap.add_argument("--golive", default=None, help="delta pass: 20 records written after this UTC timestamp are reported, not overwritten")
    a = ap.parse_args()
    if a.production:
        os.environ["ETL_PRODUCTION"] = "1"; config.PRODUCTION = True
    phases = a.phase.split(",") if a.phase else ORDER
    steps = steps_for(phases)
    if a.list:
        for s in steps:
            print(f"{s.lane:4s} {s.name}")
        return
    os.makedirs(config.LOG_DIR, exist_ok=True)
    log_file = os.path.join(config.LOG_DIR, f"etl_{a.db}.log")
    env = open_env(a.db, log_file=log_file)
    fh = logging.FileHandler(log_file); fh.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s"))
    sh = logging.StreamHandler(sys.stdout); sh.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s"))
    for h in (fh, sh):
        logging.getLogger("etl").addHandler(h)
    logging.getLogger("etl").setLevel(logging.INFO)
    eng = Engine(env, run_name=a.db)
    eng.delta_t0, eng.golive = a.delta_t0, a.golive
    eng.setup()
    if a.delta_t0:
        env.cr.execute("INSERT INTO etl_run (t0, notes) VALUES (%s, %s)", (a.delta_t0, f"delta pass, golive={a.golive}"))
        env.cr.execute("UPDATE etl_step SET status = 'delta' WHERE status = 'done'")   # every step runs again in delta mode
        env.cr.commit()
    if a.setup_only:
        print("setup done"); return
    ctx = {"engine": eng, "env": env, "src": eng.src, "idmap": eng.idmap, "resolver": eng.resolver}
    t0 = time.time()
    eng.run_steps(steps, ctx, only=a.only.split(",") if a.only else None, force=a.force)
    logging.getLogger("etl").info("ALL DONE in %.0fs; unresolved m2o by relation: %s", time.time() - t0, eng.resolver.unresolved)
    env.cr.close()


if __name__ == "__main__":
    main()
