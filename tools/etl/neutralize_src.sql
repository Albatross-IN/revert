-- Neutralize the freshly restored SOURCE snapshot (revert_src18) so nothing in it can ever
-- e-mail a client or call an external service. Run by restore_src.sh; idempotent.
-- The same rules are re-applied to every TARGET db after each ETL phase by the engine's
-- dry_run_guard (core.py) — this file is the source-side twin.

UPDATE ir_cron SET active = false WHERE active;
UPDATE ir_mail_server SET active = false WHERE active;
UPDATE fetchmail_server SET active = false WHERE active;

-- IAP (SMS, partner autocomplete, OCR): a copied account token would spend prod's credits.
UPDATE iap_account SET account_token = 'dry-run-disabled-' || id;

-- Mobile push (OCN): a copied project id would let this snapshot notify real phones.
DELETE FROM ir_config_parameter WHERE key IN ('odoo_ocn.project_id', 'ocn.uuid',
    'mail.web_push_vapid_private_key', 'mail.web_push_vapid_public_key');

-- The read-only v18 reference server renders this DB on port 8171; freeze the base url.
UPDATE ir_config_parameter SET value = 'http://localhost:8171' WHERE key = 'web.base.url';
INSERT INTO ir_config_parameter (key, value, create_date, write_date, create_uid, write_uid)
SELECT 'web.base.url.freeze', 'True', now(), now(), 1, 1
 WHERE NOT EXISTS (SELECT 1 FROM ir_config_parameter WHERE key = 'web.base.url.freeze');

-- Prod's enterprise trial date (2025-05-25) must not lock the read-only reference UI.
DELETE FROM ir_config_parameter WHERE key IN ('database.expiration_date', 'database.expiration_reason');

INSERT INTO ir_config_parameter (key, value, create_date, write_date, create_uid, write_uid)
SELECT 'database.is_neutralized', 'True', now(), now(), 1, 1
 WHERE NOT EXISTS (SELECT 1 FROM ir_config_parameter WHERE key = 'database.is_neutralized');
