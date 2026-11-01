#!/usr/bin/env python3
"""Convert publications.bib to _pub-entries.html for Quarto include.

Runs automatically before each render (see pre-render in _quarto.yml).
Handles standard well-formed BibTeX. No dependencies.
Routine use: append an entry to publications.bib, commit, push.

Optional custom BibTeX fields on any entry — rendered as link buttons
under each entry: pdf, code, data.
"""
import re
import sys
from html import escape
from pathlib import Path

BIB = Path(__file__).parent.parent / "publications.bib"
OUT = Path(__file__).parent.parent / "_pub-entries.html"

MONTHS = {m: i for i, m in enumerate(
    "jan feb mar apr may jun jul aug sep oct nov dec".split(), 1)}


def parse_entries(text):
    """Yield dicts of fields for each @entry{...} block."""
    for m in re.finditer(r"@(\w+)\s*\{", text):
        if m.group(1).lower() in ("comment", "string", "preamble"):
            continue
        depth, i = 1, m.end()
        while i < len(text) and depth:
            depth += {"{": 1, "}": -1}.get(text[i], 0)
            i += 1
        body = text[m.end():i - 1]
        key, _, fields_src = body.partition(",")
        fields = {"_key": key.strip(), "_type": m.group(1).lower()}
        for fm in re.finditer(
                r'(\w+)\s*=\s*(\{(?:[^{}]|\{[^{}]*\})*\}|"[^"]*"|\w+)',
                fields_src):
            val = fm.group(2).strip().strip('{}"')
            fields[fm.group(1).lower()] = re.sub(r"\s+", " ", val)
        yield fields


def authors(field):
    """'Doe, Jane and Roe, Richard' -> 'Jane Doe, Richard Roe'."""
    names = []
    for a in field.split(" and "):
        a = a.strip()
        if a.startswith("{"):
            continue
        last, _, first = a.partition(",")
        names.append(f"{first.strip()} {last.strip()}".strip())
    return ", ".join(names)


def strip_braces(s):
    return re.sub(r"\{([^{}]*)\}", r"\1", s)


def sort_key(e):
    year = int(e.get("year", "1900"))
    month = MONTHS.get(e.get("month", "jan")[:3].lower(), 1)
    return (-year, -month)


def main():
    entries = sorted(parse_entries(BIB.read_text(encoding="utf-8")),
                     key=sort_key)
    parts = []
    current_year = None
    for e in entries:
        # One <section> per year so the page can show the year beside its entries
        if e.get("year", "") != current_year:
            if current_year is not None:
                parts.append("</section>")
            current_year = e.get("year", "")
            y = escape(current_year)
            parts.append(f'<section class="level2 pub-year">\n<h2 id="y{y}">{y}</h2>')
        title = escape(strip_braces(e.get("title", e["_key"])))
        author = escape(authors(e.get("author", "")))
        venue = escape(e.get("journal") or e.get("booktitle") or "")
        note = escape(e["note"]) if "note" in e else ""
        url = e.get("url") or (
            f"https://doi.org/{e['doi']}" if "doi" in e else "")

        if url:
            title_html = f'<a href="{escape(url)}">{title}</a>'
        else:
            title_html = title

        # Own name in bold; add any new spelling of it here
        author = re.sub(r"(Katherine M(?:argret)? Kennedy|K M Kennedy)",
                        r"<strong>\1</strong>", author)
        meta = f"<em>{venue}</em>" + (f". {note}" if note else "")

        links = []
        for label, field in [("PDF", "pdf"), ("Code", "code"), ("Data", "data")]:
            if field in e:
                links.append(f'<a class="pub-btn" href="{escape(e[field])}">{label}</a>')

        html = (f'<div class="pub-item">\n  <p class="pub-title">{title_html}</p>'
                f'\n  <p class="pub-authors">{author}</p>'
                f'\n  <p class="pub-venue">{meta}</p>')
        if links:
            html += f'\n  <p class="pub-links">{"".join(links)}</p>'
        html += "\n</div>"
        parts.append(html)

    if current_year is not None:
        parts.append("</section>")
    OUT.write_text("\n".join(parts) + "\n", encoding="utf-8")
    print(f"bib_to_html: wrote {len(entries)} entries to {OUT.name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
