# Revert on the production server (Odoo 20)

Server `root@147.93.30.85` (Ubuntu 26.04, 4 vCPU, 15 GB RAM). One Odoo 20 install serves both
Albatross and Revert. Each database is served on its own host name, because `dbfilter = ^%h$`: the
database is named exactly after the host (Revert's database = Revert's host name). The shared base was
built by the Albatross deployment. Changes to the shared files (odoo.conf, service, PostgreSQL, apt)
are announced to the other project first, as are restarts of `erp-odoo20`, which briefly drop both sites.

| What | Where |
|---|---|
| system user | `erp` (home `/opt/erp`) |
| Odoo 20 | `/opt/erp/odoo20/{odoo,enterprise,overlay}`, the exact build tested locally |
| Python | 3.12 (uv) in `/opt/erp/venv`, same packages as the local test venv |
| Revert code | `/opt/erp/addons/revert` (`revert_customizations`, `admin_notes_viewer`, `REVISION`) |
| config | `/etc/erp/odoo20.conf` (shared; master password in `/root/erp-secrets/`) |
| service | `erp-odoo20.service`, 127.0.0.1:8069 (HTTP) and :8072 (websocket), 6 workers |
| data | `/opt/erp/data/filestore/<host>`, sessions in `/opt/erp/data/sessions` |
| log | `/var/log/erp/odoo20.log` (daily, 30 kept); nginx `/var/log/nginx/<host>.*.log` |
| PostgreSQL | 18, role `erp` (owner of the databases, not superuser), local socket only |
| nginx | `sites-available/erp-revert.conf` + shared `snippets/erp-odoo.conf`, `erp-tls.conf` |
| certificates | Let's Encrypt, `certbot.timer` renews and reloads nginx |
| firewall | ufw: 22, 80, 443 only |
| backups | `erp-backup.timer`, daily 20:30 UTC: every `erp` database + filestore to `/opt/erp/backups/<db>/<stamp>/`, checked, `SHA256SUMS`, 14 days kept |
| releases | `/opt/erp/releases/revert/` (uploaded dump, filestore archive, deploy scripts) |

## Release procedure

The scripts are in `tools/deploy/`. Everything runs as root on the server unless marked local.

1. **Build the release (local).** Start from a verified ETL target (see `migration_18_to_20.md`, which
   must print ALL GREEN). Make a copy, then remove the ETL's link to the 18 source, which is not
   needed in production: drop the `src18` schema, the user mapping and server `src18`, and the
   `postgres_fdw` extension. Keep the `etl_*` tables as the record of the 18→20 id mapping (Odoo
   ignores them). Then `pg_dump -Fc --no-owner --no-acl` the copy, tar its filestore, and write
   `sha256sum` for both.
2. **Upload** both files to `/opt/erp/releases/revert/` and check them there with `sha256sum -c`.
3. **Code:** `git archive <commit> revert_customizations admin_notes_viewer` into
   `/opt/erp/addons/revert`, owner `erp`. Then announce and do one `systemctl restart erp-odoo20`
   so the service sees new or changed modules.
4. **Database:** `[PGPORT=<cluster port>] load_db.sh <host> <dump> <filestore.tar.gz>` (PGPORT when
   Odoo 20's PostgreSQL is not the cluster on 5432). It refuses to overwrite an existing
   database or filestore. The postgres superuser creates the `vector` and `pg_trgm` extensions
   first; `erp` cannot, and a plain `odoo-bin db load` silently skips them, which drops the AI
   embedding table. Then `erp` restores the dump, and the script ends with `check_filestore.py`:
   every stored file present with the sha1 Odoo recorded.
5. **Go-live settings:** pipe `golive.py` into `odoo-bin shell` with `HOST=<host>` (the command is in
   the script's docstring). It sets `web.base.url` to `https://<host>` and turns the scheduled
   actions on as production 18 had them. It is idempotent.
6. **Site and certificate:** `vhost.sh <host> [email]`. The DNS A record must point at the server first;
   the script checks this.
7. **Checks** (below), then hand the URL to users.

## Checks

* Database identical to the verified build, table by table (row count + md5 of every table, sorted
  with `COLLATE "C"`, session in UTC). Expected differences: `ir_config_parameter` (go-live
  settings) and `orm_signaling_*` (runtime counters).
* `check_filestore.py <db>`: 0 missing, 0 altered.
* Browser QA (`tools/etl/qa/browser_qa.py`, 19 checks), run on a throwaway copy on the server, never
  on the live database (it creates and closes a MOM entry). The copy is reached through an SSH tunnel:
  * Load it with `load_db.sh revert-qa.local …`.
  * Add a temporary nginx site listening on `127.0.0.1:8090` only. Set `Host` and
    `X-Forwarded-Host` to `revert-qa.local:8090` **inside each location**: nginx does not inherit
    `proxy_set_header` into a location that sets its own.
  * In the copy, set `web.base.url` and `report.url` to `http://127.0.0.1:8090`.
  * Start a temporary forwarder `127.0.0.1:15432` → PostgreSQL socket, running as `erp`, for the
    QA's database checks.
  * Locally: `ssh -L 8090:127.0.0.1:8090 -L 15432:127.0.0.1:15432`, then run
    `PGHOST=127.0.0.1 PGPORT=15432 PGUSER=erp browser_qa.py --base http://127.0.0.1:8090
    --host-map "revert-qa.local 127.0.0.1" --db revert-qa.local …`.
  * Remove the database, the nginx site and the forwarder afterwards, before the 20:30 UTC backup.
* API, on the same copy: `/web/webclient/version_info` (what the Odoo mobile app checks first),
  `/web/session/authenticate` + `call_kw`, the JSON-2 API (`/json/2/<model>/<method>`,
  `Authorization: bearer <API key>`, `X-Odoo-Database: <db>`), XML-RPC with an API key, and the
  `/websocket` upgrade through nginx.

## Traps met on this server

* Recreating a database under the **same name** while the service runs leaves workers on the old
  registry: logins fail with "CSRF validation failed" or redirect to the database selector until the
  workers reload. Use a new name, or restart (announced).
* `odoo-bin db load` as `erp` skips `CREATE EXTENSION vector` without failing (see step 4).
* Playwright's API requests ignore Chrome's `--host-resolver-rules`, which is why the QA base URL is
  `127.0.0.1:8090` and the QA site fixes the Host header.
