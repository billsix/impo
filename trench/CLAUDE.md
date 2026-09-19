# trench — AIM open textbooks (native LaTeX source), restyled to OpenStax house look

The **trench** family carries the maintainer's restyle of open-source mathematics textbooks that ship
as **native LaTeX source** (as opposed to the OpenStax family's CNXML), into the same OpenStax house
look. Named for its first author, William F. Trench. Read the repo-root [`../CLAUDE.md`](../CLAUDE.md)
first (the impo carrier idea and the family layout); this tier-2 doc holds the trench family's
contract and its per-book index, and auto-loads for any session working under `trench/`.

## How this family differs from `openstax/`

1. **Source is LaTeX, not CNXML.** OpenStax books convert CNXML→LaTeX with a python converter
   (`openstax/tooling/tools/cnxml2tex/convert.py`). Trench books are *already* LaTeX, so there is no
   converter — the delta is a **LaTeX compatibility shim** that restyles the book's own class/macros
   onto `osbook.cls`.
2. **It REUSES the OpenStax toolchain, doesn't fork it.** Rather than duplicating the house style or
   promoting a repo-root shared `tooling/` (deferred — not worth refactoring 16 working books to add
   one), a trench book's `apply.sh` copies the osbook LaTeX layer from `../../openstax/tooling/latex/`
   and its `Makefile` builds the image from `../../openstax/tooling`. If a third family ever appears,
   revisit promoting the shared layer to the repo root.
3. **Same carrier shape otherwise.** Per-book `fetch.sh` (pin a pristine upstream into a gitignored
   `checkout/`), `apply.sh` (overlay), thin `Makefile`, `CLAUDE.md`/`README.md`. Content is the
   author's under its own license (**not** the maintainer's); the shim/toolchain is the maintainer's
   MIT.

## Per-book folder contract

`trench/<book>/`: `fetch.sh` + `apply.sh` + `Makefile` + `CLAUDE.md` + `README.md` + `.gitignore`,
plus `latex/` for that book's native shim (`trench-osbook.sty`). The fetched source and all build
artifacts live in the gitignored `checkout/`.

## Books

- **`elementary-differential-equations/`** — William F. Trench, *Elementary Differential Equations*
  (CC BY-NC-SA 3.0). github.com/billsix/differentialEquationsTrench @ `a7c17e3…`. **PDF + HTML + EPUB
  all build (2026-09-19)** — `make pdf`/`html`/`epub`. The web editions take a separate make4ht/
  tex4ebook path (native MathML), not `osbook.cls`. Tasks:
  `../tasks/add-trench-differential-equations-book.md` (main → PDF),
  `../tasks/add-trench-bv-and-student-manual.md` (BV variant + student manual, follow-on),
  `../tasks/trench-differential-equations-html-epub.md` (HTML/EPUB, done).
