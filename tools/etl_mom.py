# Move the earlier MOM entries into points and visits (docs/implementation_plan_r1.md, P5).
#
#   tools/dev.sh shell < tools/etl_mom.py                    dry run: what is there, what would move
#   APPLY=1 tools/dev.sh shell < tools/etl_mom.py            move, verify, commit
#   MAP=people.csv APPLY=1 tools/dev.sh shell < tools/etl_mom.py
#   SWITCH_OFF=1 tools/dev.sh shell < tools/etl_mom.py       after the owner's sign-off: earlier MOM screens off
#
# MAP is the sheet Revert fills in, one row per person named in the earlier entries, with the
# columns: person, kind (agency / client / staff / vendor), agency, trade, phone, same_as.
# Without it every person is kept as a vendor contact and listed below for the sheet.
# A second run moves nothing. The earlier entries themselves are never changed.
# The report is also written beside this script as etl_mom_report.txt (not for git: it names people).
import csv
import os

apply = os.environ.get("APPLY") == "1"
rows = None
if os.environ.get("MAP"):
    with open(os.environ["MAP"], newline="", encoding="utf-8-sig") as handle:
        rows = list(csv.DictReader(handle))

Etl = env["rvt.mom.etl"]  # noqa: F821  (env comes from the shell)
out = []
say = out.append
if os.environ.get("SWITCH_OFF") == "1":
    for line in Etl.switch_off_earlier_screens():
        say(line)
    env.cr.commit()  # noqa: F821
    say("Earlier MOM screens are off. The earlier records are untouched.")
else:
    report = Etl.run(apply=apply, mapping_rows=rows)
    say("Earlier MOM entries: %(source_entries)s · already moved: %(already_moved)s · to move: %(to_move)s · moved now: %(created)s" % report)
    say("Without a project (left where they are): %(without_project)s · without a person: %(without_person)s" % report)
    say("")
    say("%-44s %8s %6s %7s %7s %7s   %s" % ("project", "entries", "open", "closed", "photos", "visits", "check"))
    for row in report["projects"]:
        after = row["after"]
        check = "-" if row["equal"] is None else ("equal" if row["equal"] else "DIFFERENT")
        say("%-44s %8s %6s %7s %7s %7s   %s" % (row["project"][:44], row["entries"], row["open"], row["closed"], row["photos"], row["visits"], check))
        if after and not row["equal"]:
            say("%-44s %8s %6s %7s %7s %7s" % ("   after the move", after["entries"], after["open"], after["closed"], after["photos"], after["visits"]))
    say("")
    if report["projects"] and report["projects"][0]["equal"] is not None:
        say("ALL EQUAL: every project has the same entries, open, closed, photos (by checksum), visits and visit numbers."
            if report["all_equal"] else "NOT EQUAL: see the rows marked DIFFERENT. Nothing is committed.")
    say("People named in the entries: %s" % len(report["people"]))
    if report["unmapped"]:
        say("Not on the sheet (kept as vendor contacts), with their number of entries:")
        for name, count in report["unmapped"]:
            say("   %-40s %s" % (name, count))
    if apply and report["all_equal"]:
        env.cr.commit()  # noqa: F821
        say("Committed.")
    elif apply:
        env.cr.rollback()  # noqa: F821
        say("Rolled back.")
    else:
        say("Dry run. Set APPLY=1 to move.")
text = "\n".join(out)
print(text)
try:
    with open(os.path.join(os.getcwd(), "tools", "etl_mom_report.txt"), "w", encoding="utf-8") as handle:
        handle.write(text + "\n")
except OSError:
    pass
