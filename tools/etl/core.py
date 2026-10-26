"""Engine core: source access through postgres_fdw, id map, refusals, natural-key resolver,
ORM lane (records created through the Odoo 20 ORM) and SQL lane (INSERT ... SELECT with id offset).

Everything runs inside ONE Odoo environment (env.cr) on the target database: the Odoo 18 source
copy is visible as the foreign schema `src18` (see Src.setup_fdw), so extraction, id mapping and
loading are joins in the same transaction.
"""
import collections
import json
import logging
import re
import time

from psycopg2 import sql as psql
from psycopg2.extras import execute_values

from . import config

_logger = logging.getLogger("etl")


# --------------------------------------------------------------------------- source (fdw)
class Src:
    """The Odoo 18 database seen through postgres_fdw as schema `src18` in the target DB."""

    def __init__(self, cr):
        self.cr = cr
        self._cols = {}
        self._fields = None
        self._m2m = None
        self._xmlid = {}

    def setup_fdw(self):
        cr = self.cr
        cr.execute("select 1 from pg_namespace where nspname=%s", (config.SRC_SCHEMA,))
        if cr.fetchone():
            return
        cr.execute("CREATE EXTENSION IF NOT EXISTS postgres_fdw")
        cr.execute("select 1 from pg_foreign_server where srvname=%s", (config.SRC_SCHEMA,))
        if not cr.fetchone():
            cr.execute(psql.SQL("CREATE SERVER {} FOREIGN DATA WRAPPER postgres_fdw OPTIONS (dbname %s, fetch_size '20000', use_remote_estimate 'true')")
                       .format(psql.Identifier(config.SRC_SCHEMA)), (config.SRC_DB,))
            cr.execute(psql.SQL("CREATE USER MAPPING FOR CURRENT_USER SERVER {}").format(psql.Identifier(config.SRC_SCHEMA)))
        cr.execute(psql.SQL("CREATE SCHEMA {}").format(psql.Identifier(config.SRC_SCHEMA)))
        cr.execute(psql.SQL("IMPORT FOREIGN SCHEMA public FROM SERVER {s} INTO {s}")
                   .format(s=psql.Identifier(config.SRC_SCHEMA)))
        cr.execute("ANALYZE")  # local stats; remote estimates come from src18 itself
        _logger.info("foreign schema %s imported", config.SRC_SCHEMA)

    def table_exists(self, table):
        self.cr.execute("select 1 from information_schema.tables where table_schema=%s and table_name=%s",
                        (config.SRC_SCHEMA, table))
        return bool(self.cr.fetchone())

    def columns(self, table):
        if table not in self._cols:
            self.cr.execute("""select column_name, data_type from information_schema.columns
                               where table_schema=%s and table_name=%s order by ordinal_position""",
                            (config.SRC_SCHEMA, table))
            self._cols[table] = dict(self.cr.fetchall())
        return self._cols[table]

    @property
    def fields(self):
        """(model, name) -> dict(ttype, relation, relation_table, column1, column2, company_dependent, translate, store)"""
        if self._fields is None:
            self.cr.execute(psql.SQL("""select model, name, ttype, relation, relation_table, column1, column2,
                                          company_dependent, translate, store, field_description
                                        from {}.ir_model_fields""").format(psql.Identifier(config.SRC_SCHEMA)))
            self._fields = {(r[0], r[1]): dict(ttype=r[2], relation=r[3], relation_table=r[4], column1=r[5], column2=r[6],
                                               company_dependent=r[7], translate=r[8], store=r[9], desc=r[10])
                            for r in self.cr.fetchall()}
        return self._fields

    def m2m_values(self, model, name, ids):
        """{record_id: [related ids]} for a many2many field of 18, read from its relation table."""
        f = self.fields.get((model, name))
        if not f or not f["relation_table"]:
            return {}
        self.cr.execute(psql.SQL("select {c1}, {c2} from {s}.{t} where {c1} = any(%s)").format(
            c1=psql.Identifier(f["column1"]), c2=psql.Identifier(f["column2"]),
            s=psql.Identifier(config.SRC_SCHEMA), t=psql.Identifier(f["relation_table"])), (list(ids),))
        out = {}
        for a, b in self.cr.fetchall():
            out.setdefault(a, []).append(b)
        return out

    def xmlid(self, model, res_id):
        """module.name of an 18 record (ignoring __export__ / studio), or None."""
        key = (model, res_id)
        if key not in self._xmlid:
            self.cr.execute(psql.SQL("""select module||'.'||name from {}.ir_model_data
                                        where model=%s and res_id=%s and module not in ('__export__','studio_customization')
                                        order by id limit 1""").format(psql.Identifier(config.SRC_SCHEMA)), (model, res_id))
            r = self.cr.fetchone()
            self._xmlid[key] = r[0] if r else None
        return self._xmlid[key]

    def row(self, table, rid, cols=("*",)):
        self.cr.execute(psql.SQL("select {} from {}.{} where id=%s").format(
            psql.SQL(", ").join(psql.SQL(c) if c == "*" else psql.Identifier(c) for c in cols),
            psql.Identifier(config.SRC_SCHEMA), psql.Identifier(table)), (rid,))
        r = self.cr.fetchone()
        if r is None:
            return None
        if cols == ("*",):
            names = [d[0] for d in self.cr.description]
            return dict(zip(names, r))
        return dict(zip(cols, r))

    def iter_batches(self, table, where="true", params=(), order="id", batch=500, after_id=None):
        """Yield lists of dict rows, ordered by id, optionally only ids > after_id.
        With a non-id order (hierarchies: parent_path) the whole selection is fetched once and chunked."""
        if order != "id":
            self.cr.execute(psql.SQL("select * from {}.{} where ({}) order by {}").format(
                psql.Identifier(config.SRC_SCHEMA), psql.Identifier(table), psql.SQL(where), psql.SQL(order)), tuple(params))
            names = [d[0] for d in self.cr.description]
            rows = [dict(zip(names, r)) for r in self.cr.fetchall()]
            for i in range(0, len(rows), batch):
                yield rows[i:i + batch]
            return
        last = after_id if after_id is not None else -1
        while True:
            self.cr.execute(psql.SQL("select * from {}.{} where ({}) and id > %s order by {} limit %s").format(
                psql.Identifier(config.SRC_SCHEMA), psql.Identifier(table), psql.SQL(where), psql.SQL(order)),
                tuple(params) + (last, batch))
            names = [d[0] for d in self.cr.description]
            rows = [dict(zip(names, r)) for r in self.cr.fetchall()]
            if not rows:
                return
            yield rows
            last = rows[-1]["id"]

    def count(self, table, where="true", params=()):
        self.cr.execute(psql.SQL("select count(*) from {}.{} where {}").format(
            psql.Identifier(config.SRC_SCHEMA), psql.Identifier(table), psql.SQL(where)), tuple(params))
        return self.cr.fetchone()[0]


