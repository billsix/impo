# study/ — what each deliverable covers, and what remains

**Reference doc — living.** The state of the study family (`study/CLAUDE.md`): per deliverable,
what exists, how it was verified, and where the remaining work is tracked. Built 2026-11-21 in
`tasks/archive/impo/2026/11/21/math-literacy-tests-latex.md`, `…/math-cliff-notes-latex.md`,
`…/openstax-problem-notebooks.md` and `…/student-quiz-web-go.md`.

## Literacy tests (`make literacy-tests`)

- Four subjects × 30 questions (24 multiple choice, 6 free response; 6 strands × 5 questions),
  45–50 minutes each: prealgebra (Prealgebra 2e), algebra-1 (Elementary Algebra 2e / Algebra 1),
  geometry (Common Core G-CO, G-SRT, G-C, G-GPE, G-GMD, G-MG), algebra-2 (Intermediate Algebra 2e).
- Per subject three PDFs: the test (part A in two columns, choices in the quiz's fixed shuffled
  order; part B with work space), the answer key with worked solutions, the scoring sheet (points per
  strand, solid ≥ 80 % / shaky 50–79 % / not yet < 50 %, review links to the book sections).
- All 120 answers are sympy computations, checked by `tools/bank.py check` (in `make test`).
  The questions are AI-written and have not yet been tried on a student.

## Cliff notes (`make cliff-notes`)

- prealgebra 11 chapters (Prealgebra 2e), algebra-1 10 (Elementary Algebra 2e), geometry 7 (Common
  Core groups), algebra-2 12 (Intermediate Algebra 2e): per chapter a key-rules box, 2 worked examples
  with solutions, 3 practice problems with answers, links to the book's sections; about one page per
  chapter. 200 example/practice answers, all sympy-checked (`tools/cliffnotes.py check`).

## Problem notebooks (`make problem-notebooks BOOK=…`)

See the problem-notebook record and `tasks/openstax-problem-notebooks-remaining-books.md`.

## Quiz server (`study/quiz/`)

- Go standard library only; embeds `bank/json/*.json`; server-enforced time limit per difficulty
  (limit + 2 s grace), one question at a time, no going back, per-strand results, `/admin` behind
  `QUIZ_ADMIN_PASSWORD`, private-network-only filter. `make -C study/quiz test` (gofmt, vet, 12 tests).
