# Review the 15 Prealgebra answers that disagree with the computed ones

**Status:** proposed — needs go-ahead
**Priority:** 5
**Difficulty:** 2
**Created:** 2026-11-21 (William Emerison Six <billsix@gmail.com>), from
`tasks/archive/impo/2026/11/21/openstax-problem-notebooks.md`.

## BLUF

The Prealgebra 2e problem notebooks flag 15 exercises where the sympy answer and OpenStax's answer key
disagree. Some are errors in OpenStax's key (e.g. §7.3 answers "9(u−4)" with "9y − 36"); others are the
exercise parser misreading the problem (e.g. long-division layouts). Sort each one, fix the parser
cases, mark the errata so the notebook shows the right answer and says the book's key is wrong, and
optionally report the errata to OpenStax. Done = 0 unexplained mismatches for Prealgebra 2e.

## Context

- Read first: `study/CLAUDE.md`, the archived task above ("What was built", the four status classes),
  and `tasks/openstax-problem-notebooks-remaining-books.md` step 3 (the same review for the other books).
- The pipeline: `study/tools/notebooks.py` (writes the notebooks), the solver/checker it calls, and
  `make -C study problem-notebooks BOOK=prealgebra-2e` (the gate). Find the MISMATCH list in its output.
- OpenStax takes errata through each book's page on openstax.org ("Report an error"); a report is the
  maintainer's call (it is outward-facing).

## Plan

1. List the 15 with the book's answer, the computed answer and the restated problem.
2. Parser misreads: fix the extraction and rerun. Key errors: record them in a small errata table the
   generator reads, so the notebook prints both answers with a note.
3. Rerun the gate; record the result; draft the errata report for the maintainer if any remain.
