"""Tests for the study generators: the bank's answer checks and the documents."""

from __future__ import annotations

import dataclasses

import bank
import cliffnotes
import literacy


def make_question(**changes: object) -> bank.Question:
    """A valid multiple-choice question, with fields overridden by `changes`."""
    base: bank.Question = bank.Question(
        id="t-1",
        part="A",
        strand="s",
        difficulty=1,
        stem="$1 + 1$",
        compute="1 + 1",
        solution="Add.",
        choices=["2", "3", "4", "5"],
        choices_tex=[],
        answer="",
        answer_tex="",
        compare="value",
    )
    return dataclasses.replace(base, **changes)


def make_subject(*questions: bank.Question) -> bank.Subject:
    """A one-strand subject holding `questions`."""
    return bank.Subject(
        subject="t",
        title="T",
        minutes=10,
        standards="",
        time_limits={1: 60},
        strands=[bank.Strand("s", "Strand", [])],
        questions=list(questions),
    )


def test_valid_question_passes() -> None:
    assert bank.check(make_subject(make_question())) == []


def test_wrong_key_is_caught() -> None:
    problems: list[str] = bank.check(make_subject(make_question(choices=["3", "4", "5", "6"])))
    assert problems and "0 choices" in problems[0]


def test_two_correct_choices_are_caught() -> None:
    problems: list[str] = bank.check(make_subject(make_question(choices=["2", "4/2", "4", "5"])))
    assert problems and "2 choices" in problems[0]


def test_free_response_mismatch_is_caught() -> None:
    question: bank.Question = make_question(part="B", choices=[], answer="3")
    assert bank.check(make_subject(question))


def test_duplicate_id_and_unknown_strand() -> None:
    problems: list[str] = bank.check(make_subject(make_question(), make_question(strand="nope")))
    assert any("duplicate" in p for p in problems)
    assert any("unknown strand" in p for p in problems)


def test_form_comparison_distinguishes_factorings() -> None:
    question: bank.Question = make_question(
        compute="factor(x**2 - 4)",
        compare="form",
        choices=["(x - 2)*(x + 2)", "x**2 - 4", "(x - 2)**2", "(x + 2)**2"],
    )
    assert bank.correct_choice(question) == 0


def test_choice_order_is_deterministic_permutation() -> None:
    question: bank.Question = make_question()
    assert bank.choice_order(question) == bank.choice_order(question)
    assert sorted(bank.choice_order(question)) == [0, 1, 2, 3]


def test_every_subject_bank_and_guide_is_correct() -> None:
    subject: str
    for subject in bank.SUBJECTS:
        loaded: bank.Subject = bank.load(subject)
        assert bank.check(loaded) == [], subject
        assert len(loaded.questions) >= 28, subject
        assert cliffnotes.check(cliffnotes.load(subject)) == [], subject


def test_literacy_numbering_puts_part_a_first() -> None:
    loaded: bank.Subject = bank.load("prealgebra")
    order: list[bank.Question] = literacy.numbered(loaded)
    parts: list[str] = [q.part for q in order]
    assert parts == sorted(parts)
    assert [q.difficulty for q in order if q.part == "A"] == sorted(
        q.difficulty for q in order if q.part == "A"
    )


def test_cliffnotes_check_catches_a_wrong_answer() -> None:
    item: cliffnotes.Problem = cliffnotes.Problem("p", "", "2 + 2", "5", "", "value")
    guide: cliffnotes.Guide = cliffnotes.Guide(
        "t", "T", "", [cliffnotes.Chapter("C", [], ["r"], [item], [item])]
    )
    assert len(cliffnotes.check(guide)) == 2
