#!/usr/bin/env python3
"""Inject the book's table of contents into each chunked HTML page's left sidebar.

pandoc's chunkedhtml writer emits a `sitemap.json` (the full section tree) beside
the pages, but does NOT put a whole-book TOC on each page. This does: it reads
sitemap.json and writes the nested TOC into every page's `<!--BOOK-TOC-->`
placeholder (left in place by chunked-template.html), marking the links that live
on the current page as active.

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

PLACEHOLDER = "<!--BOOK-TOC-->"


def render(node: dict, current_page: str) -> tuple[str, bool]:
    """Render one <li> for a sitemap node; return (html, contains_active).

    A node with children is collapsible: it gets `has-children`, plus `open` when
    it (or a descendant) is on the current page, so the active branch starts
    expanded and everything else collapsed (osbook-web.js toggles the rest).
    """
    s = node.get("section") or {}
    path = s.get("path") or ""
    title = s.get("title") or ""
    number = s.get("number") or ""
    page = path.split("#", 1)[0]
    self_active = bool(page) and page == current_page
    label = (number + "  " if number else "") + title
    kids = node.get("subsections") or []

    kids_html = ""
    any_active = self_active
    for k in kids:
        kh, ka = render(k, current_page)
        kids_html += kh
        any_active = any_active or ka

    li_class = ""
    if kids:
        li_class = ' class="has-children%s"' % (" open" if any_active else "")
    a_class = ' class="active"' if self_active else ""
    li = "<li%s>" % li_class
    if kids:
        li += '<button class="toc-toggle" aria-label="Expand section"></button>'
    li += '<a href="%s"%s>%s</a>' % (html.escape(path), a_class, html.escape(label))
    if kids:
        li += "<ul>%s</ul>" % kids_html
    li += "</li>"
    return li, any_active


def main(argv: list[str]) -> int:
    if len(argv) != 1:
        print("usage: build_nav.py <output-site-dir>", file=sys.stderr)
        return 2
    site = argv[0]
    smpath = os.path.join(site, "sitemap.json")
    if not os.path.exists(smpath):
        print("build_nav: no sitemap.json in %s -- skipping" % site, file=sys.stderr)
        return 0
    with open(smpath, encoding="utf-8") as f:
        sm = json.load(f)
    chapters = sm.get("subsections") or []
    book_title = (sm.get("section") or {}).get("title") or "Contents"

    injected = 0
    for pg in sorted(glob.glob(os.path.join(site, "*.html"))):
        cur = os.path.basename(pg)
        with open(pg, encoding="utf-8") as f:
            doc = f.read()
        if PLACEHOLDER not in doc:
            continue
        toc = (
            '<a class="book-title" href="index.html">%s</a><ul>%s</ul>'
            % (html.escape(book_title), "".join(render(c, cur)[0] for c in chapters))
        )
        with open(pg, "w", encoding="utf-8") as f:
            f.write(doc.replace(PLACEHOLDER, toc))
        injected += 1
    print("build_nav: injected book TOC into %d pages in %s" % (injected, site))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
