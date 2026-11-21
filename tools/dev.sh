#!/usr/bin/env bash
# Run the Revert development server by hand (no service).
#
#   tools/dev.sh                          serve db revert20 on :8094
#   tools/dev.sh -u rvt_base --stop-after-init
#   tools/dev.sh shell                    odoo shell on the same db
#   REVERT_DB=revert20_test tools/dev.sh -i rvt_base --test-enable --stop-after-init
#
# revert20 is a neutralised restore of production (docs/deployment.md §1).
set -euo pipefail

ERP="${ERP_HOME:-/opt/erp}"
REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DB="${REVERT_DB:-revert20}"
PORT="${REVERT_PORT:-8094}"
ENTERPRISE="${ERP_ENTERPRISE:-$ERP/sub}"
# Other machines: set ODOO_PYTHON, ODOO_BIN, ODOO_ADDONS, ERP_ENTERPRISE (see docs/implementation_plan_r1.md §2).
PY="${ODOO_PYTHON:-$ERP/erp-venv/bin/python}"
BIN="${ODOO_BIN:-$ERP/odoo/odoo-bin}"
CORE="${ODOO_ADDONS:-$ERP/odoo/addons}"

CMD=()
if [ "${1:-}" = "shell" ]; then CMD=(shell); shift; fi

exec "$PY" "$BIN" "${CMD[@]}" \
    --addons-path="$CORE,$ENTERPRISE,$REPO" \
    -d "$DB" --db-filter="^${DB}\$" \
    --http-port="$PORT" --gevent-port="$((PORT + 100))" \
    --workers=0 --max-cron-threads=0 \
    "$@"
