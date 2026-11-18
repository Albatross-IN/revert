/** @odoo-module **/
// Glass Workspace — floating chatter: one reactive store shared by the window, the buttons
// (form control panel, kanban cards, list rows) and the split panel.
//
// Nothing here talks to the chatter itself: the window renders Odoo's OWN `Chatter`
// component for (resModel, resId). This store only says WHICH record to show and HOW
// (desktop window / phone mini window / full sheet / bubble), and remembers geometry.
import { proxy } from "@odoo/owl";
import { browser } from "@web/core/browser/browser";

const GEOM_KEY = "glass.chatter.geom";

function loadGeom() {
    try {
        return JSON.parse(browser.localStorage.getItem(GEOM_KEY) || "{}") || {};
    } catch {
        return {};
    }
}

export const chatterStore = proxy({
    // the record whose chatter is shown
    resModel: null,
    resId: null,
    displayName: "",
    hasActivities: true,
    open: false,
    // "split" (desktop split panel), "form" (phone form button), "card" (kanban / list button)
    source: null,
    // desktop, split source: the window follows the record selected in the list
    follow: true,
    minimized: false,
    // desktop, split source: the user pressed "Dock" — do not auto-float again this session
    dockedByUser: false,
    // phone: "mini" | "full" | "bubble"
    mode: "mini",
    // the split panel currently on screen (desktop) — { resModel, resId } or null
    split: null,
    // phone, card source: open the record itself (list / kanban controller's openRecord)
    onOpenRecord: null,
    // remembered geometry: { win, mwin, bubble }
    geom: loadGeom(),
});

export function saveGeom() {
    try {
        browser.localStorage.setItem(GEOM_KEY, JSON.stringify(chatterStore.geom));
    } catch {
        // private mode / quota: the position simply does not persist
    }
}

/** Show the chatter of a record. `opts.source` says where it was asked from. */
export function showChatter(resModel, resId, opts = {}) {
    const s = chatterStore;
    const sameRecord = s.resModel === resModel && s.resId === resId;
    s.resModel = resModel;
    s.resId = resId;
    if (!sameRecord) {
        s.displayName = "";
    }
    s.hasActivities = opts.hasActivities !== undefined ? !!opts.hasActivities : s.hasActivities;
    s.source = opts.source || s.source || "card";
    s.onOpenRecord = opts.onOpenRecord || null;
    if (opts.mode) {
        s.mode = opts.mode;
    } else if (s.mode === "bubble" && !opts.keepMode) {
        s.mode = "mini";
    }
    s.minimized = false;
    s.open = true;
}

export function hideChatter() {
    const s = chatterStore;
    s.open = false;
    s.onOpenRecord = null;
}

export function isChatterShown(resModel, resId) {
    const s = chatterStore;
    return s.open && s.resModel === resModel && s.resId === resId;
}

// ---------------------------------------------------------------------------------------
// Which models have a chatter? Answered once per model with a tiny `fields_get` and cached:
// a model gets the buttons only when it really inherits mail.thread (custom modules
// included), and the "Activities" part only with mail.activity.mixin.
// ---------------------------------------------------------------------------------------
export const chatterCaps = proxy({});
const capPending = new Map();

export function chatterCapability(orm, resModel) {
    if (!resModel) {
        return null;
    }
    const known = chatterCaps[resModel];
    if (known !== undefined) {
        return known;
    }
    if (!capPending.has(resModel)) {
        capPending.set(
            resModel,
            orm
                .call(resModel, "fields_get", [["message_ids", "activity_ids"], ["type"]])
                .then(async (fields) => {
                    let thread = "message_ids" in fields;
                    if (thread) {
                        // `message_ids` alone is not enough: res.users (and a few others) expose the
                        // fields without being a mail.thread and Odoo's chatter controllers reject
                        // them (/mail/data → AttributeError). Only models whose form view really
                        // carries a <chatter/> get the floating chatter (QA BUG-0019).
                        const views = await orm.call(resModel, "get_views", [[[false, "form"]]], {
                            options: { load_filters: false },
                        });
                        const arch = (views && views.views && views.views.form && views.views.form.arch) || "";
                        thread = /<chatter[\s/>]|oe_chatter|o-mail-Form-chatter/.test(arch);
                    }
                    chatterCaps[resModel] = {
                        thread,
                        activities: thread && "activity_ids" in fields,
                    };
                })
                .catch(() => {
                    chatterCaps[resModel] = { thread: false, activities: false };
                })
                .finally(() => capPending.delete(resModel))
        );
    }
    return null; // unknown yet — components re-render when chatterCaps gets the answer
}

/** Same, as a promise (for the split panel which must wait before auto-floating). */
export async function ensureChatterCapability(orm, resModel) {
    const known = chatterCapability(orm, resModel);
    if (known) {
        return known;
    }
    await capPending.get(resModel);
    return chatterCaps[resModel] || { thread: false, activities: false };
}

// ---------------------------------------------------------------------------------------
// Message counts for the badges (kanban cards / list rows / form button): one batched
// `mail.message` read_group per model per render, cached for a minute. Purely cosmetic —
// any failure just means "no badge".
// ---------------------------------------------------------------------------------------
export const chatterCounts = proxy({});
const countPending = new Map(); // model -> Set(ids) waiting for the next flush
const countFetchedAt = new Map(); // `${model}/${id}` -> timestamp
let countTimer = null;
let countsDisabled = false;
const COUNT_TTL = 60 * 1000;

export function requestCount(orm, resModel, resId) {
    if (countsDisabled || !resModel || !resId) {
        return;
    }
    const key = `${resModel}/${resId}`;
    const at = countFetchedAt.get(key);
    if (at && Date.now() - at < COUNT_TTL) {
        return;
    }
    countFetchedAt.set(key, Date.now()); // mark now so a re-render does not re-queue it
    if (!countPending.has(resModel)) {
        countPending.set(resModel, new Set());
    }
    countPending.get(resModel).add(resId);
    if (!countTimer) {
        countTimer = browser.setTimeout(() => flushCounts(orm), 60);
    }
}

async function flushCounts(orm) {
    countTimer = null;
    const batches = [...countPending.entries()];
    countPending.clear();
    for (const [resModel, ids] of batches) {
        const idList = [...ids];
        try {
            const rows = await orm.formattedReadGroup(
                "mail.message",
                [
                    ["model", "=", resModel],
                    ["res_id", "in", idList],
                    ["message_type", "in", ["comment", "email"]],
                ],
                ["res_id"],
                ["__count"]
            );
            const byId = chatterCounts[resModel] ? { ...chatterCounts[resModel] } : {};
            for (const id of idList) {
                byId[id] = 0;
            }
            for (const row of rows) {
                byId[row.res_id] = row.__count;
            }
            chatterCounts[resModel] = byId;
        } catch {
            // access rules or an unexpected model: badges off for this session, buttons stay
            countsDisabled = true;
        }
    }
}

/** Bump a record's badge when a message is posted from the window (no refetch needed). */
export function forgetCount(resModel, resId) {
    countFetchedAt.delete(`${resModel}/${resId}`);
}
