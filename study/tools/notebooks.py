#!/usr/bin/env python3
"""Generate one problem notebook per book section, and summarize the executed runs.

For a book (problems.py lists the extractable ones) this writes, under
`output/notebooks/<book>/`, one jupytext percent-format notebook per section
(`<x.y>.py`, converted to `.ipynb` and executed by entrypoint/build-notebooks.sh):

- a header naming the section, linking its page on the published site, and
  carrying the OpenStax CC BY 4.0 attribution (the problems are restated from it);
- per exercise, a markdown cell restating it (LaTeX turned into notebook Markdown
  by pandoc, figures linked from the book's checkout) with the book's answer when
  it has one, then a code cell that runs `solver.attempt` on it -- sympy solves the
  mechanical ones and checks them against the book (see solver.py for the
  statuses) -- and, for an exercise that graphs an x-y equation, an ePiX graph
  cell (nbplot.py);
- a last cell that writes `<x.y>.status.json` (status per exercise).

`notebooks.py summary <book>` totals the executed statuses into
`output/notebooks/<book>/summary.json` and prints them.

Usage:  python3 tools/notebooks.py generate <book> [section ...]
        python3 tools/notebooks.py summary <book>
"""

from __future__ import annotations

import collections
import glob
import json
import os
import re
import subprocess
import sys

import problems
import solver
import studytex

OUT_ROOT: str = os.path.join(studytex.STUDY, "output", "notebooks")
SEPARATOR: str = "IMPOPROBLEMSEPARATOR"


