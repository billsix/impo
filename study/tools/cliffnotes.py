#!/usr/bin/env python3
"""Generate the cliff-notes study guides: rules, worked examples, practice.

The source is one TOML file per subject (`cliffnotes/<subject>.toml`), one
`[[chapters]]` entry per chapter of the book the guide follows. Each chapter is
one or two pages: its key rules in a box, worked examples with step-by-step
solutions, and practice problems whose answers sit at the end of the chapter,
with links back to the full book's sections. Every example and practice problem
carries `compute` and `answer` (sympy expressions, evaluated by bank.py); they
must be equal, so a wrong answer cannot ship.

Usage:
    python3 tools/cliffnotes.py check [subject ...]
    python3 tools/cliffnotes.py <output-dir> [subject ...]   (check, then write .tex)
"""

from __future__ import annotations

import dataclasses
import os
import sys
import tomllib
from typing import Any

import bank
import studytex

CLIFF_DIR: str = os.path.join(studytex.STUDY, "cliffnotes")


@dataclasses.dataclass(frozen=True)
class Problem:
    """A worked example (with `steps`) or a practice problem (steps empty)."""

    problem: str
    steps: str
    compute: str
    answer: str
    answer_tex: str
    compare: str


@dataclasses.dataclass(frozen=True)
class Chapter:
    """One chapter: title, book sections, rules, examples and practice."""

    title: str
    review: list[str]
    rules: list[str]
    examples: list[Problem]
    practice: list[Problem]


@dataclasses.dataclass(frozen=True)
class Guide:
    """One subject's guide."""

    subject: str
    title: str
    based_on: str
    chapters: list[Chapter]


def problem(raw: dict[str, Any]) -> Problem:
    """Type one example/practice table."""
    return Problem(
        problem=raw["problem"].strip(),
        steps=raw.get("steps", "").strip(),
        compute=raw["compute"],
        answer=raw["answer"],
        answer_tex=raw.get("answer_tex", ""),
        compare=raw.get("compare", "value"),
    )


def load(subject: str) -> Guide:
    """Read one subject's guide source."""
    with open(os.path.join(CLIFF_DIR, "%s.toml" % subject), "rb") as handle:
        raw: dict[str, Any] = tomllib.load(handle)
    return Guide(
        subject=subject,
        title=raw["title"],
        based_on=raw.get("based_on", ""),
        chapters=[
            Chapter(
                title=c["title"],
                review=list(c.get("review", [])),
                rules=list(c["rules"]),
                examples=[problem(e) for e in c["examples"]],
                practice=[problem(p) for p in c["practice"]],
            )
            for c in raw["chapters"]
        ],
    )


def as_question(item: Problem) -> bank.Question:
    """A free-response bank question with this item's check, to reuse bank.py."""
    return bank.Question(
        id="cliff",
        part="B",
        strand="",
        difficulty=1,
        stem=item.problem,
        compute=item.compute,
        solution=item.steps,
        choices=[],
        choices_tex=[],
        answer=item.answer,
        answer_tex=item.answer_tex,
        compare=item.compare,
    )


def check(guide: Guide) -> list[str]:
    """Every item whose `compute` differs from its `answer` (empty = all good)."""
    problems: list[str] = []
    number: int
    chapter: Chapter
    for number, chapter in enumerate(guide.chapters, start=1):
        if not chapter.examples or not chapter.practice:
            problems.append("chapter %d: needs examples and practice" % number)
        kind: str
        items: list[Problem]
        for kind, items in (("example", chapter.examples), ("practice", chapter.practice)):
            index: int
            item: Problem
            for index, item in enumerate(items, start=1):
                question: bank.Question = as_question(item)
                try:
                    answer: bank.Value = (
                        bank.evaluate_unevaluated(item.answer)
                        if item.compare == "form"
                        else bank.evaluate(item.answer)
                    )
                    if not bank.comparison(question)(answer, bank.evaluate(item.compute)):
                        problems.append(
                            "chapter %d %s %d: answer %s != compute %s"
                            % (number, kind, index, item.answer, item.compute)
                        )
                except Exception as error:  # noqa: BLE001 -- report all, then fail
                    problems.append("chapter %d %s %d: %s" % (number, kind, index, error))
    return problems


def answer_math(item: Problem) -> str:
    """The item's answer as LaTeX math content."""
    return bank.answer_text(as_question(item))


def chapter_tex(number: int, chapter: Chapter) -> str:
    """One chapter's pages."""
    rules: str = "\n".join("  \\item %s" % r for r in chapter.rules)
    parts: list[str] = [
        "\\clearpage\n\\section*{%d\\quad %s}\n\\addcontentsline{toc}{section}{%d\\quad %s}\n"
        % (number, chapter.title, number, chapter.title),
        "\\begin{keyconcepts}\n\\begin{itemize}\n%s\n\\end{itemize}\n\\end{keyconcepts}\n" % rules,
    ]
    index: int
    example: Problem
    for index, example in enumerate(chapter.examples, start=1):
        parts.append(
            "\\textbf{Example %d.%d.}\\ %s\\par\n"
            "\\textit{Solution.}\\ %s\\par\n"
            "\\textbf{Answer:} $%s$\\par\\medskip\n"
            % (number, index, example.problem, example.steps, answer_math(example))
        )
    parts.append(
        "\\textbf{Practice.}\n\\begin{enumerate}\n%s\n\\end{enumerate}\n"
        % "\n".join("  \\item %s" % p.problem for p in chapter.practice)
    )
    parts.append(
        "{\\small\\textbf{Answers:} %s.}\\par\n"
        % ";\\quad ".join(
            "%d.~$%s$" % (i, answer_math(p)) for i, p in enumerate(chapter.practice, start=1)
        )
    )
    if chapter.review:
        parts.append(
            "{\\small\\textbf{In the full book:} %s.}\\par\n"
            % "; ".join(studytex.review_pointer(r) for r in chapter.review)
        )
    return "".join(parts)


def guide_tex(guide: Guide) -> str:
    """The whole guide."""
    note: str = (
        "Rules summarize, and the chapters follow, %s, licensed CC BY 4.0 "
        "(\\url{https://creativecommons.org/licenses/by/4.0/}). The examples and practice "
        "problems were written for impo (\\url{https://github.com/billsix/impo}, MIT); every "
        "answer is checked by computer (sympy)." % guide.based_on
        if guide.based_on
        else "Written for impo (\\url{https://github.com/billsix/impo}, MIT); every answer is "
        "checked by computer (sympy)."
    )
    return "".join(
        [
            studytex.preamble(
                guide.title, "rules, worked examples and practice, chapter by chapter"
            ),
            "{\\small %s\\par}\n\\tableofcontents*\n" % note,
            *(chapter_tex(i, c) for i, c in enumerate(guide.chapters, start=1)),
            "\\end{document}\n",
        ]
    )


def main(argv: list[str]) -> int:
    match argv:
        case []:
            print(__doc__, file=sys.stderr)
            return 2
        case [command, *subjects]:
            status: int = 0
            name: str
            for name in subjects or list(bank.SUBJECTS):
                guide: Guide = load(name)
                problems: list[str] = check(guide)
                print(
                    "cliffnotes %s: %d chapters, %d problems"
                    % (name, len(guide.chapters), len(problems))
                )
                print("".join("  %s\n" % p for p in problems), end="")
                if problems:
                    status = 1
                    continue
                if command != "check":
                    os.makedirs(command, exist_ok=True)
                    with open(os.path.join(command, "%s.tex" % name), "w", encoding="utf-8") as f:
                        f.write(guide_tex(guide))
            return status
        case _:
            return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
