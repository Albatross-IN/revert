#!/usr/bin/env python3
"""Turn the one-page guides (docs/guides/*.md) into A4 PDFs, one page each.

    python3 tools/guides_pdf.py [output folder, default docs/guides/pdf]

Needs Google Chrome on the machine (it prints the page); the Gujarati and Hindi pages use the
Noto fonts of the system. Run it again after the wording has been corrected.
"""
import html
import pathlib
import re
import subprocess
import sys
import tempfile

REPO = pathlib.Path(__file__).resolve().parent.parent
GUIDES = REPO / "docs" / "guides"

PAGE = """<!doctype html><html lang="%(lang)s"><head><meta charset="utf-8"><style>
@page{size:A4;margin:0}
*{box-sizing:border-box}
body{margin:0;font:%(size)spx/1.55 "Plus Jakarta Sans","Noto Sans Gujarati","Noto Sans Devanagari","Noto Sans",sans-serif;color:#1B2233}
.sheet{width:210mm;min-height:296mm;padding:15mm 16mm 16mm;position:relative}
.band{position:absolute;left:0;right:0;top:0;height:7mm;background:#0D1426}
.band i{position:absolute;left:16mm;right:16mm;bottom:0;height:.6mm;background:#D9A441}
h1{font-size:1.7em;line-height:1.25;margin:6mm 0 3mm;color:#0D1426;letter-spacing:-.2px}
h2{font-size:1.1em;margin:5.5mm 0 2mm;color:#0D1426;padding-bottom:1mm;border-bottom:.3mm solid #E8DFCC}
p{margin:0 0 2mm}
ul,ol{margin:0 0 1mm;padding-left:5.5mm}
li{margin:0 0 1.2mm}
b{color:#0D1426}
.foot{position:absolute;left:16mm;right:16mm;bottom:8mm;font-size:10px;color:#8A8F9C;display:flex;justify-content:space-between;border-top:.3mm solid #E8DFCC;padding-top:2mm}
</style></head><body><div class="sheet"><div class="band"><i></i></div>%(body)s<div class="foot"><span>Revert Architects · Ahmedabad</span><span>%(name)s</span></div></div></body></html>"""


def inline(text):
    text = html.escape(text, quote=False)
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
    return re.sub(r"\*(.+?)\*", r"<i>\1</i>", text)


def to_html(markdown):
    out, kind = [], None

    def close():
        nonlocal kind
        if kind:
            out.append("</%s>" % kind)
            kind = None

    lines = markdown.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i].rstrip()
        # a paragraph or a list item runs on to the next line until an empty line, a heading or a new item
        while i + 1 < len(lines) and lines[i + 1].strip() and not re.match(r"^(#{1,2} |- |\d+\. )", lines[i + 1]) and not line.startswith("#"):
            line += " " + lines[i + 1].strip()
            i += 1
        i += 1
        if not line.strip():
            close()
            continue
        match = re.match(r"^(#{1,2}) (.+)$", line)
        if match:
            close()
            out.append("<h%s>%s</h%s>" % (len(match.group(1)), inline(match.group(2)), len(match.group(1))))
            continue
        match = re.match(r"^(-|\d+\.) (.+)$", line)
        if match:
            want = "ul" if match.group(1) == "-" else "ol"
            if kind != want:
                close()
                out.append("<%s>" % want)
                kind = want
            out.append("<li>%s</li>" % inline(match.group(2)))
            continue
        close()
        out.append("<p>%s</p>" % inline(line))
    close()
    return "\n".join(out)


def pages(pdf):
    """Pages of a PDF, counted from the file itself."""
    return len(re.findall(rb"/Type\s*/Page[^s]", pdf.read_bytes()))


def main():
    target = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else GUIDES / "pdf"
    target.mkdir(parents=True, exist_ok=True)
    chrome = next((c for c in ("google-chrome", "chromium", "chromium-browser") if subprocess.run(["which", c], capture_output=True).returncode == 0), None)
    if not chrome:
        sys.exit("Google Chrome is needed to print the pages.")
    for source in sorted(GUIDES.glob("*.md")):
        lang = source.stem.rsplit("_", 1)[-1]
        body = to_html(source.read_text())
        out = target / ("Revert_guide_%s.pdf" % source.stem)
        # the largest type that keeps the guide on one page
        for size in (15.4, 14.6, 13.8, 13.0, 12.2, 11.4):
            page = PAGE % {"lang": lang, "size": size, "body": body, "name": source.stem.replace("_", " · ")}
            with tempfile.TemporaryDirectory() as folder:
                page_file = pathlib.Path(folder) / "page.html"
                page_file.write_text(page)
                subprocess.run([chrome, "--headless=new", "--disable-gpu", "--no-pdf-header-footer", "--user-data-dir=%s/profile" % folder,
                                "--print-to-pdf=%s" % out, page_file.as_uri()], check=True, capture_output=True, timeout=120)
            if pages(out) <= 1:
                break
        print(out.name, "%s px" % size, pages(out), "page")


if __name__ == "__main__":
    main()
