#!/usr/bin/env python3
"""Check the local links of a combined site: one directory per book under a root.

Every `href`/`src` in every page that is a relative path (same book, or
`../<other-book>/<page>` across books) must name an existing file. A link into a
book directory that is absent from the root is reported separately as
"not published here" (the target book was not built or not staged) rather than
as broken, unless --strict. Anchors (`#...`) are not checked, only files.

Usage:  python3 check_links.py [--strict] <root>     (exit 1 on a broken link)
    e.g. python3 openstax/tooling/tools/pandoc/check_links.py output/pages
"""

from __future__ import annotations

import os
import sys
import urllib.parse

from site_files import LinkCollector


def page_links(root: str, book: str, page: str) -> list[str]:
    """The root-relative files the relative links of one page point at."""
    collector: LinkCollector = LinkCollector()
    with open(os.path.join(root, book, page), encoding="utf-8") as handle:
        collector.feed(handle.read())
    targets: list[str] = []
    reference: str
    for reference in collector.references:
        path: str = urllib.parse.unquote(reference.split("#", 1)[0].split("?", 1)[0])
        scheme: str = urllib.parse.urlsplit(path).scheme
        if not path or path.startswith("/") or (scheme and scheme[0].isalpha()):
            continue
        targets.append(os.path.normpath(os.path.join(book, path)))
    return targets


def check(root: str, strict: bool) -> tuple[list[str], list[str]]:
    """Return (broken, unpublished) as `book/page -> target` lines."""
    books: set[str] = {
        entry for entry in os.listdir(root) if os.path.isdir(os.path.join(root, entry))
    }
    broken: list[str] = []
    unpublished: list[str] = []
    book: str
    for book in sorted(books):
        page: str
        for page in sorted(
            p for p in os.listdir(os.path.join(root, book)) if p.endswith(".html")
        ):
            target: str
            for target in page_links(root, book, page):
                if os.path.exists(os.path.join(root, target)):
                    continue
                line: str = "%s/%s -> %s" % (book, page, target)
                top: str = target.split(os.sep, 1)[0]
                if top in books or strict:
                    broken.append(line)
                else:
                    unpublished.append(line)
    return broken, unpublished


def main(argv: list[str]) -> int:
    strict: bool = "--strict" in argv
    rest: list[str] = [a for a in argv if a != "--strict"]
    if len(rest) != 1:
        print("usage: check_links.py [--strict] <root>", file=sys.stderr)
        return 2
    broken: list[str]
    unpublished: list[str]
    broken, unpublished = check(rest[0], strict)
    print(
        "\n".join(
            ["BROKEN " + b for b in broken] + ["UNPUBLISHED " + u for u in unpublished]
        )
    )
    print(
        "check_links: %d broken, %d into books not in %s"
        % (len(broken), len(unpublished), rest[0]),
        file=sys.stderr,
    )
    return 1 if broken else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
