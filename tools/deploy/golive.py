"""Go-live settings for the migrated Revert database on the production server.

The ETL leaves its target switched off (every scheduled action inactive, base URL on localhost) so a
test build can never e-mail or call out. This script turns on what production 18 had, once the
database is restored on the server and before users are let in. Run as the service user:

    sudo -u erp HOST=<revert host> /opt/erp/venv/bin/python /opt/erp/odoo20/odoo/odoo-bin shell \\
        -c /etc/erp/odoo20.conf -d <revert host> --no-http < tools/deploy/golive.py

* web.base.url = https://<host> (production had http://147.93.30.85:8020).
* scheduled actions: active where production had them active (16, from the 2026-08-31 backup),
  inactive where production had switched them off (automation rule check, fetchmail), and Odoo's
  own default for those new on 20. A scheduled action this script does not know stops it, so a
  module added later is decided on, not switched on blindly.

Idempotent: a second run changes nothing.
"""
import os

PROD_ACTIVE = {
    'auth_signup.ir_cron_auth_signup_send_pending_user_reminder',
    'base.autovacuum_job',
    'base.ir_cron_res_users_deletion',
    'digest.ir_cron_digest_scheduler_action',
    'mail.ir_cron_delete_notification',
    'mail.ir_cron_discuss_channel_member_unmute',
    'mail.ir_cron_mail_scheduler_action',
    'mail.ir_cron_module_update_notification',
    'mail.ir_cron_post_scheduled_message',
    'mail.ir_cron_send_scheduled_message',
    'mail.ir_cron_web_push_notification',
    'project.ir_cron_rating_project',
    'sms.ir_cron_sms_scheduler_action',
    'snailmail.snailmail_print',
}
PROD_INACTIVE = {
    'base_automation.ir_cron_data_base_automation_check',
    'mail.ir_cron_mail_gateway_action',
}
# not on production 18; active by default in their module's data
NEW_ON_20 = {
    'ai.ir_cron_embed_records',
    'ai.ir_cron_generate_embedding',
    'ai.ir_cron_run_web_scraper',
    'ai.ir_cron_update_deprecated_embedding_models',
    'ai_fields.ir_cron_fill_ai_fields',
    'mail.ir_cron_discuss_channel_sync_last_interest_dt',
    'mail.ir_cron_mail_end_polls',
    'resource.ir_cron_calendar_clean_up',
}

host = os.environ['HOST'].strip().lower()
assert host and '/' not in host and ':' not in host, f"HOST must be a bare host name, got {host!r}"
assert env.cr.dbname == host, f"database {env.cr.dbname!r} is not named after its host {host!r} (dbfilter ^%h$)"

ICP = env['ir.config_parameter'].sudo()
url = f'https://{host}'
if ICP.get_str('web.base.url') != url:
    ICP.set_str('web.base.url', url)
    print('web.base.url ->', url)
for key in ('web.base.url.freeze',):
    if ICP.get_str(key):
        ICP.search([('key', '=', key)]).unlink()
        print('removed', key)

Cron = env['ir.cron'].with_context(active_test=False)
xmlids = Cron.search([]).get_external_id()
unknown = {cron_id: xmlid for cron_id, xmlid in xmlids.items()
           if xmlid not in PROD_ACTIVE | PROD_INACTIVE | NEW_ON_20}
if unknown:
    raise SystemExit(f'scheduled actions not classified in golive.py, decide on them first: {unknown}')
for cron in Cron.search([]):
    want = xmlids[cron.id] not in PROD_INACTIVE
    if cron.active != want:
        cron.active = want
        print(f"cron {xmlids[cron.id]} -> {'active' if want else 'inactive'}")

env.cr.commit()
print('active scheduled actions:', Cron.search_count([('active', '=', True)]), 'of', Cron.search_count([]))
