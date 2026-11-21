#!/usr/bin/env python3
"""Copy the app's built screens into this module, for the page behind the client's link.

    python3 rvt_api/tools/sync_app.py [path to the revert_fe checkout, default ../revert_fe]

The client's link (/rvt/c/<token>) serves the very screens the app shows. They are built in the
app's repository (revert_fe/app: python3 tool/build_web.py) and copied here unchanged; run this
after every build that goes out, and commit the result with the phase it belongs to.
"""
import pathlib
import shutil
import sys

HERE = pathlib.Path(__file__).resolve().parent.parent
REPO = HERE.parent


def main():
    source = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else REPO.parent / "revert_fe"
    built = source / "app" / "assets" / "web"
    target = HERE / "static" / "app"
    target.mkdir(parents=True, exist_ok=True)
    for name in ("app.js", "styles.css"):
        if not (built / name).is_file():
            sys.exit("not found: %s (build the screens first: python3 tool/build_web.py)" % (built / name))
        shutil.copyfile(built / name, target / name)
        print("copied", name, (target / name).stat().st_size // 1024, "KB")


if __name__ == "__main__":
    main()
