#!/usr/bin/env python3
"""Rewrite every book folder's apply.sh and Makefile from tools/book-template/.

The two files are the same in every `openstax/osbooks-*/` folder apart from
the folder's name, which `tools/add-book.sh` fills into the template's
`@NAME@`, and the Makefile's first line, which holds the book's title. This
fills the template again and keeps each Makefile's first line, so a change to
the template reaches every folder. A second run changes nothing.

Usage (from anywhere):
    python3 tools/fill-book-folders.py
"""

from __future__ import annotations

import pathlib

ROOT: pathlib.Path = pathlib.Path(__file__).resolve().parents[1]
TEMPLATE: pathlib.Path = ROOT / "tools/book-template"


def filled(name: str, folder: pathlib.Path) -> str:
    """Return the template file `name` as it should read in `folder`."""
    text: str = (TEMPLATE / name).read_text().replace("@NAME@", folder.name)
    if name != "Makefile":
        return text
    # The first line names the book; keep the folder's own.
    title_line: str = (folder / name).read_text().split("\n", 1)[0]
    return title_line + "\n" + text.split("\n", 1)[1]


def main() -> int:
    changed: int = 0
    for folder in sorted((ROOT / "openstax").glob("osbooks-*")):
        for name in ("apply.sh", "Makefile"):
            target: pathlib.Path = folder / name
            wanted: str = filled(name, folder)
            if target.read_text() != wanted:
                target.write_text(wanted)
                changed += 1
    print(f"{changed} files rewritten")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
