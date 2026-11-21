#!/usr/bin/env python3
"""Extract a book's exercises, section by section, from the converter's output.

The OpenStax converter (openstax/tooling/tools/cnxml2tex/convert.py) already
parses every CNXML `<exercise>` into LaTeX: `\\begin{exercise}` with the problem,
and a nested `\\begin{answer}` where the book gives one (the odd-numbered
exercises). This reads those generated section files
(`openstax/<folder>/checkout/latex/sections/<module>.tex`, written by that
folder's `make convert`) in the book's section order, taken from the committed
cross-book index (crossbook/index/<book>.json), so the problems are exactly the
ones the PDF prints. For each exercise it also keeps the subsection it sits in
("Practice Makes Perfect", "Everyday Math", ...) and the instruction that
governs it ("In the following exercises, simplify."), which says what to do with
a bare expression.

Usage:  python3 tools/problems.py <book> [--json]   (summary, or every problem as JSON)
"""

from __future__ import annotations

import dataclasses
import json
import os
import re
import sys

import studytex

# The book folder holding each extractable book's checkout.
BOOK_FOLDERS: dict[str, str] = {
    "prealgebra-2e": "osbooks-prealgebra-bundle",
    "elementary-algebra-2e": "osbooks-prealgebra-bundle",
    "intermediate-algebra-2e": "osbooks-prealgebra-bundle",
    "college-algebra-2e": "osbooks-college-algebra-bundle",
    "precalculus-2e": "osbooks-college-algebra-bundle",
    "calculus-volume-1": "osbooks-calculus-bundle",
    "calculus-volume-2": "osbooks-calculus-bundle",
    "calculus-volume-3": "osbooks-calculus-bundle",
}
BOOK_CODES: dict[str, str] = {slug: code for code, (slug, _) in studytex.crossbook.BOOKS.items()}

EXERCISE: re.Pattern[str] = re.compile(r"\\begin\{exercise\}(.*?)\\end\{exercise\}", re.S)
ANSWER: re.Pattern[str] = re.compile(r"\\begin\{answer\}(.*?)\\end\{answer\}", re.S)
SUBSECTION: re.Pattern[str] = re.compile(r"\\subsection\*?\{([^}]*)\}")
INSTRUCTION: re.Pattern[str] = re.compile(
    r"(?:In|For) the following exercises?,?\s+(.*?)(?:\.|:)(?:\s|$)", re.S
)


@dataclasses.dataclass(frozen=True)
class Problem:
    """One exercise: its number in the section, context, problem and answer LaTeX."""

    number: int
    subsection: str
    instruction: str
    problem: str
    answer: str


@dataclasses.dataclass(frozen=True)
class Section:
    """One book section with its exercises."""

    book: str
    number: str
    title: str
    module: str
    page: str
    problems: list[Problem]


def checkout_dir(book: str) -> str:
    """The checkout that holds a book's converted sections."""
    return os.path.join(studytex.STUDY, "..", "openstax", BOOK_FOLDERS[book], "checkout")


def section_order(book: str) -> list[tuple[str, dict[str, str]]]:
    """The book's indexed sections, in numeric order (chapter openers included)."""
    index: dict[str, dict[str, str]] = studytex.crossbook.book_index(BOOK_CODES[book])
    return sorted(index.items(), key=lambda item: tuple(int(p) for p in item[0].split(".")))


def parse_section(tex: str) -> list[Problem]:
    """Every exercise of one generated section file, with its context.

    >>> tex = ("\\\\subsection*{Practice Makes Perfect}\\nIn the following exercises, simplify.\\n"
    ...        "\\\\begin{exercise}\\n$3+4$\\n\\\\begin{answer}\\n$7$\\n\\\\end{answer}\\n\\\\end{exercise}")
    >>> parse_section(tex)  # doctest: +NORMALIZE_WHITESPACE
    [Problem(number=1, subsection='Practice Makes Perfect', instruction='simplify',
             problem='$3+4$', answer='$7$')]
    """
    problems: list[Problem] = []
    found: re.Match[str]
    for found in EXERCISE.finditer(tex):
        before: str = tex[: found.start()]
        subsections: list[str] = SUBSECTION.findall(before)
        instructions: list[str] = INSTRUCTION.findall(before)
        # An instruction governs only the exercises of its own subsection.
        last_sub: int = max((m.start() for m in SUBSECTION.finditer(before)), default=-1)
        last_ins: int = max((m.start() for m in INSTRUCTION.finditer(before)), default=-1)
        instruction: str = (
            " ".join(instructions[-1].split()) if instructions and last_ins > last_sub else ""
        )
        body: str = found.group(1)
        answer: re.Match[str] | None = ANSWER.search(body)
        problem: str = ANSWER.sub("", body).strip()
        problems.append(
            Problem(
                number=len(problems) + 1,
                subsection=subsections[-1].strip() if subsections else "",
                instruction=instruction,
                problem=problem,
                answer=answer.group(1).strip() if answer else "",
            )
        )
    return problems


def sections(book: str) -> list[Section]:
    """Every indexed section of the book with its exercises (needs `make convert`)."""
    directory: str = os.path.join(checkout_dir(book), "latex", "sections")
    if not os.path.isdir(directory):
        raise FileNotFoundError(
            "%s: no converted sections; run make convert in openstax/%s"
            % (directory, BOOK_FOLDERS[book])
        )
    out: list[Section] = []
    number: str
    entry: dict[str, str]
    for number, entry in section_order(book):
        path: str = os.path.join(directory, "%s.tex" % entry["module"])
        if not entry["module"] or not os.path.exists(path):
            continue
        with open(path, encoding="utf-8") as handle:
            found: list[Problem] = parse_section(handle.read())
        out.append(Section(book, number, entry["title"], entry["module"], entry["page"], found))
    return out


def main(argv: list[str]) -> int:
    match argv:
        case [book] | [book, "--json"] if book in BOOK_FOLDERS:
            found: list[Section] = sections(book)
            if argv[-1] == "--json":
                print(json.dumps([dataclasses.asdict(s) for s in found], indent=1))
                return 0
            total: int = sum(len(s.problems) for s in found)
            keyed: int = sum(1 for s in found for p in s.problems if p.answer)
            print(
                "%s: %d sections, %d problems, %d with a book answer"
                % (book, len(found), total, keyed)
            )
            return 0
        case _:
            print(
                "usage: problems.py <book> [--json]; books: %s" % ", ".join(BOOK_FOLDERS),
                file=sys.stderr,
            )
            return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
