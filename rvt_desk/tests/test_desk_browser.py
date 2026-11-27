from odoo.tests import HttpCase, new_test_user, tagged

TOUR = """
(async () => {
    const sleep = ms => new Promise(r => setTimeout(r, ms));
    const q = s => document.querySelector(s);
    const act = (a, v) => {
        const el = [...document.querySelectorAll('[data-a="' + a + '"]')].find(e => v == null || e.dataset.v === String(v));
        if (!el) throw new Error('no element for ' + a + ' ' + (v == null ? '' : v));
        el.dispatchEvent(new MouseEvent('click', {bubbles: true}));
    };
    const type = (id, value) => {
        const el = document.getElementById(id);
        if (!el) throw new Error('no input ' + id);
        el.value = value;
        el.dispatchEvent(new Event('input', {bubbles: true}));
    };
    const until = async (test, what) => {
        for (let i = 0; i < 150; i++) { if (test()) return; await sleep(100); }
        throw new Error('timed out: ' + what);
    };
    try {
        // the six steps
        act('onb', ''); await sleep(150);
        type('ob_desk_name', 'Tour Residence'); type('ob_desk_client', 'Mr. Tour Client'); type('ob_desk_cphone', '98250 00000');
        type('ob_desk_area', 'Bopal');
        act('obgo', '2'); await sleep(100);
        if (!q('[data-a="obmulti"][aria-pressed="true"]')) throw new Error('the person onboarding is not pre-ticked on the team');
        act('obgo', '3'); await sleep(100);
        act('obpreset', '2 BHK'); await sleep(100);
        if (document.querySelectorAll('.entrow').length !== 9) throw new Error('2 BHK should propose 9 rooms (8 and the whole site), got ' + document.querySelectorAll('.entrow').length);
        act('obgo', '4'); await sleep(100);
        act('obgo', '5'); await sleep(150);
        if (!document.querySelectorAll('.drow.on').length) throw new Error('no drawing is proposed in step 5');
        act('obgo', '6'); await sleep(100);
        act('obfinish');
        await until(() => q('.prjh h1') && q('.prjh h1').textContent === 'Tour Residence', 'the project panel');
        // the picture is there, then one cell of the grid is changed
        if (!q('.ink')) throw new Error('no picture');
        act('ui', 'ptab=work'); await sleep(200);
        const room = [...document.querySelectorAll('[data-a="room"]')].find(e => /KITCHEN/i.test(e.textContent));
        if (!room) throw new Error('no kitchen on the plan');
        room.dispatchEvent(new MouseEvent('click', {bubbles: true})); await sleep(200);
        const cell = [...document.querySelectorAll('.ovl [data-a="cell"]')].find(e => /Civil/.test(e.textContent));
        if (!cell) throw new Error('no civil line in the kitchen');
        cell.dispatchEvent(new MouseEvent('click', {bubbles: true})); await sleep(200);
        act('set', 'c_st=work'); await sleep(100);
        act('savecell');
        await until(() => !document.documentElement.dataset.sync, 'the change to reach the server');
        await sleep(300);
        // the MOM log: a point raised from the desk, with its room chosen from the list, is one line of the table
        const click = el => { if (!el) throw new Error('nothing to click'); el.dispatchEvent(new MouseEvent('click', {bubbles: true})); };
        act('ui', 'ptab=mom'); await sleep(200);
        click(q('.card [data-a="raise"]')); await sleep(200);
        click(q('.ovl [data-a="doraise"]')); await sleep(100);
        if (!q('.ovl [data-a="doraise"]')) throw new Error('a point without text or room must not be taken');
        type('desk_rp_text', 'Tour point: check the platform height');
        click(q('.ovl [data-a="pick"][data-v^="area|"]')); await sleep(200);
        type('desk_pk_q', 'kit'); await sleep(200);
        if (document.querySelectorAll('.pklist [data-a="pickset"]').length !== 1) throw new Error('the search should leave the kitchen alone');
        click(q('.pklist [data-a="pickset"]')); await sleep(200);
        // the date comes from the calendar: the ninth day from today, in this month or the next
        if (!q('.ovl .drop.pht')) throw new Error('no clear button for the photo of the issue');
        click(q('.ovl [data-a="cal"]')); await sleep(200);
        if (document.querySelectorAll('.calw .cd').length < 28 || !q('.calw .cd.now')) throw new Error('the calendar did not open on this month');
        const pickDay = async (n, mark) => {
            // the day is in the month shown, the one after, or the one before
            const find = () => q('.calw [data-a="calset"][data-v="' + n + '"]');
            for (const move of [0, 1, -2]) {
                for (let i = 0; i < Math.abs(move); i++) click(q('.calw [data-a="calmo"][data-v="' + (move > 0 ? 1 : -1) + '"]'));
                if (move) await sleep(200);
                if (find()) break;
            }
            if (mark && !find().querySelector('i.d')) throw new Error('the calendar does not mark the day a point falls due');
            click(find()); await sleep(250);
        };
        await pickDay(9);
        if (!q('.ovl [data-a="doraise"]') || q('.ovl .chip.calc').getAttribute('aria-pressed') !== 'true') throw new Error('the date from the calendar was not taken back to the point');
        click(q('.ovl [data-a="doraise"]'));
        await until(() => !document.documentElement.dataset.sync && !q('.ovl'), 'the point to reach the server');
        await sleep(300);
        const heads = [...document.querySelectorAll('.ptlog thead th')].map(t => t.textContent).join('|');
        if (heads !== 'No|Visit|Area|Point|For|Raised by|On|Due|Photo|Status|') throw new Error('the log has other columns: ' + heads);
        const line = [...document.querySelectorAll('.ptlog tbody tr')].find(r => /Tour point/.test(r.textContent));
        if (!line) throw new Error('the point is not a line of the log');
        const cells = [...line.children].map(c => c.textContent.trim());
        if (cells[0] !== '1' || cells[1] !== 'office' || !/^Kitchen/.test(cells[2])) throw new Error('the line reads: ' + cells.join(' | '));
        if (!/^\\d{1,2} [A-Z][a-z]{2}$/.test(cells[7])) throw new Error('the date chosen in the calendar is not the due date: ' + cells[7]);
        // visits are looked up by date: the day the point falls due shows it, another day does not
        if (!q('.card.visc [data-a="cal"]')) throw new Error('no date search on the visits');
        click(q('.card.visc [data-a="cal"]')); await sleep(200);
        await pickDay(9, true);
        if (!/Tour point/.test(q('.card.visc').textContent)) throw new Error('the point is not listed on the day it falls due');
        click(q('.card.visc [data-a="cal"]')); await sleep(200);
        await pickDay(3);
        if (/Tour point/.test(q('.card.visc').textContent)) throw new Error('the point is listed on a day it is not due');
        act('ui', 'vd='); await sleep(100);
        // Questions has its own place in the bar on top
        act('nav', 'questions'); await sleep(200);
        if (!q('.dh h1') || q('.dh h1').textContent !== 'Questions' || !q('.qsp')) throw new Error('the Questions section did not open');
        console.log('test successful');
    } catch (e) {
        console.error('desk tour: ' + e.message);
    }
})();
"""


