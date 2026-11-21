#!/usr/bin/env python3
"""Inject the book's table of contents into each chunked HTML page's left sidebar.

pandoc's chunkedhtml writer emits a `sitemap.json` (the full section tree) beside
the pages, but does NOT put a whole-book TOC on each page. This does: it reads
sitemap.json and writes the nested TOC into every page's `<!--BOOK-TOC-->`
placeholder (left in place by chunked-template.html), marking the links that live
on the current page as active. It also fills the `<!--DOWNLOADS-->` placeholder:
the book's first page (index.html) gets a box linking the PDF, EPUB and zipped
HTML (GitHub Release assets, see DEFAULT_DOWNLOAD_BASE), and every page's
sidebar gets a "Downloads" entry pointing at that box.

Done at BUILD time on purpose: a client-side `fetch('sitemap.json')` is blocked
under `file://` (readers open these locally), so the TOC is baked into each page
instead. Right-sidebar ("On this page") + scrollspy are the browser's job
(osbook-web.js) since those only need the page's own headings.

Usage:  python3 build_nav.py <output-site-dir>   (the dir holding sitemap.json)
"""

from __future__ import annotations

import glob
import html
import json
import os
import sys
from typing import Any, TypeAlias

# A sitemap node is a JSON object parsed from sitemap.json (pandoc's chunkedhtml
# writer output): {"section": {...}, "subsections": [SitemapNode, ...]}. Genuinely
# dynamic JSON, so Any inside the dict rather than a hand-maintained TypedDict.
SitemapNode: TypeAlias = dict[str, Any]

PLACEHOLDER: str = "<!--BOOK-TOC-->"
DOWNLOADS_PLACEHOLDER: str = "<!--DOWNLOADS-->"

# Where the book's PDF / EPUB / zipped-HTML downloads live: the assets of impo's
# newest GitHub Release, which `.github/workflows/release.yml` attaches on a tag
# push as <slug>.pdf, <slug>.epub and <slug>-html.zip. `releases/latest/download/`
# always resolves to the newest release, so the URL stays fixed across releases.
# OSBOOK_DOWNLOAD_BASE overrides it; set it empty to build without downloads.
DEFAULT_DOWNLOAD_BASE: str = "https://github.com/billsix/impo/releases/latest/download"


def render(node: SitemapNode, current_page: str) -> tuple[str, bool]:
    """Render one <li> for a sitemap node; return (html, contains_active).

    A node with children is collapsible: it gets `has-children`, plus `open` when
    it (or a descendant) is on the current page, so the active branch starts
    expanded and everything else collapsed (osbook-web.js toggles the rest).
    """
    s: SitemapNode = node.get("section") or {}
    path: str = s.get("path") or ""
    title: str = s.get("title") or ""
    number: str = s.get("number") or ""
    page: str = path.split("#", 1)[0]
    self_active: bool = bool(page) and page == current_page
    # Front matter is numbered 0.0.x; show it title-only ("Preface"), not
    # "0.0.1 Preface". Chapters/sections keep their number ("1 Levels …").
    label: str
    if number and not number.startswith("0."):
        label = number + "  " + title
    else:
        label = title

    # The left TOC has ONE entry per PAGE. A child that lives on a page already
    # listed here -- the parent's own page (e.g. section 2.1's 2.1.1, 2.1.2 …) or an
    # earlier sibling's page (e.g. the front matter 0.0.1–0.0.7, all on page 001) --
    # is an on-page anchor, so it collapses into that page's single entry and shows
    # only in the right "On this page" sidebar. Recurse only into new pages.
    kids_html: str = ""
    any_active: bool = self_active
    seen_pages: set[str] = {page} if page else set()
    k: SitemapNode
    for k in node.get("subsections") or []:
        k_page: str = ((k.get("section") or {}).get("path") or "").split("#", 1)[0]
        if k_page and k_page in seen_pages:
            continue
        if k_page:
            seen_pages.add(k_page)
        kh: str
        ka: bool
        kh, ka = render(k, current_page)
        kids_html += kh
        any_active = any_active or ka

    has_kids: bool = bool(kids_html)
    li_class: str = ""
    if has_kids:
        li_class = ' class="has-children%s"' % (" open" if any_active else "")
    a_class: str = ' class="active"' if self_active else ""
    li: str = "<li%s>" % li_class
    if has_kids:
        li += '<button class="toc-toggle" aria-label="Expand section"></button>'
    li += '<a href="%s"%s>%s</a>' % (html.escape(path), a_class, html.escape(label))
    if has_kids:
        li += "<ul>%s</ul>" % kids_html
    li += "</li>"
    return li, any_active


