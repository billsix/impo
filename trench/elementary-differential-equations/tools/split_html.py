#!/usr/bin/env python3
r"""Split make4ht's monolithic bookW.html into OpenStax-style chunked pages.

Route (a) of tasks/archive/impo/2026/09/19/trench-differential-equations-html-epub.md. The trench web
edition is compiled by make4ht (a real LaTeX engine via tex4ht) into ONE big
bookW.html carrying tex4ht's own CSS + native MathML. This restyles it to match
the OpenStax family's Furo-like chunked theme WITHOUT re-rendering the math.

**Granularity: ONE PAGE PER CHAPTER** (maintainer's call, 2026-09-19). Trench is
only two levels deep (chapter -> section, monolithic sections), so per-section
pages would leave the right "On this page" bar empty. Splitting per CHAPTER makes
the chapter's `h3.sectionHead` sections the on-page subheadings, so:
  * the LEFT book-TOC (build_nav.py, from sitemap.json) lists the 10 chapters, and
  * the RIGHT "On this page" bar (osbook-web.js, from the page's h3[id]) lists that
    chapter's sections.
That mirrors the OpenStax left=outer / right=inner sidebar gist using trench's real
structure. Front matter (the Preface) is its own page.

For each page this script: promotes the chapter's `h2.chapterHead` (or the front
matter) to `<h1>`, LEAVES the `h3.sectionHead` sections in place (they carry ids,
so osbook-web.js lists them + they deep-link as `chapter.html#section-slug`), wraps
the page in the shared chunked-template layout, and emits `sitemap.json` (chapters
only -- sections are on-page, so the left TOC stays one entry per chapter). tex4ht's
`bookW.css` is kept for content typography; the caller layers osbook-web.css (theme)
+ trench-web.css (adapter). MathML is untouched. build_nav.py + osbook-web.js are
reused unchanged.

Run (from build_web.sh, after make4ht; paths relative to cwd):
  python3 tools/split_html.py bookW.html output/html \
      --title "Elementary Differential Equations" --subtitle "Formatted by Bill Six"
"""
from __future__ import annotations

import argparse
import html as htmlmod
import json
import re
from pathlib import Path

# make4ht/tex4ht heading markup. Chapters split the book; sections stay ON the
# chapter page as its subheadings (the right "On this page" bar reads them).
CHAPTER: re.Pattern[str] = re.compile(r"<h2\b([^>]*)>(.*?)</h2>", re.DOTALL)
ID_RE: re.Pattern[str] = re.compile(r"id='([^']*)'")
TAG_RE: re.Pattern[str] = re.compile(r"<[^>]+>")
# The centered "Preface" banner tex4ht emits for the front matter -- dropped
# because split_html promotes it to the page's own <h1>.
FRONT_BANNER: re.Pattern[str] = re.compile(
    r"^\s*<div class='centerline'>\s*<span[^>]*>\s*Preface\s*</span>\s*</div>",
    re.IGNORECASE,
)


class Page:
    """One output page: the front matter, or a whole chapter (with its sections)."""

    def __init__(
        self, *, pid: str, number: str, title: str, body: str, is_front: bool = False
    ) -> None:
        self.pid: str = pid              # anchor id (a clean slug from tex4ht)
        self.number: str = number        # "0.1" (front) / "1".."10" (chapter)
        self.title: str = title          # heading text, number stripped
        self.body: str = body            # inner content HTML (chapter heading removed,
        #                                  the h3.sectionHead sections left intact)
        self.is_front: bool = is_front
        self.filename: str = ""          # assigned in document order: "NNN-slug.html"


def clean_text(inner: str) -> str:
    """Strip inner tags + collapse whitespace from a heading's inner HTML."""
    return re.sub(r"\s+", " ", TAG_RE.sub("", inner)).strip()


def parse_chapter(text: str) -> tuple[str, str]:
    """(number, title) from a chapter heading: 'Chapter 2  Introduction' ->
    ('2', 'Introduction'). Falls back to ('', text) if the prefix is absent."""
    m: re.Match[str] | None = re.match(r"Chapter\s+(\S+)\s+(.*)", text)
    if m is None:
        return "", text
    return m.group(1), m.group(2).strip()


