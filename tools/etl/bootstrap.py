"""Open an Odoo 20 environment on the ETL target database without going through odoo-bin shell."""
import logging
import os
import sys

from . import config


def open_env(db, log_file=None):
    # The repo root is on sys.path so `tools.etl` imports, but it is also an addons dir: its
    # vendored `fastapi` addon would shadow the pip `fastapi` package the addon itself imports
    # (circular ImportError on any target with fastapi installed). `tools.etl` is loaded by now
    # and resolves further submodules through its package __path__, so the root can go.
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    sys.path[:] = [p for p in sys.path if os.path.abspath(p or os.getcwd()) != repo_root]
    if config.ODOO_ROOT not in sys.path:
        sys.path.insert(0, config.ODOO_ROOT)
    import odoo
    from odoo.tools import config as ocfg
    args = ["-c", config.ODOO_CONF, "-d", db, "--workers=0", "--max-cron-threads=0", f"--http-port={config.PORT_SHELL20}"]
    if log_file:
        args += ["--logfile", log_file]
    ocfg.parse_config(args)
    odoo.netsvc.init_logger()
    logging.getLogger("odoo.sql_db").setLevel(logging.WARNING)
    registry = odoo.modules.registry.Registry(db)
    cr = registry.cursor()
    env = odoo.api.Environment(cr, odoo.SUPERUSER_ID, {})
    return env
