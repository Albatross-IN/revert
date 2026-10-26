"""Phase 'project': project tags + stages, projects, task stages (project stages and every user's
personal stages), tasks with their sub-task tree and assignees, project updates, favourites,
the project e-mail aliases. ORM lane (Odoo 20 business logic validates every record); dates and
authors restored from 18 by the engine."""
import logging

from ..core import OrmStep, SqlStep, FuncStep
from .. import config
from .common import map_by_xmlid

_logger = logging.getLogger("etl.project")
S = config.SRC_SCHEMA


def _xmlid_maps(engine, ctx):
    """Module-data records of this phase land ON the fresh module rows (project stages, ...)."""
    return {m: map_by_xmlid(engine, m) for m in ("project.project.stage", "project.task.type", "project.tags")}


XMLID_MAPS = FuncStep("project.xmlid_maps", _xmlid_maps)

# 18 activity-type icons are FontAwesome names; 20 renders Material Symbols names only
FA_ICONS = {"fa-check": "check", "fa-tasks": "checklist", "fa-envelope": "mail", "fa-phone": "phone",
            "fa-users": "group", "fa-upload": "upload", "fa-warning": "warning", "fa-clipboard": "assignment"}


def _activity_type_transform(vals, row, ctx):
    icon = vals.get("icon") or ""
    if icon.startswith("fa-"):
        vals["icon"] = FA_ICONS.get(icon, "task_alt")
    # 18 categories 20 no longer has (web_studio's 'grant_approval') become a plain activity
    categories = ctx["env"]["mail.activity.type"]._fields["category"].get_values(ctx["env"])
    if vals.get("category") not in categories:
        vals["category"] = "default"
    return vals


# activity types prod uses that 20 no longer ships (web_studio's "Grant Approval")
ACTIVITY_TYPES = OrmStep("mail.activity.type", key=["name"], transform=_activity_type_transform,
                         skip={"chaining_type", "keep_done", "triggered_next_type_id", "previous_type_ids",
                               "suggested_next_type_id", "mail_template_ids", "default_user_id"})

TAGS = OrmStep("project.tags", key=["name"], skip={"project_ids", "task_ids"})
PROJECT_STAGES = OrmStep("project.project.stage", key=["name"])

PROJECTS = OrmStep(
    "project.project",
    skip={"alias_id", "alias_name", "alias_defaults", "alias_domain_id", "alias_contact", "alias_force_thread_id",
          "alias_model_id", "alias_parent_model_id", "alias_parent_thread_id", "alias_bounced_content",
          "alias_status", "alias_incoming_local", "rating_status", "rating_status_period", "rating_active",
          "rating_request_deadline", "task_ids", "type_ids", "favorite_user_ids", "collaborator_ids",
          "last_update_id", "update_ids", "milestone_ids", "tag_ids"},
    force_fields={"last_update_status", "stage_id", "date_start", "date"},
    # 20 gives a new project four default task stages; a migrated project has exactly prod's
    # stages (linked by the stage steps below)
    defaults={"type_ids": [(6, 0, [])]},
)

# On 20 the stage owner (user_id) is a stored compute whose DEFAULT is the current user: a stage
# created without an explicit owner becomes a personal stage of the ETL user. Both steps
# therefore write user_id explicitly (force_fields).
# Project stages (no owner) are created with their projects; the SQL re-link below is a safety net.
TASK_TYPES = OrmStep("project.task.type", name="project.task.type.project", where="user_id IS NULL",
                     skip={"rating_template_id", "rating_active", "rating_status",
                           "rating_status_period", "rating_request_deadline", "mail_template_id"},
                     force_fields={"user_id"}, defaults={"user_id": False})
# personal stages (Inbox, Today, ...) are per user and 20 creates them with the user: the one with
# the same owner and name is reused, so nobody ends up with two "Inbox" columns in My Tasks
PERSONAL_STAGES = OrmStep("project.task.type", name="project.task.type.personal", where="user_id IS NOT NULL",
                          key=["user_id", "name"], update_existing=False, force_fields={"user_id"},
                          skip={"project_ids", "rating_template_id", "mail_template_id"})
TASK_TYPE_PROJECTS = SqlStep("project.task.type.projects", f"""
    INSERT INTO project_task_type_rel (type_id, project_id)
    SELECT t.new_id, p.new_id FROM {{S}}.project_task_type_rel r
    JOIN etl_idmap t ON t.model = 'project.task.type' AND t.old_id = r.type_id
    JOIN etl_idmap p ON p.model = 'project.project' AND p.old_id = r.project_id
    ON CONFLICT DO NOTHING""")