CONFIGURE_TOUR = """
(async () => {
    const sleep = ms => new Promise(r => setTimeout(r, ms));
    const q = s => document.querySelector(s);
    const click = el => { if (!el) throw new Error('nothing to click'); el.dispatchEvent(new MouseEvent('click', {bubbles: true})); };
    const type = (id, value) => {
        const el = document.getElementById(id);
        if (!el) throw new Error('no input ' + id);
        el.value = value;
        el.dispatchEvent(new Event('input', {bubbles: true}));
    };
    const until = async (test, what) => {
        for (let i = 0; i < 150; i++) { if (test()) return; await sleep(100); }
        throw new Error('timed out: ' + what);
    };
    const step = () => (q('.obb') || {}).dataset ? +q('.obb').dataset.sc.slice(2) : 0;
    try {
        // a project of the earlier way, with no client on it: its own button opens the wizard on it
        click(q('[data-a="proj"][data-v="__PID__"]')); await sleep(300);
        click(q('.prjh [data-a="onb"][data-v="__PID__"]')); await sleep(300);
        const name = document.getElementById('ob_desk_name');
        if (!name || name.value !== 'Earlier Site Without Client') throw new Error('the wizard did not open on the project');
        if (document.getElementById('ob_desk_cphone').value !== '') throw new Error('a number appeared for a client nobody gave');
        // a number alone is not taken: it needs the client's name
        type('ob_desk_cphone', '98250 11111');
        click(q('[data-a="obgo"][data-v="2"]')); await sleep(150);
        if (step() !== 1) throw new Error('a number without a client name went through');
        // no client at all is fine: the project is configured without one
        type('ob_desk_cphone', '');
        click(q('[data-a="obgo"][data-v="2"]')); await sleep(150);
        if (step() !== 2) throw new Error('the wizard asks for a client before step 2');
        click(q('[data-a="obgo"][data-v="3"]')); await sleep(100);
        click(q('[data-a="obpreset"][data-v="2 BHK"]')); await sleep(100);
        click(q('[data-a="obgo"][data-v="4"]')); await sleep(100);
        click(q('[data-a="obgo"][data-v="5"]')); await sleep(150);
        click(q('[data-a="obgo"][data-v="6"]')); await sleep(100);
        if ([...document.querySelectorAll('[data-a="obinv"]')].some(e => e.dataset.v === 'client')) throw new Error('a client nobody gave is offered an invitation');
        click(q('[data-a="obfinish"]'));
        await until(() => q('.prjh') && q('.prjh').textContent.includes('Project configuration'), 'the configured project');
        if (!q('.prjh').textContent.includes('no client yet')) throw new Error('the project does not say it has no client yet');
        // later: the client's tab offers to add the client, on step 1, saved from there
        click(q('[data-a="ui"][data-v="ptab=client"]')); await sleep(300);
        click(q('.card [data-a="onb"][data-v="__PID__"]')); await sleep(300);
        if (step() !== 1) throw new Error('Add client did not open step 1');
        type('ob_desk_client', 'Mr. Kiran Shah'); type('ob_desk_cphone', '98250 11111');
        const save = [...document.querySelectorAll('.obf [data-a="obfinish"]')].find(e => /Save changes/.test(e.textContent));
        if (!save) throw new Error('no Save changes on step 1 of a configured project');
        click(save);
        await until(() => q('.prjh') && q('.prjh').textContent.includes('Kiran Shah'), 'the client on the project');
        click(q('[data-a="ui"][data-v="ptab=client"]')); await sleep(300);
        if (!q('.card [data-a="invite"]')) throw new Error('the client added later cannot be invited');
        console.log('test successful');
    } catch (e) {
        console.error('configure tour: ' + e.message);
    }
})();
"""


