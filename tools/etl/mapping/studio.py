"""Phase 'studio': prod's Studio customizations, carried as data (the studio_customization module
is virtual — it only exists as the records Studio wrote). Prod has:
  * x_studio_responsible_person (char) on project.task, filled on 182 tasks;
  * two Studio views that show it on the task form, the sub-task list and the task list;
  * the manual model x_mom.rec (MOM) with 5 fields and three one2many fields on project.task.

Fields and models are created through the ORM (exactly what Studio does), BEFORE the project phase,
so the task load copies x_studio_responsible_person like any other column. The views are created
after it. Every record keeps its studio_customization xmlid."""
import logging

from ..core import FuncStep
from .. import config

_logger = logging.getLogger("etl.studio")
S = config.SRC_SCHEMA

# ir.model.fields attributes carried from 18 (only those that exist on both versions)
FIELD_ATTRS = ("field_description", "ttype", "relation", "relation_field", "required", "readonly", "index",
               "copied", "store", "help", "translate", "on_delete", "domain", "tracking", "size", "selectable",
               "group_expand", "related", "depends", "compute", "sanitize", "strip_style", "strip_classes")


def _tr(v):
    if isinstance(v, dict):
        return v.get("en_US") or next(iter(v.values()), None)
    return v


def _xmlid(env, record, module, name):
    env["ir.model.data"].sudo().create({"module": module, "name": name, "model": record._name,
                                         "res_id": record.id, "noupdate": True})


def _src_xmlid(cr, model, res_id):
    cr.execute(f"SELECT module, name FROM {S}.ir_model_data WHERE model = %s AND res_id = %s ORDER BY id LIMIT 1",
               (model, res_id))
    return cr.fetchone()


def _field_vals(env, row, model_rec):
    F = env["ir.model.fields"]._fields
    vals = {"name": row["name"], "model_id": model_rec.id, "state": "manual"}
    for k in FIELD_ATTRS:
        if k in F and k in row and row[k] is not None:
            vals[k] = _tr(row[k])
    return vals


def _studio_fields(engine, ctx):
    cr, env = engine.cr, engine.env
    out = {"models": [], "fields": [], "skipped": []}
    if not env["ir.module.module"].search([("name", "=", "web_studio"), ("state", "=", "installed")]):
        return dict(skipped="web_studio not installed on the target")
    env["ir.module.module"].sudo().get_studio_module()
    IrModel, IrField = env["ir.model"].sudo(), env["ir.model.fields"].sudo()

    # 1. manual models (with their own fields, many2one first so one2many inverses exist)
    cr.execute(f"SELECT id, model, name, info, transient FROM {S}.ir_model WHERE state = 'manual' ORDER BY id")
    for mid, model, name, info, transient in cr.fetchall():
        rec = IrModel.search([("model", "=", model)])
        if not rec:
            rec = IrModel.create({"model": model, "name": _tr(name), "info": _tr(info), "state": "manual",
                                  "transient": bool(transient)})
            out["models"].append(model)
        engine.idmap.add_many("ir.model", [(mid, rec.id)])
        x = _src_xmlid(cr, "ir.model", mid)
        if x and not env.ref(f"{x[0]}.{x[1]}", raise_if_not_found=False):
            _xmlid(env, rec, *x)

    # 2. manual fields on every model, ordered so a one2many comes after its inverse many2one
    cr.execute(f"""SELECT * FROM {S}.ir_model_fields WHERE state = 'manual'
                   ORDER BY CASE ttype WHEN 'one2many' THEN 2 WHEN 'many2many' THEN 1 ELSE 0 END, id""")
    names = [d[0] for d in cr.description]
    for row in [dict(zip(names, r)) for r in cr.fetchall()]:
        model_rec = IrModel.search([("model", "=", row["model"])])
        if not model_rec:
            out["skipped"].append(f"{row['model']}.{row['name']} (model missing on 20)")
            engine.idmap.refuse("studio.fields", "ir.model.fields", row["id"], f"model {row['model']} missing on 20")
            continue
        rec = IrField.search([("model", "=", row["model"]), ("name", "=", row["name"])])
        if not rec:
            try:
                with cr.savepoint():
                    rec = IrField.create(_field_vals(env, row, model_rec))
                out["fields"].append(f"{row['model']}.{row['name']}")
            except Exception as e:  # noqa: BLE001
                engine.idmap.refuse("studio.fields", "ir.model.fields", row["id"], f"create: {e}", row)
                out["skipped"].append(f"{row['model']}.{row['name']}: {e}")
                continue
        engine.idmap.add_many("ir.model.fields", [(row["id"], rec.id)])
        x = _src_xmlid(cr, "ir.model.fields", row["id"])
        if x and not env.ref(f"{x[0]}.{x[1]}", raise_if_not_found=False):
            _xmlid(env, rec, *x)
    return out


