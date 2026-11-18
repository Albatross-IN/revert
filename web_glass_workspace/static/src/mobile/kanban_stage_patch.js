/** @odoo-module **/
// Mobile stage picker — the production-grade half. Patches the Kanban controller so that, on a
// phone, a single-groupby grouped kanban publishes its stages (with REAL server totals) to the
// stageStore and exposes apply(). apply() adds a real search-domain facet on the group-by field
// (via searchModel.splitAndAddDomain) so Odoo re-queries and loads ONLY the chosen stage's
// records, ANDed with the view's default domain and any custom filters. Picking "All" removes
// just our facet. Desktop is untouched (everything is gated on ui.isSmall).
import { KanbanController } from "@web/views/kanban/kanban_controller";
import { patch } from "@web/core/utils/patch";
import { onMounted, onPatched, onWillUnmount } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { stageStore } from "./stage_store";

let ownerSeq = 0;

patch(KanbanController.prototype, {
    setup() {
        super.setup();
        this.glassUi = useService("ui");
        // who publishes: a plain token, never the controller itself — the store is a proxy, and
        // an object read back from it is a proxy of that object (never === the controller)
        this._glassOwner = ++ownerSeq;
        this._glassGid = null; // groupId of the facet we added (to remove it later)
        this._glassSig = "";
        // after every render, never during one (the store is read by the shell's own render)
        onMounted(() => this.glassPublishStages());
        onPatched(() => this.glassPublishStages());
        onWillUnmount(() => {
            if (stageStore.owner === this._glassOwner) {
                stageStore.reset();
            }
        });
    },

    glassPublishStages() {
        try {
            this._glassPublishStages();
        } catch {
            // the stage picker must never break a kanban render — fail silently
            if (stageStore.owner === this._glassOwner) {
                stageStore.reset();
            }
        }
    },

    _glassPublishStages() {
        const root = this.model && this.model.root;
        const ok =
            this.glassUi.isSmall &&
            root &&
            root.isGrouped &&
            root.groupByField &&
            (root.groupBy || []).length === 1;
        if (!ok) {
            if (stageStore.owner === this._glassOwner) {
                stageStore.reset();
            }
            return;
        }
        // Write reactive props only when they actually change, so the overlay does not re-render on
        // every kanban render. In particular bind apply() once (a fresh closure would always differ).
        if (stageStore.owner !== this._glassOwner) {
            // a NEW grouped kanban is taking over — start fresh so a stale filter/label from the
            // previous view can never leak in (e.g. CRM's "Won" carrying into Sales)
            stageStore.owner = this._glassOwner;
            stageStore.selected = null;
            stageStore.groups = [];
            this._glassSig = "";
            this._glassGid = null;
        }
        if (!stageStore.active) {
            stageStore.active = true;
        }
        const field = root.groupByField.name;
        if (stageStore.field !== field) {
            stageStore.field = field;
        }
        if (!this._glassApplyBound) {
            this._glassApplyBound = (value) => this.glassApplyStage(value);
        }
        if (stageStore.apply !== this._glassApplyBound) {
            stageStore.apply = this._glassApplyBound;
        }
        // Refresh the full stage list + totals only while unfiltered — once a stage is applied the
        // model holds just that one group, but the picker must still list every stage to switch to.
        if (stageStore.selected === null) {
            const groups = (root.groups || []).map((g) => ({
                label: g.displayName || (g.value === false || g.value === undefined ? "None" : String(g.value)),
                value: g.serverValue,
                count: g.count,
            }));
            const sig = groups.map((s) => `${s.label}:${s.count}`).join("|");
            if (sig !== this._glassSig) {
                this._glassSig = sig;
                stageStore.groups = groups;
            }
        }
    },

    async glassApplyStage(value) {
        const sm = this.env.searchModel;
        if (!sm || !sm.splitAndAddDomain) {
            return;
        }
        // drop the facet we added last time (leave the user's own filters alone)
        if (this._glassGid != null) {
            sm.deactivateGroup(this._glassGid);
            this._glassGid = null;
        }
        stageStore.selected = value === undefined ? null : value;
        if (stageStore.selected !== null) {
            const field = stageStore.field;
            const type = this.model.root.groupByField.type;
            const leaf =
                type === "many2many"
                    ? [field, "in", value ? [value] : false]
                    : [field, "=", value];
            const gid = sm.nextGroupId; // the groupId splitAndAddDomain's new filter will use
            await sm.splitAndAddDomain([leaf]);
            this._glassGid = gid;
        }
    },
});
