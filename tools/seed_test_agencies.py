#!/usr/bin/env python3
"""Put invented agencies on a TEST copy, at least one for every trade, so the desk and the app can be
tried with something to choose from.

    python3 tools/seed_test_agencies.py              dry run: shows what would be added
    python3 tools/seed_test_agencies.py --apply      adds them
    python3 tools/seed_test_agencies.py --url http://127.0.0.1:8094 --db revert20 --login … --password … [--apply]

It talks to a running server as a staff login and adds each agency with the desk's own "add agency"
action, so the records are exactly what the screens make. Run it twice and nothing is added twice.

It refuses a database that is not marked as a test copy (`database.is_neutralized`). A test copy never
sends a message, and the names and mobile numbers below are invented. Never run it on the live database.

Every firm and person gets the contact tag "Sample data", so they can be found and removed later.

The numbers follow one rule, so a tester needs no list:

    90000 TT0AP     TT = the trade, 01 Civil … 15 Landscape (the order in Setup)
                    A  = which agency of that trade, P = which of its people

    90000 01011 is the first civil agency's first person; 90000 01012 is its second person.
An agency with several trades is filed under the first one.
"""
import argparse
import http.cookiejar
import json
import re
import sys
import urllib.request

TAG = "Sample data"
TRADES = ["civ", "tile", "stone", "elec", "plmb", "pop", "carp", "col", "alu", "fab", "ac", "av", "sf", "soft", "land"]

# firm, trades, language of its messages, which agency of its first trade, people (name, what they do)
AGENCIES = [
    ("Ambica Civil Works", ["civ"], "gu", 1, [("Bharatbhai Prajapati", "Owner"), ("Mukeshbhai Prajapati", "Site supervisor")]),
    ("Ramdev Construction", ["civ", "tile"], "hi", 2, [("Ramlal Kumawat", "Contractor")]),
    ("Shreeji Tiles Fitting", ["tile"], "hi", 1, [("Dinesh Kumawat", "Tile fitter")]),
    ("Marwar Stone Works", ["stone"], "hi", 1, [("Bhanwarlal Salat", "Stone mason")]),
    ("Umiya Electricals", ["elec"], "gu", 1, [("Nileshbhai Patel", "Owner"), ("Sanjay Thakor", "Wireman")]),
    ("Khodiyar Plumbing Works", ["plmb"], "gu", 1, [("Rameshbhai Makwana", "Owner")]),
    ("Aqua Line Plumbing", ["plmb"], "hi", 2, [("Imran Shaikh", "Plumber")]),
    ("Royal POP Ceiling", ["pop"], "hi", 1, [("Salim Ansari", "Owner")]),
    ("Shakti POP and Colour", ["pop", "col"], "hi", 2, [("Rajkumar Yadav", "Contractor")]),
    ("Vishwakarma Wood Works", ["carp"], "hi", 1, [("Sureshji Jangid", "Mistri"), ("Mohanlal Jangid", "Carpenter")]),
    ("Rangoli Painting Works", ["col"], "gu", 1, [("Kanubhai Parmar", "Owner")]),
    ("Crystal Aluminium and Glass", ["alu"], "gu", 1, [("Jigneshbhai Panchal", "Owner")]),
    ("Bajrang Fabrication", ["fab"], "gu", 1, [("Jayeshbhai Luhar", "Owner")]),
    ("Cool Point Air Conditioning", ["ac"], "en", 1, [("Ankit Trivedi", "Sales engineer"), ("Vipul Rana", "Service engineer")]),
    ("Swar AV and Networks", ["av"], "en", 1, [("Parth Desai", "Project engineer")]),
    ("Aangan Furniture Studio", ["sf"], "en", 1, [("Riya Mehta", "Order coordinator")]),
    ("Resham Furnishings", ["soft"], "gu", 1, [("Nehaben Vora", "Owner")]),
    ("Green Leaf Landscapes", ["land"], "gu", 1, [("Maheshbhai Mali", "Owner")]),
]
LANG = {"gu": "gu_IN", "hi": "hi_IN", "en": "en_US"}


def number(trade, agency_no, person_no):
    return "90000 %02d0%d%d" % (TRADES.index(trade) + 1, agency_no, person_no)


def digits(phone):
    return re.sub(r"\D", "", phone or "")[-10:]


class Server:
    def __init__(self, url, db):
        self.url, self.db = url.rstrip("/"), db
        self.opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))

    def post(self, path, params):
        body = json.dumps({"jsonrpc": "2.0", "method": "call", "params": params}).encode()
        request = urllib.request.Request(self.url + path, data=body, headers={"Content-Type": "application/json"})
        answer = json.loads(self.opener.open(request, timeout=120).read())
        if answer.get("error"):
            data = answer["error"].get("data") or {}
            raise SystemExit("The server refused: %s" % (data.get("message") or answer["error"].get("message")))
        return answer.get("result")

    def login(self, login, password):
        result = self.post("/web/session/authenticate", {"db": self.db, "login": login, "password": password})
        if not result or not result.get("uid"):
            raise SystemExit("Could not sign in as %s on %s." % (login, self.db))

    def call(self, model, method, *args, **kwargs):
        return self.post("/web/dataset/call_kw/%s/%s" % (model, method),
                         {"model": model, "method": method, "args": list(args), "kwargs": kwargs})