# --------------------------------------------------------------------------- id map / bookkeeping
class IdMap:
    DDL = """
    CREATE TABLE IF NOT EXISTS etl_run (id serial PRIMARY KEY, started timestamptz DEFAULT now(), t0 timestamptz, notes text);
    CREATE TABLE IF NOT EXISTS etl_idmap (model varchar NOT NULL, old_id integer NOT NULL, new_id integer NOT NULL,
                                          legacy13_id varchar, PRIMARY KEY (model, old_id));
    CREATE INDEX IF NOT EXISTS etl_idmap_new ON etl_idmap (model, new_id);
    CREATE TABLE IF NOT EXISTS etl_refusal (id serial PRIMARY KEY, step varchar, model varchar, old_id integer, reason text,
                                            vals jsonb, created timestamptz DEFAULT now());
    CREATE TABLE IF NOT EXISTS etl_step (name varchar PRIMARY KEY, status varchar, started timestamptz, finished timestamptz, info jsonb);
    CREATE TABLE IF NOT EXISTS etl_conflict (id serial PRIMARY KEY, model varchar, old_id integer, new_id integer,
                                             fields_18 jsonb, fields_20 jsonb, created timestamptz DEFAULT now());
    """

    def __init__(self, cr):
        self.cr = cr
        self._cache = {}

    def setup(self):
        self.cr.execute(self.DDL)

    def load(self, model):
        if model not in self._cache:
            self.cr.execute("select old_id, new_id from etl_idmap where model=%s", (model,))
            self._cache[model] = dict(self.cr.fetchall())
        return self._cache[model]

    def get(self, model, old_id):
        if old_id is None:
            return None
        return self.load(model).get(old_id)

    def add_many(self, model, pairs, legacy=None):
        """pairs: iterable of (old_id, new_id); legacy: {old_id: legacy13 value}"""
        pairs = list(pairs)
        if not pairs:
            return
        cache = self.load(model)
        rows = [(model, o, n, (legacy or {}).get(o)) for o, n in pairs]
        execute_values(self.cr, """INSERT INTO etl_idmap (model, old_id, new_id, legacy13_id) VALUES %s
                                   ON CONFLICT (model, old_id) DO UPDATE SET new_id = EXCLUDED.new_id""", rows)
        for o, n in pairs:
            cache[o] = n

    def max_old(self, model):
        self.cr.execute("select coalesce(max(old_id), 0) from etl_idmap where model=%s", (model,))
        return self.cr.fetchone()[0]

    def count(self, model):
        self.cr.execute("select count(*) from etl_idmap where model=%s", (model,))
        return self.cr.fetchone()[0]

    def refuse(self, step, model, old_id, reason, vals=None):
        self.cr.execute("INSERT INTO etl_refusal (step, model, old_id, reason, vals) VALUES (%s,%s,%s,%s,%s)",
                        (step, model, old_id, reason[:2000], json.dumps(vals, default=str) if vals is not None else None))

    def step_status(self, name):
        self.cr.execute("select status from etl_step where name=%s", (name,))
        r = self.cr.fetchone()
        return r[0] if r else None

    def step_start(self, name, keep_progress=True):
        self.cr.execute("""INSERT INTO etl_step (name, status, started) VALUES (%s, 'running', now())
                           ON CONFLICT (name) DO UPDATE SET status='running', started=now(), finished=NULL,
                           info = CASE WHEN %s AND etl_step.status='running' THEN etl_step.info ELSE NULL END""", (name, keep_progress))

    def step_progress(self, name, last_id):
        self.cr.execute("""UPDATE etl_step SET info = coalesce(info, '{}'::jsonb) || jsonb_build_object('last_id', %s::int)
                           WHERE name=%s""", (last_id, name))

    def step_last(self, name):
        self.cr.execute("select info->>'last_id' from etl_step where name=%s and status='running'", (name,))
        r = self.cr.fetchone()
        return int(r[0]) if r and r[0] else None

    def step_done(self, name, info=None):
        self.cr.execute("UPDATE etl_step SET status='done', finished=now(), info=%s WHERE name=%s",
                        (json.dumps(info or {}, default=str), name))


