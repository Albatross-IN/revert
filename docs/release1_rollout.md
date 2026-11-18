# Release 1: how it goes live

Phase P11 of `implementation_plan_r1.md`. This is the run sheet for the person who releases
(the project owner). **Nothing in it has been run on the server.** Everything was built and tested
on a neutralised copy of the live database on a development machine; the server is untouched.

The base procedure, the server layout and its traps are in `deploy_production.md`. This page
adds what is new with Release 1.

## 1. What goes out

| Piece | Where from | Version |
|---|---|---|
| `rvt_base`, `rvt_project`, `rvt_drawing`, `rvt_mom`, `rvt_notify`, `rvt_desk`, `rvt_api`, `rvt_bill` | this repository, branch `20.0-release1` | see each `__manifest__.py` |
| `identity`, `web_theme_glass`, `web_glass_workspace` | copied into this repository, unchanged | as committed |
| `open_whatsapp_connector` and its helper service (`sidecar/`) | copied into this repository, unchanged | 20.0.95.0.0 |
| `fastapi`, `endpoint_route_handler` | copied into this repository, unchanged | 20.0.1.1.0, 20.0.1.2.0 |
| The app, Android | `revert_fe`, `app/` | 1.0.0 |
| The app, iPhone | `revert_fe`, `app/` (not built yet: needs a Mac) | 1.0.0 |

Python packages the server's environment needs first: `requirements.txt`.

## 2. Before the day

1. **Decisions still open** (`phase1_adoption.md` §9): the dedicated WhatsApp number and who keeps
   the phone; the pilot projects and agencies with their numbers; whether the helper service may run
   on the server shared with Albatross.
2. **Names in `tools/assign_roles.py`** match the people of the live database (dry run shows who is
   matched and who is not).
3. **Trade names of the earlier MOM** are mapped: `tools/etl_mom.py` dry run on a fresh copy of the
   live database prints the unmapped ones; fill `MAP=<csv>` until none is left.
4. **A rehearsal on a fresh copy of the live database** on the development machine or on a
   throwaway database on the server (never the live one): steps 3.2 to 3.7 below, then the checks of §4.
5. Announce the restart to Albatross: one restart of `erp-odoo20` drops both sites for a few seconds.

## 3. The day (maintenance window)

Run as on `deploy_production.md`: root on the server, `erp` owns the files.

1. **Backup first.** Run the backup unit by hand and check its `SHA256SUMS`. Note the stamp: it is
   the way back (§6).
2. **Code.** `git archive <commit of 20.0-release1>` of the module folders listed in §1 into
   `/opt/erp/addons/revert`, owner `erp`. Install the packages of `requirements.txt` into
   `/opt/erp/venv`.
3. **One restart** (announced), so the service sees the new modules.
4. **Install**, in one run, with the service's own configuration:
   `odoo-bin -c /etc/erp/odoo20.conf -d <host> -i rvt_bill --stop-after-init --no-http`
   (`rvt_bill` pulls every other `rvt_*` module and the copied ones). Then restart once more.
5. **Roles.** `APPLY=1 … shell < tools/assign_roles.py`. Open the desk as each role once.
6. **The earlier MOM.** Dry run first (`… shell < tools/etl_mom.py`), read the report, then
   `APPLY=1 MAP=<csv> …`. Keep the verification report with the release notes. Run it again with
   `SWITCH_OFF=1` only after the owner has seen the moved points in the desk: it hides the earlier
   MOM screens.
