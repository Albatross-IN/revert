"""Phase 'discuss': the 18 conversations (direct chats, groups, channels) and their members,
SQL lane at +OFFSET; their messages travel with the chatter phase (model discuss.channel).
18→20 drift: member custom_channel_name/fetched_message_id/fold_state and channel
allow_public_upload are gone; a direct chat needs member_indices (computed here)."""
import logging

from ..core import FuncStep, TableCopy, SqlStep, IDM
from .. import config
from .common import map_by_xmlid

_logger = logging.getLogger("etl.discuss")
S = config.SRC_SCHEMA


def _xmlid_maps(engine, ctx):
    """Module-data channels (#general) land ON the fresh module channel."""
    return {"discuss.channel": map_by_xmlid(engine, "discuss.channel")}


XMLID_MAPS = FuncStep("discuss.xmlid_maps", _xmlid_maps)

_NOT_MAPPED = "NOT EXISTS (SELECT 1 FROM etl_idmap x WHERE x.model = 'discuss.channel' AND x.old_id = s.id)"
_MI = ("LEFT JOIN LATERAL (SELECT string_agg('p' || pm.new_id, ',' ORDER BY pm.new_id) AS mi, count(*) AS n "
       "FROM {S}.discuss_channel_member scm "
       "JOIN etl_idmap pm ON pm.model = 'res.partner' AND pm.old_id = scm.partner_id "
       "WHERE scm.channel_id = s.id AND scm.partner_id IS NOT NULL) mix ON true")
CHANNELS = TableCopy(
    "discuss.channel", "discuss_channel",
    joins=[_MI],
    where=_NOT_MAPPED,
    overrides={"id": "s.id + {OFF}", "group_public_id": "NULL", "parent_channel_id": "NULL",
               "from_message_id": "NULL", "ai_agent_id": "NULL", "discuss_category_id": "NULL",
               "channel_type": "CASE WHEN s.channel_type = 'chat' AND coalesce(mix.n, 0) < 2 THEN 'group' "
                               "ELSE s.channel_type END"},
    extra={"member_indices": "CASE WHEN s.channel_type = 'chat' AND coalesce(mix.n, 0) >= 2 THEN mix.mi END"},
    register=("discuss.channel", "discuss_channel"),
)
CHANNEL_LINKS = SqlStep("discuss.channel.links", f"""
    UPDATE discuss_channel t SET parent_channel_id = p.id
    FROM {{S}}.discuss_channel s JOIN discuss_channel p ON p.id = s.parent_channel_id + {{OFF}}
    WHERE t.id = s.id + {{OFF}} AND s.parent_channel_id IS NOT NULL""")

MEMBERS = TableCopy(
    "discuss.channel.member", "discuss_channel_member",
    joins=["JOIN etl_idmap ch ON ch.model = 'discuss.channel' AND ch.old_id = s.channel_id",
           IDM("pa", "res.partner", "s.partner_id")],
    where="s.guest_id IS NULL AND (s.partner_id IS NULL OR pa.new_id IS NOT NULL)"
          " AND NOT EXISTS (SELECT 1 FROM discuss_channel_member e WHERE e.channel_id = ch.new_id AND e.partner_id = pa.new_id)",
    overrides={"id": "s.id + {OFF}", "channel_id": "ch.new_id", "partner_id": "pa.new_id", "guest_id": "NULL",
               "seen_message_id": "NULL", "rtc_inviting_session_id": "NULL"},
    register=("discuss.channel.member", "discuss_channel_member"),
)

# group-restricted channels and auto-join groups, by group xmlid
CHANNEL_GROUPS = SqlStep("discuss.channel.groups", """
    UPDATE discuss_channel c SET group_public_id = tgt.res_id
    FROM etl_idmap m
    JOIN {S}.discuss_channel s ON s.id = m.old_id
    JOIN {S}.ir_model_data sd ON sd.model = 'res.groups' AND sd.res_id = s.group_public_id
    JOIN ir_model_data tgt ON tgt.model = 'res.groups' AND tgt.module = sd.module AND tgt.name = sd.name
    WHERE m.model = 'discuss.channel' AND c.id = m.new_id
      AND s.group_public_id IS NOT NULL AND c.group_public_id IS DISTINCT FROM tgt.res_id;
    INSERT INTO discuss_channel_res_groups_rel (discuss_channel_id, res_groups_id)
    SELECT m.new_id, tgt.res_id FROM {S}.discuss_channel_res_groups_rel r
    JOIN etl_idmap m ON m.model = 'discuss.channel' AND m.old_id = r.discuss_channel_id
    JOIN {S}.ir_model_data sd ON sd.model = 'res.groups' AND sd.res_id = r.res_groups_id
    JOIN ir_model_data tgt ON tgt.model = 'res.groups' AND tgt.module = sd.module AND tgt.name = sd.name
    ON CONFLICT DO NOTHING""")


def _recompute_channels(engine, ctx):
    env, cr = engine.env, engine.cr
    env.invalidate_all()
    cr.execute("SELECT new_id FROM etl_idmap WHERE model = 'discuss.channel'")
    channels = env["discuss.channel"].browse([r[0] for r in cr.fetchall()]).exists()
    C = env["discuss.channel"]
    for f in ("member_indices", "member_count"):
        if f in C._fields and C._fields[f].store and C._fields[f].compute:
            env.add_to_compute(C._fields[f], channels)
    C.flush_model()
    for t in ("discuss_channel", "discuss_channel_member"):
        cr.execute(f"SELECT setval(pg_get_serial_sequence('{t}', 'id'), GREATEST((SELECT coalesce(max(id), 1) FROM {t}), 1))")
    return dict(channels=len(channels))


RECOMPUTE = FuncStep("discuss.recompute", _recompute_channels)

# after chatter: each member's read position (seen/fetched message) and the thread a sub-channel came from
POST_LINKS = SqlStep("discuss.member.positions", f"""
    UPDATE discuss_channel_member t SET seen_message_id = msg.id
    FROM {{S}}.discuss_channel_member s JOIN mail_message msg ON msg.id = s.seen_message_id + {{OFF}}
    WHERE t.id = s.id + {{OFF}} AND s.seen_message_id IS NOT NULL;
    UPDATE discuss_channel t SET from_message_id = msg.id
    FROM {{S}}.discuss_channel s JOIN mail_message msg ON msg.id = s.from_message_id + {{OFF}}
    WHERE t.id = s.id + {{OFF}} AND s.from_message_id IS NOT NULL""")

STEPS = [XMLID_MAPS, CHANNELS, CHANNEL_LINKS, MEMBERS, CHANNEL_GROUPS, RECOMPUTE]
POST_CHATTER_STEPS = [POST_LINKS]