# --------------------------------------------------------------------------- natural-key resolver
class Resolver:
    """18 many2one id -> 20 id. Order: etl_idmap, xmlid of the 18 record, natural key (per relation), None."""

    # relation -> function(src_row: dict, env) -> 20 record or None. src_row is the 18 record (all columns).
    KEYS = {}

    def __init__(self, env, src, idmap):
        self.env, self.src, self.idmap = env, src, idmap
        self._cache = {}
        self.unresolved = {}

    @staticmethod
    def _tr(v):
        """translatable jsonb -> en_US string"""
        if isinstance(v, dict):
            return v.get("en_US") or next(iter(v.values()), None)
        return v

    def resolve(self, relation, old_id):
        if not old_id:
            return None
        hit = self.idmap.get(relation, old_id)
        if hit is not None:
            return hit
        key = (relation, old_id)
        if key in self._cache:
            return self._cache[key]
        res = None
        if relation == "res.company":
            res = self.env.company.id
        elif relation == "res.users" and old_id in (1, 2):
            res = old_id
        elif relation in self.env:
            xmlid = self.src.xmlid(relation, old_id)
            if xmlid:
                rec = self.env.ref(xmlid, raise_if_not_found=False)
                if rec is not None and rec._name == relation:
                    res = rec.id
            if res is None and relation in self.KEYS:
                table = relation.replace(".", "_")
                row = self.src.row(table, old_id) if self.src.table_exists(table) else None
                if row:
                    try:
                        rec = self.KEYS[relation](row, self)
                        res = rec.id if rec else None
                    except Exception as e:  # noqa: BLE001
                        _logger.warning("resolver %s#%s failed: %s", relation, old_id, e)
                        res = None
        if res is None:
            self.unresolved[relation] = self.unresolved.get(relation, 0) + 1
        self._cache[key] = res
        return res

    def search1(self, model, domain):
        rec = self.env[model].sudo().with_context(active_test=False).search(domain, limit=1)
        return rec or None


def natural(relation):
    """decorator registering a natural-key lookup for a relation"""
    def deco(fn):
        Resolver.KEYS[relation] = fn
        return fn
    return deco


def _errmsg(e):
    txt = str(e) or getattr(e, "pgerror", "") or ""
    first = next((l for l in txt.splitlines() if l.strip()), "")
    return f"{type(e).__name__}: {first}"[:400]


# --------------------------------------------------------------------------- ORM lane
class OrmStep:
    """Declarative description of one ORM-lane load.

    model:      20 model name.                 table: 18 table (default model with dots -> underscores)
    where:      SQL on the 18 table.           order: SQL order (default id)
    key:        list of 20 field names forming a natural key: an existing 20 record with that key is
                reused (written) instead of created (reference data).
    skip:       18 columns/fields never copied.  rename: {18 column: 20 field}
    selection:  {field: {old_key: new_key}}    defaults: {field: value} applied when the value is missing
    transform:  fn(vals, row, ctx) -> vals or None (None = skip the row, recorded as refusal 'transform')
    after:      fn(ctx) called once when the step completes (post hooks)
    context:    extra ORM context.             batch: create batch size
    legacy:     18 column holding the v13 id to store in etl_idmap.legacy13_id (auto-detected if omitted)
    keep_ids:   create every new record with its 18 id (records are created one by one, the table's id
                sequence pointed at the 18 id first). URLs, bookmarks and record links in messages then
                stay valid. An id already taken on the target falls back to a fresh id (reported).
    id_sequences: fn(row) -> {table: id}: further sequences to point before each create (the partner a
                res.users create makes on its own)
    lane:       'orm'
    """

    def __init__(self, model, **kw):
        self.model = model
        self.name = kw.pop("name", model)
        self.table = kw.pop("table", model.replace(".", "_"))
        self.where = kw.pop("where", "true")
        self.params = kw.pop("params", ())
        self.order = kw.pop("order", "id")
        self.key = kw.pop("key", None)
        self.skip = set(kw.pop("skip", ())) | config.IGNORED_COLUMNS
        self.rename = kw.pop("rename", {})
        self.selection = kw.pop("selection", {})
        self.defaults = kw.pop("defaults", {})
        self.transform = kw.pop("transform", None)
        self.after = kw.pop("after", None)
        self.context = kw.pop("context", {})
        self.batch = kw.pop("batch", config.ORM_BATCH)
        self.legacy = kw.pop("legacy", None)
        self.force_fields = set(kw.pop("force_fields", ()))   # readonly/computed fields written anyway
        self.restore_dates = kw.pop("restore_dates", True)
        self.update_existing = kw.pop("update_existing", True)
        self.write_mapped = kw.pop("write_mapped", False)     # rows already in etl_idmap are written, not skipped
        self.retry = kw.pop("retry", None)                    # fn(vals, error_text) -> new vals to retry once, or None
        self.key_allow_null = kw.pop("key_allow_null", False)  # natural key may contain empty values (matched as = False)
        self.keep_ids = kw.pop("keep_ids", False)
        self.id_sequences = kw.pop("id_sequences", None)
        self.lane = "orm"
        if kw:
            raise TypeError(f"unknown OrmStep options: {kw}")


class SqlStep:
    """One SQL-lane load: `sql` is executed as-is (may use {S} for the source schema and {OFF} for the offset),
    typically INSERT INTO target SELECT ... FROM {S}.table ... . `register` = (model, table) adds the
    old_id -> old_id+OFF rows to etl_idmap for every row of the 18 table that got inserted (by matching
    ids in the target table). `chunk` = 18 table name + range size to split big tables by id ranges."""

    def __init__(self, name, sql, register=None, chunk=None, before=None, after=None, restore_dates=None):
        self.name, self.sql, self.register, self.chunk = name, sql, register, chunk
        self.before, self.after, self.restore_dates = before, after, restore_dates
        self.lane = "sql"


class FuncStep:
    """Arbitrary python step: fn(engine, ctx) -> info dict."""

    def __init__(self, name, fn):
        self.name, self.fn, self.lane = name, fn, "func"


