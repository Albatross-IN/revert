# Revert: production deployment plan

Status: v0.1 · 2026-10-31 · **partly superseded on 2026-11-17**

> **Decided 2026-11-17:** the platform is released into the **existing production**: database `erp.revert.co.in` on the shared server `147.93.30.85`, `https://erp.revert.co.in`. That server, its paths and its release procedure are described in the repo's `docs/deploy_production.md` (branch `20.0`).
> - **No longer applies:** §2 sizing as a new server, §3 layout (`/opt/revert`, `revert.service`, database `revert`), Phase A, Phase B steps 1 and 5, and §6 questions 1–2.
> - **Still applies:** Phase B steps 2–4 (as module installs on the existing database), Phase C integrations, Phase D staging, the Phase E checklist and §5 (adapted to the shared service: a restart also drops Albatross, so it is announced).
> - **To add on the shared server:** S3 backups (today: local daily, 14 days kept), a staging host, nginx rules for `/api/rvt/v1` (rate limits, 40 MB body), and a disk check before media uploads start.
> This document is rewritten in the v0.2 round.
Pattern: the Bhuj Runners VPS build (`erp20-*`) and the Marut backup/staging tooling, adapted. The as-built record will be [deployment.md](deployment.md).

## 1. Requirement as understood
1. Odoo 20 Enterprise from Revert's odoo.com download (`platform_version=deb_20e`), unpacked, never installed as a system package.
2. Host the Revert project (`rvt_*`, vendored modules, Identity, Glass) on an HTTPS domain Revert owns; the Flutter app talks to `/api/rvt/v1` on the same host.
3. Backups from day one (agency KYC and client project data), a staging copy for training and tests.
4. Official WhatsApp through Odoo, Firebase push, an SMS gateway for OTP fallback.

## 2. Server sizing
| Item | Recommendation |
|---|---|
| Location | India (Mumbai region) for latency to Ahmedabad sites and DPDP data residency comfort |
| Size | 4 vCPU, 8 GB RAM, 160 GB SSD to start (photos and video grow: plan 2–5 GB per project); Ubuntu LTS |
| PostgreSQL | 16 or newer, local socket only |
| Odoo workers | `workers=6`, `max_cron_threads=2`, gevent on its own port; `limit_memory_hard` tuned to 8 GB |
| Media | filestore on the same disk at first; move to S3-compatible object storage (`cloud_storage` or attachment location) when the filestore passes 50 GB |

## 3. Target layout (names use `revert`; nothing else of the client's is on the box)
| Thing | Name / path |
|---|---|
| System user / group | `revert` / `revert` (system account, home `/opt/revert`, `nologin`) |
| Code: platform (community) | `/opt/revert/server` |
| Code: enterprise addons | `/opt/revert/enterprise` |
| Code: project | `/opt/revert/custom/revert` (release commit in `RELEASE`) |
| Python venv | `/opt/revert/venv` (Odoo requirements + `pyjwt`, `fastapi`, `uvicorn` deps of the OCA module, `phonenumbers`, `pdfminer.six`, `rlPyCairo`, `freetype-py`) |
| Config | `/etc/revert/revert.conf` (0640 root:revert); secrets: JWT secret, FCM service-account path, S3 keys, SMS gateway key, `admin_passwd` hash |
| Data | `/var/lib/revert` (filestore, sessions) |
| Logs | `/var/log/revert/revert.log` + logrotate (weekly, 8 kept) |
| Service | `revert.service` (enabled); `revert-staging.service` |
| Launcher | `/opt/revert/bin/revert-server` wrapper around the platform launcher |
| PostgreSQL role | `revert` (CREATEDB, not superuser) |
| Databases | `revert` (prod), `revert_staging` |
| Internal ports | prod HTTP `127.0.0.1:8169`, gevent `127.0.0.1:8172`; staging `8269` / `8272` |
| nginx | `/etc/nginx/sites-available/revert`: 443 for the domain (+ `staging.` subdomain), 80 for ACME + redirect; rate limits on `/web/login`, `/api/rvt/v1/auth/*` and `/api/rvt/v1/media`; `client_max_body_size 40m` for video; `/websocket` to gevent |
| TLS | Let's Encrypt for the domain, `www` and `staging`, webroot `/var/www/letsencrypt`, certbot timer, nginx reload hook |
| Back office | `/office` (Identity); `/odoo/...` → 301 |
| Database manager | disabled (`list_db = False`) |

## 4. Phases

