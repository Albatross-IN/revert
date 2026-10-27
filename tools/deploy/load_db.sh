#!/bin/bash
# Load a Revert release onto the shared Odoo 20 server (service erp-odoo20, user erp) as a NEW
# database named after the host it is served on (dbfilter ^%h$). Run as root on the server:
#   [PGPORT=5433] load_db.sh <db = host> <release.dump> <filestore.tar.gz>
# PGPORT selects the PostgreSQL cluster (default 5432); sudo drops the environment, so it is passed on
# explicitly to every command.
#
# Never overwrites: refuses if the database or its filestore directory already exists.
# The extensions are created first by the postgres superuser (the erp role cannot, and a plain
# `odoo-bin db load` as erp silently skips them, which drops the vector-typed ai_embedding table),
# then the dump is restored by erp so erp owns everything. Ends with the filestore check.
set -euo pipefail
DB=${1:?database name = host name}
DUMP=${2:?release .dump (pg_dump -Fc)}
FS=${3:?filestore .tar.gz}
HERE=$(cd "$(dirname "$0")" && pwd)
PORT=${PGPORT:-5432}
DATA=/opt/erp/data
FSDIR=$DATA/filestore/$DB

if sudo -u postgres psql -p "$PORT" -XAtq -d postgres -c "SELECT 1 FROM pg_database WHERE datname = '$DB'" | grep -q 1; then
    echo "database $DB already exists: refusing" >&2; exit 1
fi
if [ -e "$FSDIR" ]; then
    echo "$FSDIR already exists: refusing" >&2; exit 1
fi
sudo -u erp test -r "$DUMP" && sudo -u erp test -r "$FS" || { echo "erp cannot read $DUMP / $FS" >&2; exit 1; }

echo "[$(date +%T)] create $DB (owner erp) + extensions, cluster port $PORT"
sudo -u postgres createdb -p "$PORT" -O erp "$DB"
sudo -u postgres psql -p "$PORT" -XAtq -v ON_ERROR_STOP=1 -d "$DB" \
    -c "CREATE EXTENSION IF NOT EXISTS vector" -c "CREATE EXTENSION IF NOT EXISTS pg_trgm"

echo "[$(date +%T)] restore $DUMP"
LIST=$(mktemp)
trap 'rm -f "$LIST"' EXIT
# -p also picks the matching client version on a multi-cluster Debian/Ubuntu box (pg_wrapper)
pg_restore -p "$PORT" -l "$DUMP" | grep -vE " EXTENSION | COMMENT - EXTENSION " > "$LIST"
chmod 0644 "$LIST"
sudo -u erp pg_restore -p "$PORT" --no-owner --no-acl --exit-on-error -L "$LIST" -d "$DB" "$DUMP"

echo "[$(date +%T)] filestore -> $FSDIR"
install -d -o erp -g erp -m 0750 "$DATA/filestore"
install -d -o erp -g erp -m 0750 "$FSDIR"
sudo -u erp tar -C "$FSDIR" -xzf "$FS"

sudo -u erp env PGPORT="$PORT" /opt/erp/venv/bin/python "$HERE/check_filestore.py" "$DB"
