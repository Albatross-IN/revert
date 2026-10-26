#!/bin/bash
# Restore a production backup as the ETL SOURCE database (revert_src18), neutralize it, and
# stage its filestore. Re-runnable: drops and rebuilds the source every time — exactly what
# the cutover does with a fresh production backup.
#
#   [ETL_SRC=<source db>] tools/etl/restore_src.sh <backup.zip>
#   [ETL_SRC=<source db>] tools/etl/restore_src.sh <dump> <filestore_dir>
#
# <backup.zip>: the database manager's "zip" backup (dump.sql + filestore/ + manifest.json).
# <dump>:       pg_dump -Fc (custom) or plain SQL; <filestore_dir> = that database's filestore.
# Nothing here touches production: the backup is taken there by the operator (runbook §1).
set -euo pipefail
HERE=$(cd "$(dirname "$0")" && pwd)
DB=${ETL_SRC:-revert_src18}
ETL_DIR=/opt/odoo20/etl_revert
STAGE=$ETL_DIR/data18/filestore/$DB
IN=${1:?backup zip, or dump + filestore dir}

WORK=""
if [[ "$IN" == *.zip ]]; then
    WORK=$(mktemp -d "$ETL_DIR/unzip.XXXXXX")
    trap 'rm -rf "$WORK"' EXIT
    echo "[$(date +%T)] unzipping $IN"
    unzip -q "$IN" -d "$WORK"
    DUMP=$WORK/dump.sql; FS=$WORK/filestore
    [ -f "$WORK/manifest.json" ] && python3 -c "import json,sys; m=json.load(open(sys.argv[1])); print('backup manifest: db', m['db_name'], 'version', m['version'], 'pg', m.get('pg_version'), '-', len(m['modules']), 'modules')" "$WORK/manifest.json"
else
    DUMP=$IN; FS=${2:?filestore dir}
fi
[ -f "$DUMP" ] || { echo "dump not found: $DUMP" >&2; exit 1; }
[ -d "$FS" ]   || { echo "filestore dir not found: $FS" >&2; exit 1; }

echo "[$(date +%T)] restoring $DUMP -> $DB"
dropdb --if-exists "$DB"
createdb -T template0 -E UTF8 "$DB"
if head -c 5 "$DUMP" | grep -q PGDMP; then
    pg_restore --no-owner --role="$(whoami)" -d "$DB" "$DUMP"
else
    psql -q -v ON_ERROR_STOP=1 -d "$DB" -f "$DUMP" > /dev/null
fi

echo "[$(date +%T)] neutralizing (crons, mail, IAP, push, base url)"
psql -q -d "$DB" -v ON_ERROR_STOP=1 -f "$HERE/neutralize_src.sql"

echo "[$(date +%T)] staging filestore -> $STAGE"
mkdir -p "$(dirname "$STAGE")"
rm -rf "$STAGE"
# plain copy, verified (a hardlink shortcut across owners is refused by fs.protected_hardlinks)
cp -a "$FS" "$STAGE"
SRC_N=$(find "$FS" -type f | wc -l); DST_N=$(find "$STAGE" -type f | wc -l)
[ "$SRC_N" = "$DST_N" ] || { echo "FATAL: filestore copy incomplete ($DST_N/$SRC_N files)" >&2; exit 1; }

echo "[$(date +%T)] summary:"
psql -d "$DB" -Atc "
SELECT 'installed modules: '||count(*) FROM ir_module_module WHERE state='installed';
SELECT 'revert module:     '||latest_version FROM ir_module_module WHERE name='revert_customizations';
SELECT 'users:             '||count(*) FROM res_users;
SELECT 'projects / tasks:  '||(SELECT count(*) FROM project_project)||' / '||(SELECT count(*) FROM project_task);
SELECT 'mail_message:      '||count(*) FROM mail_message;
SELECT 'mail_activity:     '||count(*) FROM mail_activity;
SELECT 'mom lines:         '||count(*) FROM mom_meeting;
SELECT 'ir_attachment:     '||count(*) FROM ir_attachment;
SELECT 'last activity:     '||max(write_date) FROM mail_message;
SELECT 'active crons:      '||count(*) FROM ir_cron WHERE active;
SELECT 'active mail srv:   '||count(*) FROM ir_mail_server WHERE active;"
echo "filestore files:   $DST_N"
MISSING=$(psql -d "$DB" -Atc "SELECT DISTINCT store_fname FROM ir_attachment WHERE store_fname IS NOT NULL" \
          | while read -r f; do [ -f "$STAGE/$f" ] || echo "$f"; done | wc -l)
echo "referenced files missing from the filestore: $MISSING"
echo "[$(date +%T)] done. Source ready: $DB"
