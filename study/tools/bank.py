#!/usr/bin/env python3
"""The literacy-test question bank: load, check every answer with sympy, export.

The bank's source is one TOML file per subject (`bank/<subject>.toml`, written by
hand/AI, reviewed). Each question names its answer by computation, not by
assertion: `compute` is a sympy expression for the problem's answer, and

- a multiple-choice question (part A) lists `choices` as sympy expressions; the
  answer is the ONE choice equal to `compute` (no match, or two matches, is an
  error, so a wrong key or an accidentally-correct distractor cannot ship);
- a free-response question (part B) gives `answer`, which must equal `compute`.

`python3 tools/bank.py check` checks every subject; `python3 tools/bank.py export`
also writes `bank/json/<subject>.json` (choices shuffled into a fixed order, each
text in LaTeX and in HTML with MathML via pandoc), the file the quiz server
(`study/quiz/`) embeds. That JSON is generated but committed, so the Go build
needs no Python, sympy or pandoc; `bank.py export --check` (in `make test`) fails
when it is stale.

Expressions are evaluated with sympy's namespace and the symbols a-z, so
`solve(Eq(2*x + 3, 11), x)` works; a Python list result is a solution SET
(compared as a FiniteSet), a tuple is an ordered tuple (a point).
"""

from __future__ import annotations

import dataclasses
import json
import os
import random
import re
import string
import subprocess
import sys
import tomllib
from collections.abc import Callable
from typing import Any, TypeAlias

import sympy

# Evaluated sympy value of a `compute` / `choices` / `answer` string.
Value: TypeAlias = Any

STUDY: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BANK_DIR: str = os.path.join(STUDY, "bank")
JSON_DIR: str = os.path.join(BANK_DIR, "json")
SUBJECTS: tuple[str, ...] = ("prealgebra", "algebra-1", "geometry", "algebra-2")

# sympy's names, the Python builtins a computation needs, and every letter as a
# symbol (an upper-case letter only where sympy has no meaning for it: E, I, N,
# O, Q and S stay sympy's).
SYMPY_NAMES: dict[str, Any] = {
    name: getattr(sympy, name) for name in dir(sympy) if not name.startswith("_")
}
NAMESPACE: dict[str, Any] = {
    **{letter: sympy.Symbol(letter) for letter in string.ascii_uppercase},
    **SYMPY_NAMES,
    **{letter: sympy.Symbol(letter) for letter in string.ascii_lowercase},
    **{f.__name__: f for f in (abs, len, max, min, sorted, tuple, list, range)},
}


@dataclasses.dataclass(frozen=True)
class Strand:
    """One topic of a test, with the book sections to review when it is weak."""

    id: str
    name: str
    review: list[str]


@dataclasses.dataclass(frozen=True)
class Question:
    """One question; `choices`/`choices_tex` are empty for free response."""

    id: str
    part: str
    strand: str
    difficulty: int
    stem: str
    compute: str
    solution: str
    choices: list[str]
    choices_tex: list[str]
    answer: str
    answer_tex: str
    compare: str


@dataclasses.dataclass(frozen=True)
class Subject:
    """One subject's bank: metadata, strands, time limits and questions."""

    subject: str
    title: str
    minutes: int
    standards: str
    time_limits: dict[int, int]
    strands: list[Strand]
    questions: list[Question]


def evaluate(expression: str) -> Value:
    """Evaluate a bank expression with sympy (lists become solution sets).

    >>> evaluate("Rational(3, 4) + Rational(1, 6)")
    11/12
    >>> evaluate("solve(x**2 - 5*x + 6, x)")
    {2, 3}
    """
    value: Value = eval(expression, {"__builtins__": {}, **NAMESPACE})  # noqa: S307 (trusted data)
    match value:
        case list():
            return sympy.FiniteSet(*value)
        case tuple():
            return sympy.Tuple(*value)
        case int() | float():
            return sympy.sympify(value)
        case _:
            return value


def equal(first: Value, second: Value) -> bool:
    """True when two evaluated values are mathematically the same.

    >>> equal(evaluate("sqrt(8)"), evaluate("2*sqrt(2)"))
    True
    >>> equal(evaluate("[3, 2]"), evaluate("FiniteSet(2, 3)"))
    True
    >>> equal(evaluate("(1, 2)"), evaluate("(2, 1)"))
    False
    """
    if isinstance(first, sympy.Expr) and isinstance(second, sympy.Expr):
        return sympy.simplify(first - second) == 0
    if isinstance(first, sympy.Tuple) and isinstance(second, sympy.Tuple):
        return len(first) == len(second) and all(
            equal(a, b) for a, b in zip(first, second, strict=True)
        )
    if isinstance(first, sympy.Basic) and isinstance(second, sympy.Basic):
        return bool(sympy.simplify(first) == sympy.simplify(second))
    return bool(first == second)


