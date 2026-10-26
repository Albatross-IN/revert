#!/bin/bash
# Create a fresh Odoo 20 TARGET database for the ETL: base, then the company identity read
# from the SOURCE (name, country, currency), then the frozen production module list. Run as om1203:
#   tools/etl/mkdb.sh revert20_etl_dry1              # full target
#   tools/etl/mkdb.sh revert20_etl_smoke --base-only # 1-minute smoke target (base only)
set -euo pipefail
HERE=$(cd "$(dirname "$0")" && pwd)
DB=${1:?database name}
MODE=${2:-full}
SRC=${ETL_SRC:-revert_src18}
TAG=$([ "$SRC" = revert_src18 ] && echo "" || echo "_$SRC")
PY=/opt/odoo20/odoo20-venv/bin/python
ODOO=/opt/odoo20/odoo20/odoo-bin
CONF=$HERE/conf/odoo20-etl.conf
mkdir -p /opt/odoo20/etl_revert/logs
LOG=/opt/odoo20/etl_revert/logs/mkdb_${DB}.log
COMMON="-c $CONF -d $DB --workers=0 --max-cron-threads=0 --http-port=8173 --logfile=$LOG"

echo "[$(date +%T)] creating $DB (log: $LOG)"
dropdb --if-exists "$DB"; createdb "$DB"
$PY $ODOO $COMMON -i base --stop-after-init

read -r CNAME CCOUNTRY CCUR < <(psql -d "$SRC" -AtF$'\t' -c "
    SELECT replace(c.name, ' ', '~'), co.code, cur.name FROM res_company c
    JOIN res_partner p ON p.id = c.partner_id LEFT JOIN res_country co ON co.id = p.country_id
    JOIN res_currency cur ON cur.id = c.currency_id ORDER BY c.id LIMIT 1")
echo "[$(date +%T)] base installed; company from $SRC: ${CNAME//\~/ } / $CCOUNTRY / $CCUR"
CNAME="${CNAME//\~/ }" CCOUNTRY="$CCOUNTRY" CCUR="$CCUR" $PY $ODOO shell $COMMON --no-http <<'PYEOF'
import os
c = env.company
vals = {'name': os.environ['CNAME']}
if os.environ.get('CCOUNTRY'):
    vals['country_id'] = env['res.country'].search([('code', '=', os.environ['CCOUNTRY'])], limit=1).id
cur = env['res.currency'].with_context(active_test=False).search([('name', '=', os.environ['CCUR'])], limit=1)
cur.write({'active': True})
vals['currency_id'] = cur.id
c.write(vals)
env.cr.commit()
print("company:", c.name, c.country_id.code, c.currency_id.name)
PYEOF

if [ "$MODE" != "--base-only" ]; then
    MODS=$(grep -v '^#' "$HERE/target_modules_prod$TAG.txt" | grep -v '^$' | paste -sd,)
    N=$(echo "$MODS" | tr ',' '\n' | wc -l)
    echo "[$(date +%T)] installing $N modules"
    $PY $ODOO $COMMON -i "$MODS" --stop-after-init
fi

# a migration target must never run automation on its own: every cron off, outgoing mail off.
psql -d "$DB" -qc "UPDATE ir_cron SET active = false; UPDATE ir_mail_server SET active = false;"

echo "[$(date +%T)] done; sanity:"
psql -d "$DB" -Atc "SELECT 'installed: '||count(*) FROM ir_module_module WHERE state='installed';
SELECT 'revert_customizations: '||coalesce((SELECT state||' '||latest_version FROM ir_module_module WHERE name='revert_customizations'), 'ABSENT')"
{ grep -cE " (ERROR|CRITICAL) " "$LOG" || true; } | sed 's/^/errors in log: /'