TASK_SKIP = {"email_cc", "child_ids", "depend_on_ids", "dependent_ids", "personal_stage_type_ids", "personal_stage_id",
             "personal_stage_type_id", "recurrence_id", "recurring_task", "subtask_count", "closed_subtask_count",
             "rating_ids", "rating_last_value", "rating_avg", "rating_count", "rating_active", "display_in_project",
             "message_partner_ids", "attachment_ids", "displayed_image_id", "working_hours_open", "working_hours_close",
             "working_days_open", "working_days_close", "portal_user_names", "is_closed", "mom_meeting_ids",
             "person_ids", "mom_activity_ids", "html_field_history", "html_field_history_metadata"}
TASK_FORCE = {"date_last_stage_update", "date_assign", "date_end", "date_deadline", "stage_id", "user_ids",
              "priority", "state", "sequence", "planned_date_begin"}
# 20's project.task.create() applies the project of the parent to the WHOLE batch when the batch
# holds sub-tasks of a single parent, private to-dos included: private tasks (no project, no
# parent) are therefore created on their own.
TASKS = OrmStep("project.task", batch=300, order="id", where="project_id IS NOT NULL OR parent_id IS NOT NULL",
                skip=TASK_SKIP, force_fields=TASK_FORCE)
PRIVATE_TASKS = OrmStep("project.task", name="project.task.private", batch=1, order="id",
                        where="project_id IS NULL AND parent_id IS NULL", skip=TASK_SKIP, force_fields=TASK_FORCE)


def _task_fixups(engine, ctx):
    """What the create lane cannot set: the parent link of a sub-task whose parent was refused,
    active (archived tasks), each assignee's personal stage, the cover image (after chatter)."""
    cr = engine.cr
    cr.execute(f"""UPDATE project_task t SET parent_id = pm.new_id
                   FROM etl_idmap m JOIN {S}.project_task s ON s.id = m.old_id
                   JOIN etl_idmap pm ON pm.model = 'project.task' AND pm.old_id = s.parent_id
                   WHERE m.model = 'project.task' AND t.id = m.new_id AND t.parent_id IS DISTINCT FROM pm.new_id""")
    parents = cr.rowcount
    cr.execute(f"""UPDATE project_task t SET active = s.active
                   FROM etl_idmap m JOIN {S}.project_task s ON s.id = m.old_id
                   WHERE m.model = 'project.task' AND t.id = m.new_id AND t.active IS DISTINCT FROM s.active""")
    actives = cr.rowcount
    # dates 20 stamps with "now" while creating (assignment, stage change, closing)
    cr.execute(f"""UPDATE project_task t SET date_assign = s.date_assign, date_end = s.date_end,
                          date_last_stage_update = s.date_last_stage_update
                   FROM etl_idmap m JOIN {S}.project_task s ON s.id = m.old_id
                   WHERE m.model = 'project.task' AND t.id = m.new_id
                     AND (t.date_assign IS DISTINCT FROM s.date_assign OR t.date_end IS DISTINCT FROM s.date_end
                          OR t.date_last_stage_update IS DISTINCT FROM s.date_last_stage_update)""")
    dates = cr.rowcount
    # values 20 derives while creating that prod never had: the project's default stage for a task
    # created without one, and project_enterprise's allocated time computed from the planned dates
    cr.execute(f"""UPDATE project_task t SET stage_id = st.new_id, allocated_hours = s.allocated_hours
                   FROM etl_idmap m JOIN {S}.project_task s ON s.id = m.old_id
                   LEFT JOIN etl_idmap st ON st.model = 'project.task.type' AND st.old_id = s.stage_id
                   WHERE m.model = 'project.task' AND t.id = m.new_id
                     AND (t.stage_id IS DISTINCT FROM st.new_id
                          OR coalesce(t.allocated_hours, 0) IS DISTINCT FROM coalesce(s.allocated_hours, 0))""")
    derived = cr.rowcount
    # personal stage of every (task, assignee): the 20 create lane put the user's default one
    cr.execute(f"""UPDATE project_task_user_rel r SET stage_id = st.new_id
                   FROM {S}.project_task_user_rel s
                   JOIN etl_idmap tm ON tm.model = 'project.task' AND tm.old_id = s.task_id
                   JOIN etl_idmap um ON um.model = 'res.users' AND um.old_id = s.user_id
                   JOIN etl_idmap st ON st.model = 'project.task.type' AND st.old_id = s.stage_id
                   WHERE r.task_id = tm.new_id AND r.user_id = um.new_id AND r.stage_id IS DISTINCT FROM st.new_id""")
    personal = cr.rowcount
    cr.execute(f"""INSERT INTO project_task_user_rel (task_id, user_id, stage_id)
                   SELECT tm.new_id, um.new_id, st.new_id FROM {S}.project_task_user_rel s
                   JOIN etl_idmap tm ON tm.model = 'project.task' AND tm.old_id = s.task_id
                   JOIN etl_idmap um ON um.model = 'res.users' AND um.old_id = s.user_id
                   LEFT JOIN etl_idmap st ON st.model = 'project.task.type' AND st.old_id = s.stage_id
                   WHERE NOT EXISTS (SELECT 1 FROM project_task_user_rel e WHERE e.task_id = tm.new_id AND e.user_id = um.new_id)""")
    missing_assignees = cr.rowcount
    engine._restore_dates("project_task", "project.task")
    return dict(parents_relinked=parents, active_restored=actives, dates_restored=dates, derived_restored=derived,
                personal_stages=personal,
                assignees_added=missing_assignees)


