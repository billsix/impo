# A Jupyter notebook for every problem in the main books: restate, solve, plot with ePiX

**Status:** proposed — needs go-ahead (decisions recorded 2026-11-21; no open questions)
**Priority:** 6
**Difficulty:** 9 (thousands of problems; every solution must be checked)
**Created:** 2026-11-21 (William Emerison Six <billsix@gmail.com>)

## BLUF

For every problem in the main books, write a Jupyter notebook entry that **restates the problem**,
**solves it** step by step (symbolically with sympy where it applies), and **plots** it with ePiX
where a picture helps (graphs, geometry, vectors). The solutions are checked by computer against
the book's answer key where the book has one. Done = notebooks for every problem in the chosen
books, organized one notebook per section, executed clean by a `make` target, with the plots
rendered.

## Context

- Read first: `CLAUDE.md`, `openstax/CLAUDE.md`, `tasks/reference/openstax/book-inventory.md`.
- **Scale is the first issue.** Exercise counts in the committed caches alone: Algebra 1 932,
  Contemporary Mathematics 3073, Organic Chemistry 1959, Biology 2337, Physics 846, Python 613. The
  end-of-section exercises written in the CNXML itself (prealgebra bundle, college algebra, calculus)
  are not in a cache and are not counted yet; the first step counts them. The total is likely in
  the tens of thousands across all books, so the scope must be narrowed (Decisions: the math ladder first).
- **Problem source:** the converter already parses every exercise (CNXML `<exercise>` and the
  os-embed caches) for the LaTeX build (`openstax/tooling/`), so the notebook generator reads the
  same parsed problems rather than scraping. OpenStax books give answers for odd-numbered exercises
  (the answer key); those become the check for each computed answer.
- **ePiX:** the maintainer's mirror github.com/billsix/epix-mirror. geometricalgebra already draws
  ePiX figures **live in notebook cells** through its Python `epix` package (nanobind, built from
  source and pinned by commit) and its scene helpers; that is the model to copy here (see that
  repo's `CLAUDE.md`, "ePiX in the image", and `tasks/reference/book-and-docs-pipeline.md`). It needs
  the ePiX build in this repo's image (a new image dependency).
- Notebooks as jupytext percent-format `.py` (diffable), converted to `.ipynb` at build, as in
  geometricalgebra. Licensing: a restated problem is CC BY OpenStax content; every notebook carries
  the attribution.
- Generated vs written: the restatement can be generated from the parsed problem; the solution and
  plot are AI-written per problem and must be verified (sympy equality with the answer key, or a
  numeric check). Problems with no checkable answer (proofs, explanations, word answers) are
  flagged for review, not silently accepted.

## Plan

1. Count the problems per book (a discovery script under `tasks/adhoc/openstax-problem-notebooks/`
   with a committed worklog) and report the totals, to settle the scope.
2. Image: add the ePiX build and Jupyter/sympy to an image (the osbook TeX image or a separate
   notebook image).
3. One section end to end (e.g. Algebra 1, one section): generator for the restatement, solutions,
   plots, answer-key check, `make problem-notebooks BOOK=…` executing them clean.
4. Fan out over the chosen books, one book at a time, each with its answer-key match rate recorded.

## Decisions (William Emerison Six <billsix@gmail.com>, 2026-11-21: "go with your recommendations")

- **Main books = the math ladder first:** prealgebra bundle, Algebra 1, College Algebra, Calculus 1–3.
- **Every problem;** even-numbered ones (no book answer) are marked "unchecked" until reviewed.
- **One notebook per section.**
- **Lives in `study/`** (as the literacy tests decided).
