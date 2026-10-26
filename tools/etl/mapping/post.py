"""Phase 'post' (after chatter): settings (config parameters, company details and report layout,
digest), canned responses, module channels' names, menu-group deltas, tz aliases, and the
purge of fresh-install onboarding records prod does not have."""
import logging

from ..core import OrmStep, FuncStep, SqlStep
from .. import config

_logger = logging.getLogger("etl.post")
S = config.SRC_SCHEMA

# never copied: identity of the database, URLs, push/IAP endpoints, ids of records
PARAM_DENY = ("database.", "web.base.url", "mail.catchall", "mail.bounce", "mail.default.from", "iap", "ocn.",
              "odoo_ocn.", "mail_mobile.", "web.push", "mail.web_push", "publisher_warranty.", "web_tour",
              "digest.default_digest_id", "analytic.project_plan", "report.url")
# settings the user chose on 18: written even when 20 already holds its own default
PARAM_OVERWRITE = ("auth_signup.", "base_setup.", "base.login_cooldown", "mail.activity.gc.", "mail.restrict.",
                   "base.default_max_email_size", "digest.default_digest_emails")


def _params(engine, ctx):
    cr = engine.cr
    cr.execute(f"SELECT key, value FROM {S}.ir_config_parameter")
    src = dict(cr.fetchall())
    cr.execute("SELECT key, value FROM ir_config_parameter")
    have = dict(cr.fetchall())
    P = engine.env["ir.config_parameter"].sudo()
    copied, overwritten = [], []
    for k, v in sorted(src.items()):
        if any(k.startswith(p) for p in PARAM_DENY):
            continue
        if k not in have:
            P.set_str(k, v); copied.append(k)
        elif have[k] != v and any(k.startswith(p) for p in PARAM_OVERWRITE):
            P.set_str(k, v); overwritten.append(f"{k}: {have[k]} -> {v}")
    return dict(copied=copied, overwritten=overwritten)


PARAMS = FuncStep("ir.config_parameter", _params)


def _company(engine, ctx):
    """Company details mkdb did not set: report layout + colours + font + header/footer, paper format.
    Name, address, e-mail, phone and logo came with the company partner (base phase + chatter)."""
    cr, env = engine.cr, engine.env
    cr.execute(f"""SELECT c.report_header, c.report_footer, c.company_details, c.primary_color, c.secondary_color,
                          c.font, c.external_report_layout_id, c.paperformat_id, c.email_primary_color,
                          c.email_secondary_color
                   FROM {S}.res_company c ORDER BY c.id LIMIT 1""")
    row = cr.fetchone()
    if not row:
        return {}
    header, footer, details, c1, c2, font, layout, paper, mail1, mail2 = row

    def _tr(v):
        if isinstance(v, dict):
            return v.get("en_US") or next(iter(v.values()), None)
        return v

    company = env.company
    vals = {}
    for f, v in (("report_header", _tr(header)), ("report_footer", _tr(footer)), ("company_details", _tr(details)),
                 ("primary_color", c1), ("secondary_color", c2), ("font", font),
                 ("email_primary_color", mail1), ("email_secondary_color", mail2)):
        if v and f in company._fields:
            vals[f] = v
    for field, model, old in (("external_report_layout_id", "ir.ui.view", layout),
                              ("paperformat_id", "report.paperformat", paper)):
        if old:
            cr.execute(f"SELECT module||'.'||name FROM {S}.ir_model_data WHERE model = %s AND res_id = %s", (model, old))
            r = cr.fetchone()
            rec = env.ref(r[0], raise_if_not_found=False) if r else None
            if rec:
                vals[field] = rec.id
    if vals:
        company.write(vals)
    env.invalidate_all()
    return dict(written=sorted(vals))


COMPANY_DETAILS = FuncStep("res.company.details", _company)


def _digest(engine, ctx):
    """Prod's periodic digest: periodicity, state and subscribers (by xmlid)."""
    cr, env = engine.cr, engine.env
    cr.execute(f"""SELECT g.id, g.periodicity, g.state, d.module||'.'||d.name FROM {S}.digest_digest g
                   LEFT JOIN {S}.ir_model_data d ON d.model = 'digest.digest' AND d.res_id = g.id""")
    out = {}
    for gid, periodicity, state, xmlid in cr.fetchall():
        digest = env.ref(xmlid, raise_if_not_found=False) if xmlid else None
        if not digest:
            continue
        cr.execute(f"""SELECT u.new_id FROM {S}.digest_digest_res_users_rel r
                       JOIN etl_idmap u ON u.model = 'res.users' AND u.old_id = r.res_users_id
                       WHERE r.digest_digest_id = %s""", (gid,))
        users = [r[0] for r in cr.fetchall()]
        digest.write({"periodicity": periodicity, "state": state, "user_ids": [(6, 0, users)]})
        engine.idmap.add_many("digest.digest", [(gid, digest.id)])
        out[xmlid] = dict(periodicity=periodicity, state=state, subscribers=len(users))
    return out


