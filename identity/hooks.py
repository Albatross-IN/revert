# -*- coding: utf-8 -*-
import logging

from odoo.tools import split_every

_logger = logging.getLogger(__name__)

# Sent / received e-mails are the record of what actually went over the wire and
# are left untouched.  On a migrated database they are also the bulk of the
# bot's messages (100k rows, 1.7 GB on marut, whose only match is the
# "Odoo Unicode Support Noto" font name in inline CSS).
EMAIL_TYPES = ('email', 'email_outgoing')
CHUNK = 1000


def post_init_hook(env):
    """Recompute the cached menu icons so the Identity set shows up
    immediately (icons are otherwise only computed when a menu is
    created or its ``web_icon`` is written)."""
    env['ir.ui.menu']._identity_refresh_icons()
    env['identity.brand']._sync_bot()
    _debrand_bot_messages(env)


def _debrand_bot_messages(env):
    """Rewrite the brand in the messages the bot posted before installation
    (onboarding chats, activity notifications).

    Done in SQL and in chunks: the ORM prefetches ``body`` for the whole
    recordset, which on a large database is gigabytes of HTML in one worker
    (MemoryError on production).  ``write_date`` is left as it was: the content
    is not edited by a user, only the brand name is swapped.  Same rules as
    :func:`identity_brand.debrand_text`: case-sensitive, ``OdooBot`` first.
    """
    brand = env['identity.brand'].get()
    if not brand['replace_text']:
        return
    root = env.ref('base.partner_root', raise_if_not_found=False)
    if not root:
        return
    cr = env.cr
    cr.execute("""
        SELECT id
          FROM mail_message
         WHERE author_id = %s
           AND message_type NOT IN %s
           AND body LIKE '%%Odoo%%'
         ORDER BY id
    """, [root.id, EMAIL_TYPES])
    ids = [row[0] for row in cr.fetchall()]
    if not ids:
        return
    done = 0
    for chunk in split_every(CHUNK, ids):
        cr.execute("""
            UPDATE mail_message
               SET body = replace(replace(body, 'OdooBot', %s), 'Odoo', %s)
             WHERE id IN %s
        """, [brand['bot_name'], brand['name'], chunk])
        done += cr.rowcount
    env['mail.message'].invalidate_model(['body'])
    _logger.info("Identity: debranded %d bot messages", done)


def uninstall_hook(env):
    """Restore the stock Odoo icons and the bot name."""
    env['ir.ui.menu'].with_context(identity_skip_icons=True)._identity_refresh_icons()
    env['identity.brand']._sync_bot(restore=True)