FIELDS = FuncStep("studio.fields", _studio_fields)


def _studio_records(engine, ctx):
    """Rows of the manual models (x_mom.rec is empty on prod; copied generically for later pulls):
    plain columns verbatim, many2one columns through the id map, ids at +OFFSET."""
    cr = engine.cr
    out = {}
    cr.execute(f"SELECT model FROM {S}.ir_model WHERE state = 'manual'")
    for (model,) in cr.fetchall():
        table = model.replace(".", "_")
        if not engine.src.table_exists(table):
            continue
        cr.execute(f"SELECT name, relation FROM {S}.ir_model_fields WHERE model = %s AND ttype = 'many2one' AND store",
                   (model,))
        m2o = dict(cr.fetchall())
        cr.execute("SELECT column_name FROM information_schema.columns WHERE table_schema='public' AND table_name=%s",
                   (table,))
        cols20 = {r[0] for r in cr.fetchall()}
        cols = [c for c in engine.src.columns(table) if c in cols20]
        exprs, joins = [], []
        for c in cols:
            if c == "id":
                exprs.append(f"s.id + {config.OFFSET}")
            elif c in ("create_uid", "write_uid") or c in m2o:
                rel = "res.users" if c in ("create_uid", "write_uid") else m2o[c]
                joins.append(f"LEFT JOIN etl_idmap j_{c} ON j_{c}.model = '{rel}' AND j_{c}.old_id = s.{c}")
                exprs.append(f"j_{c}.new_id")
            else:
                exprs.append(f's."{c}"')
        cr.execute(f"""INSERT INTO "{table}" ({', '.join(f'"{c}"' for c in cols)})
                       SELECT {', '.join(exprs)} FROM {S}."{table}" s {' '.join(joins)} ON CONFLICT DO NOTHING""")
        out[model] = cr.rowcount
        cr.execute(f"""INSERT INTO etl_idmap (model, old_id, new_id) SELECT %s, id - {config.OFFSET}, id
                       FROM "{table}" WHERE id > {config.OFFSET} ON CONFLICT DO NOTHING""", (model,))
        cr.execute(f"SELECT setval(pg_get_serial_sequence('{table}', 'id'), GREATEST((SELECT coalesce(max(id), 1) FROM \"{table}\"), 1))")
    engine.idmap._cache.clear()
    return out


RECORDS = FuncStep("studio.records", _studio_records)


def _studio_views(engine, ctx):
    """Studio's inherited views, re-attached to the same parent view by xmlid. A view whose arch
    no longer applies on 20 is refused (and reported), never forced in."""
    cr, env = engine.cr, engine.env
    View = env["ir.ui.view"].sudo()
    out = {"created": [], "refused": []}
    cr.execute(f"""SELECT v.id, v.name, v.model, v.inherit_id, v.priority, v.mode, v.active, v.arch_db, v.key, d.module, d.name
                   FROM {S}.ir_ui_view v JOIN {S}.ir_model_data d ON d.model = 'ir.ui.view' AND d.res_id = v.id
                   WHERE d.module = 'studio_customization' ORDER BY v.id""")
    for vid, name, model, inherit, prio, mode, active, arch, key, xmod, xname in cr.fetchall():
        if env.ref(f"{xmod}.{xname}", raise_if_not_found=False):
            continue
        parent = None
        if inherit:
            px = _src_xmlid(cr, "ir.ui.view", inherit)
            parent = env.ref(f"{px[0]}.{px[1]}", raise_if_not_found=False) if px else None
            if not parent:
                out["refused"].append(f"{xname}: parent view {px} missing on 20")
                engine.idmap.refuse("studio.views", "ir.ui.view", vid, f"parent view {px} missing on 20")
                continue
        try:
            with cr.savepoint():
                rec = View.create({"name": name, "model": model, "inherit_id": parent.id if parent else False,
                                   "priority": prio, "mode": mode, "active": active, "arch": _tr(arch), "key": key})
                _xmlid(env, rec, xmod, xname)
            engine.idmap.add_many("ir.ui.view", [(vid, rec.id)])
            out["created"].append(xname)
        except Exception as e:  # noqa: BLE001
            out["refused"].append(f"{xname}: {e}")
            engine.idmap.refuse("studio.views", "ir.ui.view", vid, f"create: {e}", {"arch": _tr(arch)})
    return out


VIEWS = FuncStep("studio.views", _studio_views)

STEPS = [FIELDS]
POST_STEPS = [RECORDS, VIEWS]
