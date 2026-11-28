"""Rewrite every book folder's apply.sh and Makefile from tools/book-template/.

The two files are the same in all 45 folders apart from the folder's name and
title, which tools/add-book.sh fills into the template's @NAME@ and @TITLE@.
This fills the template again and keeps each Makefile's first line (the one
that holds the title), so the folders pick up a template change. Running it twice
changes nothing the second time.

Usage: python3 tasks/adhoc/openstax-build-refresh-overlay/regenerate_from_template.py
"""

import pathlib

root: pathlib.Path = pathlib.Path(__file__).resolve().parents[3]
template: pathlib.Path = root / "tools/book-template"

changed: int = 0
for folder in sorted((root / "openstax").glob("osbooks-*")):
    for name in ("apply.sh", "Makefile"):
        target: pathlib.Path = folder / name
        current: str = target.read_text()
        filled: str = (template / name).read_text().replace("@NAME@", folder.name)
        if name == "Makefile":
            # The first line names the book; keep the folder's own.
            filled = current.split("\n", 1)[0] + "\n" + filled.split("\n", 1)[1]
        if current != filled:
            target.write_text(filled)
            changed += 1
print(f"{changed} files rewritten")
