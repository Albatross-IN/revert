# -*- coding: utf-8 -*-
from odoo import fields, models

# Preferences a user changes about themselves (the Glass panel writes them with the user's own
# rights): Odoo 20 marks such fields `user_writeable=True` (19's SELF_WRITEABLE_FIELDS is gone).


class ResUsers(models.Model):
    _inherit = "res.users"

    glass_nav = fields.Selection(
        [("top", "Odoo top bar only"), ("side", "Left pane, expanded"), ("mini", "Left pane, icons")],
        string="Navigation",
        default="top",
        help="The Odoo top bar is always there. A left pane can be shown next to it, "
             "expanded or collapsed to icons; the ☰ button in the top bar toggles it at any time.",
        user_writeable=True,
    )
    glass_split = fields.Boolean(
        string="Split Form View",
        default=False,
        help="Open records from a list or kanban in a panel beside the list "
             "instead of navigating to the form.",
        user_writeable=True,
    )
    glass_split_side = fields.Selection(
        [("right", "Right of the list"), ("bottom", "Below the list")],
        string="Split panel position",
        default="right",
        user_writeable=True,
    )
    glass_split_chatter = fields.Selection(
        [("float", "Floats automatically"), ("docked", "Docked below the form")],
        string="Chatter in the split view",
        default="float",
        help="Floating: when a record opens in the split panel its chatter pops out into a "
             "movable, resizable window that follows the selected record. Docked: the chatter "
             "stays below the form inside the panel (it can still be floated with a click).",
        user_writeable=True,
    )
    glass_chatter = fields.Selection(
        [("right", "Right of the form"), ("bottom", "Below the form")],
        string="Chatter position",
        default="right",
        user_writeable=True,
    )
    # phones only: the Apps · Menu · Activity · Account tab bar while a record's form is open
    glass_m_tabbar = fields.Selection(
        [("keep", "Kept under the record's actions"), ("hide", "Hidden while a record is open")],
        string="Phone: tab bar on a record",
        default="keep",
        help="On a phone, a record's form has its own bar of actions at the bottom. Keep the "
             "app tab bar under it (two bars), or hide the tab bar while a record is open — "
             "the Back key returns to the list, like a mail app.",
        user_writeable=True,
    )

    def _glass_prefs(self):
        """Preferences as sent to the web client (session_info)."""
        self.ensure_one()
        return {
            "nav": self.glass_nav or "top",
            "split": bool(self.glass_split),
            "split_side": self.glass_split_side or "right",
            "split_chatter": self.glass_split_chatter or "float",
            "chatter": self.glass_chatter or "right",
            "m_tabbar": self.glass_m_tabbar or "keep",
        }
