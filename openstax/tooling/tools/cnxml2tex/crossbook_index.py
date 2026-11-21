#!/usr/bin/env python3
"""Write the cross-book page index of a built web edition (crossbook/index/<book>.json).

A link from one book to another names the target section by its OFFICIAL OpenStax
number ("IA 8.2" = Intermediate Algebra 2e section 8.2), but a book's page files
(`059-mod:m81444.html`) are only known after its web edition is built, and a book
folder's build container mounts only its own checkout. So the page index of each
book that links or is linked is generated once from that book's built
`sitemap.json` and committed beside the converter; `crossbook.py` reads it at
convert time. Re-run this after a pin bump or a converter change that moves pages
(`tools/pandoc/check_links.py` over the built site reports a stale index).

Official numbering: the web edition's sitemap numbers a chapter's opening
"Introduction" module as section x.1, which OpenStax does not number, so every
later section is one higher than the book's own numbering. The index renumbers:
a chapter's FIRST module, when its title starts with "Introduction" and it has no
subsections of its own, is the unnumbered chapter opener (key "x.0").

Usage (from openstax/tooling/):
    python3 tools/cnxml2tex/crossbook_index.py ../osbooks-*/checkout/output/<book> ...
"""

from __future__ import annotations

import json
import os
import re
import sys
from typing import Any, TypeAlias

# A sitemap node, as pandoc's chunkedhtml writer emits it (dynamic JSON).
SitemapNode: TypeAlias = dict[str, Any]
# One index entry: {"module": "m81444", "page": "059-mod:m81444.html", "title": ...}.
IndexEntry: TypeAlias = dict[str, str]

INDEX_DIR: str = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "crossbook", "index"
)
MODULE_IN_PAGE: re.Pattern[str] = re.compile(r"mod:(m\d+)")


def is_chapter_opener(position: int, node: SitemapNode) -> bool:
    """True for a chapter's unnumbered opening module (see the module docstring).

    >>> is_chapter_opener(0, {"section": {"title": "Introduction"}, "subsections": []})
    True
    >>> is_chapter_opener(0, {"section": {"title": "Introduction to Integers"},
    ...                       "subsections": [{"section": {}}]})
    False
    >>> is_chapter_opener(1, {"section": {"title": "Introduction"}, "subsections": []})
    False
    """
    title: str = (node.get("section") or {}).get("title") or ""
    return (
        position == 0
        and title.startswith("Introduction")
        and not node.get("subsections")
    )


def chapter_entries(
    chapter_number: str, sections: list[SitemapNode]
) -> dict[str, IndexEntry]:
    """Index one numbered chapter's sections under their official numbers.

    >>> nodes = [{"section": {"title": "Introduction", "path": "058-mod:m1.html#x"},
    ...           "subsections": []},
    ...          {"section": {"title": "Roots", "path": "059-mod:m2.html#y"},
    ...           "subsections": [{}]}]
    >>> sorted(chapter_entries("8", nodes).items())  # doctest: +NORMALIZE_WHITESPACE
    [('8.0', {'module': 'm1', 'page': '058-mod:m1.html', 'title': 'Introduction'}),
     ('8.1', {'module': 'm2', 'page': '059-mod:m2.html', 'title': 'Roots'})]
    """
    entries: dict[str, IndexEntry] = {}
    number: int = 0
    position: int
    node: SitemapNode
    for position, node in enumerate(sections):
        section: SitemapNode = node.get("section") or {}
        page: str = (section.get("path") or "").split("#", 1)[0]
        found: re.Match[str] | None = MODULE_IN_PAGE.search(page)
        key: str
        if is_chapter_opener(position, node):
            key = "%s.0" % chapter_number
        else:
            number += 1
            key = "%s.%d" % (chapter_number, number)
        entries[key] = {
            "module": found.group(1) if found else "",
            "page": page,
            "title": section.get("title") or "",
        }
    return entries


def book_index(sitemap: SitemapNode) -> dict[str, IndexEntry]:
    """Index every numbered chapter of a book (front/back matter has no number)."""
    entries: dict[str, IndexEntry] = {}
    chapter: SitemapNode
    for chapter in sitemap.get("subsections") or []:
        number: str | None = (chapter.get("section") or {}).get("number")
        if number and number.isdigit():
            entries.update(chapter_entries(number, chapter.get("subsections") or []))
    return entries


def main(argv: list[str]) -> int:
    if not argv:
        print(__doc__, file=sys.stderr)
        return 2
    os.makedirs(INDEX_DIR, exist_ok=True)
    site: str
    for site in argv:
        book: str = os.path.basename(os.path.normpath(site))
        with open(os.path.join(site, "sitemap.json"), encoding="utf-8") as handle:
            sitemap: SitemapNode = json.load(handle)
        entries: dict[str, IndexEntry] = book_index(sitemap)
        out: str = os.path.join(INDEX_DIR, "%s.json" % book)
        with open(out, "w", encoding="utf-8") as handle:
            json.dump(entries, handle, indent=1, sort_keys=True)
            handle.write("\n")
        print("crossbook_index: %s (%d sections) -> %s" % (book, len(entries), out))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
