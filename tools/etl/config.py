"""Static configuration of the Revert 18→20 ETL. Everything run-specific comes from run.py's CLI.

Engine inherited from the mark 19→20 ETL (/opt/odoo20/custom/mark/tools/etl), itself from the
sudi and marut ETLs. Revert's source is an Odoo 18 Enterprise database: see docs/etl_runbook.md.
"""
import os

SRC_DB = os.environ.get("ETL_SRC", "revert_src18")    # restored production dump (same PG cluster)
SRC_SCHEMA = "src18"                                   # foreign schema exposing SRC_DB inside the target DB
SRC_TAG = "" if SRC_DB == "revert_src18" else "_" + SRC_DB
TARGET_MODULES_FILE = os.path.join(os.path.dirname(__file__), f"target_modules_prod{SRC_TAG}.txt")
OFFSET = 10_000_000                                    # SQL-lane id offset (old_id + OFFSET)
ODOO_CONF = os.path.join(os.path.dirname(__file__), "conf", "odoo20-etl.conf")
ODOO_ROOT = "/opt/odoo20/odoo20"
ETL_DIR = "/opt/odoo20/etl_revert"
LOG_DIR = f"{ETL_DIR}/logs"
ARCHIVE_DIR = f"{ETL_DIR}/archive"
BASELINE_DIR = f"{ETL_DIR}/baseline"
BASELINE_FILE = f"{BASELINE_DIR}/checksums_src{SRC_TAG}.json"
FILESTORE_SRC = f"{ETL_DIR}/data18/filestore/{SRC_DB}"  # v18 filestore staged by restore_src.sh
COMPANY = 1                                            # the single company (Studio Revert)
ORM_BATCH = 500

# Port block reserved for Revert on this machine (agreed with the parallel Albatross ETL, which
# owns 8161-8166; sudi 8119-8124, mark 8141-8144). Nothing here ever binds 8069.
PORT_BASELINE18 = 8171   # read-only v18 server on the source snapshot
PORT_SHELL20 = 8172      # bootstrap.open_env / odoo shell against targets
PORT_MKDB = 8173         # module installs while building a target DB
PORT_TARGET20 = 8174     # v20 server on the ETL target for validation/QA

# Modules ADDED on 20 beyond the production module set (documented exceptions):
# mail_tracking: v20 split mail.tracking.value out of mail; prod holds 1,890 tracked values.
EXTRA_MODULES = ("mail_tracking",)

# 18→20 module merges / removals (gen_target_modules.py refuses any name without a v20 directory).
MERGED_MODULES = {
    "web_editor": "html_editor",          # the 18 editor was folded into html_editor
    # studio_customization is the virtual module Studio writes into; prod's Studio work
    # (x_studio_responsible_person, two view tweaks, the empty x_mom.rec model) is carried
    # as data by mapping/studio.py.
    "studio_customization": "web_studio",
}

# Legacy IANA aliases an 18 DB may hold in tz columns; v20's selection lists only canonical names.
TZ_ALIASES = {
    "Asia/Calcutta": "Asia/Kolkata", "Asia/Katmandu": "Asia/Kathmandu", "Asia/Saigon": "Asia/Ho_Chi_Minh",
    "Asia/Rangoon": "Asia/Yangon", "Asia/Dacca": "Asia/Dhaka", "Asia/Thimbu": "Asia/Thimphu",
    "Europe/Kiev": "Europe/Kyiv", "America/Buenos_Aires": "America/Argentina/Buenos_Aires",
    "US/Eastern": "America/New_York", "US/Central": "America/Chicago", "US/Pacific": "America/Los_Angeles",
}

# context that keeps the 20 ORM quiet while loading history
SILENT_CTX = dict(
    tracking_disable=True, mail_create_nolog=True, mail_create_nosubscribe=True, mail_notrack=True,
    mail_activity_automation_skip=True, mail_auto_subscribe_no_notify=True, active_test=False,
)

# columns never copied by the ORM lane
IGNORED_COLUMNS = {"id", "create_date", "write_date", "create_uid", "write_uid", "__last_update", "display_name",
                   "message_main_attachment_id", "website_message_ids", "message_ids", "activity_ids",
                   "message_follower_ids", "rating_ids", "access_token", "access_url"}
# Revert never went through an earlier data migration — no legacy id columns.
LEGACY_PREFIXES = ()

# A run is a *production* run only when explicitly asked (run.py --production). Every other run is a
# dry run: the engine deactivates crons and outgoing mail servers and blanks IAP tokens on the target
# after each phase, so nothing loaded from 18 can ever e-mail a client from a test database.
PRODUCTION = os.environ.get("ETL_PRODUCTION") == "1"
