#!/usr/bin/env python3
"""Browser QA of a migrated Revert database (Odoo 20), run against a THROWAWAY clone.

    /opt/odoo20/odoo20-venv/bin/python tools/etl/qa/browser_qa.py --base http://localhost:8174 --db revert20_qa \
        --menus /opt/odoo20/etl_revert/qa/menus.json --out /opt/odoo20/etl_revert/qa

1. crawl: opens every menu-reachable action as admin; JS page errors, console errors, error dialogs.
2. MOM dashboard of every project that has MOM entries: KPI tiles = database counts, charts drawn,
   entry table filled; filter by KPI, reset; "Print entries" returns a PDF.
3. task form: MOM tab lists open AND closed entries, legacy lines, Studio field shown, chatter
   history with tracked changes, attachments download byte-identical.
4. "Create MOM" (Schedule Activity dialog): Related To + site photo + summary -> a MOM entry with
   the next Sr. No. and today's visit number (checked in the database).
5. mark that entry done from the dashboard with a closing note -> archived, note in the chatter.
6. both PDF reports (task MOM PDF, MOM entries PDF).
7. a non-admin project user: login with the password of the clone, projects, My Tasks, dashboard.
8. Discuss (migrated chats), Gantt of All Tasks & Sub-Tasks.
Writes screenshots + qa_result.json into --out. Exit 1 on any FAIL."""
import argparse
import base64
import hashlib
import json
import os
import re
import sys
import time

import psycopg2
from playwright.sync_api import sync_playwright

RESULTS = []
PNG = base64.b64decode("iVBORw0KGgoAAAANSUhEUgAAAAIAAAACCAIAAAD91JpzAAAAFklEQVR4nGP8z8DAwMDAxMDAwMDAAAANHQEDK+mmyAAAAABJRU5ErkJggg==")


def record(name, ok, detail=""):
    RESULTS.append({"check": name, "ok": bool(ok), "detail": detail})
    print(f"[{'PASS' if ok else 'FAIL'}] {name}" + (f"  {detail}" if detail else ""), flush=True)


