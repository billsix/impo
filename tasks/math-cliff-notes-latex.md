# Cliff-notes LaTeX study guide per book: worked examples and solutions first

**Status:** proposed — needs go-ahead (open questions below)
**Priority:** 5
**Difficulty:** 7 (one condensed guide per book; scale depends on which books)
**Created:** 2026-11-21 (William Emerison Six <billsix@gmail.com>)

## BLUF

For each book, write a short LaTeX **study guide** in the style of Cliff Notes: per section, the one
or two rules that matter, then **worked examples with full solutions**, step by step, then a few
practice problems with answers. The guides are led by examples and solutions, not by prose. Done =
one PDF per book in scope, built by a `make` target in the osbook house style, each section linking
back to the full book's section.

## Context

- Read first: `CLAUDE.md`, `openstax/CLAUDE.md` (house class `osbook.cls`, licensing),
  `tasks/reference/openstax/book-inventory.md`, and the sibling
  `tasks/math-literacy-tests-latex.md` (same subjects, same "where in the repo" question, its Open
  question 5).
- "Each one" is read as each subject of the literacy tests (prealgebra, algebra 1, geometry,
  algebra 2), i.e. the same scope as that task. Open question 1 checks.
- Licensing: a condensed guide that follows an OpenStax book's structure and adapts its examples is
  a derivative of CC BY content and must carry the attribution ("based on OpenStax *<title>*, CC BY
  4.0", with a link). New examples are the maintainer's.
- Every worked solution's answer is checked by sympy before it ships (same mechanism as the tests'
  question bank), so a wrong solution never reaches a child.

## Plan

1. One section of one book (e.g. Prealgebra 2e ch. 1) as a sample for the maintainer to approve the
   format (length, density, example count).
2. That whole book, then the rest of the scope.
3. `make cliff-notes` → `output/cliff-notes/<book>.pdf`.

## Open questions

1. **Scope:** the four literacy-test subjects only, or every math book in impo (adding College
   Algebra, Calculus 1–3, Contemporary Mathematics), or every book including the sciences?
   *Recommend the four subjects first.*
2. **Length target:** about how many pages per book? *Recommend 1–2 pages per chapter.*
3. **Geometry:** no geometry book in impo, so its guide has no book to follow. Same choice as the
   literacy tests' Open question 1; *recommend whatever is decided there.*
