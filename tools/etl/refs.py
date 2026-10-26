"""Natural-key lookups: how an unmapped 18 many2one is found on 20.
Each function receives the 18 row (dict of all columns) and the resolver; returns a 20 record or None.
Registered through @natural(relation); used automatically by the ORM lane for that relation."""
from .core import natural, Resolver

tr = Resolver._tr


@natural("res.country")
def _country(row, r):
    return r.search1("res.country", [("code", "=", row["code"])])


@natural("res.country.state")
def _state(row, r):
    country = r.resolve("res.country", row["country_id"])
    rec = r.search1("res.country.state", [("country_id", "=", country), ("code", "=", row["code"])])
    if rec is None and country:  # user-made states of 18 (IN-201301 ...) are created as-is
        rec = r.env["res.country.state"].sudo().create({"country_id": country, "code": row["code"], "name": tr(row["name"]) or row["code"]})
    return rec


@natural("res.currency")
def _currency(row, r):
    rec = r.search1("res.currency", [("name", "=", row["name"])])
    if rec is not None and not rec.active:
        rec.write({"active": True})
    return rec


@natural("res.lang")
def _lang(row, r):
    return r.search1("res.lang", [("code", "=", row["code"])])


@natural("uom.uom")
def _uom(row, r):
    rec = r.search1("uom.uom", [("name", "=", tr(row["name"]))])
    if rec is not None and not rec.active:
        rec.write({"active": True})
    if rec is None:
        rec = r.env["uom.uom"].sudo().create({"name": tr(row["name"]), "relative_factor": 1.0})
    return rec


@natural("res.partner.industry")
def _industry(row, r):
    return r.search1("res.partner.industry", [("name", "=", tr(row["name"]))])


@natural("res.partner.category")
def _pcateg(row, r):
    return r.search1("res.partner.category", [("name", "=", tr(row["name"]))])


@natural("account.analytic.plan")
def _aplan(row, r):
    return r.search1("account.analytic.plan", [("name", "=", tr(row["name"]))])


@natural("mail.message.subtype")
def _subtype(row, r):
    return r.search1("mail.message.subtype", [("name", "=", tr(row["name"])), ("res_model", "=", row.get("res_model"))])


@natural("mail.activity.type")
def _atype(row, r):
    return r.search1("mail.activity.type", [("name", "=", tr(row["name"]))])


@natural("ir.model")
def _model(row, r):
    return r.search1("ir.model", [("model", "=", row["model"])])


@natural("ir.model.fields")
def _field(row, r):
    return r.search1("ir.model.fields", [("model", "=", row["model"]), ("name", "=", row["name"])])


@natural("res.users")
def _user(row, r):
    return r.search1("res.users", [("login", "=", row["login"])])


@natural("res.groups")
def _group(row, r):
    return None  # groups only by xmlid: prod has no DB-created groups


@natural("ir.ui.menu")
def _menu(row, r):
    return None  # menus only by xmlid


@natural("ir.sequence")
def _seq(row, r):
    return r.search1("ir.sequence", [("code", "=", row["code"])]) if row.get("code") else None


@natural("ir.actions.report")
def _report(row, r):
    return r.search1("ir.actions.report", [("report_name", "=", row["report_name"])])


@natural("mail.template")
def _tmpl(row, r):
    return r.search1("mail.template", [("name", "=", tr(row["name"]))])


@natural("res.partner.title")
def _title(row, r):
    return None  # model gone on 20; the partner transform keeps the title as a name prefix


@natural("res.company")
def _company(row, r):
    return r.env.company
