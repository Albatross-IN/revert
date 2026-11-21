# Give the present users their Revert roles (docs/implementation_plan_r1.md, P1).
#
#   tools/dev.sh shell < tools/assign_roles.py            dry run: shows what would change
#   APPLY=1 tools/dev.sh shell < tools/assign_roles.py    writes and commits
#
# Users differ per database, so this is a script and not a data file. People are
# matched by the name on their user record (case and extra spaces ignored).
# Roles: owner, principal, designer, coordinator. A person may hold several.
import os

ROLES = {
    "Pratik Anavadiya": ["owner", "principal"],
    "Parija": ["owner"],
    "Harshal Sharma": ["coordinator"],
    "Hitesh Mevada": ["designer"],
    "Arpita Amin": ["designer"],
    "Harsha Mahawar": ["designer"],
    "Kishan": ["designer"],
    "Ruchit Shah": ["designer"],
    "Akshay Oda": ["designer"],
}

apply = os.environ.get("APPLY") == "1"
norm = lambda s: " ".join((s or "").lower().split())
users = env["res.users"].search([("share", "=", False)])  # noqa: F821  (env comes from the shell)
by_name = {norm(u.name): u for u in users}
print("%-22s %-28s %s" % ("person", "now", "after"))
missing = []
for name, roles in ROLES.items():
    user = by_name.get(norm(name))
    if not user:
        missing.append(name)
        continue
    before = user.rvt_roles()
    if apply:
        user.rvt_set_roles(roles)
        after = user.rvt_roles()
    else:
        after = sorted(roles, key=["owner", "principal", "designer", "coordinator"].index)
    print("%-22s %-28s %s" % (name, ", ".join(before) or "-", ", ".join(after) or "-"))
for name in missing:
    print("NOT FOUND: %s (no internal user with this name)" % name)
others = [u.name for u in users if norm(u.name) not in {norm(n) for n in ROLES} and not u.rvt_roles()]
if others:
    print("No role (unchanged): %s" % ", ".join(others))
if apply:
    env.cr.commit()  # noqa: F821
    print("Roles written.")
else:
    print("Dry run. Set APPLY=1 to write.")
