#!/usr/bin/env python3
"""Links between books: "(IA x.y.z)" references and the "Prerequisites" boxes.

Two kinds of cross-book link, both emitted by the converter into the LaTeX, so
the PDF, the EPUB and the HTML web edition all carry them:

1. **Explicit references.** The corequisite-support material tags learning
   objectives with their match in Intermediate Algebra 2e, as literal text
   "(IA 8.2.1)" = that book's section 8.2, objective 1. `link_ia_references`
   turns each into an `\\href` to that section's page.
2. **Prerequisites.** `crossbook/prerequisites.txt` (reviewed data) lists, per
   section of a math-ladder book, the earlier-book sections it builds on;
   `prerequisites_box` renders them as a `prerequisites` box of
   "Review: <book> §x.y" links at the top of the section.

Every link is an absolute URL on the published site (SITE_BASE, the gh-pages
site of impo, one directory per book). The HTML build (entrypoint/html.sh)
rewrites the site prefix to `../`, so on the site the links are relative and
resolve between books; the PDF and EPUB keep the absolute URL. Section numbers
are resolved to pages through the committed `crossbook/index/<book>.json`
(written by crossbook_index.py from each book's built sitemap).

`python3 crossbook.py --check` validates the data and prints the review list.
"""

from __future__ import annotations

import functools
import json
import os
import re
import sys
from typing import TypeAlias

# (book code, official section number), e.g. ("IA", "8.2").
SectionRef: TypeAlias = tuple[str, str]
# One prerequisites.txt line: the source section and its target sections.
Entry: TypeAlias = tuple[SectionRef, list[SectionRef]]

HERE: str = os.path.join(os.path.dirname(os.path.abspath(__file__)), "crossbook")

# Where the books are published (`make publish-pages`); OSBOOK_SITE_BASE overrides.
SITE_BASE: str = os.environ.get("OSBOOK_SITE_BASE", "https://billsix.github.io/impo/")

# Book code -> (published directory = collection slug, display title).
BOOKS: dict[str, tuple[str, str]] = {
    "PA": ("prealgebra-2e", "Prealgebra 2e"),
    "EA": ("elementary-algebra-2e", "Elementary Algebra 2e"),
    "IA": ("intermediate-algebra-2e", "Intermediate Algebra 2e"),
    "CA": ("college-algebra-2e", "College Algebra 2e"),
    "PC": ("precalculus-2e", "Precalculus 2e"),
    "C1": ("calculus-volume-1", "Calculus Volume 1"),
    "C2": ("calculus-volume-2", "Calculus Volume 2"),
    "C3": ("calculus-volume-3", "Calculus Volume 3"),
}

# "(IA 8.2.1)" or "(IA 8.2)": chapter and section are the link target; an
# objective sub-number has no anchor of its own, so it links the section page.
IA_REFERENCE: re.Pattern[str] = re.compile(r"\(IA (\d+)\.(\d+)((?:\.\d+)*)\)")

LATEX_SPECIALS: dict[str, str] = {
    "\\": r"\textbackslash{}",
    "&": r"\&",
    "%": r"\%",
    "$": r"\$",
    "#": r"\#",
    "_": r"\_",
    "{": r"\{",
    "}": r"\}",
    "~": r"\textasciitilde{}",
    "^": r"\textasciicircum{}",
}


def latex_text(text: str) -> str:
    """Escape plain text for LaTeX.

    >>> latex_text("Cost & 5% off_x")
    'Cost \\\\& 5\\\\% off\\\\_x'
    """
    return "".join(LATEX_SPECIALS.get(character, character) for character in text)


@functools.cache
def book_index(code: str) -> dict[str, dict[str, str]]:
    """The committed page index of one book (official section number -> entry)."""
    with open(
        os.path.join(HERE, "index", "%s.json" % BOOKS[code][0]), encoding="utf-8"
    ) as f:
        return json.load(f)


def section_url(ref: SectionRef) -> str:
    """The published URL of a section's page.

    >>> section_url(("IA", "8.2"))
    'https://billsix.github.io/impo/intermediate-algebra-2e/060-mod:m81445.html'
    """
    code: str
    number: str
    code, number = ref
    return "%s%s/%s" % (SITE_BASE, BOOKS[code][0], book_index(code)[number]["page"])