### Phase A — Provision (root, about 2 h)
1. Create user, directories, PostgreSQL role, firewall (`ufw`: 22 from admin IPs, 80, 443).
2. Unpack the Enterprise `.deb`: community to `/opt/revert/server`, enterprise addons to `/opt/revert/enterprise` (926 modules), themes if needed.
3. venv with Python 3.12+ (the distro's), `pip install -r requirements.txt` + the extras above; `wkhtmltopdf 0.12.6` patched qt (or the distro's) for PDFs.
4. `rsync` the project repo from a clean committed tree (`tools/deploy.sh`), including vendored modules.
5. Write `/etc/revert/revert.conf` from `deploy/revert.conf.example`; set `db_filter`, `proxy_mode = True`, `--load=base,rpc,web,queue_job` in the service, `identity_web_prefix = /office`.
6. systemd unit + wrapper; start; check `/web/login`.
7. nginx site + certbot; HSTS on; `/api/rvt/v1/docs` blocked at nginx in prod.

### Phase B — Database (about 1 h)
1. Create `revert` **fresh** (no demo data): `-i base --without-demo`, then `tools/setup_company.py` (company name, GSTIN, PAN, address, logo, currency INR, fiscal year, `l10n_in` chart).
2. Install standard modules then `rvt_*` in dependency order; activate `en_IN`, `hi_IN`, `gu_IN`.
3. Create office users (named logins, no shared accounts), owner group to the owner only; TOTP on for office users.
4. Identity brand: name, logo, icon, colours; Glass tokens.
5. Register the Enterprise subscription **before trial day 30** (create the prod DB about 2 weeks before go-live).

### Phase C — Integrations (depends on Revert accounts)
1. **Firebase**: project in Revert's Google account (or Albatross first), service-account JSON at `/etc/revert/fcm.json` root-only, path in config; Android `google-services.json` and iOS APNs key in the app build.
2. **WhatsApp**: Meta Business verification, a new number, the Odoo `whatsapp` account record with tokens; webhook URL `https://<domain>/whatsapp/webhook`; templates (en/hi/gu) submitted for approval.
3. **SMS**: DLT-registered sender and templates (TRAI), gateway key in config.
4. **Email**: Google Workspace SMTP (or a transactional provider) for client documents; `mail.catchall` on the domain.
5. **S3 backups**: bucket `revert-erp-backups`, a no-delete IAM user, `tools/backup.sh` + systemd timer at 19:30 UTC (`pg_dump -Fc` + filestore tar), 30-day lifecycle on `daily/`, monthly copy to `master/`; healthcheck ping; **restore drill** on staging in week 1.

### Phase D — Staging
1. `revert_staging` restored nightly from the latest backup by `tools/staging_refresh.sh`: restore → neutralise (mail servers off, WhatsApp account disabled, push dummy, SMS key blank, S3 off, `database.is_neutralized`) → rename-swap, at 20:30 UTC.
2. Separate service, ports and nginx server name `staging.<domain>` with basic auth.
3. The app has a *staging* environment switch in debug builds only.

### Phase E — Go-live checklist
- [ ] Prod DB created ≤ 14 days before go-live; subscription code at hand
- [ ] Backups verified by a restore to staging
- [ ] WhatsApp templates approved (invite, OTP, visit reminder, drawing released, payment paid, MOM shared)
- [ ] Push tested on Android and iPhone from prod
- [ ] Office users created, TOTP on, roles checked (owner-only money view confirmed by a non-owner test)
- [ ] Agency and client record-rule tests run against prod config (`tools/vps_test.sh` on a throwaway DB)
- [ ] Rate limits and body size checked with a 25 MB video upload
- [ ] Privacy policy (en/hi/gu) published at `/privacy`; consent text versions set
- [ ] Monitoring: uptime check on `/api/rvt/v1/health`, disk alert at 80%, backup healthcheck
- [ ] Release tag + `RELEASE` file written; `docs/deployment.md` filled in as built

## 5. Release process (after go-live)
```bash
# dev machine, clean committed tree
tools/deploy.sh                       # rsync code + restart prod
tools/deploy.sh rvt_site,rvt_design   # rsync + upgrade listed modules (service stopped meanwhile) + restart
tools/deploy.sh --staging ...         # same against staging
```
Risky releases are rehearsed on staging first and on a throwaway test DB on the server (`tools/vps_test.sh`, `--workers=0` for API tests). The project owner runs prod deploys (rules.md §8.7).

## 6. Questions for Revert before Phase A
1. Domain (e.g. `app.<revert domain>`) and who holds DNS.
2. VPS provider and account (Revert's or Albatross's billed through), region India.
3. Who receives the Enterprise subscription (Revert's odoo.com account) and the number of office users to license.
4. Google account for Firebase and Workspace; Meta Business account for WhatsApp; SMS gateway provider.
5. S3 (AWS) account for backups, or an Indian object store.
6. Admin login name for the owner; who else is a system administrator.