def to_markdown(snippets: list[str], media: str) -> list[str]:
    """LaTeX snippets to notebook Markdown (one pandoc call), figures re-pointed at
    the checkout's media directory `media` (relative to the notebook)."""
    if not snippets:
        return []
    source: str = ("\n\n%s\n\n" % SEPARATOR).join(snippets)
    text: str = subprocess.run(
        [
            "pandoc",
            "-f",
            "latex",
            "-t",
            "markdown-raw_html-raw_tex-fenced_divs-bracketed_spans",
            "--wrap=none",
        ],
        input=source,
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    parts: list[str] = [p.strip() for p in text.split(SEPARATOR)]
    if len(parts) != len(snippets):
        raise RuntimeError("pandoc merged snippets (%d in, %d out)" % (len(snippets), len(parts)))
    return [
        re.sub(r"!\[([^\]]*)\]\(([^)/]+)\)(\{[^}]*\})?", r"![\1](%s/\2)" % media, p) for p in parts
    ]


def drop_crossrefs(tex: str) -> str:
    r"""Drop the book's in-book pointers (``\cref`` to a label in another page),
    which mean nothing in a notebook: "If you missed this problem, review ...".

    >>> drop_crossrefs(r"Solve $x=1$. \\ If you missed this problem, review \cref{a-b}.")
    'Solve $x=1$.'

    A link with words of its own (``\hyperref[label]{words}``) keeps the words:

    >>> drop_crossrefs(r"Use the \hyperref[mod:m1]{order of operations}.")
    'Use the order of operations.'
    """
    text: str = re.sub(
        r"(\\\\)?\s*If you missed this problem, review\s*\\cref\{[^}]*\}\.?", "", tex
    )
    text = re.sub(r"\\hyperref\[[^\]]*\]\{([^{}]*)\}", r"\1", text)
    return re.sub(r"\\cref\{[^}]*\}", "", text).strip()


def commented(markdown: str) -> str:
    """A jupytext percent-format markdown cell body (every line behind `# `)."""
    return "\n".join(("# " + line).rstrip() for line in markdown.splitlines())


def notebook_text(section: problems.Section, media: str) -> str:
    """One section's notebook, as jupytext percent-format Python."""
    code: str = problems.BOOK_CODES[section.book]
    title: str = "%s §%s %s" % (studytex.crossbook.BOOKS[code][1], section.number, section.title)
    url: str = studytex.crossbook.section_url((code, section.number))
    snippets: list[str] = []
    problem: problems.Problem
    for problem in section.problems:
        snippets.append(drop_crossrefs(problem.problem))
        snippets.append(drop_crossrefs(problem.answer) or "(none)")
    rendered: list[str] = to_markdown(snippets, media)
    cells: list[str] = [
        "# ---\n# jupyter:\n#   jupytext:\n#     formats: py:percent\n"
        "#   kernelspec:\n#     display_name: Python 3\n#     language: python\n"
        "#     name: python3\n# ---\n",
        "# %%%% [markdown]\n%s\n"
        % commented(
            "# %s: problems\n\nEvery exercise of [this section](%s), restated, then solved by "
            "sympy where it is mechanical and checked against the book's answer (the book "
            "answers the odd-numbered exercises). Statuses: **checked** (matches the book), "
            "**mismatch** (differs: review it), **computed** (no book answer: unchecked until "
            "reviewed), **manual** (restated only: a person solves it).\n\n"
            "The exercises are from OpenStax, *%s*, licensed "
            "[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) "
            "(https://openstax.org); restated here by impo (github.com/billsix/impo)."
            % (title, url, studytex.crossbook.BOOKS[code][1])
        ),
        "# %%\nimport json\n\nimport nbplot\nimport solver\n\nstatuses: dict[str, str] = {}\n",
    ]
    subsection: str = ""
    index: int
    for index, problem in enumerate(section.problems):
        if problem.subsection != subsection:
            subsection = problem.subsection
            cells.append(
                "# %%%% [markdown]\n%s\n" % commented("## %s" % (subsection or "Exercises"))
            )
        instruction: str = (
            "*In the following exercises, %s.*\n\n" % problem.instruction
            if problem.instruction
            else ""
        )
        answer: str = "\n\n*Book answer:* %s" % rendered[2 * index + 1] if problem.answer else ""
        cells.append(
            "# %%%% [markdown]\n%s\n"
            % commented(
                "**Exercise %d.** %s%s%s"
                % (problem.number, instruction, rendered[2 * index], answer)
            )
        )
        cells.append(
            "# %%%%\nresult = solver.attempt(\n    instruction=%r,\n    problem=%r,\n    answer=%r,\n)\n"
            "statuses[%r] = result.status\nprint(result.show())\n"
            % (problem.instruction, problem.problem, problem.answer, str(problem.number))
        )
        if (
            solver.graph_target(problem.problem) is not None
            and "graph" in (problem.instruction + problem.problem).lower()
        ):
            cells.append("# %%%%\nnbplot.graph(problem=%r)\n" % problem.problem)
    cells.append(
        '# %%%%\nwith open(%r, "w", encoding="utf-8") as handle:\n'
        "    json.dump(statuses, handle, indent=1)\n" % ("%s.status.json" % section.number)
    )
    return "\n".join(cells)


def generate(book: str, only: list[str]) -> int:
    """Write the book's notebooks; returns how many."""
    out: str = os.path.join(OUT_ROOT, book)
    os.makedirs(out, exist_ok=True)
    media: str = os.path.relpath(os.path.join(problems.checkout_dir(book), "media"), out)
    written: int = 0
    section: problems.Section
    for section in problems.sections(book):
        if (only and section.number not in only) or not section.problems:
            continue
        with open(os.path.join(out, "%s.py" % section.number), "w", encoding="utf-8") as handle:
            handle.write(notebook_text(section, media))
        written += 1
    print("notebooks: wrote %d section notebooks for %s in %s" % (written, book, out))
    return written


def summary(book: str) -> dict[str, object]:
    """Total the executed notebooks' statuses (and list unexecuted sections)."""
    out: str = os.path.join(OUT_ROOT, book)
    totals: collections.Counter[str] = collections.Counter()
    per_section: dict[str, dict[str, int]] = {}
    path: str
    for path in sorted(glob.glob(os.path.join(out, "*.status.json"))):
        with open(path, encoding="utf-8") as handle:
            statuses: dict[str, str] = json.load(handle)
        counts: collections.Counter[str] = collections.Counter(statuses.values())
        per_section[os.path.basename(path).removesuffix(".status.json")] = dict(counts)
        totals.update(counts)
    notebooks: list[str] = [
        os.path.basename(p).removesuffix(".py") for p in glob.glob(os.path.join(out, "*.py"))
    ]
    result: dict[str, object] = {
        "book": book,
        "notebooks": len(notebooks),
        "executed": len(per_section),
        "not_executed": sorted(set(notebooks) - set(per_section)),
        "totals": dict(totals),
        "sections": per_section,
    }
    with open(os.path.join(out, "summary.json"), "w", encoding="utf-8") as handle:
        json.dump(result, handle, indent=1, sort_keys=True)
    return result


def main(argv: list[str]) -> int:
    match argv:
        case ["generate", book, *only] if book in problems.BOOK_FOLDERS:
            return 0 if generate(book, only) else 1
        case ["summary", book] if book in problems.BOOK_FOLDERS:
            result: dict[str, object] = summary(book)
            print(json.dumps({k: v for k, v in result.items() if k != "sections"}, indent=1))
            return 1 if result["not_executed"] or not result["executed"] else 0
        case _:
            print(__doc__, file=sys.stderr)
            return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
