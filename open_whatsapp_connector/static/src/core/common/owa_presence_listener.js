import { registry } from "@web/core/registry";

/**
 * Phase B3 — pipes `owa_presence` bus events into the DiscussChannel model so
 * the sidebar/header can show an online dot. Backend emits one event per chat
 * with `{ channel_id, typing, online }` payload; we mirror them onto the
 * matching channel record's transient flags. (Odoo 20: channels are
 * DiscussChannel records, no longer Thread.)
 */
export const owaPresenceListenerService = {
    dependencies: ["bus_service", "mail.store"],
    start(env, { bus_service, "mail.store": store }) {
        bus_service.subscribe("owa_presence", (payload) => {
            if (!payload?.channel_id) {
                return;
            }
            const channel = store["discuss.channel"].get(payload.channel_id);
            if (!channel) {
                return;
            }
            channel.owaOnline = !!payload.online;
            channel.owaTyping = !!payload.typing;
        });
        bus_service.start();
    },
};

registry.category("services").add("owa.presence_listener", owaPresenceListenerService);