DIGEST = FuncStep("digest.digest", _digest)

CANNED = OrmStep("mail.canned.response", key=["source"], skip={"description", "group_ids", "is_shared", "is_editable"})


def _module_channels(engine, ctx):
    """#general and Administrators exist on both sides (xmlid-mapped): prod's name and description win."""
    cr = engine.cr
    cr.execute(f"""UPDATE discuss_channel t SET name = s.name, description = s.description
                   FROM etl_idmap m JOIN {S}.discuss_channel s ON s.id = m.old_id
                   WHERE m.model = 'discuss.channel' AND t.id = m.new_id AND t.id < {config.OFFSET}
                     AND (t.name IS DISTINCT FROM s.name OR t.description IS DISTINCT FROM s.description)""")
    return dict(renamed=cr.rowcount)


MODULE_CHANNELS = FuncStep("discuss.channel.module_channels", _module_channels)


def _purge_install_artifacts(engine, ctx):
    """Fresh-install onboarding records prod does not have (Welcome task, its project-less to-do):
    delete every record of these models the id map does not own."""
    cr, env = engine.cr, engine.env
    out = {}
    for model in ("project.task", "project.project", "project.update", "discuss.channel"):
        table = model.replace(".", "_")
        cr.execute(f"""SELECT t.id FROM {table} t WHERE NOT EXISTS
                       (SELECT 1 FROM etl_idmap m WHERE m.model = %s AND m.new_id = t.id)""", (model,))
        ids = [r[0] for r in cr.fetchall()]
        if ids:
            env[model].sudo().with_context(active_test=False).browse(ids).unlink()
        out[model] = len(ids)
    return out


PURGE_INSTALL = FuncStep("parity.purge_install_artifacts", _purge_install_artifacts)

# menu visibility customized IN THE DATABASE: group DELTAS carried by menu + group xmlid
MENU_GROUPS = SqlStep("ir.ui.menu.group_deltas", """
    INSERT INTO ir_ui_menu_group_rel (menu_id, gid)
    SELECT tm.res_id, tg.res_id
    FROM {S}.ir_ui_menu_group_rel r
    JOIN {S}.ir_model_data smd ON smd.model = 'ir.ui.menu' AND smd.res_id = r.menu_id
    JOIN ir_model_data tm ON tm.model = 'ir.ui.menu' AND tm.module = smd.module AND tm.name = smd.name
    JOIN {S}.ir_model_data sgd ON sgd.model = 'res.groups' AND sgd.res_id = r.gid
    JOIN ir_model_data tg ON tg.model = 'res.groups' AND tg.module = sgd.module AND tg.name = sgd.name
    WHERE NOT EXISTS (SELECT 1 FROM ir_ui_menu_group_rel e
                      WHERE e.menu_id = tm.res_id AND e.gid = tg.res_id)""")


def _tz_aliases(engine, ctx):
    cr, fixed = engine.cr, {}
    cr.execute("""SELECT c.table_name, c.column_name FROM information_schema.columns c
                  JOIN information_schema.tables t ON t.table_schema = c.table_schema AND t.table_name = c.table_name
                  WHERE c.table_schema = 'public' AND t.table_type = 'BASE TABLE'
                    AND c.column_name IN ('tz', 'user_tz', 'timezone')
                    AND c.data_type IN ('character varying', 'text')""")
    for table, col in cr.fetchall():
        for old, new in config.TZ_ALIASES.items():
            cr.execute(f'UPDATE "{table}" SET "{col}" = %s WHERE "{col}" = %s', (new, old))
            if cr.rowcount:
                fixed[f"{table}.{col}"] = fixed.get(f"{table}.{col}", 0) + cr.rowcount
    return fixed


TZ_ALIASES = FuncStep("parity.tz_aliases", _tz_aliases)

STEPS = [PARAMS, COMPANY_DETAILS, DIGEST, CANNED, MODULE_CHANNELS, PURGE_INSTALL, MENU_GROUPS, TZ_ALIASES]
