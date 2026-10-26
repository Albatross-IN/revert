"""Ordered phases of the Revert 18→20 ETL. Each phase is a list of steps
(OrmStep / SqlStep / FuncStep / TableCopy — see core.py)."""
from . import base, studio, project, revert, discuss, chatter, post  # noqa: F401

PHASES = {
    "base": base.STEPS,
    "studio": studio.STEPS,                     # Studio fields BEFORE the tasks carry their values
    "project": project.STEPS,
    "revert": revert.STEPS,                     # legacy MOM lines, responsibilities
    "discuss": discuss.STEPS,
    "studio_post": studio.POST_STEPS,           # x_mom.rec rows, Studio views
    "activities": revert.ACTIVITY_STEPS,        # before chatter: activity photos are attachments
    "chatter": chatter.STEPS,
    "post_chatter": project.POST_CHATTER_STEPS + discuss.POST_CHATTER_STEPS,
    "upgrade": revert.POST_CHATTER_STEPS,       # revert_customizations migrations 1.1 -> 1.6
    "post": post.STEPS,
}
ORDER = ["base", "studio", "project", "revert", "discuss", "studio_post", "activities", "chatter",
         "post_chatter", "upgrade", "post"]


def steps_for(phases=None):
    out = []
    for p in (phases or ORDER):
        out += PHASES[p]
    return out
