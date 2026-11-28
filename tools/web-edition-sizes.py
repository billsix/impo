#!/usr/bin/env python3
"""Measure the built web editions against the GitHub Pages size limit.

For every built site (`openstax/osbooks-*/checkout/output/<book>/index.html`)
this sums the files its pages use, as `openstax/tooling/tools/pandoc/site_files.py`
lists them, which is what `tools/build-books.sh` copies into `output/<book>/`
and `tools/publish-pages.sh` publishes. The sites of one book folder link the
same `media/` directory, so a figure two volumes both use is published twice;
the "shared" column is the part of a book's size that a sibling in its folder
also uses.

Usage (from the repo root):
    python3 tools/web-edition-sizes.py                 # every built site
    python3 tools/web-edition-sizes.py --books FILE    # only the books FILE lists

FILE holds one book name per line (`#` starts a comment), the format of
`tools/pages-books.txt`. The last lines give the total, the total with each
shared file counted once, and the limit.
"""

from __future__ import annotations

import argparse
import collections
import pathlib
import sys

ROOT: pathlib.Path = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "openstax/tooling/tools/pandoc"))

import site_files  # found through the path added above

LIMIT_MB: int = 1000
MEGABYTE: int = 1024 * 1024


def listed_books(path: pathlib.Path) -> list[str]:
    """Return the book names a list file holds, in order, without comments."""
    lines: list[str] = [
        line.split("#", 1)[0].strip() for line in path.read_text().splitlines()
    ]
    return [line for line in lines if line]


def megabytes(size: int) -> str:
    """Format a byte count as megabytes with one decimal.

    >>> megabytes(1572864)
    '1.5'
    """
    return f"{size / MEGABYTE:.1f}"


def main(argv: list[str]) -> int:
    parser: argparse.ArgumentParser = argparse.ArgumentParser(
        description=__doc__.split("\n")[0]
    )
    parser.add_argument(
        "--books", type=pathlib.Path, help="measure only the books this file lists"
    )
    arguments: argparse.Namespace = parser.parse_args(argv)
    wanted: list[str] | None = (
        listed_books(arguments.books) if arguments.books else None
    )

    # book -> (folder, {real path of a used file: size})
    sites: dict[str, tuple[str, dict[pathlib.Path, int]]] = {}
    for index in sorted(ROOT.glob("openstax/osbooks-*/checkout/output/*/index.html")):
        site: pathlib.Path = index.parent
        if wanted is not None and site.name not in wanted:
            continue
        used: dict[pathlib.Path, int] = {}
        for relative in site_files.site_files(str(site)):
            real: pathlib.Path = (site / relative).resolve()
            if real.is_file():
                used[real] = real.stat().st_size
        sites[site.name] = (site.parents[2].name, used)

    missing: list[str] = [book for book in wanted or [] if book not in sites]
    if missing:
        print("not built: " + " ".join(missing), file=sys.stderr)
        return 2

    users: collections.Counter[pathlib.Path] = collections.Counter(
        path for _, used in sites.values() for path in used
    )
    print(f"{'book':<48} {'folder':<34} {'files':>6} {'MB':>9} {'shared MB':>9}")
    for book, (folder, used) in sorted(
        sites.items(), key=lambda item: (item[1][0], item[0])
    ):
        shared: int = sum(size for path, size in used.items() if users[path] > 1)
        book_size: str = megabytes(sum(used.values()))
        print(
            f"{book:<48} {folder:<34} {len(used):>6} {book_size:>9} {megabytes(shared):>9}"
        )
    total: int = sum(sum(used.values()) for _, used in sites.values())
    once: dict[pathlib.Path, int] = {}
    for _, used in sites.values():
        once.update(used)
    print(f"total: {megabytes(total)} MB in {len(sites)} sites")
    deduplicated: str = megabytes(sum(once.values()))
    print(f"total with each shared file counted once: {deduplicated} MB")
    print(f"GitHub Pages limit: {LIMIT_MB} MB")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
