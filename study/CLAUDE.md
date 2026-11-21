# study — literacy tests, cliff notes, problem notebooks and the quiz server

The **study** family holds study material built on top of the books, not books
themselves: four **literacy tests** (prealgebra, algebra 1, geometry, algebra 2), four
**cliff-notes** study guides for the same subjects, **problem notebooks** (every exercise
of a math-ladder book restated, solved by sympy where it is mechanical, checked against
the book's answer key, graphed with ePiX), and a Go **quiz server** that gives the
literacy tests' multiple-choice part as a timed quiz. Read the repo-root `CLAUDE.md`
first. Added 2026-11-21 (William Emerison Six <billsix@gmail.com>).

## How it reuses the OpenStax toolchain

- **Image:** `make image` builds `../openstax/tooling` (tag `osbook-study-base`, a cache
  hit on any machine that built a book) and adds `python3-sympy` (`./Dockerfile`, tag
  `impo-study`). The notebook image (`notebooks/Dockerfile`, `impo-study-notebooks`) adds a
  uv `/venv` pinned by `notebooks/constraints.txt` (Jupyter, jupytext, sympy, the
  antlr LaTeX-parser runtime) and ePiX built from github.com/billsix/epix-mirror at
  `EPIX_COMMIT` (scripts copied from github.com/billsix/geometricalgebra). The quiz has its
  own Fedora + golang image (`quiz/Dockerfile`).
- **Mount:** the whole impo checkout is mounted at `/impo` (`:z`), work dir `/impo/study`,
  because the generators read `../openstax/tooling/latex/` (the house class `osbook.cls`,
  via `TEXINPUTS`) and the cross-book index `../openstax/tooling/tools/cnxml2tex/crossbook/`
  (section titles and published URLs for every "review" pointer).
- **Problems come from the converter's output:** `tools/problems.py` reads a book folder's
  generated `checkout/latex/sections/<module>.tex` (`make convert` in that folder), in the
  section order of the cross-book index — the same exercises the PDF prints.

## Layout

- `bank/<subject>.toml` — the question bank (source): strands with review pointers, time
  limits per difficulty, 30 questions per subject (24 part-A multiple choice, 6 part-B free
  response). Each question's answer is a **sympy computation** (`compute`): multiple choice
  must have exactly one choice equal to it (`compare = "form"` for "factor" questions, where
  every choice has the same value); free response must equal `answer`. `tools/bank.py`.
- `bank/json/<subject>.json` — **generated but committed** (the quiz embeds it, and the Go
  image has no Python/pandoc); `make bank` regenerates it, and `make test` fails when stale.
- `cliffnotes/<subject>.toml` — one entry per chapter: rules, worked examples, practice;
  every example/practice answer sympy-checked. `tools/cliffnotes.py`.
- `tools/` — `bank.py`, `literacy.py` (test, key, scoring sheet), `cliffnotes.py`,
  `studytex.py` (shared LaTeX + review-pointer links), `problems.py`, `solver.py`,
  `notebooks.py`, `nbplot.py` (ePiX graphs; imports `epix` only when drawing).
- `entrypoint/` — `build-pdfs.sh`, `build-notebooks.sh`, `check.sh` (the gate).
- `quiz/` — the Go server; see `quiz/README.md`.
- `output/` — generated PDFs and notebooks (gitignored).

## Contracts

- **Licensing.** New questions, examples and practice problems are the maintainer's (MIT).
  The cliff notes follow an OpenStax book's chapters and say so (CC BY 4.0 attribution in
  each PDF); the notebooks restate OpenStax exercises (CC BY 4.0, attribution in each
  notebook's header). Geometry has no OpenStax book: its strands and chapters follow the
  Common Core high-school geometry standards.
- **No unchecked answer ships.** The generators refuse a subject whose bank/guide check
  fails; `make test` runs every check.
- **Python house rules** as in `openstax/tooling`: every binding annotated (the shared
  `check_local_annotations.py`), Google docstrings, `match` + `case _`.

## Commands

`make test`, `make literacy-tests`, `make cliff-notes`, `make bank`,
`make problem-notebooks BOOK=prealgebra-2e [SECTIONS="3.2 11.3"]`; quiz: `make -C quiz test`.
Status per deliverable (what is complete, what remains): `tasks/reference/study/status.md`.