def parse_prerequisites(text: str) -> list[Entry]:
    """Parse prerequisites.txt: `SRC x.y  TGT a.b [TGT c.d ...]`, `#` comments.

    >>> parse_prerequisites("# c\\nCA 1.1  IA 1.1 IA 1.5\\n")
    [(('CA', '1.1'), [('IA', '1.1'), ('IA', '1.5')])]
    """
    entries: list[Entry] = []
    line: str
    for line in text.splitlines():
        words: list[str] = line.split("#", 1)[0].split()
        if not words:
            continue
        if len(words) < 4 or len(words) % 2:
            raise ValueError("prerequisites.txt: malformed line: %r" % line)
        pairs: list[SectionRef] = [
            (words[i], words[i + 1]) for i in range(0, len(words), 2)
        ]
        entries.append((pairs[0], pairs[1:]))
    return entries


@functools.cache
def entries() -> list[Entry]:
    """The reviewed prerequisites map."""
    with open(os.path.join(HERE, "prerequisites.txt"), encoding="utf-8") as f:
        return parse_prerequisites(f.read())


@functools.cache
def module_prerequisites() -> dict[str, list[SectionRef]]:
    """Module id -> its prerequisite sections (union over books sharing it).

    Modules are shared between books of a bundle (Calculus Volume 2 reuses
    Volume 1's integration chapters), so a module's box lists every target
    declared for any book section built from it, once, in file order, never the
    module itself.
    """
    result: dict[str, list[SectionRef]] = {}
    source: SectionRef
    targets: list[SectionRef]
    for source, targets in entries():
        module: str = book_index(source[0])[source[1]]["module"]
        listed: list[SectionRef] = result.setdefault(module, [])
        target: SectionRef
        for target in targets:
            if (
                target not in listed
                and book_index(target[0])[target[1]]["module"] != module
            ):
                listed.append(target)
    return result


def prerequisites_box(module: str) -> str:
    """The LaTeX `prerequisites` box for one module, or "" when it has none."""
    targets: list[SectionRef] = module_prerequisites().get(module, [])
    if not targets:
        return ""
    items: str = "\n".join(
        "  \\item Review: \\href{%s}{%s \\S%s} %s"
        % (
            section_url(target),
            BOOKS[target[0]][1],
            target[1],
            latex_text(book_index(target[0])[target[1]]["title"]),
        )
        for target in targets
    )
    return (
        "\\begin{prerequisites}\n\\begin{itemize}\n%s\n\\end{itemize}\n\\end{prerequisites}\n"
        % items
    )


def link_ia_references(tex: str) -> str:
    """Turn each "(IA x.y.z)" whose section is indexed into an `\\href`.

    >>> link_ia_references("Graph a parabola (IA 11.2.1)")  # doctest: +ELLIPSIS
    'Graph a parabola (\\\\href{https://billsix.github.io/impo/intermediate-algebra-2e/...}{IA 11.2.1})'
    >>> link_ia_references("(IA 99.9)")
    '(IA 99.9)'
    """

    def replace(found: re.Match[str]) -> str:
        number: str = "%s.%s" % (found.group(1), found.group(2))
        if number not in book_index("IA"):
            return found.group(0)
        return "(\\href{%s}{IA %s%s})" % (
            section_url(("IA", number)),
            number,
            found.group(3),
        )

    return IA_REFERENCE.sub(replace, tex)


def review_lines() -> list[str]:
    """One Markdown bullet per prerequisites entry, titles on both sides.

    Raises KeyError for a book code or section number that does not resolve.
    """
    lines: list[str] = []
    source: SectionRef
    targets: list[SectionRef]
    for source, targets in entries():
        reviews: str = "; ".join(
            "%s §%s %s" % (BOOKS[t[0]][1], t[1], book_index(t[0])[t[1]]["title"])
            for t in targets
        )
        lines.append(
            "- %s §%s %s ← %s"
            % (
                BOOKS[source[0]][1],
                source[1],
                book_index(source[0])[source[1]]["title"],
                reviews,
            )
        )
    return lines


def main(argv: list[str]) -> int:
    match argv:
        case ["--check"]:
            print("\n".join(review_lines()))
            print(
                "crossbook: %d entries, %d modules with a box"
                % (len(entries()), len(module_prerequisites())),
                file=sys.stderr,
            )
            return 0
        case _:
            print("usage: crossbook.py --check", file=sys.stderr)
            return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
