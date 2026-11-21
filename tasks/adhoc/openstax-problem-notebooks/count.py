#!/usr/bin/env python3
"""Count the exercises (and those with a solution) per math-ladder book.

Discovery for tasks/openstax-problem-notebooks.md: reads each book's collection
XML for its module list and each module's CNXML for <exercise> elements, and
writes data/counts.tsv (book, modules, exercises, with-solution). os-embed
exercises (Algebra 1's committed cache) are counted from the cache; that API
gives no answers. Needs the books' checkouts (./fetch.sh in each folder).
"""

from __future__ import annotations

import glob
import os
import re

HERE: str = os.path.dirname(os.path.abspath(__file__))
ROOT: str = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
FOLDERS: tuple[str, ...] = (
    "osbooks-prealgebra-bundle",
    "osbooks-algebra-1",
    "osbooks-college-algebra-bundle",
    "osbooks-calculus-bundle",
)
EXERCISE: re.Pattern[str] = re.compile(r"<exercise\b.*?</exercise>", re.S)


def main() -> None:
    rows: list[str] = ["book\tmodules\texercises\twith_solution\tos_embed"]
    folder: str
    for folder in FOLDERS:
        checkout: str = os.path.join(ROOT, "openstax", folder, "checkout")
        collection: str
        for collection in sorted(glob.glob(os.path.join(checkout, "collections", "*.collection.xml"))):
            book: str = os.path.basename(collection).removesuffix(".collection.xml")
            with open(collection, encoding="utf-8") as handle:
                modules: list[str] = re.findall(r'document="(m\d+)"', handle.read())
            exercises: int = 0
            solved: int = 0
            embedded: int = 0
            module: str
            for module in modules:
                path: str = os.path.join(checkout, "modules", module, "index.cnxml")
                if not os.path.exists(path):
                    continue
                with open(path, encoding="utf-8") as handle:
                    text: str = handle.read()
                found: list[str] = EXERCISE.findall(text)
                exercises += len(found)
                solved += sum(1 for e in found if "<solution" in e)
                embedded += sum(1 for e in found if "os-embed" in e or "#exercise/" in e)
            rows.append("%s\t%d\t%d\t%d\t%d" % (book, len(modules), exercises, solved, embedded))
    os.makedirs(os.path.join(HERE, "data"), exist_ok=True)
    with open(os.path.join(HERE, "data", "counts.tsv"), "w", encoding="utf-8") as handle:
        handle.write("\n".join(rows) + "\n")
    print("\n".join(rows))


if __name__ == "__main__":
    main()
