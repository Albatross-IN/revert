# Revert: environments as built

Status: 2026-10-31 · **nothing deployed**. This file records what exists today and is filled in as each environment is built, following [deployment_plan.md](deployment_plan.md).

## 1. Development (this machine) — as of 2026-10-31
| Item | Value |
|---|---|
| Odoo 20 | community `/opt/erp/odoo`, enterprise `/opt/erp/sub`, venv `/opt/erp/erp-venv` (Python 3.14.4) |
| Project path | `/opt/erp/custom/revert`, checkout of `Albatross-IN/revert`, branch `20.0-release1` |
| Database | `revert20` — neutralised restore of production, built 2026-11-18 with `tools/dev_db.sh` (backup of 2026-11-17 20:32 UTC) |
| Port | 8094 (reserved; 8095 Slate, 8096 Bhuj Runners, 8097 SFJ, 8098 Alps, 8099 Sudi) |
| Run | `tools/dev.sh` (serve), `tools/dev.sh shell`, `tools/dev.sh -u <module> --stop-after-init` |
| Vendored module sources | `/opt/erp/custom/marut_20` (`fastapi`, `endpoint_route_handler`, `queue_job`), `/opt/projects/aic_apps-20.0` (`identity*`, `web_theme_glass`, `web_glass_workspace`, `open_whatsapp_connector`) |
| Messaging in dev | dummy dispatcher that logs; no real WhatsApp, SMS, push or email (rules.md §5.1) |

## 2. Staging — not built
To be filled from deployment_plan.md Phase D: host, service `revert-staging`, DB `revert_staging`, ports 8269/8272, refresh timer, neutralisation checks.

## 3. Production — live (existing system; recorded 2026-11-17)
The platform will be released into this environment (decision of 2026-11-17). No `rvt_*` platform module is installed yet. Full description and release procedure: the repo's `docs/deploy_production.md`.

| Item | Value |
|---|---|
| Server | `147.93.30.85`, shared with Albatross (one Odoo 20 service, one database per host name, `dbfilter = ^%h$`) |
| Domain | `https://erp.revert.co.in` (Odoo) · `https://revert.co.in` (static website) · `revert.albatross.work` redirects |
| Database | `erp.revert.co.in` (renamed from `revert.albatross.work` on 2026-11-16) |
| Service / user | `erp-odoo20.service` / `erp`; HTTP 8069, websocket 8072, 6 workers |
| Code | `/opt/erp/addons/revert` (`revert_customizations`, `admin_notes_viewer`, `rvt_website_lead`, `REVISION`) |
| Config | `/etc/erp/odoo20.conf` (shared) |
| Python / PostgreSQL | 3.12 / 18 |
| TLS | Let's Encrypt, one certificate for `revert.co.in`, `www` and `erp` |
| Backups | `erp-backup.timer` daily 20:30 UTC to local disk, 14 days kept. **No S3 yet** |
| Website enquiry | `/api/lead` on `revert.co.in` → Odoo `/rvt/lead` → CRM lead (Sales team, source "Website (revert.co.in)") |
| Firebase / WhatsApp / SMS | — |
| Back office at `/office` (Identity) | not installed |

## 4. Operating
```bash
systemctl status erp-odoo20          # restart drops Albatross too: announce first
tail -f /var/log/erp/odoo20.log
nginx -t && systemctl reload nginx
```

## 5. Change log
| Date | Change |
|---|---|
| 2026-10-31 | Documents written; port 8094 and DB name `revert20` reserved for dev |
| 2026-11-16 | Production moved to `erp.revert.co.in`; website live on `revert.co.in`; CRM + `rvt_website_lead` installed |
| 2026-11-17 | Decided: platform extends the existing repo and production database; `revert20` becomes a restore of production |
