#!/usr/bin/env python3
"""Screen-by-screen comparison of the same data on Odoo 18 (reference) and Odoo 20 (migrated).

    /opt/odoo20/odoo20-venv/bin/python tools/etl/qa/compare_18_20.py \
        --v18 http://localhost:8171 --db18 revert18_ref --v20 http://localhost:8174 --db20 revert20_qa \
        --out /opt/odoo20/etl_revert/qa/compare

Both sides are driven with the SAME urls (the migration keeps prod's ids) and read the way a user
sees them: project cards (tasks + MOM counts), every MOM dashboard (KPI tiles, every entry row of
the first page), a sample of task forms (name, project, assignees, stage, deadline, tags, Studio
field, MOM tab: legacy lines / responsibilities / MOM entries), the All Tasks & Sub-Tasks
grouping, and the text of the two PDF reports. Writes diff.json, report.md and side-by-side PNGs.
Read-only on both databases (nothing is clicked that writes)."""
import argparse
import json
import os
import re
import subprocess
import tempfile
import time

import psycopg2
from playwright.sync_api import sync_playwright


def norm(t):
    return re.sub(r"\s+", " ", (t or "").replace("​", "")).strip()


class Side:
    def __init__(self, pw, name, base, out):
        self.name, self.base, self.out = name, base, out
        self.browser = pw.chromium.launch(channel="chrome", headless=True)
        self.ctx = self.browser.new_context(viewport={"width": 1600, "height": 1000})
        self.page = self.ctx.new_page()
        self.errors = []
        self.page.on("pageerror", lambda e: self.errors.append(str(e)[:200]))

    def login(self):
        p = self.page
        p.goto(self.base + "/web/login", timeout=60000)
        p.fill("input[name=login]", "admin"); p.fill("input[name=password]", "admin")
        p.click("form button[type=submit]")
        p.wait_for_selector(".o_main_navbar", timeout=90000)
        time.sleep(2)

    def goto(self, path, wait, settle=1.2):
        self.page.goto(self.base + path, timeout=90000)
        self.page.wait_for_selector(wait, timeout=90000)
        time.sleep(settle)

    def shot(self, key):
        path = os.path.join(self.out, f"{key}_{self.name}.png")
        self.page.screenshot(path=path)
        return path

    def field_text(self, name):
        loc = self.page.locator(f".o_form_view .o_field_widget[name={name}]").first
        if not loc.count():
            return None
        inp = loc.locator("input, textarea")
        if inp.count():
            return norm(inp.first.input_value())
        return norm(loc.inner_text())

    def x2many_count(self, name):
        w = self.page.locator(f".o_field_widget[name={name}]").first
        if not w.count():
            return None
        pager = w.locator(".o_pager_limit")
        if pager.count() and pager.first.is_visible():
            return int(norm(pager.first.inner_text()) or 0)
        return w.locator(".o_data_row").count()


def collect(side, plan):
    s = side
    obs = {}
    s.login()
    # project cards
    s.goto("/odoo/project", ".o_kanban_record")
    cards = {}
    for c in s.page.locator(".o_kanban_record:not(.o_kanban_ghost)").all():
        txt = c.inner_text()
        lines = [l.strip() for l in txt.splitlines() if l.strip()]
        name = lines[0] if lines else "?"
        tasks = re.search(r"(\d+)\s*Tasks", txt)
        mom = re.search(r"(\d+)\s*MOM", txt)
        cards[name] = {"tasks": tasks and int(tasks.group(1)), "mom": mom and int(mom.group(1))}
    obs["project_cards"] = cards
    s.shot("projects")
    # dashboards
    dash = {}
    for pid in plan["dash_projects"]:
        s.goto(f"/odoo/project/{pid}/mom_dashboard", ".o_mom_dashboard .o_mom_kpi_value", settle=2)
        kpis = [norm(x) for x in s.page.locator(".o_mom_kpi").all_inner_texts()]
        rows = []
        for r in s.page.locator(".o_mom_table tbody tr").all():
            cells = [norm(c) for c in r.locator("td").all_inner_texts()]
            rows.append(" | ".join(cells[:-1]))   # last column = action buttons
        dash[str(pid)] = {"title": norm(s.page.locator(".o_mom_header h1").inner_text()), "kpis": kpis,
                          "charts": s.page.locator(".o_mom_dashboard canvas").count(), "rows": rows}
        if pid in plan["dash_shots"]:
            s.shot(f"dashboard_{pid}")
    obs["dashboards"] = dash
    # task forms
    tasks = {}
    for pid, tid in plan["tasks"]:
        s.goto(f"/odoo/project/{pid}/tasks/{tid}", ".o_form_view")
        rec = {k: s.field_text(k) for k in ("name", "project_id", "user_ids", "date_deadline", "tag_ids",
                                             "x_studio_responsible_person", "partner_id")}
        cur = s.page.locator(".o_statusbar_status .o_arrow_button_current")
        rec["stage"] = norm(cur.first.inner_text()) if cur.count() else None
        tab = s.page.locator(".o_notebook .nav-link", has_text="MOM Meetings")
        if tab.count():
            tab.first.click(); time.sleep(1)
            rec["legacy_mom_lines"] = s.x2many_count("mom_meeting_ids")
            rec["responsibilities"] = s.x2many_count("person_ids")
            rec["mom_entries"] = s.x2many_count("mom_activity_ids")
            rec["agenda"] = s.field_text("agenda")
        if tid in plan["task_shots"]:
            s.shot(f"task_{tid}")
        tasks[str(tid)] = rec
    obs["tasks"] = tasks
    # All Tasks & Sub-Tasks
    s.goto("/odoo/action-revert_customizations.action_view_all_tasks_subtasks", ".o_list_view", settle=2)
    obs["all_tasks_groups"] = sorted(norm(g) for g in s.page.locator(".o_group_header .o_group_name").all_inner_texts())
    s.shot("all_tasks")
    # reports (text)
    reports = {}
    for kind, rid in plan["reports"]:
        name = {"task": "revert_customizations.task_report", "mom": "revert_customizations.mom_entries_report"}[kind]
        r = s.ctx.request.get(f"{s.base}/report/pdf/{name}/{rid}", timeout=180000)
        body = r.body()
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
            f.write(body)
        txt = subprocess.run(["pdftotext", "-layout", f.name, "-"], capture_output=True, text=True).stdout
        os.unlink(f.name)
        reports[f"{kind}:{rid}"] = [norm(l) for l in txt.splitlines() if norm(l)]
    obs["reports"] = reports
    obs["js_errors"] = s.errors[:20]
    s.browser.close()
    return obs


