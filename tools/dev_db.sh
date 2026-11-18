#!/usr/bin/env bash
# Build the development database from the latest nightly production backup.
#
#   tools/dev_db.sh                 fetch the newest backup, restore as revert20, neutralise
#   tools/dev_db.sh --keep-dump     same, but reuse a dump already in $BACKUP_DIR
#   REVERT_DB=revert20_b tools/dev_db.sh
#
# The backup holds client data: it stays out of git and off shared drives.
# The result is neutralised (no scheduled actions, no outgoing mail) and its
# base URL points at the local port. It never overwrites an existing database.
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
SERVER="${REVERT_SERVER:-root@147.93.30.85}"
REMOTE_ROOT=/opt/erp/backups/erp.revert.co.in
BACKUP_DIR="${BACKUP_DIR:-$ERP/backups/revert-prod}"
FILESTORE="${ODOO_FILESTORE:-$HOME/.local/share/Odoo/filestore}"

if psql -d postgres -Atc "select 1 from pg_database where datname='$DB'" | grep -q 1; then
    echo "Database $DB exists. Drop it yourself first (dropdb $DB; rm -rf $FILESTORE/$DB)." >&2
    exit 1
fi
[ -e "$FILESTORE/$DB" ] && { echo "Filestore $FILESTORE/$DB exists." >&2; exit 1; }

mkdir -p "$BACKUP_DIR"
if [ "${1:-}" != "--keep-dump" ]; then
    latest="$(ssh -o BatchMode=yes "$SERVER" "ls -d $REMOTE_ROOT/*/ | sort | tail -1")"
    echo "Fetching $latest"
    scp -q -o BatchMode=yes "$SERVER:${latest}db.dump" "$SERVER:${latest}filestore.tar.zst" \
        "$SERVER:${latest}SHA256SUMS" "$BACKUP_DIR/"
fi
(cd "$BACKUP_DIR" && sha256sum -c SHA256SUMS)

createdb "$DB"
# The dump expects these; a plain restore skips them silently (docs/deploy_production.md).
psql -q -d "$DB" -c "create extension if not exists vector; create extension if not exists pg_trgm; create extension if not exists unaccent;"
pg_restore --no-owner --no-acl -d "$DB" "$BACKUP_DIR/db.dump" 2>&1 | grep -v -e 'already exists' -e 'Command was' -e '^pg_restore: warning' || true

tmp="$(mktemp -d)"
tar --zstd -C "$tmp" -xf "$BACKUP_DIR/filestore.tar.zst"
mkdir -p "$FILESTORE"
mv "$tmp"/* "$FILESTORE/$DB"
rmdir "$tmp"

"$PY" "$BIN" neutralize -d "$DB" \
    --addons-path="$CORE,$ENTERPRISE,$REPO"
psql -q -d "$DB" -c "update ir_config_parameter set value='http://localhost:$PORT' where key='web.base.url'"

psql -d "$DB" -Atc "select 'neutralised: '||value from ir_config_parameter where key='database.is_neutralized';
select 'users: '||count(*) from res_users where active and share is not true;
select 'projects: '||count(*) from project_project where active;
select 'tasks: '||count(*) from project_task;"
echo "Ready: tools/dev.sh   (http://localhost:$PORT)"