class Engine:
    def __init__(self, env, run_name="run"):
        self.env = env
        self.cr = env.cr
        self.src = Src(self.cr)
        self.idmap = IdMap(self.cr)
        self.resolver = Resolver(env, self.src, self.idmap)
        self.run_name = run_name
        self.stats = {}
        self.delta_t0 = None      # plan §4.1: only rows created/modified on 18 after this timestamp
        self.golive = None        # 20 records written after this timestamp are never overwritten (-> etl_conflict)

    # ---- setup
    def setup(self):
        self.idmap.setup()
        self.src.setup_fdw()
        self.cr.execute("""
        CREATE OR REPLACE FUNCTION etl_shift_urls(body text, off integer) RETURNS text LANGUAGE plpgsql IMMUTABLE AS $$
        DECLARE m text[]; out text := body;
        BEGIN
          IF body IS NULL OR position('/web/' in body) = 0 THEN RETURN body; END IF;
          FOR m IN SELECT DISTINCT x FROM regexp_matches(body, '/web/(image|content)/(\\d+)', 'g') AS x LOOP
            out := regexp_replace(out, '/web/' || m[1] || '/' || m[2] || '(?!\\d)',
                                  '/web/' || m[1] || '/' || (m[2]::bigint + off)::text, 'g');
          END LOOP;
          RETURN out;
        END $$;""")
        self.cr.commit()

    def dry_run_guard(self):
        """Non-production runs: no channel out of the target DB (crons, outgoing/incoming mail, IAP)."""
        if config.PRODUCTION:
            return
        cr = self.cr
        cr.execute("UPDATE ir_cron SET active = false WHERE active")
        cr.execute("UPDATE ir_mail_server SET active = false WHERE active")
        cr.execute("SELECT to_regclass('public.fetchmail_server')")
        if cr.fetchone()[0]:
            cr.execute("UPDATE fetchmail_server SET active = false WHERE active")
        # IAP accounts are not migrated; any a module created on the target holds no prod token
        cr.execute("UPDATE ir_config_parameter SET value = %s WHERE key = 'web.base.url'",
                   (f"http://localhost:{config.PORT_TARGET20}",))
        self.cr.commit()

    # ---- helpers
    _ALIGN_TYPES = ("many2one", "integer", "date", "datetime", "selection", "boolean")

    class Misaligned(Exception):
        pass

    def _check_alignment(self, step, Model, vals_list, recs):
        """create() may return the records in another order than the vals (documents.document regroups its vals by
        res_model). Read the created records back and compare the plain values sent (m2o, ints, dates, selections,
        booleans; chars are excluded: 20 formats phones/e-mails). Any difference -> Misaligned, and the caller rolls the
        batch back and creates one by one, which is exact by construction."""
        if len(recs) != len(vals_list):
            raise self.Misaligned(f"{len(recs)} records for {len(vals_list)} vals")
        if len(recs) < 2:
            return
        F = Model._fields
        names = [k for k in sorted({k for v in vals_list for k in v}) if k in F and F[k].store and F[k].type in self._ALIGN_TYPES
                 and not F[k].compute and not F[k].related and not F[k].company_dependent]

        def norm(x):
            if x is None or x is False or x == "":
                return None
            if isinstance(x, (list, tuple)):
                return norm(x[0]) if x else None
            return str(x)[:19]   # datetimes without microseconds; ints/selections as text

        # anchors: the sent fields with the most distinct values in this batch. A reordered record differs on several of
        # them at once; a value 20 changed on its own (pan entity derived from the GSTIN, ...) differs on one only.
        card = {n: len({norm(v.get(n)) for v in vals_list}) for n in names}
        anchors = [n for n, c in sorted(card.items(), key=lambda kv: -kv[1]) if c > 1][:3]
        if not anchors:
            return
        need = min(2, len(anchors))
        got = recs.read(anchors, load=None)
        bad = collections.Counter(); moved = 0
        for v, d in zip(vals_list, got):
            diffs = [n for n in anchors if norm(v.get(n)) != norm(d.get(n))]
            bad.update(diffs)
            if len(diffs) >= need:
                moved += 1
        if moved:
            _logger.warning("%s: batch of %d not aligned with create() result: %d records differ on %s; creating one by one",
                            step.name, len(vals_list), moved, ", ".join(f"{k}:{c}" for k, c in bad.most_common(4)))
            raise self.Misaligned(str(bad.most_common(3)))

    def _fields20(self, Model):
        return Model.fields_get(attributes=["type", "relation", "store", "readonly", "related", "selection", "required"])

    def _plan_fields(self, step, Model, f20):
        """Which 18 columns / m2m fields feed which 20 fields."""
        cols18 = self.src.columns(step.table)
        plan = []   # (src_name, kind, target, meta)
        model18 = step.model
        for c, dtype in cols18.items():
            if c in step.skip:
                continue
            target = step.rename.get(c, c)
            if target not in f20:
                continue
            fld = Model._fields[target]
            if fld.compute and fld.readonly and not fld.inverse and not fld.related and target not in step.force_fields:
                continue
            if f20[target]["type"] == "one2many":
                continue
            meta = self.src.fields.get((model18, c), {})
            plan.append((c, "col", target, {"dtype": dtype, "ttype20": f20[target]["type"], "rel": f20[target].get("relation"),
                                             "company_dependent": meta.get("company_dependent"), "translate": meta.get("translate")}))
        # many2many of 18 whose 20 counterpart is a many2many
        for (m, name), meta in self.src.fields.items():
            if m != model18 or meta["ttype"] != "many2many" or not meta["relation_table"] or name in step.skip:
                continue
            target = step.rename.get(name, name)
            if target in f20 and f20[target]["type"] == "many2many":
                fld = Model._fields[target]
                if fld.compute and fld.readonly and not fld.inverse and target not in step.force_fields:
                    continue
                plan.append((name, "m2m", target, {"rel": f20[target]["relation"]}))
        return plan

    def _legacy_col(self, step):
        if step.legacy:
            return step.legacy
        for c in self.src.columns(step.table):
            if c.startswith(config.LEGACY_PREFIXES):
                return c
        return None

    def _convert(self, step, row, plan, m2m_cache, f20):
        vals, unresolved = {}, []
        for src_name, kind, target, meta in plan:
            if kind == "m2m":
                ids = m2m_cache.get(src_name, {}).get(row["id"], [])
                new = [self.resolver.resolve(meta["rel"], i) for i in ids]
                new = [i for i in new if i]
                if ids and not new:
                    unresolved.append(src_name)
                vals[target] = [(6, 0, new)]
                continue
            v = row.get(src_name)
            if v is None:
                continue
            if meta["dtype"] == "jsonb" and isinstance(v, dict):
                if meta.get("company_dependent"):
                    v = v.get(str(config.COMPANY), next(iter(v.values()), None))
                elif meta.get("translate") or meta["ttype20"] in ("char", "text", "html"):
                    v = v.get("en_US") or next(iter(v.values()), None)
            if v is None or v == "":
                continue
            t = meta["ttype20"]
            if t == "many2one":
                nv = self.resolver.resolve(meta["rel"], int(v))
                if nv is None:
                    unresolved.append(src_name)
                    continue
                vals[target] = nv
            elif t == "selection":
                if target == "tz":
                    v = config.TZ_ALIASES.get(v, v)
                mp = step.selection.get(target)
                if mp:
                    v = mp.get(v, v)
                    if v is None:
                        continue
                vals[target] = v
            elif t in ("integer",) and isinstance(v, float):
                vals[target] = int(round(v))
            elif t in ("date", "datetime"):
                vals[target] = v
            elif t == "binary":
                continue  # binaries travel as attachments (SQL lane)
            else:
                vals[target] = v
        for k, dv in step.defaults.items():
            vals.setdefault(k, dv() if callable(dv) else dv)
        return vals, unresolved

    def _find_existing(self, step, Model, vals):
        if not step.key:
            return None
        dom = []
        for k in step.key:
            v = vals.get(k)
            if v in (None, False, ""):
                if not step.key_allow_null:
                    return None
                dom.append((k, "=", False)); continue
            dom.append((k, "=", v))
        rec = Model.search(dom, limit=1)
        return rec.id if rec else None

    def _restore_dates(self, table, model):
        """create/write date and uid from 18 for every mapped row of `model` in `table`."""
        cols = self.src.columns(table)
        if "create_date" not in cols:
            return
        set_uid = "write_uid" in cols and "create_uid" in cols
        self.cr.execute(psql.SQL("""
            UPDATE {t} x SET create_date = s.create_date, write_date = s.write_date {uids}
            FROM etl_idmap m JOIN {S}.{t} s ON s.id = m.old_id
            {ujoin}
            WHERE m.model = %s AND x.id = m.new_id""").format(
            t=psql.Identifier(table), S=psql.Identifier(config.SRC_SCHEMA),
            # a creator 18 never recorded stays unrecorded; an unmapped one becomes the system user
            uids=psql.SQL(", create_uid = CASE WHEN s.create_uid IS NULL THEN NULL ELSE COALESCE(u1.new_id, CASE WHEN s.create_uid IN (1,2) THEN s.create_uid END, 1) END,"
                          " write_uid = CASE WHEN s.write_uid IS NULL THEN NULL ELSE COALESCE(u2.new_id, CASE WHEN s.write_uid IN (1,2) THEN s.write_uid END, 1) END") if set_uid else psql.SQL(""),
            ujoin=psql.SQL("LEFT JOIN etl_idmap u1 ON u1.model='res.users' AND u1.old_id = s.create_uid "
                           "LEFT JOIN etl_idmap u2 ON u2.model='res.users' AND u2.old_id = s.write_uid") if set_uid else psql.SQL("")),
            (model,))
        return self.cr.rowcount

    # ---- ORM lane
    def run_orm(self, step, ctx):
        env = self.env
        if step.model not in env:
            _logger.error("%s: model missing on 20", step.name); return
        if not self.src.table_exists(step.table):
            _logger.warning("%s: table %s missing on 18", step.name, step.table); return
        Model = env[step.model].with_context(**{**config.SILENT_CTX, **step.context})
        f20 = self._fields20(Model)
        plan = self._plan_fields(step, Model, f20)
        m2m_names = [p[0] for p in plan if p[1] == "m2m"]
        legacy_col = self._legacy_col(step)
        where, params = step.where, tuple(step.params)
        if self.delta_t0 and "create_date" in self.src.columns(step.table):
            where = f"({where}) AND (create_date > %s OR write_date > %s)"; params = params + (self.delta_t0, self.delta_t0)
        total = self.src.count(step.table, where, params)
        after = self.idmap.step_last(step.name) if step.order == "id" else None   # resume where this step stopped
        done_before = self.idmap.count(step.model)
        created = updated = refused = 0
        unresolved = {}
        t0 = time.time()
        _logger.info("%s: %d rows on 18, %d already mapped, %d fields (%d m2m)", step.name, total, done_before, len(plan), len(m2m_names))
        conflicts = 0
        ids_changed = []
        for rows in self.src.iter_batches(step.table, where, params, step.order, step.batch, after_id=after):
            mapped = self.idmap.load(step.model)
            if self.delta_t0:
                # modified rows: overwrite only when the 20 copy was not touched since go-live
                keep = []
                for r in rows:
                    new = mapped.get(r["id"])
                    if new is None or not self.golive:
                        keep.append(r); continue
                    self.cr.execute(psql.SQL("select write_date from {} where id=%s").format(psql.Identifier(step.table)), (new,))
                    wd = self.cr.fetchone()
                    if wd and wd[0] and wd[0] > self.golive:
                        self.cr.execute("INSERT INTO etl_conflict (model, old_id, new_id, fields_18, fields_20) VALUES (%s,%s,%s,%s,%s)",
                                        (step.model, r["id"], new, json.dumps({k: v for k, v in r.items() if k != "id"}, default=str),
                                         json.dumps({"write_date": wd[0]}, default=str)))
                        conflicts += 1
                    else:
                        keep.append(r)
                rows = keep
            elif not step.write_mapped:
                rows = [r for r in rows if r["id"] not in mapped]
            if not rows:
                continue
            m2m_cache = {n: self.src.m2m_values(step.model, n, [r["id"] for r in rows]) for n in m2m_names}
            todo = []  # (old_id, vals, existing_id)
            for row in rows:
                vals, unres = self._convert(step, row, plan, m2m_cache, f20)
                for u in unres:
                    unresolved[u] = unresolved.get(u, 0) + 1
                if step.transform:
                    try:
                        vals = step.transform(vals, row, ctx)
                    except Exception as e:  # noqa: BLE001
                        self.idmap.refuse(step.name, step.model, row["id"], f"transform: {e}", vals); refused += 1; continue
                    if vals is None:
                        if step.write_mapped:
                            continue   # nothing to write for this already-mapped row
                        self.idmap.refuse(step.name, step.model, row["id"], "transform: skipped", None); refused += 1; continue
                existing = mapped.get(row["id"]) if (step.write_mapped or self.delta_t0) else None
                existing = existing or self._find_existing(step, Model, vals)
                todo.append((row["id"], vals, existing))
            legacy = {r["id"]: r.get(legacy_col) for r in rows} if legacy_col else None
            # existing (reference data) -> write
            pairs = []
            for old, vals, existing in [t for t in todo if t[2]]:
                try:
                    with self.cr.savepoint():
                        if step.update_existing:
                            Model.browse(existing).write(vals)
                    pairs.append((old, existing)); updated += 1
                except Exception as e:  # noqa: BLE001
                    self.idmap.refuse(step.name, step.model, old, f"write: {_errmsg(e)}", vals); refused += 1
            # new -> batch create, fall back to one-by-one to isolate refusals
            new = [t for t in todo if not t[2]]
            if new and step.keep_ids:
                rows_by_id = {r["id"]: r for r in rows}
                for old, vals, _ in new:
                    rec, msg = None, ""
                    for attempt in (vals, None):
                        if attempt is None:
                            attempt = step.retry(dict(vals), msg) if step.retry and msg else None
                            if not attempt:
                                break
                        try:
                            rec = self._create_with_id(step, Model, old, attempt, rows_by_id[old])
                            break
                        except Exception as e2:  # noqa: BLE001
                            msg = _errmsg(e2)
                    if rec is None:
                        self.idmap.refuse(step.name, step.model, old, f"create: {msg}", vals); refused += 1
                        continue
                    pairs.append((old, rec.id)); created += 1
                    if rec.id != old:
                        ids_changed.append(old)
            elif new:
                try:
                    with self.cr.savepoint():
                        recs = Model.create([v for _, v, _ in new])
                        self._check_alignment(step, Model, [v for _, v, _ in new], recs)   # raises inside the savepoint
                    pairs += [(old, rec.id) for (old, _, _), rec in zip(new, recs)]; created += len(new)
                except Exception as e:  # noqa: BLE001
                    _logger.debug("%s: batch create failed (%s), retrying one by one", step.name, str(e)[:120])
                    for old, vals, _ in new:
                        try:
                            with self.cr.savepoint():
                                rec = Model.create(vals)
                            pairs.append((old, rec.id)); created += 1
                        except Exception as e2:  # noqa: BLE001
                            msg = _errmsg(e2)
                            vals2 = step.retry(dict(vals), msg) if step.retry else None
                            if vals2:
                                try:
                                    with self.cr.savepoint():
                                        rec = Model.create(vals2)
                                    pairs.append((old, rec.id)); created += 1
                                    continue
                                except Exception as e3:  # noqa: BLE001
                                    msg = _errmsg(e3)
                            self.idmap.refuse(step.name, step.model, old, f"create: {msg}", vals); refused += 1
            self.idmap.add_many(step.model, pairs, legacy)
            if step.order == "id":
                self.idmap.step_progress(step.name, rows[-1]["id"])
            self.cr.commit()
            if (created + updated + refused) % (step.batch * 10) < step.batch:
                _logger.info("%s: %d/%d (%.0f rec/s)", step.name, created + updated + refused, total - done_before,
                             (created + updated + refused) / max(time.time() - t0, 1e-6))
        if step.keep_ids:
            # past every id now in use: nothing created later can take an id a prod record needs
            for table in [Model._table] + list((step.id_sequences({}) if step.id_sequences else {}).keys()):
                self.cr.execute(psql.SQL("SELECT setval(pg_get_serial_sequence(%s, 'id'), "
                                         "GREATEST((SELECT coalesce(max(id), 1) FROM {}), 1))").format(psql.Identifier(table)),
                                (table,))
        restored = self._restore_dates(step.table, step.model) if step.restore_dates else None
        if step.after:
            step.after(ctx)
        self.cr.commit()
        info = dict(src=total, created=created, updated=updated, refused=refused, unresolved=unresolved,
                    restored=restored, conflicts=conflicts, seconds=round(time.time() - t0, 1))
        if step.keep_ids:
            info["ids_kept"] = created - len(ids_changed)
            info["ids_changed"] = ids_changed[:50]
        self.stats[step.name] = info
        _logger.info("%s: DONE %s", step.name, json.dumps(info, default=str))
        return info

    def _point_sequence(self, table, wanted):
        """Make the next id of `table` be `wanted` when it is free; otherwise move the sequence past every
        id in use, so the record gets a fresh id instead of one a later prod record needs."""
        self.cr.execute(psql.SQL("SELECT 1 FROM {} WHERE id = %s").format(psql.Identifier(table)), (wanted,))
        if not self.cr.fetchone():
            self.cr.execute("SELECT setval(pg_get_serial_sequence(%s, 'id'), %s, false)", (table, wanted))
            return True
        self.cr.execute(psql.SQL("SELECT setval(pg_get_serial_sequence(%s, 'id'), "
                                 "GREATEST((SELECT coalesce(max(id), 1) FROM {}), 1))").format(psql.Identifier(table)),
                        (table,))
        return False

    def _create_with_id(self, step, Model, old, vals, row):
        """keep_ids: create one record with its 18 id (and the ids id_sequences asks for)."""
        with self.cr.savepoint():
            self._point_sequence(Model._table, old)
            for table, wanted in (step.id_sequences(row) if step.id_sequences else {}).items():
                if wanted:
                    self._point_sequence(table, wanted)
            return Model.create(vals)

    # ---- SQL lane
    def run_sql(self, step, ctx):
        t0 = time.time()
        if step.before:
            step.before(ctx)
        fmt = dict(S=config.SRC_SCHEMA, OFF=config.OFFSET)
        inserted = 0
        if step.chunk:
            table, size = step.chunk
            self.cr.execute(psql.SQL("select coalesce(min(id),0), coalesce(max(id),0) from {}.{}").format(
                psql.Identifier(config.SRC_SCHEMA), psql.Identifier(table)))
            lo, hi = self.cr.fetchone()
            start = lo
            while start <= hi:
                end = start + size - 1
                self.cr.execute(step.sql.format(LO=start, HI=end, **fmt))
                inserted += self.cr.rowcount if self.cr.rowcount > 0 else 0
                if step.register:
                    self._register(step.register, start, end)
                self.cr.commit()
                _logger.info("%s: ids %d-%d done (%d rows so far)", step.name, start, end, inserted)
                start = end + 1
        else:
            self.cr.execute(step.sql.format(LO=0, HI=2**31 - 1, **fmt))
            inserted = self.cr.rowcount if self.cr.rowcount > 0 else 0
            if step.register:
                self._register(step.register, 0, 2**31 - 1)
            self.cr.commit()
        if step.after:
            step.after(ctx)
        self.cr.commit()
        info = dict(inserted=inserted, seconds=round(time.time() - t0, 1))
        self.stats[step.name] = info
        _logger.info("%s: DONE %s", step.name, json.dumps(info))
        return info

    def _register(self, reg, lo, hi):
        model, table = reg
        lo_t = lo + config.OFFSET
        hi_t = min(hi + config.OFFSET, 2**31 - 1)
        self.cr.execute(psql.SQL("""
            INSERT INTO etl_idmap (model, old_id, new_id)
            SELECT %s, t.id - %s, t.id FROM {t} t
            WHERE t.id BETWEEN %s AND %s
            ON CONFLICT (model, old_id) DO NOTHING""").format(t=psql.Identifier(table)),
            (model, config.OFFSET, lo_t, hi_t))
        self.idmap._cache.pop(model, None)

    # ---- orchestration
    def _absent_tables(self, step):
        """Tables a step needs that this source snapshot (or the target) does not have.
        A smaller production source (fewer modules than the ETL was built against) must
        skip those steps instead of crashing: the data simply does not exist to migrate."""
        absent = []
        if isinstance(step, TableCopy):
            if not self.src.table_exists(step.table18):
                absent.append(f"src.{step.table18}")
            self.cr.execute("select 1 from information_schema.tables where table_schema='public' and table_name=%s",
                            (step.table20,))
            if not self.cr.fetchone():
                absent.append(f"target.{step.table20}")
        elif step.lane == "sql" and step.sql:
            for t in set(re.findall(r"\{S\}\.([a-z0-9_]+)", step.sql)):
                if not self.src.table_exists(t):
                    absent.append(f"src.{t}")
        return absent

    def run_steps(self, steps, ctx, only=None, force=False):
        for step in steps:
            if only and step.name not in only:
                continue
            status = self.idmap.step_status(step.name)
            if status == "done" and not force:
                _logger.info("%s: already done, skipped", step.name); continue
            absent = self._absent_tables(step)
            if absent:
                _logger.warning("%s: skipped, table(s) absent on this source/target: %s", step.name, ", ".join(absent))
                self.idmap.step_done(step.name, {"skipped_absent_tables": absent}); self.cr.commit()
                continue
            self.idmap.step_start(step.name, keep_progress=not force); self.cr.commit()
            try:
                if step.lane == "orm":
                    info = self.run_orm(step, ctx)
                elif step.lane == "sql":
                    info = self.run_sql(step, ctx)
                else:
                    t0 = time.time(); info = step.fn(self, ctx) or {}; info["seconds"] = round(time.time() - t0, 1)
                    self.cr.commit(); _logger.info("%s: DONE %s", step.name, json.dumps(info, default=str))
            except Exception:
                self.cr.rollback()
                _logger.exception("%s: FAILED", step.name)
                raise
            self.idmap.step_done(step.name, info); self.cr.commit()
            self.dry_run_guard()