def factors(value: Value) -> list[Value]:
    """The factors of a product, nested products flattened (one item otherwise).

    >>> factors(evaluate_unevaluated("3*(x - 3)*(x + 3)"))
    [3, x - 3, x + 3]
    """
    if isinstance(value, sympy.Mul):
        return [f for arg in value.args for f in factors(arg)]
    return [value]


def evaluate_unevaluated(expression: str) -> Value:
    """Evaluate a bank expression WITHOUT sympy's automatic simplification, so a
    written form such as `3*(x - 3)*(x + 3)` keeps its factors."""
    with sympy.evaluate(False):
        return evaluate(expression)


def same_form(first: Value, second: Value) -> bool:
    """True when two products have the same factors, each equal in value (for
    "factor completely" questions, where every choice has the same value).

    >>> same_form(evaluate_unevaluated("3*(x - 3)*(x + 3)"), evaluate("factor(3*x**2 - 27)"))
    True
    >>> same_form(evaluate_unevaluated("3*(x**2 - 9)"), evaluate("factor(3*x**2 - 27)"))
    False
    """
    remaining: list[Value] = factors(second)
    factor: Value
    for factor in factors(first):
        match_index: int | None = next(
            (i for i, other in enumerate(remaining) if equal(factor, other)), None
        )
        if match_index is None:
            return False
        remaining.pop(match_index)
    return not remaining


def comparison(question: Question) -> Callable[[Value, Value], bool]:
    """The equality a question's `compare` field selects."""
    match question.compare:
        case "value":
            return equal
        case "form":
            return same_form
        case other:
            raise ValueError("%s: compare must be value or form, not %s" % (question.id, other))


def to_latex(expression: str) -> str:
    """LaTeX for a bank expression, as sympy prints its value."""
    return sympy.latex(evaluate(expression))


def load(subject: str) -> Subject:
    """Read and type one subject's TOML source."""
    with open(os.path.join(BANK_DIR, "%s.toml" % subject), "rb") as handle:
        raw: dict[str, Any] = tomllib.load(handle)
    strands: list[Strand] = [Strand(s["id"], s["name"], list(s["review"])) for s in raw["strands"]]
    questions: list[Question] = [
        Question(
            id=q["id"],
            part=q["part"],
            strand=q["strand"],
            difficulty=int(q["difficulty"]),
            stem=q["stem"].strip(),
            compute=q["compute"],
            solution=q["solution"].strip(),
            choices=list(q.get("choices", [])),
            choices_tex=list(q.get("choices_tex", [])),
            answer=q.get("answer", ""),
            answer_tex=q.get("answer_tex", ""),
            compare=q.get("compare", "value"),
        )
        for q in raw["questions"]
    ]
    return Subject(
        subject=subject,
        title=raw["title"],
        minutes=int(raw["minutes"]),
        standards=raw.get("standards", ""),
        time_limits={int(k): int(v) for k, v in raw["time_limits"].items()},
        strands=strands,
        questions=questions,
    )


def correct_choice(question: Question) -> int:
    """Index of the one choice equal to `compute`; ValueError unless exactly one."""
    target: Value = evaluate(question.compute)
    same: Callable[[Value, Value], bool] = comparison(question)
    parse: Callable[[str], Value] = evaluate_unevaluated if question.compare == "form" else evaluate
    matches: list[int] = [
        i for i, choice in enumerate(question.choices) if same(parse(choice), target)
    ]
    if len(matches) != 1:
        raise ValueError(
            "%s: %d choices equal compute=%s (want exactly 1)"
            % (question.id, len(matches), question.compute)
        )
    return matches[0]


def check(bank: Subject) -> list[str]:
    """Every problem with the subject's bank, as messages (empty = all good)."""
    problems: list[str] = []
    strand_ids: set[str] = {s.id for s in bank.strands}
    seen: set[str] = set()
    question: Question
    for question in bank.questions:
        if question.id in seen:
            problems.append("%s: duplicate id" % question.id)
        seen.add(question.id)
        if question.strand not in strand_ids:
            problems.append("%s: unknown strand %s" % (question.id, question.strand))
        if question.difficulty not in bank.time_limits:
            problems.append(
                "%s: no time limit for difficulty %d" % (question.id, question.difficulty)
            )
        try:
            match question.part:
                case "A":
                    correct_choice(question)
                    if question.choices_tex and len(question.choices_tex) != len(question.choices):
                        problems.append("%s: choices_tex length differs" % question.id)
                case "B":
                    answer: Value = (
                        evaluate_unevaluated(question.answer)
                        if question.compare == "form"
                        else evaluate(question.answer)
                    )
                    if not comparison(question)(answer, evaluate(question.compute)):
                        problems.append(
                            "%s: answer %s != compute %s"
                            % (question.id, question.answer, question.compute)
                        )
                case other:
                    problems.append("%s: part must be A or B, not %s" % (question.id, other))
        except Exception as error:  # noqa: BLE001 -- report every bad entry, then fail
            problems.append("%s: %s" % (question.id, error))
    return problems


