# AI-written LaTeX literacy tests: prealgebra, algebra 1, geometry, algebra 2

**Done 2026-11-21** (branch `study-and-publishing`). Not yet tried on a student; the questions are
AI-written and await the maintainer's read. State of the study family:
`tasks/reference/study/status.md`; contracts: `study/CLAUDE.md`.

## Decisions (William Emerison Six <billsix@gmail.com>, 2026-11-21: "go with your recommendations")

- Geometry strands from the Common Core high-school geometry standards; "Algebra 2" = Intermediate
  Algebra 2e; part A multiple choice + part B show-your-work; about 30 questions and 40–50 minutes;
  a new `study/` family reusing `openstax/tooling/`'s image and class.

## Choices made while building (the maintainer was away)

- **Bank source = TOML per subject** (`study/bank/<subject>.toml`): multi-line literal strings hold
  LaTeX without escaping, and Python reads it with the standard library. **Answers are computations**:
  `compute` (a sympy expression) must equal exactly one multiple-choice option (so a wrong key or a
  second correct option fails the check) or the free-response `answer`; `compare = "form"` handles
  "factor completely" questions whose options are all equal in value.
- **The quiz's copy is generated JSON, committed** (`study/bank/json/`), with every text also in HTML +
  MathML (pandoc), so the Go build needs no Python/pandoc; `make test` fails when it is stale.
- Shape per subject: 6 strands × (4 multiple choice + 1 free response) = 30 questions; part A ordered
  easy to hard; free response scored 0/1/2; bands solid ≥ 80 %, shaky 50–79 %, not yet < 50 %.
- Outputs in `study/output/literacy/` (the family's own output dir, like a book folder's).
- New questions are MIT; review pointers cite the OpenStax books by section through the cross-book
  index (`openstax/tooling/tools/cnxml2tex/crossbook.py`), linked to the published site.

## What was built

- `study/` family: `Dockerfile` (the toolchain image + sympy), `Makefile` (`image`, `test`,
  `literacy-tests`, `bank`, `format`, `shell`), `entrypoint/build-pdfs.sh`, `entrypoint/check.sh`
  (ruff, the shared annotation checker, ty, pytest, the bank/cliff-notes checks, the stale-JSON
  check), `pyproject.toml`, `CLAUDE.md`, `README.md`.
- `study/tools/bank.py` (load, check, export), `study/tools/literacy.py` (test, answer key, scoring
  sheet), `study/tools/studytex.py` (osbook preamble, review-pointer links).
- `study/bank/{prealgebra,algebra-1,geometry,algebra-2}.toml`: 120 questions (96 multiple choice,
  24 free response), and `study/bank/json/*.json`.
- Repo docs: `CLAUDE.md` (the third family), `README.md`, `tasks/reference/study/status.md`.

## Verification

- `tools/bank.py check`: 120 questions, 0 problems; the checker caught real slips while writing (two
  options of "√72" equal in value, a factored-form question with three equal options, a complex
  root from `solve`), each fixed in the bank.
- `make -C study test` (container): exit 0 — ruff, annotations, ty, 20 pytest (incl. tests that a
  wrong key, two right options and a wrong free-response answer are caught), every check, and the
  committed JSON identical to a fresh export.
- `make -C study literacy-tests` (container): exit 0, 12 PDFs (tests 5–6 pages, keys 3, scoring
  sheets 2).
- Read by eye: the prealgebra test (8 pages before part A went to two columns) and its scoring
  sheet; the other subjects only through the build and the checks.
