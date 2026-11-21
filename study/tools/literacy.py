#!/usr/bin/env python3
"""Generate the literacy tests from the question bank: test, answer key, scoring.

For each subject (bank/<subject>.toml, checked first by bank.py) this writes
three LaTeX files into the output directory:

- `<subject>.tex` -- the test: part A multiple choice (choices in the same fixed
  shuffled order the quiz server uses), part B free response with room to work;
- `<subject>-key.tex` -- every answer with its worked solution;
- `<subject>-scoring.tex` -- the scoring sheet: per strand, the question numbers,
  the points (1 per part-A question, 2 per part-B question: 2 right with work,
  1 partly right, 0), the "solid / shaky / not yet" bands, and the book sections
  to review.

Part A runs easy to hard (by difficulty, then strand order); part B follows.

Usage:  python3 tools/literacy.py <output-dir> [subject ...]
"""

from __future__ import annotations

import os
import sys

import bank
import studytex

LETTERS: str = "ABCDEFGH"
# Score bands, as a fraction of a strand's points.
SOLID: float = 0.8
SHAKY: float = 0.5
LICENSE_NOTE: str = (
    "Questions written for impo (\\url{https://github.com/billsix/impo}), MIT license; "
    "every answer is checked by computer (sympy). Review pointers cite OpenStax "
    "textbooks (CC BY 4.0, \\url{https://openstax.org})."
)


def numbered(subject: bank.Subject) -> list[bank.Question]:
    """The questions in test order (part A easy to hard, then part B)."""
    strand_order: dict[str, int] = {s.id: i for i, s in enumerate(subject.strands)}
    part_a: list[bank.Question] = sorted(
        (q for q in subject.questions if q.part == "A"),
        key=lambda q: (q.difficulty, strand_order[q.strand]),
    )
    part_b: list[bank.Question] = sorted(
        (q for q in subject.questions if q.part == "B"),
        key=lambda q: strand_order[q.strand],
    )
    return part_a + part_b


def choices_line(question: bank.Question) -> str:
    """The lettered choices of one question, in quiz order."""
    texts: list[str] = bank.choice_texts(question)
    return "\\\\[0.3em]\n".join(
        "\\textbf{(%s)}~$%s$" % (LETTERS[slot], texts[i])
        for slot, i in enumerate(bank.choice_order(question))
    )


def test_tex(subject: bank.Subject) -> str:
    """The test itself."""
    order: list[bank.Question] = numbered(subject)
    count_a: int = sum(1 for q in order if q.part == "A")
    parts: list[str] = [
        studytex.preamble(
            subject.title, "%d questions, about %d minutes" % (len(order), subject.minutes)
        ),
        "Name: \\rule{6cm}{0.4pt}\\qquad Date: \\rule{3cm}{0.4pt}\\par\\medskip\n",
        "\\section*{Part A: Multiple choice}\n"
        "Circle the letter of the best answer. Work on scrap paper if you need to.\n"
        "\\begin{multicols}{2}\n\\begin{enumerate}\n",
    ]
    question: bank.Question
    for question in order[:count_a]:
        parts.append(
            "\\item %s\\par\\smallskip\n%s\n\\medskip\n" % (question.stem, choices_line(question))
        )
    parts.append(
        "\\end{enumerate}\n\\end{multicols}\n\\newpage\n"
        "\\section*{Part B: Show your work}\n"
        "Write each answer in the space below the question and show how you got it.\n"
        "\\begin{enumerate}\\setcounter{enumi}{%d}\n" % count_a
    )
    for question in order[count_a:]:
        parts.append("\\item %s\\par\\vspace{5.5cm}\n" % question.stem)
    parts.append("\\end{enumerate}\n")
    parts.append(studytex.footer(LICENSE_NOTE))
    return "".join(parts)


def key_tex(subject: bank.Subject) -> str:
    """The answer key with worked solutions."""
    order: list[bank.Question] = numbered(subject)
    parts: list[str] = [
        studytex.preamble(subject.title + " --- Answer Key", "answers and worked solutions")
    ]
    parts.append("\\begin{enumerate}\n")
    question: bank.Question
    for question in order:
        if question.part == "A":
            slot: int = bank.choice_order(question).index(bank.correct_choice(question))
            right: str = bank.choice_texts(question)[bank.correct_choice(question)]
            answer: str = "\\textbf{(%s)}~$%s$" % (LETTERS[slot], right)
        else:
            answer = "$%s$" % bank.answer_text(question)
        parts.append(
            "\\item \\textbf{Answer:} %s\\par\n{\\small %s}\\par\n" % (answer, question.solution)
        )
    parts.append("\\end{enumerate}\n")
    parts.append(studytex.footer(LICENSE_NOTE))
    return "".join(parts)


def scoring_tex(subject: bank.Subject) -> str:
    """The per-strand scoring sheet."""
    order: list[bank.Question] = numbered(subject)
    number: dict[str, int] = {q.id: i + 1 for i, q in enumerate(order)}
    parts: list[str] = [
        studytex.preamble(
            subject.title + " --- Scoring Sheet", "per strand: solid, shaky or not yet"
        ),
        "Score part A 1 point per correct answer. Score part B 2 points for a correct answer "
        "with correct work, 1 for partly correct work, 0 otherwise. For each strand, divide "
        "the points earned by the points possible: \\textbf{solid} at %d\\%% or more, "
        "\\textbf{shaky} from %d\\%% to %d\\%%, \\textbf{not yet} below %d\\%%. "
        "A shaky or not-yet strand lists the book sections to review.\\par\\medskip\n"
        % (round(SOLID * 100), round(SHAKY * 100), round(SOLID * 100) - 1, round(SHAKY * 100)),
    ]
    strand: bank.Strand
    for strand in subject.strands:
        mine: list[bank.Question] = [q for q in order if q.strand == strand.id]
        possible: int = sum(1 if q.part == "A" else 2 for q in mine)
        questions: str = ", ".join(
            "%d%s" % (number[q.id], "" if q.part == "A" else " (B)") for q in mine
        )
        reviews: str = "\\\\\n".join(studytex.review_pointer(r) for r in strand.review)
        parts.append(
            "\\subsection*{%s}\n"
            "Questions: %s.\\quad Points: \\rule{1.2cm}{0.4pt} / %d\\par "
            "$\\square$ solid\\quad $\\square$ shaky\\quad $\\square$ not yet\\par\n"
            "{\\small Review: %s}\\par\n" % (strand.name, questions, possible, reviews)
        )
    parts.append(studytex.footer(LICENSE_NOTE))
    return "".join(parts)


def main(argv: list[str]) -> int:
    if not argv:
        print(__doc__, file=sys.stderr)
        return 2
    out: str = argv[0]
    os.makedirs(out, exist_ok=True)
    status: int = 0
    name: str
    for name in argv[1:] or list(bank.SUBJECTS):
        subject: bank.Subject = bank.load(name)
        problems: list[str] = bank.check(subject)
        if problems:
            print("literacy: %s has bank problems; run tools/bank.py check" % name, file=sys.stderr)
            status = 1
            continue
        suffix: str
        text: str
        for suffix, text in (
            ("", test_tex(subject)),
            ("-key", key_tex(subject)),
            ("-scoring", scoring_tex(subject)),
        ):
            with open(os.path.join(out, "%s%s.tex" % (name, suffix)), "w", encoding="utf-8") as f:
                f.write(text)
        print("literacy: wrote %s{,-key,-scoring}.tex in %s" % (name, out))
    return status


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