def choice_order(question: Question) -> list[int]:
    """A fixed shuffle of the choices (seeded by the question id), so the right
    answer is not always first and a re-export is byte-identical."""
    order: list[int] = list(range(len(question.choices)))
    random.Random(question.id).shuffle(order)
    return order


def choice_texts(question: Question) -> list[str]:
    """Each choice's LaTeX (math mode content), in the bank's order."""
    if question.choices_tex:
        return list(question.choices_tex)
    if question.compare == "form":
        return [sympy.latex(evaluate_unevaluated(c)) for c in question.choices]
    return [to_latex(c) for c in question.choices]


def answer_text(question: Question) -> str:
    """The free-response answer's LaTeX (math mode content)."""
    return question.answer_tex or to_latex(question.answer)


def to_html(snippets: dict[str, str]) -> dict[str, str]:
    """Render LaTeX-flavoured text snippets ($math$, prose) to HTML with MathML.

    One pandoc call for all snippets: each becomes a fenced div whose id is the
    dict key, and the divs are split back out of pandoc's output.
    """
    source: str = "\n\n".join("::: {#%s}\n%s\n:::" % (key, text) for key, text in snippets.items())
    html: str = subprocess.run(
        ["pandoc", "-f", "markdown", "-t", "html", "--mathml", "--wrap=none"],
        input=source,
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    found: dict[str, str] = {
        m.group(1): m.group(2).strip()
        for m in re.finditer(r'<div id="([^"]+)">\n?(.*?)\n?</div>', html, re.S)
    }
    missing: list[str] = [key for key in snippets if key not in found]
    if missing:
        raise RuntimeError("pandoc lost snippets: %s" % missing[:5])
    return found


def export(bank: Subject) -> dict[str, Any]:
    """The quiz server's JSON for one subject (see the module docstring)."""
    snippets: dict[str, str] = {}
    question: Question
    for question in bank.questions:
        snippets["%s-stem" % question.id] = question.stem
        snippets["%s-solution" % question.id] = question.solution
        i: int
        tex: str
        for i, tex in enumerate(choice_texts(question)):
            snippets["%s-choice-%d" % (question.id, i)] = "$%s$" % tex
    html: dict[str, str] = to_html(snippets)
    questions: list[dict[str, Any]] = []
    for question in bank.questions:
        entry: dict[str, Any] = {
            "id": question.id,
            "part": question.part,
            "strand": question.strand,
            "difficulty": question.difficulty,
            "stem_tex": question.stem,
            "stem_html": html["%s-stem" % question.id],
            "solution_tex": question.solution,
            "solution_html": html["%s-solution" % question.id],
        }
        if question.part == "A":
            order: list[int] = choice_order(question)
            texts: list[str] = choice_texts(question)
            right: int = correct_choice(question)
            entry["choices"] = [
                {"tex": texts[i], "html": html["%s-choice-%d" % (question.id, i)]} for i in order
            ]
            entry["answer"] = order.index(right)
        else:
            entry["answer_tex"] = answer_text(question)
        questions.append(entry)
    return {
        "subject": bank.subject,
        "title": bank.title,
        "minutes": bank.minutes,
        "time_limits": {str(k): v for k, v in sorted(bank.time_limits.items())},
        "strands": [dataclasses.asdict(s) for s in bank.strands],
        "questions": questions,
        "license": "Questions written for impo (github.com/billsix/impo), MIT license.",
    }


def export_text(bank: Subject) -> str:
    """The exported JSON file's exact text."""
    return json.dumps(export(bank), indent=1, ensure_ascii=False) + "\n"


def main(argv: list[str]) -> int:
    match argv:
        case ["check" | "export" as command, *rest]:
            stale_only: bool = command == "export" and rest[:1] == ["--check"]
            subjects: list[str] = [s for s in rest if s != "--check"] or list(SUBJECTS)
            failed: bool = False
            subject: str
            for subject in subjects:
                bank: Subject = load(subject)
                problems: list[str] = check(bank)
                print(
                    "bank %s: %d questions, %d problems"
                    % (subject, len(bank.questions), len(problems))
                )
                print("".join("  %s\n" % p for p in problems), end="")
                failed = failed or bool(problems)
                if command != "export" or problems:
                    continue
                path: str = os.path.join(JSON_DIR, "%s.json" % subject)
                text: str = export_text(bank)
                if stale_only:
                    current: str = ""
                    if os.path.exists(path):
                        with open(path, encoding="utf-8") as f:
                            current = f.read()
                    if current != text:
                        print("  %s is stale: run make bank" % path)
                        failed = True
                    continue
                os.makedirs(JSON_DIR, exist_ok=True)
                with open(path, "w", encoding="utf-8") as f:
                    f.write(text)
            return 1 if failed else 0
        case _:
            print("usage: bank.py check|export [--check] [subject ...]", file=sys.stderr)
            return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