@tagged("post_install", "-at_install")
class TestDeskBrowser(HttpCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.coordinator = new_test_user(
            cls.env, "t_tour_coord", groups="rvt_base.group_rvt_coordinator", name="Meera Joshi")
        new_test_user(cls.env, "t_tour_owner", groups="rvt_base.group_rvt_owner,rvt_base.group_rvt_principal", name="Ar. Pranav Vora")
        # the tour's coordinator sets the project up: ticked by hand, as an owner may do
        cls.coordinator.write({"group_ids": [(4, cls.env.ref("rvt_base.group_rvt_acc_projects").id)]})

    def test_login_page_is_the_desks_own(self):
        page = self.url_open("/web/login").text
        self.assertIn("Welcome back", page)
        self.assertIn("Every site,", page)
        self.assertIn('class="dlogin enter"', page)
        self.assertIn('name="csrf_token"', page)
        self.assertNotIn("Powered by", page)
        classic = self.url_open("/web/login?classic=1").text
        self.assertNotIn("dlogin", classic)
        # switched off (a live database where the office still works the earlier way): the standard page for everybody
        self.env["ir.config_parameter"].sudo().set_bool("rvt.desk_login", False)
        standard = self.url_open("/web/login").text
        self.assertNotIn("dlogin", standard)
        self.assertIn('name="csrf_token"', standard)

    def test_staff_land_on_the_desk(self):
        self.authenticate("t_tour_coord", "t_tour_coord")
        page = self.url_open("/rvt/desk")
        self.assertEqual(page.status_code, 200)
        self.assertIn("/rvt/desk/app.js", page.text)
        script = self.url_open("/rvt/desk/app.js")
        self.assertEqual(script.status_code, 200)
        self.assertIn("liveBoot();", script.text)
        # somebody who is not staff has no desk
        new_test_user(self.env, "t_tour_portal", groups="base.group_portal")
        self.authenticate("t_tour_portal", "t_tour_portal")
        self.assertNotIn("/rvt/desk/app.js", self.url_open("/rvt/desk").text)

    def test_configure_an_earlier_project_without_client(self):
        """Production, 27 Nov 2026: every earlier project had no client and no contact, and "Configure this
        project" did nothing. Such a project is configured without a client, and the client is added later."""
        project = self.env["project.project"].create({"name": "Earlier Site Without Client"})
        self.env["project.task"].create({"name": "Hand-made task", "project_id": project.id})
        self.assertFalse(project.partner_id or project.rvt_client_id or project.rvt_client_contact_ids)
        self.browser_js("/rvt/desk", CONFIGURE_TOUR.replace("__PID__", str(project.id)),
                        ready="!!document.querySelector('.gnav')", login="t_tour_owner", timeout=120)
        self.assertTrue(project.rvt_onboarded)
        self.assertEqual(project.rvt_client_id.name, "Mr. Kiran Shah")
        self.assertEqual(project.rvt_client_contact_ids.mapped("name"), ["Kiran Shah"])
        self.assertIn("11111", project.rvt_client_contact_ids.phone)
        codes = project.rvt_drawing_ids.mapped("code")
        self.assertEqual(len(codes), len(set(codes)), "saving the client again adds no drawing twice")
        self.assertEqual(project.task_ids.filtered(lambda t: t.name == "Hand-made task").project_id, project, "nothing is removed")

    def test_onboarding_tour(self):
        """A coordinator opens the desk, onboards a 2 BHK from the preset and changes a cell."""
        self.browser_js("/rvt/desk", TOUR, ready="!!document.querySelector('.gnav')", login="t_tour_coord", timeout=120)
        project = self.env["project.project"].search([("name", "=", "Tour Residence")])
        self.assertEqual(len(project), 1)
        self.assertTrue(project.rvt_onboarded)
        self.assertEqual(project.rvt_coordinator_ids, self.coordinator)
        self.assertIn("principal", project.rvt_principal_id.rvt_roles(), "the wizard starts with the real principal")
        self.assertEqual(project.rvt_site_label, "2 BHK")
        self.assertEqual(len(project.rvt_entity_ids), 9)
        self.assertEqual(len(project.rvt_trade_plan_ids), 7)
        drawings = project.rvt_drawing_ids
        self.assertTrue(drawings, "step 5 put the ticked standard drawings on the list")
        self.assertIn("FL", drawings.mapped("code"))
        self.assertEqual(set(drawings.mapped("state")), {"to_draw"})
        self.assertFalse(drawings.filtered(lambda d: not d.designer_id), "every drawing has its designer")
        line = self.env["project.task"].search([
            ("project_id", "=", project.id), ("rvt_kind", "=", "work"),
            ("parent_id.name", "=", "Kitchen"), ("rvt_trade_id.code", "=", "civ")])
        self.assertEqual(line.rvt_work_state, "working")