def main():
    parser = argparse.ArgumentParser(description="Invented agencies for a test copy, one or more per trade.")
    parser.add_argument("--url", default="http://127.0.0.1:8069")
    parser.add_argument("--db", default="revert20_dev")
    parser.add_argument("--login", default="admin")
    parser.add_argument("--password", default="admin")
    parser.add_argument("--apply", action="store_true", help="write (without it: a dry run)")
    opts = parser.parse_args()

    server = Server(opts.url, opts.db)
    server.login(opts.login, opts.password)
    flag = server.call("ir.config_parameter", "search_read", [("key", "=", "database.is_neutralized")], fields=["value"])
    if not flag or str(flag[0]["value"]).lower() not in ("true", "1"):
        raise SystemExit("%s is not marked as a test copy (database.is_neutralized). Nothing was done." % opts.db)

    trades = {t["code"]: t for t in server.call("rvt.trade", "search_read", [], fields=["code", "name"])}
    firms = {f["name"].strip().lower(): f for f in server.call(
        "res.partner", "search_read", [("rvt_is_agency", "=", True)], fields=["name", "rvt_trade_ids"])}
    taken = {digits(p["phone"]): p for p in server.call(
        "res.partner", "search_read", [("phone", "like", "90000")], fields=["name", "phone", "parent_id"])}
    tag = None
    if opts.apply:
        found = server.call("res.partner.category", "search", [("name", "=", TAG)], limit=1)
        tag = found[0] if found else server.call("res.partner.category", "create", {"name": TAG})

    def tagged(vals):
        return dict(vals, category_id=[(4, tag)]) if tag else vals

    print("%-30s %-12s %-3s %-24s %-12s %s" % ("agency", "trades", "lng", "person", "mobile", ""))
    added = people_added = 0
    for name, codes, lang, agency_no, people in AGENCIES:
        missing = [c for c in codes if c not in trades]
        codes = [c for c in codes if c in trades]
        if not codes:
            print("%-30s not added: this database has no trade %s" % (name, ", ".join(missing)))
            continue
        rows = [(person, role, number(codes[0], agency_no, n)) for n, (person, role) in enumerate(people, 1)]
        firm = firms.get(name.lower())
        if not firm and server.call("res.partner", "search_count", [("name", "=ilike", name)]):
            print("%-30s not added: another contact already has this name" % name)
            continue
        firm_id, state = firm and firm["id"], "already there"
        if not firm:
            state = "new" if opts.apply else "would be added"
            added += 1
            if opts.apply:
                first = rows[0]
                firm_id = int(server.call("rvt.desk", "op", "add_agency", {
                    "name": name, "trades": codes, "lang": lang, "person": first[0], "phone": first[2]})["id"][1:])
                server.call("res.partner", "write", [firm_id], tagged({}))
                person_id = server.call("res.partner", "search", [("parent_id", "=", firm_id)], order="id", limit=1)
                server.call("res.partner", "write", person_id, tagged({"function": first[1]}))
                taken[digits(first[2])] = {"parent_id": [firm_id, name]}
                people_added += 1
        elif opts.apply:
            wanted = [trades[c]["id"] for c in codes if trades[c]["id"] not in firm["rvt_trade_ids"]]
            if wanted:
                server.call("res.partner", "write", [firm_id], {"rvt_trade_ids": [(4, t) for t in wanted]})
        for n, (person, role, phone) in enumerate(rows):
            holder = taken.get(digits(phone))
            note = state if n == 0 else ""
            if holder and (not firm_id or (holder.get("parent_id") or [None])[0] != firm_id):
                note = "number already on another contact: person not added"
            elif not holder:
                people_added += 1
                if opts.apply:
                    server.call("res.partner", "create", tagged({
                        "name": person, "phone": phone, "parent_id": firm_id, "lang": LANG[lang], "function": role}))
                    note = note or ("person added" if firm else "")
                elif firm:
                    note = "person would be added"
            print("%-30s %-12s %-3s %-24s %-12s %s" % (
                name if n == 0 else "", ",".join(codes) if n == 0 else "", lang if n == 0 else "", person, phone, note))

    print()
    after = server.call("res.partner", "search_read", [("rvt_is_agency", "=", True)], fields=["rvt_trade_ids"])
    by_trade = {code: sum(1 for f in after if t["id"] in f["rvt_trade_ids"]) for code, t in trades.items()}
    if not opts.apply:  # what the dry run would add
        for name, codes, _lang, _no, _people in AGENCIES:
            if name.lower() not in firms:
                for code in codes:
                    if code in by_trade:
                        by_trade[code] += 1
    for code in sorted(trades, key=lambda c: TRADES.index(c) if c in TRADES else 99):
        print("  %-28s %s" % (trades[code]["name"], by_trade[code] or "NO AGENCY"))
    verb = "added" if opts.apply else "to add (dry run: nothing written, run again with --apply)"
    print("\n%d agencies and %d people %s on %s." % (added, people_added, verb, opts.db))
    return 0


if __name__ == "__main__":
    sys.exit(main())