# --------------------------------------------------------------------------- SQL lane: table copy helper
class TableCopy(SqlStep):
    """INSERT INTO <table20> (shared columns) SELECT <exprs> FROM src18.<table18> s <joins> WHERE <where>.

    overrides: {column: SQL expression} (may use {OFF}, {S}, and aliases from `joins`); columns present only
    on one side are ignored automatically; `exclude` drops shared columns; `extra` adds 20-only columns
    with an expression. `register`=(model, table20) maps old ids -> ids in the target (id must be id+OFF).
    `chunk` = range size on s.id (None = one statement). `on_conflict` = 'DO NOTHING' etc.
    Common id-map joins are available via the helpers below: IDM(alias, model, expr) -> LEFT JOIN etl_idmap.
    """

    def __init__(self, name, table18, table20=None, overrides=None, joins=(), where="true", exclude=(), extra=None,
                 register=None, chunk=None, on_conflict=None, before=None, after=None, order=None, verbatim_ok=()):
        super().__init__(name, None, register=register, chunk=(table18, chunk) if chunk else None, before=before, after=after)
        self.table18, self.table20 = table18, table20 or table18
        self.overrides, self.joins, self.where, self.exclude = overrides or {}, list(joins), where, set(exclude)
        self.extra, self.on_conflict, self.order = extra or {}, on_conflict, order
        self.verbatim_ok = set(verbatim_ok)   # FK columns deliberately copied as-is (same ids on both sides)

    def build(self, engine):
        cols18 = engine.src.columns(self.table18)
        engine.cr.execute("select column_name from information_schema.columns where table_schema='public' and table_name=%s",
                          (self.table20,))
        cols20 = [r[0] for r in engine.cr.fetchall()]
        cols = [c for c in cols20 if (c in cols18 or c in self.overrides or c in self.extra) and c not in self.exclude]
        exprs = []
        for c in cols:
            if c in self.overrides:
                exprs.append(self.overrides[c])
            elif c in self.extra:
                exprs.append(self.extra[c])
            elif c in ("create_uid", "write_uid"):
                exprs.append(f"COALESCE(u_{c}.new_id, CASE WHEN s.{c} IN (1,2) THEN s.{c} END, 1)")
            else:
                exprs.append(f's."{c}"')   # quoted: mail_mail.references is a reserved word
        # FK audit: a foreign-key column copied verbatim carries a 19 id into a 20 table —
        # silently wrong whenever the ids differ. Every FK must be overridden, excluded,
        # or explicitly declared verbatim_ok.
        engine.cr.execute("""SELECT DISTINCT kcu.column_name FROM information_schema.table_constraints tc
            JOIN information_schema.key_column_usage kcu ON kcu.constraint_name = tc.constraint_name
                 AND kcu.constraint_schema = tc.constraint_schema
            WHERE tc.constraint_type = 'FOREIGN KEY' AND tc.table_name = %s""", (self.table20,))
        fkcols = {r[0] for r in engine.cr.fetchall()}
        loose = [c for c in cols if c in fkcols and c not in self.overrides and c not in self.extra
                 and c not in ("create_uid", "write_uid") and c not in self.verbatim_ok]
        if loose:
            raise RuntimeError(f"{self.name}: FK columns copied verbatim without a mapping decision: {sorted(loose)}")
        joins = list(self.joins)
        for c in ("create_uid", "write_uid"):
            if c in cols and c not in self.overrides:
                joins.append(f"LEFT JOIN etl_idmap u_{c} ON u_{c}.model = 'res.users' AND u_{c}.old_id = s.{c}")
        where = self.where
        # a leaner source (fewer modules than the ETL was written against) lacks some s.<col>
        # the joins/where reference; every such lookup is a LEFT JOIN, so NULL is the honest value.
        missing = sorted({c for c in re.findall(r"\bs\.([a-z0-9_]+)", " ".join(joins) + " " + where)
                          if c not in cols18})
        if missing:
            _logger.warning("%s: source lacks column(s) %s; treated as NULL", self.name, ", ".join(missing))
            pat = re.compile(r"\bs\.(%s)\b" % "|".join(missing))
            joins = [pat.sub("NULL", j) for j in joins]
            where = pat.sub("NULL", where)
        on_conflict = self.on_conflict
        if engine.delta_t0:
            if "create_date" in cols18:
                where = f"({where}) AND s.create_date > '{engine.delta_t0}'"
            on_conflict = on_conflict or "DO NOTHING"
        sql = (f"INSERT INTO {self.table20} ({', '.join(f'\"{c}\"' for c in cols)})\nSELECT {', '.join(exprs)}\n"
               f"FROM {{S}}.{self.table18} s\n" + "\n".join(joins) +
               f"\nWHERE ({where}) AND s.id BETWEEN {{LO}} AND {{HI}}" + (f"\nORDER BY {self.order}" if self.order else "") +
               (f"\nON CONFLICT {on_conflict}" if on_conflict else ""))
        return sql


def IDM(alias, model, expr):
    """LEFT JOIN etl_idmap <alias> for model on <expr> (an 18 id expression)."""
    return f"LEFT JOIN etl_idmap {alias} ON {alias}.model = '{model}' AND {alias}.old_id = {expr}"


def _run_sql_with_build(self, step, ctx):
    if isinstance(step, TableCopy):
        step.sql = step.build(self)
        _logger.debug("%s:\n%s", step.name, step.sql)
    return Engine._run_sql_orig(self, step, ctx)


Engine._run_sql_orig = Engine.run_sql
Engine.run_sql = _run_sql_with_build