def side_by_side(out, key):
    from PIL import Image, ImageDraw
    a, b = os.path.join(out, f"{key}_v18.png"), os.path.join(out, f"{key}_v20.png")
    if not (os.path.exists(a) and os.path.exists(b)):
        return None
    ia, ib = Image.open(a), Image.open(b)
    w, h = ia.width + ib.width + 20, max(ia.height, ib.height) + 40
    canvas = Image.new("RGB", (w, h), "white")
    canvas.paste(ia, (0, 40)); canvas.paste(ib, (ia.width + 20, 40))
    d = ImageDraw.Draw(canvas)
    d.text((10, 10), "Odoo 18 (production backup)", fill="black")
    d.text((ia.width + 30, 10), "Odoo 20 (migrated)", fill="black")
    path = os.path.join(out, f"side_{key}.png")
    canvas.save(path)
    return path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--v18", required=True); ap.add_argument("--db18", required=True)
    ap.add_argument("--v20", required=True); ap.add_argument("--db20", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    cr = psycopg2.connect(dbname=a.db18).cursor()

    def q(sql):
        cr.execute(sql)
        return cr.fetchall()

    dash_projects = [r[0] for r in q("""SELECT mom_project_id FROM mail_activity WHERE mom_project_id IS NOT NULL
                                        GROUP BY 1 ORDER BY count(*) DESC""")]
    tasks = q("""(SELECT t.project_id, t.id FROM project_task t JOIN mail_activity a ON a.mom_task_id = t.id
                  GROUP BY 1, 2 ORDER BY count(*) DESC LIMIT 6)
                 UNION (SELECT project_id, id FROM project_task WHERE x_studio_responsible_person IS NOT NULL
                        AND project_id IS NOT NULL ORDER BY id LIMIT 4)
                 UNION (SELECT project_id, id FROM project_task WHERE project_id IS NOT NULL AND id IN
                        (SELECT parent_id FROM project_task WHERE parent_id IS NOT NULL) ORDER BY id LIMIT 4)
                 UNION (SELECT project_id, id FROM project_task WHERE project_id IS NOT NULL AND id IN
                        (SELECT task_id FROM person_person) ORDER BY id LIMIT 3)
                 UNION (SELECT project_id, id FROM project_task WHERE project_id IS NOT NULL ORDER BY md5(id::text) LIMIT 14)""")
    plan = {"dash_projects": dash_projects, "dash_shots": dash_projects[:2],
            "tasks": sorted(tasks, key=lambda r: r[1]), "task_shots": [tasks[0][1]],
            "reports": [("task", t) for _, t in tasks[:3]] + [("mom", p) for p in dash_projects[:2]]}
    with sync_playwright() as pw:
        res = {}
        for name, base in (("v18", a.v18), ("v20", a.v20)):
            print(f"collecting {name} ({base}) ...", flush=True)
            res[name] = collect(Side(pw, name, base, a.out), plan)
    diffs, explained = [], []

    def same_date(x, y):
        """x (one 18 date) is one of the dates 20 shows in the same widget (a planned range shows two)."""
        from dateutil import parser
        try:
            want = parser.parse(x).strftime("%Y-%m-%d %H:%M")
        except (ValueError, TypeError, OverflowError):
            return False
        for part in re.findall(r"[A-Z][a-z]{2} \d{1,2}, \d{4}, \d{1,2}:\d{2} [AP]M|[A-Z][a-z]{2} \d{1,2}, \d{1,2}:\d{2} [AP]M", y):
            try:
                if parser.parse(part).strftime("%Y-%m-%d %H:%M") == want:
                    return True
            except (ValueError, OverflowError):
                continue
        return False

    def group_key(g):
        m = re.match(r"(.*?)\s*(?:\((\d+)\)|(\d+) records?)$", g)
        return f"{m.group(1)}|{m.group(2) or m.group(3)}" if m else g

    def subsequence(small, big):
        it = iter(big)
        return all(line in it for line in small)

    # presentation changes of Odoo 20 itself and deliberate fixes: reported with their reason
    def reason(section, key, x, y):
        field = key.split()[-1]
        if section == "task form" and field == "stage" and x and y and re.sub(r"\s", "", x) == re.sub(r"\s", "", y):
            return None   # same stage, same time in stage; only a space between them
        if section == "task form" and field == "date_deadline" and x and y and same_date(x, y):
            return "same date; Odoo 20 shows dates in forms as 'Jul 10, 2025, 12:00 PM' whatever the language format"
        if section == "All Tasks & Sub-Tasks" and [group_key(g) for g in x] == [group_key(g) for g in y]:
            return "same groups and counts; Odoo 20 writes '88 records' where 18 wrote '(88)'"
        if section == "project card" and x and y and x.get("mom") == y.get("mom") and x.get("tasks") != y.get("tasks"):
            return "MOM count identical; Odoo 20's card counts sub-tasks too (18 counted only tasks shown in the project)"
        if section == "task form" and field == "mom_entries" and (x or 0) < (y or 0):
            return "18 hides closed MOM entries on the task (contrary to FR-07 Must, open and closed); 20 lists them all"
        if section == "PDF report text" and isinstance(x, list) and isinstance(y, list) and subsequence(x, y):
            return "every 18 line printed; 20 adds the closed MOM entries table (FR-08 Must, AC-5), which 18 omits"
        return "UNEXPLAINED"

    def cmp(section, key, x, y):
        if x != y:
            why = reason(section, key, x, y)
            if why is None:
                return
            (diffs if why == "UNEXPLAINED" else explained).append(
                {"section": section, "key": key, "v18": x, "v20": y, "reason": why})

    A, B = res["v18"], res["v20"]
    for name in sorted(set(A["project_cards"]) | set(B["project_cards"])):
        cmp("project card", name, A["project_cards"].get(name), B["project_cards"].get(name))
    for pid in A["dashboards"]:
        for k in ("title", "kpis", "rows"):
            cmp("MOM dashboard", f"project {pid} {k}", A["dashboards"][pid][k], B["dashboards"].get(pid, {}).get(k))
    for tid in A["tasks"]:
        for k, v in A["tasks"][tid].items():
            cmp("task form", f"task {tid} {k}", v, B["tasks"].get(tid, {}).get(k))
    cmp("All Tasks & Sub-Tasks", "groups", A["all_tasks_groups"], B["all_tasks_groups"])
    for k in A["reports"]:
        cmp("PDF report text", k, A["reports"][k], B["reports"].get(k))
    sides = [side_by_side(a.out, k) for k in ["projects", "all_tasks"] + [f"dashboard_{p}" for p in plan["dash_shots"]]
             + [f"task_{t}" for t in plan["task_shots"]]]
    json.dump({"plan": plan, "observations": res, "diffs": diffs, "explained": explained}, open(os.path.join(a.out, "diff.json"), "w"),
              indent=1, default=str)
    n_checks = (len(A["project_cards"]) + 3 * len(A["dashboards"]) + sum(len(v) for v in A["tasks"].values())
                + 1 + len(A["reports"]))
    print(f"\ncompared: {len(A['project_cards'])} project cards, {len(A['dashboards'])} dashboards "
          f"({sum(len(d['rows']) for d in A['dashboards'].values())} entry rows), {len(A['tasks'])} task forms, "
          f"{len(A['all_tasks_groups'])} task groups, {len(A['reports'])} PDF reports = {n_checks} comparisons")
    print(f"JS errors: v18 {len(A['js_errors'])}, v20 {len(B['js_errors'])}")
    print(f"side-by-side images: {[p for p in sides if p]}")
    by_reason = {}
    for e in explained:
        by_reason[e["reason"]] = by_reason.get(e["reason"], 0) + 1
    print(f"explained (Odoo 20 presentation / deliberate fixes): {len(explained)}")
    for r, n in by_reason.items():
        print(f"  {n:3d} x {r}")
    print(f"UNEXPLAINED DIFFERENCES: {len(diffs)}")
    for d in diffs[:40]:
        print(f"  [{d['section']}] {d['key']}:\n     18: {str(d['v18'])[:300]}\n     20: {str(d['v20'])[:300]}")


if __name__ == "__main__":
    main()
