# AI-written LaTeX literacy tests: prealgebra, algebra 1, geometry, algebra 2

**Status:** proposed — needs go-ahead (open questions below)
**Priority:** 4
**Difficulty:** 6 (writing and checking four tests with answer keys; geometry has no source book here)
**Created:** 2026-11-21 (William Emerison Six <billsix@gmail.com>)

## BLUF

Write four LaTeX tests, **prealgebra, algebra 1, geometry, algebra 2**, that measure how much a
student understands each subject, so the maintainer can test his kids. Each test covers the
subject's main topics (strands), from easy to hard, and comes with an answer key and a scoring sheet
that turns the results into "solid / shaky / not yet" per strand, each strand pointing at the book
sections to review. The questions are written by AI and every answer is checked by computer
(sympy) before the test is used. Done = four printable PDFs + answer keys, built by one `make`
target in the house osbook style.

## Context

- Read first: `CLAUDE.md`, `openstax/CLAUDE.md` (the house LaTeX class `osbook.cls` in
  `openstax/tooling/`, licensing split), `trench/CLAUDE.md` (an example of reusing `osbook.cls`
  outside the converter), `tasks/reference/openstax/book-inventory.md`.
- Source books in impo for the strands and the "review" pointers:
  - prealgebra → Prealgebra 2e (`osbooks-prealgebra-bundle`);
  - algebra 1 → Algebra 1 (`osbooks-algebra-1`) and Elementary Algebra 2e (prealgebra bundle);
  - algebra 2 → Intermediate Algebra 2e (prealgebra bundle) and/or College Algebra
    (`osbooks-college-algebra-bundle`); OpenStax has no book titled "Algebra 2" (Open question 2);
  - geometry → **no geometry book in impo** (OpenStax has none). Open question 1.
- Licensing: the questions are newly written, not copied from OpenStax, so they are the
  maintainer's (MIT, like the toolchain). The review pointers cite the CC BY books by name and
  section. If any question is adapted from an OpenStax exercise, it carries the CC BY attribution.
- The same question bank should feed `tasks/student-quiz-web-go.md` (the timed quiz site). Store
  questions as data (YAML/JSON: strand, difficulty, stem, choices, answer, worked solution, sympy
  check) and generate the LaTeX from it, rather than writing LaTeX by hand.
- Siblings: `tasks/math-cliff-notes-latex.md` (study guides) and
  `tasks/openstax-problem-notebooks.md` (every problem solved in a notebook).

## Plan

1. Strand list per subject (from the books' tables of contents; Common Core high-school standards
   for geometry and algebra 2 if Open question 1/2 say so).
2. Question-bank schema + a generator (data → LaTeX test + key + scoring sheet); one subject end to
   end (prealgebra) for the maintainer to try on one child.
3. The other three subjects; every answer verified by a sympy check in the generator's test step.
4. `make literacy-tests` (in the osbook TeX image) → `output/literacy/<subject>{,-key}.pdf`.

## Open questions

1. **Geometry source:** impo has no geometry book. Base the strands on (a) the Common Core
   high-school geometry standards, (b) a specific textbook you name (possibly the same high-school
   geometry book as geometricalgebra's `tasks/book-opening-vectors-supersede-geometry-types.md`), or
   (c) skip geometry for now? *Recommend (a); it is public and standard.*
2. **"Algebra 2" = which book:** Intermediate Algebra 2e, College Algebra, or the Common Core
   Algebra II standards? *Recommend Intermediate Algebra 2e for strands, with review pointers into it.*
3. **Format:** (a) multiple choice only (fast to mark, matches the quiz site), (b) show-your-work
   free response, or (c) both, in two parts? *Recommend (c): multiple choice measures recall and
   speed, free response shows understanding.*
4. **Length and time:** about how long should one test take a child? *Recommend 40–50 minutes,
   about 30 questions.*
5. **Where in the repo:** a new top-level family folder (e.g. `study/` beside `openstax/` and
   `trench/`) for the tests, cliff notes, notebooks and quiz site, or a separate repo? *Recommend a
   `study/` folder in impo, reusing `openstax/tooling/`'s image and class.*
