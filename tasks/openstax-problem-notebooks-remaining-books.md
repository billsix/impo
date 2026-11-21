# Problem notebooks for the rest of the math ladder (and better solving)

**Status:** proposed — needs go-ahead
**Priority:** 7
**Difficulty:** 7
**Created:** 2026-11-21 (follow-on of `tasks/archive/impo/2026/11/21/openstax-problem-notebooks.md`)

## BLUF

The problem-notebook pipeline exists and Prealgebra 2e is done end to end (every exercise of every
section restated in an executed notebook, the mechanical ones solved by sympy and checked against the
answer key, graphing exercises drawn with ePiX). The other math-ladder books are not generated yet,
and most exercises in any book are "manual" (restated only). Done = notebooks generated and executed
for every remaining ladder book, each book's status totals recorded in
`tasks/reference/study/status.md`, and the automatic-solve rate raised where it is cheap.

## Context

- Pipeline and statuses: `study/CLAUDE.md`, `study/tools/solver.py` (module docstring),
  `study/tools/notebooks.py`; command `make -C study problem-notebooks BOOK=<book>`.
- Prerequisite per book: its folder's converted LaTeX
  (`cd openstax/<folder> && ./fetch.sh && ./apply.sh && make convert`), and its page index in
  `openstax/tooling/tools/cnxml2tex/crossbook/index/` (every ladder book but algebra-1 has one).
- Exercise counts (CNXML `<exercise>`, with a `<solution>`), from
  `tasks/archive/impo/2026/11/21/openstax-problem-notebooks.md`:

  | book | exercises | with answer | notebooks |
  |---|---|---|---|
  | prealgebra-2e | 8105 (7368 exercises + 737 worked examples) | 5240 | **done** |
  | elementary-algebra-2e | 9406 | 6106 | not generated |
  | intermediate-algebra-2e | 8209 | 5238 | not generated |
  | college-algebra-2e | 6087 | 3551 | not generated |
  | precalculus-2e | 7250 | 4279 | not generated (only as a Calculus-1 prerequisite source) |
  | calculus-volume-1 | 3029 | 1796 | not generated |
  | calculus-volume-2 | 3138 | 1783 | not generated |
  | calculus-volume-3 | 3093 | 1803 | not generated |
  | algebra-1 | 4577 (932 os-embed) | 3642 | not supported yet: it has no page index (its pages are named by slug, not `mod:` id, so `crossbook_index.py` would need a module lookup), and its 932 os-embed exercises have no answers |

## Plan

1. Generate + execute each remaining book, one at a time; record its totals.
2. Raise coverage where cheap: calculus tasks ("find the derivative", "evaluate the integral",
   "find the limit") map onto `sympy.diff` / `integrate` / `limit`; word problems stay manual.
3. Review the MISMATCH list of each book (several Prealgebra mismatches are OpenStax answer-key
   errors, e.g. §7.3 `9(u-4)` answered `9y - 36`); report real errata.
4. Algebra 1: key its sections by page instead of module, or skip it (decide).
