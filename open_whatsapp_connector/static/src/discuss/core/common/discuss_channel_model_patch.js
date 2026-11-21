import { fields } from "@mail/model/export";
import { DiscussChannel } from "@mail/discuss/core/common/discuss_channel_model";
import { patch } from "@web/core/utils/patch";
import { deserializeDateTime } from "@web/core/l10n/dates";

import { toRaw } from "@odoo/owl";

// Odoo 20 port: channel-level state moved from the Thread record to the
// DiscussChannel record (which no longer extends Thread), so every WhatsApp
// channel field/getter the connector used to patch onto Thread lives here now.
/** @type {import("models").DiscussChannel} */
const discussChannelPatch = {
    setup() {
        super.setup(...arguments);
        this.owa_account_id = fields.One("owa.account");
        this.whatsapp_partner_id = fields.One("res.partner");
        // Own name: the official WhatsApp app defines `whatsappMember` as a
        // computed; two definitions of one name leave a raw marker behind
        // (member.channel_id.whatsappMember.eq is not a function). (#meta-coexist)
        this.owaWhatsappMember = fields.One("discuss.channel.member", {
            /** @this {import("models").DiscussChannel} */
            compute() {
                return (
                    this.channel_type === "whatsapp" &&
                    this.channel_member_ids.find((member) =>
                        member.partner_id?.eq(this.whatsapp_partner_id)
                    )
                );
            },
        });
        // Phase B3 — transient presence flags driven by the `owa_presence`
        // bus event. Not persisted; cleared on reload.
        this.owaOnline = false;
        this.owaTyping = false;
        // Conversation type (dm/group/community/channel) for the WhatsApp
        // messaging-menu tab filters; populated from _store_channel_fields.
        this.whatsapp_kind = "";
    },
    get importantCounter() {
        if (this.channel_type === "whatsapp") {
            return this.self_member_id?.message_unread_counter || this.message_needaction_counter;
        }
        return super.importantCounter;
    },
    get autoOpenChatWindowOnNewMessage() {
        return this.channel_type === "whatsapp" || super.autoOpenChatWindowOnNewMessage;
    },
    showThreadIcon(...args) {
        return this.channel_type === "whatsapp" || super.showThreadIcon(...args);
    },
    get avatarUrl() {
        if (this.channel_type === "whatsapp" && this.correspondent?.persona?.avatarUrl) {
            return this.correspondent.persona.avatarUrl;
        }
        return super.avatarUrl;
    },
    get isChatChannel() {
        return this.channel_type === "whatsapp" || super.isChatChannel;
    },
    get hasMemberList() {
        return this.channel_type === "whatsapp" || super.hasMemberList;
    },
    get computedDisplayName() {
        // WhatsApp-Web-style naming for the Discuss sidebar/header: prefer the
        // contact's name when it is a *real* name — either set manually in
        // Contacts or the WhatsApp display name (pushName) captured on inbound.
        // A name made up of only phone characters is treated as "no real name
        // yet", so we fall back to the default (the bare number on the channel).
        if (this.channel_type === "whatsapp") {
            const partnerName = this.whatsapp_partner_id?.name;
            if (partnerName && !/^[\d\s()+.\-]*$/.test(partnerName)) {
                return partnerName;
            }
        }
        return super.computedDisplayName;
    },
    get whatsappChannelValidUntilDatetime() {
        if (!this.whatsapp_channel_valid_until) {
            return undefined;
        }
        return toRaw(deserializeDateTime(this.whatsapp_channel_valid_until));
    },
};
patch(DiscussChannel.prototype, discussChannelPatch);