def split_pages(body: str) -> list[Page]:
    """Cut the tex4ht <body> content into ordered pages at CHAPTER boundaries."""
    chapters: list[re.Match[str]] = list(CHAPTER.finditer(body))
    pages: list[Page] = []

    # Front matter: everything before the first chapter (the Preface).
    first: int = chapters[0].start() if chapters else len(body)
    front_body: str = FRONT_BANNER.sub("", body[:first]).strip()
    if front_body:
        pages.append(
            Page(pid="preface", number="0.1", title="Preface", body=front_body, is_front=True)
        )

    for i, m in enumerate(chapters):
        attrs: str = m.group(1)
        id_m: re.Match[str] | None = ID_RE.search(attrs)
        pid: str = id_m.group(1) if id_m else f"chapter{i}"
        number: str
        title: str
        number, title = parse_chapter(clean_text(m.group(2)))
        end: int = chapters[i + 1].start() if i + 1 < len(chapters) else len(body)
        # Everything after this chapter's heading up to the next chapter -- INCLUDING
        # the chapter's h3.sectionHead sections, kept in place as the page subheadings.
        seg: str = body[m.end():end].strip()
        pages.append(Page(pid=pid, number=number, title=title, body=seg))

    for n, pg in enumerate(pages, start=1):
        pg.filename = f"{n:03d}-{pg.pid}.html"
    return pages


def build_sitemap(pages: list[Page], book_title: str) -> dict:
    """Flat chapter list (+ front) under the book root -- the left TOC has one entry
    per page; sections are on-page (right bar), so they are NOT sitemap nodes."""
    root: dict = {
        "section": {"id": "", "level": "0", "number": None,
                    "path": "index.html", "title": book_title},
        "subsections": [],
    }
    for pg in pages:
        root["subsections"].append({
            "section": {
                "id": pg.pid,
                "level": "2",
                "number": pg.number,
                "path": f"{pg.filename}#{pg.pid}",
                "title": pg.title,
            },
            "subsections": [],
        })
    return root


def render_breadcrumb(book_title: str) -> str:
    """Every page sits directly under the book (no section-level pages)."""
    return (
        '    <div class="breadcrumb">\n'
        '      <a href="index.html" accesskey="t" rel="top">%s</a>\n'
        "    </div>" % htmlmod.escape(book_title)
    )


def render_prevnext(prev: Page | None, nxt: Page | None) -> str:
    """The big Prev/Next footer buttons (osbook .prevnext)."""
    out: list[str] = ['    <nav class="prevnext" aria-label="Chapter navigation">']
    if prev is not None:
        out.append(
            '      <a class="pn prev" href="%s" accesskey="p" rel="previous">'
            '<span class="pn-dir">← Previous</span>'
            '<span class="pn-title">%s</span></a>'
            % (prev.filename, htmlmod.escape(prev.title))
        )
    else:
        out.append('      <span class="pn placeholder"></span>')
    if nxt is not None:
        out.append(
            '      <a class="pn next" href="%s" accesskey="n" rel="next">'
            '<span class="pn-dir">Next →</span>'
            '<span class="pn-title">%s</span></a>'
            % (nxt.filename, htmlmod.escape(nxt.title))
        )
    else:
        out.append('      <span class="pn placeholder"></span>')
    out.append("    </nav>")
    return "\n".join(out)


def page_shell(*, title_tag: str, book_title: str, inner: str) -> str:
    """Wrap a page's <main> inner HTML in the full chunked-template layout."""
    return (
        "<!DOCTYPE html>\n"
        '<html lang="en" xml:lang="en">\n<head>\n'
        '  <meta charset="utf-8" />\n'
        '  <meta name="viewport" content="width=device-width, initial-scale=1.0,'
        ' user-scalable=yes" />\n'
        f"  <title>{title_tag} – {htmlmod.escape(book_title)}</title>\n"
        '  <link rel="stylesheet" href="bookW.css" />\n'
        '  <link rel="stylesheet" href="osbook-web.css" />\n'
        '  <link rel="stylesheet" href="trench-web.css" />\n'
        "</head>\n<body>\n"
        '<div class="layout">\n'
        '  <button id="nav-toggle" class="nav-toggle" aria-label="Toggle chapter'
        ' list">☰ Chapters</button>\n'
        '  <nav class="book-toc" id="book-toc" aria-label="Book contents">'
        "<!--BOOK-TOC--></nav>\n"
        '  <main class="content">\n'
        f"{inner}\n"
        "  </main>\n"
        '  <nav class="page-toc" id="page-toc" aria-label="On this page"></nav>\n'
        "</div>\n"
        '<div class="nav-scrim" id="nav-scrim"></div>\n'
        '<script src="osbook-web.js"></script>\n'
        "</body>\n</html>\n"
    )