7. **Settings** (Setup in the desk, or system parameters):
   - `web.base.url` is the public address (links in messages and the client's link are built from it).
   - `rvt_api.jwt_secret` exists (the install creates it; never copy it from a test database).
   - `database.is_neutralized` is **absent**. Its presence marks a test copy, and nothing is ever
     sent from a test copy, whatever the switch says.
   - `rvt.notify_sending_on` stays **off** until step 8 is done.
   - nginx: `client_max_body_size 30m` on the site (drawings up to 25 MB, bills up to 15 MB), and
     gzip on for `application/json` (the staff snapshot is about 120 KB plain).
8. **WhatsApp.** Build and start the helper service (`open_whatsapp_connector/sidecar`, see its
   `SETUP.md`) as a system service of its own, bound to 127.0.0.1. Pair the dedicated number from
   the connector's settings. Send one test message to a staff phone. Only then switch
   `rvt.notify_sending_on` on in Setup.
9. **Push notifications** (when a Firebase project exists): put the service account JSON into the
   system parameter `rvt_api.fcm_service_account`. Without it everything works; phones simply get
   no push, only WhatsApp and what the app shows when opened.

## 4. Checks after the release

| Check | Expected |
|---|---|
| `GET https://<host>/api/rvt/v1/health` | `{"status":"ok", …}` |
| Log in to the back office as each role | staff land on the desk (`/rvt/desk`); the log-in page is Revert's |
| Desk, a pilot project | Picture, Work, Drawings, MOM, Client, Bills open; counts match the back office |
| App, staff | sign in with the office login; Today shows the same items as the desk |
| App, agency | a pilot agency signs in with its number and the code that arrives on WhatsApp |
| Release one test drawing to a staff member's own number | the message arrives; opening the link marks "opened" in the desk |
| "Copy link" on a pilot project's Client tab | the link opens that project in a phone browser without sign-in |
| Message log (Setup → WhatsApp) | "sent", not "held" |
| Module tests | were run before the release on a copy: 164 pass (`/rvt_base,/rvt_project,/rvt_drawing,/rvt_mom,/rvt_notify,/rvt_desk,/rvt_api,/rvt_bill`). Never run tests on the live database |

## 5. The app

- **Android.** A release key is made once and kept outside git (`android/key.properties`, the
  keystore file). Build: `flutter build appbundle --release --dart-define=API_BASE=https://<host>`.
  Application id `in.co.revert.app`. Listing text: `store_listing.md`. Privacy page: `privacy_page.md`
  must be reachable at a public address before the listing is submitted.
- **iPhone.** On a Mac: open `ios/Runner.xcworkspace`, set the signing team, then
  `flutter build ipa --release --dart-define=API_BASE=https://<host>`. Bundle id `in.co.revert.app`.
  The usage texts for camera, photos and Face ID are in place.
- After every app build that goes out: `python3 rvt_api/tools/sync_app.py` in this repository and
  release the module, so the client's link shows the same screens as the app.
- Before the first public build: a native reader checks the Gujarati and Hindi wording
  (`revert_fe/app/web/mobile.js`, the message texts of `rvt_notify`, and `docs/guides/`).

## 6. The way back

Release 1 adds tables and fields; it changes no existing record except by the two scripts of
steps 5 and 6, and each of those prints what it does before it writes.

- A fault in the new screens only: staff keep working in the back office (set the system
  parameter `rvt.desk_only` to False to show the standard menus again).
- Messages going wrong: switch `rvt.notify_sending_on` off. Nothing is sent from that moment.
- A fault in the data: restore the backup of step 3.1 with the procedure of `deploy_production.md`
  under a new database name, check it, then switch the host to it. Work done since the backup is
  lost; this is why the window is kept short and the pilot starts the next morning.

## 7. After the day: the waves

As `phase1_adoption.md` §8. In short: staff and the desk first (running projects onboarded, the
release rule starts), then the MOM at site on the app, then the carpenter and the electrician of the
pilot sites (signed in on site by the coordinator), then the pilot clients (a short message from the
principal, with the link), then bills at the next sensible billing point. Guides for agencies and
clients, one page each, in English, Gujarati and Hindi: `docs/guides/`.

## 8. Open at hand-over

| What | Who |
|---|---|
| The dedicated WhatsApp number, paired; one real message checked on a phone | Revert + the releaser |
| The app built for iPhone and tried on one | needs a Mac |
| Push notifications | needs a Firebase project |
| Release key for Android, the store listings | the account holder |
| Gujarati and Hindi wording checked by a native reader | Revert |
| `SWITCH_OFF` of the earlier MOM screens | after the owner's sign-off |
| The exit check of P8 on two more phones (a second Android phone, an iPhone) | at the pilot |
