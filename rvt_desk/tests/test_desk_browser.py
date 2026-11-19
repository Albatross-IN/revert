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
        click(q('.ovl [data-a="doraise"]'));
        await until(() => !document.documentElement.dataset.sync && !q('.ovl'), 'the point to reach the server');
        await sleep(300);
        const heads = [...document.querySelectorAll('.ptlog thead th')].map(t => t.textContent).join('|');
        if (heads !== 'No|Visit|Area|Point|For|Raised by|On|Due|Photo|Status|') throw new Error('the log has other columns: ' + heads);
        const line = [...document.querySelectorAll('.ptlog tbody tr')].find(r => /Tour point/.test(r.textContent));
        if (!line) throw new Error('the point is not a line of the log');
        const cells = [...line.children].map(c => c.textContent.trim());
        if (cells[0] !== '1' || cells[1] !== 'office' || !/^Kitchen/.test(cells[2])) throw new Error('the line reads: ' + cells.join(' | '));
        console.log('test successful');
    } catch (e) {
        console.error('desk tour: ' + e.message);
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

    def test_login_page_is_the_desks_own(self):
        page = self.url_open("/web/login").text
        self.assertIn("Welcome back", page)
        self.assertIn("Every site,", page)
        self.assertIn('class="dlogin enter"', page)
        self.assertIn('name="csrf_token"', page)
        self.assertNotIn("Powered by", page)
        classic = self.url_open("/web/login?classic=1").text
        self.assertNotIn("dlogin", classic)

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