def render_page(pg: Page, prev: Page | None, nxt: Page | None, book_title: str) -> str:
    """A content page (front matter or a chapter). The chapter's h3.sectionHead
    sections are already in pg.body; osbook-web.js turns them into the right bar."""
    num: str = "" if pg.is_front else htmlmod.escape(pg.number)
    heading: str = '    <h1%s id="%s">%s</h1>' % (
        f' data-number="{num}"' if num else "",
        htmlmod.escape(pg.pid),
        htmlmod.escape(pg.title),
    )
    inner: str = "\n".join(
        [render_breadcrumb(book_title), heading, pg.body, render_prevnext(prev, nxt)]
    )
    return page_shell(title_tag=htmlmod.escape(pg.title), book_title=book_title, inner=inner)


def render_index(pages: list[Page], book_title: str, subtitle: str) -> str:
    """The landing page: title, subtitle, license note, and a Start link. The full
    contents arrive in the left sidebar via build_nav.py."""
    first: Page | None = pages[0] if pages else None
    start: str = (
        '    <p><a class="pn next" href="%s"><span class="pn-dir">Start →</span>'
        '<span class="pn-title">%s</span></a></p>'
        % (first.filename, htmlmod.escape(first.title))
        if first is not None
        else ""
    )
    inner: str = (
        '    <header id="title-block-header">\n'
        f'      <h1 class="title">{htmlmod.escape(book_title)}</h1>\n'
        f'      <p class="subtitle">{htmlmod.escape(subtitle)}</p>\n'
        "    </header>\n"
        "    <p>William F. Trench’s <em>Elementary Differential Equations</em>, "
        "restyled in the OpenStax house look. The complete table of contents is in "
        "the sidebar.</p>\n"
        f"{start}\n"
        '    <p style="font-size:.85rem;color:#555;margin-top:2rem">Licensed '
        "under the Creative Commons Attribution-NonCommercial-ShareAlike 3.0 "
        "Unported License (CC BY-NC-SA 3.0). © William F. Trench.</p>"
    )
    return page_shell(title_tag=htmlmod.escape(book_title), book_title=book_title, inner=inner)


def main() -> None:
    ap: argparse.ArgumentParser = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("source", help="make4ht monolithic HTML (bookW.html)")
    ap.add_argument("outdir", help="output site directory")
    ap.add_argument("--title", default="Elementary Differential Equations")
    ap.add_argument("--subtitle", default="Formatted by Bill Six")
    a: argparse.Namespace = ap.parse_args()

    doc: str = Path(a.source).read_text(encoding="utf-8")
    bstart: int = doc.index("<body>") + len("<body>")
    bend: int = doc.rindex("</body>")
    body: str = doc[bstart:bend]

    pages: list[Page] = split_pages(body)
    if not pages:
        raise SystemExit("split_html: no chapter headings found")

    out: Path = Path(a.outdir)
    out.mkdir(parents=True, exist_ok=True)

    for idx, pg in enumerate(pages):
        prev: Page | None = pages[idx - 1] if idx > 0 else None
        nxt: Page | None = pages[idx + 1] if idx + 1 < len(pages) else None
        (out / pg.filename).write_text(
            render_page(pg, prev, nxt, a.title), encoding="utf-8"
        )

    (out / "index.html").write_text(render_index(pages, a.title, a.subtitle), encoding="utf-8")
    (out / "sitemap.json").write_text(
        json.dumps(build_sitemap(pages, a.title), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"split_html: wrote index.html + {len(pages)} pages (per chapter) + sitemap.json to {out}")


if __name__ == "__main__":
    main()