def downloads_box(slug: str, base: str) -> str:
    """Return the "Downloads" box for the book's first page (empty without a base).

    >>> "https://h/r/b-html.zip" in downloads_box("b", "https://h/r/")
    True
    >>> downloads_box("b", "")
    ''
    """
    if not base:
        return ""
    root: str = base.rstrip("/")
    links: str = " ".join(
        '<a class="download" href="%s/%s%s">%s</a>'
        % (html.escape(root), html.escape(slug), suffix, label)
        for suffix, label in (
            (".pdf", "PDF"),
            (".epub", "EPUB"),
            ("-html.zip", "HTML (zip, read offline)"),
        )
    )
    return (
        '<aside class="downloads" id="downloads" aria-label="Downloads">'
        "<strong>Download this book:</strong> %s</aside>" % links
    )


def downloads_nav_item(base: str) -> str:
    """Return the side-nav "Downloads" entry (points at the box on index.html)."""
    if not base:
        return ""
    return '<a class="book-downloads" href="index.html#downloads">Downloads</a>'


def main(argv: list[str]) -> int:
    if len(argv) != 1:
        print("usage: build_nav.py <output-site-dir>", file=sys.stderr)
        return 2
    site: str = argv[0]
    smpath: str = os.path.join(site, "sitemap.json")
    if not os.path.exists(smpath):
        print("build_nav: no sitemap.json in %s -- skipping" % site, file=sys.stderr)
        return 0
    with open(smpath, encoding="utf-8") as f:
        sm: SitemapNode = json.load(f)
    chapters: list[SitemapNode] = sm.get("subsections") or []
    book_title: str = (sm.get("section") or {}).get("title") or "Contents"
    slug: str = os.path.basename(os.path.normpath(site))
    base: str = os.environ.get("OSBOOK_DOWNLOAD_BASE", DEFAULT_DOWNLOAD_BASE)

    injected: int = 0
    pg: str
    for pg in sorted(glob.glob(os.path.join(site, "*.html"))):
        cur: str = os.path.basename(pg)
        with open(pg, encoding="utf-8") as f:
            doc: str = f.read()
        if PLACEHOLDER not in doc:
            continue
        # Dedup the TOP-LEVEL entries by page too (the front matter 0.0.1–0.0.7 all
        # live on page 001 -> collapse to a single entry), the same one-entry-per-page
        # rule render() applies to nested children.
        seen: set[str] = set()
        parts: list[str] = []
        c: SitemapNode
        for c in chapters:
            c_page: str = ((c.get("section") or {}).get("path") or "").split("#", 1)[0]
            if c_page and c_page in seen:
                continue
            if c_page:
                seen.add(c_page)
            parts.append(render(c, cur)[0])
        toc: str = '<a class="book-title" href="index.html">%s</a>%s<ul>%s</ul>' % (
            html.escape(book_title),
            downloads_nav_item(base),
            "".join(parts),
        )
        # The downloads box goes on the book's first page only.
        box: str = downloads_box(slug, base) if cur == "index.html" else ""
        with open(pg, "w", encoding="utf-8") as f:
            f.write(doc.replace(PLACEHOLDER, toc).replace(DOWNLOADS_PLACEHOLDER, box))
        injected += 1
    print("build_nav: injected book TOC into %d pages in %s" % (injected, site))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
