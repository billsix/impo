#!/usr/bin/env python3
"""List the files a built web-edition site actually uses, relative to the site dir.

A chunked site (`output/<slug>/`) links its pages to a `media/` directory that
holds the WHOLE bundle's figures (a bundle folder shares one `media/` across its
volumes, raw SVGs and originals included), so copying the directory publishes
several times what the pages reference. This lists only what the site needs:
every top-level page/style/script/sitemap file, plus each local file an `src=`
or `href=` attribute of a page points at (de-duplicated, sorted).

Used by `entrypoint/html.sh` (the `<slug>-html.zip` download) and by the
repo-level `tools/publish-pages.sh` (the GitHub Pages staging tree).

Usage:  python3 site_files.py <site-dir>        (one relative path per line)
"""

from __future__ import annotations

import os
import sys
import urllib.parse
from html.parser import HTMLParser

# Top-level files of the site itself, always included (by extension).
SITE_EXTENSIONS: tuple[str, ...] = (".html", ".css", ".js", ".json")


def local_target(reference: str) -> str | None:
    """Return the site-relative file a link points at, or None if it is not local.

    Drops the fragment and query, decodes %-escapes, and rejects absolute URLs,
    `mailto:`-style schemes, root-absolute paths and paths that climb out of the
    site.

    >>> local_target("media/fig%201.png")
    'media/fig 1.png'
    >>> local_target("002-mod:m81241.html#sec") is None
    False
    >>> [local_target(r) for r in ("https://x.org/a.png", "#top", "/abs.png", "../x.png")]
    [None, None, None, None]
    """
    path: str = urllib.parse.unquote(reference.split("#", 1)[0].split("?", 1)[0])
    scheme: str = urllib.parse.urlsplit(path).scheme
    # A page name like "002-mod:m81241.html" parses with scheme "002-mod" in
    # urlsplit, but a URL scheme must start with a letter, so a browser reads it
    # as a relative path; treat it that way too.
    is_scheme: bool = bool(scheme) and scheme[0].isalpha()
    normal: str = os.path.normpath(path) if path else ""
    match (is_scheme, normal):
        case (True, _) | (_, ""):
            return None
        case (_, n) if n.startswith("/") or n == ".." or n.startswith("../"):
            return None
        case (_, n):
            return n


class LinkCollector(HTMLParser):
    """Collect every `src` / `href` attribute value of one HTML document."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.references: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        name: str
        value: str | None
        for name, value in attrs:
            if name in ("src", "href") and value:
                self.references.append(value)


def site_files(site: str) -> list[str]:
    """Return the sorted site-relative paths the site at `site` needs.

    Missing link targets are skipped (they are a broken link, not a file to copy).
    """
    files: set[str] = {
        entry
        for entry in os.listdir(site)
        if entry.endswith(SITE_EXTENSIONS) and os.path.isfile(os.path.join(site, entry))
    }
    page: str
    for page in sorted(f for f in files if f.endswith(".html")):
        collector: LinkCollector = LinkCollector()
        with open(os.path.join(site, page), encoding="utf-8") as handle:
            collector.feed(handle.read())
        files.update(
            target
            for target in (local_target(r) for r in collector.references)
            if target is not None and os.path.isfile(os.path.join(site, target))
        )
    return sorted(files)


def main(argv: list[str]) -> int:
    if len(argv) != 1:
        print("usage: site_files.py <site-dir>", file=sys.stderr)
        return 2
    print("\n".join(site_files(argv[0])))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