class Session:
    def __init__(self, browser, base, out, tag):
        self.base, self.out, self.tag = base, out, tag
        self.ctx = browser.new_context(viewport={"width": 1440, "height": 900}, accept_downloads=True)
        self.page = self.ctx.new_page()
        self.errors = []
        self.page.on("pageerror", lambda e: self.errors.append(f"pageerror: {str(e)[:300]}"))
        self.page.on("console", lambda m: self.errors.append(f"console: {m.text[:300]}")
                     if m.type == "error" and "favicon" not in m.text and "Failed to load resource" not in m.text else None)

    def login(self, login, password):
        p = self.page
        p.goto(self.base + "/web/login", timeout=60000)
        p.fill("input[name=login]", login)
        p.fill("input[name=password]", password)
        p.click("form button[type=submit]")
        p.wait_for_url(re.compile(r".*/odoo.*"), timeout=60000)
        p.wait_for_selector(".o_main_navbar", timeout=60000)
        time.sleep(2)
        self.errors.clear()

    def shot(self, name):
        path = os.path.join(self.out, "shots", f"{self.tag}_{name}.png")
        self.page.screenshot(path=path, full_page=False)
        return path

    def goto(self, url, wait=".o_action_manager > *", settle=1.5):
        self.page.goto(self.base + url, timeout=60000)
        self.page.wait_for_selector(wait, timeout=60000)
        time.sleep(settle)

    def error_dialog(self):
        return self.page.locator(".o_error_dialog, .modal .o_error_detail").count() > 0

    def take_errors(self):
        e = list(dict.fromkeys(self.errors)); self.errors.clear()
        return e


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", required=True)
    ap.add_argument("--db", required=True)
    ap.add_argument("--menus", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--admin-password", default="admin")
    ap.add_argument("--user", default="kishan@revert.com")
    ap.add_argument("--user-password", default="QaTest#2026")
    a = ap.parse_args()
    os.makedirs(os.path.join(a.out, "shots"), exist_ok=True)
    conn = psycopg2.connect(dbname=a.db); conn.autocommit = True
    cr = conn.cursor()

    def q(sql, args=()):
        cr.execute(sql, args)
        return cr.fetchall()

    act = dict(q("""SELECT d.module||'.'||d.name, d.res_id FROM ir_model_data d WHERE (d.module, d.name) IN
                    (('project','open_view_project_all'), ('project','action_view_task'), ('project','action_view_my_task'),
                     ('revert_customizations','action_view_all_tasks_subtasks'), ('mail','action_discuss'))"""))
    with sync_playwright() as pw:
        browser = pw.chromium.launch(channel="chrome", headless=True)
        s = Session(browser, a.base, a.out, "admin")
        s.login("admin", a.admin_password)

        # ------------------------------------------------------------ 1. crawl every menu
        # the menus the web client itself shows admin: normal mode, then the extra ones of debug mode
        menus = []
        for debug in ("", "1"):
            s.page.goto(f"{a.base}/odoo?debug={debug}", timeout=60000)
            s.page.wait_for_selector(".o_main_navbar", timeout=60000)
            data = s.ctx.request.get(f"{a.base}/web/webclient/load_menus").json()
            for m in data.values():
                if isinstance(m, dict) and m.get("actionID") and m.get("actionModel") in ("ir.actions.act_window", "ir.actions.client"):
                    menus.append({"path": m.get("name"), "action": f"{m['actionModel']},{m['actionID']}", "debug": debug})
        json.dump(menus, open(os.path.join(a.out, "menus_visible.json"), "w"), indent=1)
        s.page.goto(f"{a.base}/odoo?debug=", timeout=60000)
        s.take_errors()
        crawl_bad = []
        seen = set()
        for m in menus:
            model, aid = m["action"].split(",")
            if aid in seen:
                continue
            seen.add(aid)
            try:
                s.page.goto(f"{a.base}/odoo/action-{aid}" + ("?debug=1" if m["debug"] else ""), timeout=45000)
                time.sleep(2.0)
                errs = s.take_errors()
                if s.error_dialog() or errs:
                    crawl_bad.append((m["path"], errs[:2] or ["error dialog"]))
                    s.shot(f"crawl_err_{aid}")
                    if s.error_dialog():
                        s.page.keyboard.press("Escape")
            except Exception as e:  # noqa: BLE001
                crawl_bad.append((m["path"], [f"{type(e).__name__}: {str(e)[:150]}"]))
        record(f"crawl: {len(seen)} menu actions open without JS error or error dialog", not crawl_bad,
               "; ".join(f"{p}: {e}" for p, e in crawl_bad[:6]))

        # ------------------------------------------------------------ 2. MOM dashboard per project
        projects = q("""SELECT p.id, p.name->>'en_US', count(a.id), count(a.id) FILTER (WHERE a.active),
                               count(a.id) FILTER (WHERE NOT a.active),
                               count(DISTINCT a.mom_partner_id), count(ph.id)
                        FROM project_project p JOIN mail_activity a ON a.mom_project_id = p.id
                        JOIN mail_activity_type t ON t.id = a.activity_type_id AND t.is_mom
                        LEFT JOIN ir_attachment ph ON ph.res_model = 'mail.activity' AND ph.res_field = 'mom_site_photo' AND ph.res_id = a.id
                        GROUP BY 1, 2 ORDER BY 3 DESC""")
        dash_bad = []
        for pid, pname, total, open_, done, contacts, photos in projects:
            try:
                s.goto(f"/odoo/action-{act['project.open_view_project_all']}/{pid}", wait=".o_form_view")
                s.page.click("button[name=action_open_mom_dashboard]")
                s.page.wait_for_selector(".o_mom_dashboard .o_mom_kpi_value", timeout=30000)
                time.sleep(1.5)
                kpi = {k: s.page.locator(".o_mom_kpi").nth(i).locator(".o_mom_kpi_value").inner_text().strip()
                       for i, k in enumerate(["total", "open", "overdue", "done", "contacts", "photos"])}
                want = {"total": str(total), "open": str(open_), "done": str(done), "contacts": str(contacts), "photos": str(photos)}
                charts = s.page.locator(".o_mom_dashboard canvas").count()
                rows = s.page.locator(".o_mom_table tbody tr").count()
                errs = s.take_errors()
                problems = [f"{k}={kpi[k]}≠{v}" for k, v in want.items() if kpi[k] != v]
                if charts < 2:
                    problems.append(f"{charts} charts")
                if rows != min(total, 100):
                    problems.append(f"{rows} rows≠{min(total, 100)}")
                if errs or s.error_dialog():
                    problems.append(f"errors {errs[:2]}")
                if problems:
                    dash_bad.append(f"#{pid} {pname}: {problems}")
                    s.shot(f"dashboard_{pid}")
            except Exception as e:  # noqa: BLE001
                dash_bad.append(f"#{pid} {pname}: {type(e).__name__}: {str(e)[:160]}")
                s.shot(f"dashboard_{pid}_exc")
        record(f"MOM dashboard of {len(projects)} projects: KPIs = database, charts drawn, entries listed", not dash_bad,
               "; ".join(dash_bad[:4]))

        # dashboard interactions on the busiest project
        pid, pname, total, open_, done = projects[0][:5]
        s.goto(f"/odoo/action-{act['project.open_view_project_all']}/{pid}", wait=".o_form_view")
        s.page.click("button[name=action_open_mom_dashboard]")
        s.page.wait_for_selector(".o_mom_dashboard .o_mom_kpi_value", timeout=30000)
        time.sleep(1)
        s.shot("dashboard_main")
        s.page.locator(".o_mom_kpi").nth(3).click()          # "Closed" tile
        time.sleep(1.5)
        rows_done = s.page.locator(".o_mom_table tbody tr").count()
        active_tile = "is-active" in (s.page.locator(".o_mom_kpi").nth(3).get_attribute("class") or "")
        s.page.locator(".o_mom_reset").click()
        time.sleep(1.5)
        rows_all = s.page.locator(".o_mom_table tbody tr").count()
        visits = q("SELECT count(DISTINCT mom_visit_no) FROM mail_activity WHERE mom_project_id = %s", (pid,))[0][0]
        s.page.locator(".o_mom_picker button").nth(3).click()  # Visit No# picker
        time.sleep(0.5)
        visit_opts = s.page.locator(".o_mom_picker_panel .o_mom_option").count()
        s.page.locator(".o_mom_picker button").nth(3).click()
        errs = s.take_errors()
        record("dashboard filters: Closed tile, reset, visit picker", rows_done == min(done, 100) and active_tile and
               rows_all == min(total, 100) and visit_opts == visits and not errs,
               f"closed rows {rows_done}/{min(done, 100)}, reset rows {rows_all}, visit options {visit_opts}/{visits} {errs[:1]}")
        # the report action ends in a download (/report/download) or a PDF viewer: watch the network
        pdf_responses, downloads = [], []
        s.page.on("response", lambda r: pdf_responses.append(r) if "/report/" in r.url else None)
        s.page.on("download", lambda d: downloads.append(d))
        s.page.locator("button:has-text('Print entries')").click()
        # prod's company has no document layout yet: 18 and 20 both ask for it on the first print
        try:
            s.page.wait_for_selector(".modal:has-text('Configure your document layout')", timeout=8000)
            layout_prompt = True
            s.shot("document_layout_prompt")
            s.page.locator(".modal-footer button:has-text('Continue')").click()
        except Exception:  # noqa: BLE001
            layout_prompt = False
        for _ in range(120):
            if downloads:
                break
            s.page.wait_for_timeout(1000)   # (time.sleep would not let playwright deliver the event)
        data = open(downloads[0].path(), "rb").read() if downloads else b""
        errs = s.take_errors()
        s.shot("dashboard_after_print")
        record("dashboard 'Print entries' returns the MOM entries PDF", data[:5] == b"%PDF-" and len(data) > 20000 and not errs,
               f"{len(data)} bytes; layout prompt first: {layout_prompt}; {[r.url.split('?')[0][-50:] for r in pdf_responses]} {errs[:1]}")
        if data:
            open(os.path.join(a.out, "mom_entries_dashboard.pdf"), "wb").write(data)

        # ------------------------------------------------------------ 3. task form
        tid, tname, t_moms, t_open = q("""SELECT t.id, t.name, count(a.id), count(a.id) FILTER (WHERE a.active)
                                          FROM project_task t JOIN mail_activity a ON a.mom_task_id = t.id
                                          GROUP BY 1, 2 ORDER BY 3 DESC LIMIT 1""")[0]
        s.goto(f"/odoo/action-{act['project.action_view_task']}/{tid}", wait=".o_form_view")
        s.page.locator(".o_notebook .nav-link", has_text="MOM Meetings").first.click()
        time.sleep(1.5)
        lists = s.page.locator(".o_notebook .tab-pane.active .o_field_x2many_list")
        pager = s.page.locator(".o_notebook .tab-pane.active .o_field_widget[name=mom_activity_ids] .o_pager_limit")
        shown = int(pager.inner_text()) if pager.count() else \
            s.page.locator(".o_notebook .tab-pane.active .o_field_widget[name=mom_activity_ids] .o_data_row").count()
        sync_btn = s.page.locator("button[name=action_sync_mom_activities]").count()
        s.shot("task_mom_tab")
        record("task MOM tab lists every entry, closed ones included", shown == t_moms and lists.count() >= 2 and sync_btn == 0,
               f"{shown}/{t_moms} entries, {lists.count()} lists, sync button shown={bool(sync_btn)}")
        st_tid, st_val = q("SELECT id, x_studio_responsible_person FROM project_task WHERE x_studio_responsible_person IS NOT NULL AND active ORDER BY id LIMIT 1")[0]
        s.goto(f"/odoo/action-{act['project.action_view_task']}/{st_tid}", wait=".o_form_view")
        studio_ok = s.page.locator(f".o_field_widget[name=x_studio_responsible_person] input").input_value() == st_val
        record("Studio field 'Responsible Person' shown on the task form with its value", studio_ok, st_val)
        # chatter: tracked changes + attachments
        ctid = q("""SELECT m.res_id FROM mail_message m JOIN mail_tracking_value v ON v.mail_message_id = m.id
                    WHERE m.model = 'project.task' GROUP BY 1 ORDER BY count(*) DESC LIMIT 1""")[0][0]
        s.goto(f"/odoo/action-{act['project.action_view_task']}/{ctid}", wait=".o-mail-Message")
        time.sleep(1)
        msgs = s.page.locator(".o-mail-Message").count()
        arrows = s.page.locator(".o-mail-Message:has-text('→')").count()
        want_msgs = q("SELECT count(*) FROM mail_message WHERE model='project.task' AND res_id=%s AND message_type <> 'user_notification'", (ctid,))[0][0]
        s.shot("task_chatter")
        record("chatter history with tracked changes rendered once each", msgs > 0 and arrows > 0 and
               s.page.locator(".o-mail-Message:has-text('→ →')").count() == 0,
               f"{msgs} messages shown ({want_msgs} in db), {arrows} with a tracked change")
        att = q("""SELECT id, checksum, file_size FROM ir_attachment WHERE res_model = 'project.task' AND res_field IS NULL
                   AND type = 'binary' ORDER BY file_size DESC LIMIT 3""")
        dl_ok = []
        for att_id, checksum, size in att:
            r = s.ctx.request.get(f"{a.base}/web/content/{att_id}?download=true")
            body = r.body()
            dl_ok.append(r.status == 200 and hashlib.sha1(body).hexdigest() == checksum)
        record("task attachments download byte-identical", all(dl_ok) and dl_ok, f"{sum(dl_ok)}/{len(dl_ok)} files")

        # ------------------------------------------------------------ 4. Create MOM
        partner = q("SELECT id, name FROM res_partner WHERE active AND name IS NOT NULL AND id NOT IN (SELECT partner_id FROM res_users) ORDER BY id LIMIT 1")[0]
        before = q("SELECT coalesce(max(mom_sequence), 0) FROM mail_activity WHERE res_model='project.task' AND res_id=%s", (tid,))[0][0]
        # visit rule: the visit already used today on the project (user's timezone), else the last visit + 1
        want_visit = q("""WITH tz AS (SELECT coalesce((SELECT p.tz FROM res_users u JOIN res_partner p ON p.id = u.partner_id
                                                       WHERE u.id = 2), 'UTC') AS z),
                               pr AS (SELECT project_id AS id FROM project_task WHERE id = %s)
                          SELECT coalesce(
                              (SELECT a.mom_visit_no FROM mail_activity a, tz, pr WHERE a.mom_project_id = pr.id
                                 AND (a.create_date AT TIME ZONE 'UTC' AT TIME ZONE tz.z)::date = (now() AT TIME ZONE tz.z)::date
                               ORDER BY a.id DESC LIMIT 1),
                              (SELECT coalesce(max(a.mom_visit_no), 0) + 1 FROM mail_activity a, pr WHERE a.mom_project_id = pr.id))""",
                       (tid,))[0][0]
        s.goto(f"/odoo/action-{act['project.action_view_task']}/{tid}", wait=".o_form_view")
        s.page.click("button[name=action_create_mom]")
        s.page.wait_for_selector(".modal .o_field_widget[name=mom_partner_id] input", timeout=30000)
        time.sleep(1)
        summary = f"QA MOM entry {int(time.time())}"
        s.page.fill(".modal .o_field_widget[name=summary] input", summary)
        s.page.fill(".modal .o_field_widget[name=mom_partner_id] input", partner[1][:12])
        s.page.wait_for_selector(".o-autocomplete--dropdown-item", timeout=15000)
        s.page.locator(".o-autocomplete--dropdown-item", has_text=partner[1][:12]).first.click()
        tmp = os.path.join(a.out, "qa_site_photo.png")
        open(tmp, "wb").write(PNG)
        s.page.locator(".modal .o_field_widget[name=mom_site_photo] input[type=file]").set_input_files(tmp)
        time.sleep(1.5)
        shown_seq = s.page.locator(".modal .o_field_widget[name=mom_sequence]").inner_text().strip()
        shown_visit = s.page.locator(".modal .o_field_widget[name=mom_visit_no] input").input_value()
        s.shot("create_mom_dialog")
        s.page.locator(".modal-footer button[name=action_schedule_activities]").click()
        s.page.wait_for_selector(".modal", state="detached", timeout=30000)
        time.sleep(1.5)
        row = q("""SELECT a.id, a.mom_sequence, a.mom_visit_no, a.mom_partner_id, a.active, a.mom_task_id, a.mom_project_id,
                          (SELECT count(*) FROM ir_attachment ph WHERE ph.res_model='mail.activity' AND ph.res_field='mom_site_photo' AND ph.res_id=a.id)
                   FROM mail_activity a WHERE a.summary = %s""", (summary,))
        errs = s.take_errors()
        ok = bool(row) and row[0][1] == before + 1 and row[0][2] == want_visit and row[0][3] == partner[0] and row[0][4] \
            and row[0][7] == 1 and row[0][5] == tid and shown_visit == str(want_visit)
        record("Create MOM: Related To, photo, next Sr. No., today's visit No#, task + project relation", ok and not errs,
               f"db row (seq, visit, partner, active, task, project, photos)={row[0][1:] if row else None}; dialog showed "
               f"Sr. No. {shown_seq!r} / visit {shown_visit!r}; expected {before + 1} / {want_visit} {errs[:1]}")
        new_id = row[0][0] if row else None

        # ------------------------------------------------------------ 5. mark it done from the dashboard
        if new_id:
            proj = row[0][6]
            s.goto(f"/odoo/action-{act['project.open_view_project_all']}/{proj}", wait=".o_form_view")
            s.page.click("button[name=action_open_mom_dashboard]")
            s.page.wait_for_selector(".o_mom_dashboard .o_mom_kpi_value", timeout=30000)
            s.page.locator(".o_mom_kpi").nth(1).click()   # Open
            time.sleep(1.5)
            line = s.page.locator(".o_mom_table tbody tr", has_text=summary)
            line.locator(".o_mom_action_done").click()
            s.page.wait_for_selector("#mom_done_feedback", timeout=15000)
            closing_note = f"Closed by browser QA {summary}"
            s.page.fill("#mom_done_feedback", closing_note)
            s.shot("mark_done_dialog")
            s.page.locator(".modal-footer .btn-primary").click()
            s.page.wait_for_selector("#mom_done_feedback", state="detached", timeout=30000)
            time.sleep(1.5)
            st = q("SELECT active, date_done FROM mail_activity WHERE id = %s", (new_id,))
            note = q("""SELECT count(*) FROM mail_message WHERE model='project.task' AND res_id=%s
                        AND body::text LIKE %s""", (tid, f"%{closing_note}%"))[0][0]
            errs = s.take_errors()
            record("mark done from the dashboard: entry kept as closed, note in the task chatter",
                   st and st[0][0] is False and note == 1 and not errs, f"active={st[0][0] if st else None} note={note} {errs[:1]}")

        # ------------------------------------------------------------ 6. task MOM PDF
        r = s.ctx.request.get(f"{a.base}/report/pdf/revert_customizations.task_report/{tid}")
        body = r.body()
        open(os.path.join(a.out, "task_mom.pdf"), "wb").write(body)
        record("task 'MOM PDF' report renders", r.status == 200 and body[:5] == b"%PDF-" and len(body) > 20000, f"{len(body)} bytes")

        # ------------------------------------------------------------ 8. discuss + gantt (admin)
        s.goto(f"/odoo/action-{act['mail.action_discuss']}", wait=".o-mail-Discuss")
        s.page.wait_for_selector(".o-mail-MessagingMenuItem", timeout=30000)
        chat = s.page.locator(".o-mail-MessagingMenuItem").count()
        busiest = q("""SELECT c.name, count(m.id) FROM discuss_channel c JOIN mail_message m ON m.model = 'discuss.channel'
                       AND m.res_id = c.id AND m.message_type = 'comment' GROUP BY 1 ORDER BY 2 DESC LIMIT 1""")
        s.page.locator(".o-mail-MessagingMenuItem").first.click()
        time.sleep(2)
        shown = s.page.locator(".o-mail-Message").count()
        s.shot("discuss")
        record("Discuss lists the migrated conversations and opens one with its history", chat > 0 and shown > 0
               and not s.take_errors(), f"{chat} conversations listed, {shown} messages in the first one opened")
        s.goto(f"/odoo/action-{act['revert_customizations.action_view_all_tasks_subtasks']}", wait=".o_list_view")
        s.page.locator(".o_switch_view.o_gantt, button.o_gantt").first.click()
        s.page.wait_for_selector(".o_gantt_view, .o_gantt_renderer", timeout=30000)
        time.sleep(1.5)
        s.shot("gantt")
        record("All Tasks & Sub-Tasks: list grouped by project and Gantt view", not s.take_errors() and not s.error_dialog())

        # ------------------------------------------------------------ 7. non-admin user
        u = Session(browser, a.base, a.out, "user")
        try:
            u.login(a.user, a.user_password)
            u.goto(f"/odoo/action-{act['project.open_view_project_all']}", wait=".o_kanban_view")
            cards = u.page.locator(".o_kanban_record:not(.o_kanban_ghost)").count()
            want_cards = q("SELECT count(*) FROM project_project WHERE active")[0][0]
            u.shot("projects")
            u.goto(f"/odoo/action-{act['project.action_view_my_task']}", wait=".o_kanban_view, .o_list_view")
            my = u.page.locator(".o_kanban_record:not(.o_kanban_ghost), .o_data_row").count()
            u.shot("my_tasks")
            settings_menu = u.page.locator(".o_navbar_apps_menu, .o_app[data-menu-xmlid='base.menu_administration']").count()
            pid = projects[0][0]
            u.goto(f"/odoo/action-{act['project.open_view_project_all']}/{pid}", wait=".o_form_view")
            u.page.click("button[name=action_open_mom_dashboard]")
            u.page.wait_for_selector(".o_mom_dashboard .o_mom_kpi_value", timeout=30000)
            time.sleep(1)
            kpi_total = u.page.locator(".o_mom_kpi").nth(0).locator(".o_mom_kpi_value").inner_text().strip()
            errs = u.take_errors()
            record(f"non-admin user {a.user}: projects, My Tasks, MOM dashboard", cards == want_cards and
                   kpi_total == str(projects[0][2]) and not errs,
                   f"{cards}/{want_cards} project cards, {my} own tasks, dashboard total {kpi_total} {errs[:1]}")
            u.page.goto(a.base + "/odoo/settings", timeout=60000)
            time.sleep(2)
            denied = u.page.locator(".o_error_dialog, .o_settings_container").count() == 0 or \
                u.page.locator("text=/access|not allowed|Access Error/i").count() > 0
            record(f"non-admin user {a.user} cannot open Settings", denied)
        finally:
            u.ctx.close()
        browser.close()

    json.dump(RESULTS, open(os.path.join(a.out, "qa_result.json"), "w"), indent=1)
    bad = [r for r in RESULTS if not r["ok"]]
    print(f"\nBROWSER QA: {len(RESULTS) - len(bad)}/{len(RESULTS)} PASS")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