TASK_FIXUPS = FuncStep("project.task.fixups", _task_fixups)

UPDATES = OrmStep("project.update", skip={"email_cc"}, force_fields={"status", "progress", "date"})


def _project_links(engine, ctx):
    """Links that need the updates / users: last update + status, favourites, the e-mail alias."""
    cr = engine.cr
    cr.execute(f"""UPDATE project_project p SET last_update_id = um.new_id, last_update_status = s.last_update_status
                   FROM etl_idmap m JOIN {S}.project_project s ON s.id = m.old_id
                   LEFT JOIN etl_idmap um ON um.model = 'project.update' AND um.old_id = s.last_update_id
                   WHERE m.model = 'project.project' AND p.id = m.new_id""")
    status = cr.rowcount
    cr.execute(f"""UPDATE project_project p SET active = s.active
                   FROM etl_idmap m JOIN {S}.project_project s ON s.id = m.old_id
                   WHERE m.model = 'project.project' AND p.id = m.new_id AND p.active IS DISTINCT FROM s.active""")
    actives = cr.rowcount
    cr.execute(f"""INSERT INTO project_favorite_user_rel (project_id, user_id)
                   SELECT p.new_id, u.new_id FROM {S}.project_favorite_user_rel r
                   JOIN etl_idmap p ON p.model = 'project.project' AND p.old_id = r.project_id
                   JOIN etl_idmap u ON u.model = 'res.users' AND u.old_id = r.user_id
                   ON CONFLICT DO NOTHING""")
    favs = cr.rowcount
    cr.execute(f"""INSERT INTO project_project_project_tags_rel (project_project_id, project_tags_id)
                   SELECT p.new_id, t.new_id FROM {S}.project_project_project_tags_rel r
                   JOIN etl_idmap p ON p.model = 'project.project' AND p.old_id = r.project_project_id
                   JOIN etl_idmap t ON t.model = 'project.tags' AND t.old_id = r.project_tags_id
                   ON CONFLICT DO NOTHING""")
    tags = cr.rowcount
    # e-mail alias of each project (alias name + who may write to it)
    cr.execute(f"""UPDATE mail_alias a SET alias_name = sa.alias_name, alias_contact = sa.alias_contact,
                          alias_defaults = sa.alias_defaults
                   FROM etl_idmap m JOIN {S}.project_project s ON s.id = m.old_id
                   JOIN {S}.mail_alias sa ON sa.id = s.alias_id
                   JOIN project_project p ON p.id = m.new_id
                   WHERE m.model = 'project.project' AND a.id = p.alias_id
                     AND (a.alias_name IS DISTINCT FROM sa.alias_name OR a.alias_contact IS DISTINCT FROM sa.alias_contact)""")
    aliases = cr.rowcount
    engine._restore_dates("project_project", "project.project")
    return dict(last_update=status, active_restored=actives, favourites=favs, tags=tags, aliases=aliases)


PROJECT_LINKS = FuncStep("project.project.links", _project_links)


def _task_cover(engine, ctx):
    """Cover image of a task (displayed_image_id), once the attachments exist (+OFFSET)."""
    cr = engine.cr
    cr.execute(f"""UPDATE project_task t SET displayed_image_id = a.id
                   FROM etl_idmap m JOIN {S}.project_task s ON s.id = m.old_id
                   JOIN ir_attachment a ON a.id = s.displayed_image_id + {config.OFFSET}
                   WHERE m.model = 'project.task' AND t.id = m.new_id AND s.displayed_image_id IS NOT NULL""")
    return dict(covers=cr.rowcount)


TASK_COVER = FuncStep("project.task.cover", _task_cover)

STEPS = [XMLID_MAPS, ACTIVITY_TYPES, TAGS, PROJECT_STAGES, PROJECTS, TASK_TYPES, PERSONAL_STAGES, TASK_TYPE_PROJECTS,
         TASKS, PRIVATE_TASKS, TASK_FIXUPS, UPDATES, PROJECT_LINKS]
POST_CHATTER_STEPS = [TASK_COVER]
