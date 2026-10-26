"""Transform helpers shared by several phases."""
import ast


def remap_res(vals, row, ctx, model_col="res_model", id_col="res_id", model_id_col="res_model_id", drop_unresolved=False):
    """res_model/res_id plain columns -> repoint res_id through the id map . Folded models."""
    fold = {}  # models folded into another model on 20 — none in the Revert module set
    model = row.get(model_col)
    if model and row.get(id_col):
        model20 = fold.get(model, model)
        new = ctx["idmap"].get(model20 if model20 != model else model, row[id_col]) if model20 == model else ctx["idmap"].get(model, row[id_col])
        if new:
            vals[id_col] = new
            vals[model_col] = model20
            if model_id_col in vals or model_id_col in row:
                rec = ctx["env"]["ir.model"]._get(model20)
                if rec:
                    vals[model_id_col] = rec.id
        else:
            if drop_unresolved:
                return None
            for k in (id_col, model_col, model_id_col):
                vals.pop(k, None)
    return vals


def rewrite_domain(domain_str, model, ctx):
    """Rewrite record ids inside a stored domain string through the id map (many2one/many2many fields of `model`)."""
    if not domain_str:
        return domain_str
    try:
        dom = ast.literal_eval(domain_str)
    except Exception:  # noqa: BLE001
        return domain_str
    env = ctx["env"]
    if model not in env:
        return domain_str
    fields = env[model]._fields
    out = []
    for leaf in dom:
        if isinstance(leaf, (list, tuple)) and len(leaf) == 3:
            f, op, v = leaf
            base = str(f).split(".")[0]
            fld = fields.get(base)
            if fld and fld.type in ("many2one", "many2many", "one2many") and "." not in str(f):
                rel = fld.comodel_name
                if isinstance(v, int) and not isinstance(v, bool):
                    v = ctx["idmap"].get(rel, v) or v
                elif isinstance(v, (list, tuple)) and all(isinstance(x, int) and not isinstance(x, bool) for x in v):
                    v = [ctx["idmap"].get(rel, x) or x for x in v]
            out.append((f, op, v))
        else:
            out.append(leaf)
    return repr(out)


def recompute_stored(env, model, ids, names):
    """Queue the stored computed fields `names` of `model` for the given ids and flush (dates untouched: no write())."""
    from .. import config
    M = env[model].with_context(**config.SILENT_CTX)   # no tracking messages from the flush
    recs = M.browse(ids)
    fields = [M._fields[n] for n in names if n in M._fields and M._fields[n].store and M._fields[n].compute]
    recs.invalidate_recordset([f.name for f in fields])
    for f in fields:
        env.add_to_compute(f, recs)
    M.flush_model([f.name for f in fields])
    return [f.name for f in fields]


def mapped_ids(cr, model):
    cr.execute("SELECT new_id FROM etl_idmap WHERE model = %s", (model,))
    return [r[0] for r in cr.fetchall()]


def map_by_xmlid(engine, model, extra_models=()):
    """Register idmap rows for `model` by matching module.name xmlids on both sides.
    Returns the number of newly mapped records."""
    n = 0
    from .. import config
    for m in (model, *extra_models):
        engine.cr.execute(f"""INSERT INTO etl_idmap (model, old_id, new_id)
            SELECT %s, d19.res_id, d20.res_id FROM {config.SRC_SCHEMA}.ir_model_data d19
            JOIN ir_model_data d20 ON d20.module = d19.module AND d20.name = d19.name AND d20.model = %s
            WHERE d19.model = %s AND d19.module NOT IN ('__export__', 'studio_customization')
            ON CONFLICT DO NOTHING""", (m, m, m))
        n += engine.cr.rowcount
        engine.idmap._cache.pop(m, None)
    return n
