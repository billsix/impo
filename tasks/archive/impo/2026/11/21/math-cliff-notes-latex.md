# Cliff-notes LaTeX study guides: worked examples and solutions first

**Done 2026-11-21** (branch `study-and-publishing`) for the four literacy-test subjects. Not yet
read by the maintainer. State: `tasks/reference/study/status.md`; contracts: `study/CLAUDE.md`.

## Decisions (William Emerison Six <billsix@gmail.com>, 2026-11-21: "go with your recommendations")

- Scope: prealgebra, algebra 1, geometry, algebra 2 (= Intermediate Algebra 2e); 1–2 pages per
  chapter; geometry follows the Common Core high-school geometry standards; lives in `study/`.

## Choices made while building

- Source per subject `study/cliffnotes/<subject>.toml`, one entry per chapter of the book it follows
  (Prealgebra 2e 11, Elementary Algebra 2e 10, Intermediate Algebra 2e 12; geometry 7 chapters by
  Common Core standard groups). Per chapter: a key-rules box (the house `keyconcepts` environment),
  2 worked examples with step-by-step solutions, 3 practice problems with answers at the chapter's
  end, and links to the full book's sections. Examples and practice are newly written (MIT); the
  rules summarize the book, and each PDF carries the OpenStax CC BY 4.0 attribution (geometry's has
  none to carry).
- The format sample-then-approve step of the plan was skipped (the maintainer was away); all four
  guides were written in the same format, so a format change is one generator edit.
- The checks reuse the bank's evaluator (`study/tools/bank.py`): every example's and practice
  problem's `compute` must equal its `answer`.

## What was built

- `study/tools/cliffnotes.py` (check, generate), `study/cliffnotes/*.toml` (40 chapters, 200 checked
  answers), `make -C study cliff-notes` → `study/output/cliff-notes/<subject>.pdf`; tests in
  `study/tests/test_study.py`.

## Verification

- `tools/cliffnotes.py check`: 40 chapters, 0 problems (it caught absolute-value inequalities that
  sympy only solves over the reals, fixed with `solveset(..., S.Reals)`).
- `make -C study test`: exit 0. `make -C study cliff-notes` (container): exit 0; page
  counts prealgebra 12, algebra-1 11, geometry 8, algebra-2 13 (with a contents page) — about one
  page per chapter.
- Read by eye: one Algebra 2 chapter page; the rest only through the build and the checks.
