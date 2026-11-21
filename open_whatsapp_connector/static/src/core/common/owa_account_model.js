import { Record } from "@mail/model/export";

export class OwaAccount extends Record {
    static id = "id";
    static _name = "owa.account";

    /** @type {number} */
    id;
    /** @type {string} */
    name;
}

OwaAccount.register();
