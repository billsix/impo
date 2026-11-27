# Added `osbooks-college-success-bundle` to impo (3 books)

**Done 2026-11-27** (agent; part of `tasks/openstax-add-remaining-english-books.md`. William Emerison Six <billsix@gmail.com>, 2026-11-27: "you can make a branch, temporarily turn off gpg signing, and start working on all of them (minus the business ones for now)").

## What was added

`openstax/osbooks-college-success-bundle/`, created with `tools/add-book.sh college-success-bundle "College Success"` and pinned at the upstream head `cca7cd1d4ab230f2e2cb6131ed7e161d50548f07`. It builds 3 books:

| Book | Collection | Shape | PDF | Web pages |
|---|---|---|---|---|
| *College Success 2e* | `college-success-2e` | 75 modules in 12 chapters; one level of nesting | 468 pages | 89 |
| *College Success Concise* | `college-success-concise` | 44 modules in 8 chapters; one level of nesting | 294 pages | 54 |
| *Preparing for College Success* | `preparing-for-college-success` | 49 modules in 9 chapters; one level of nesting | 325 pages | 60 |

- **Licence:** CC BY-NC-SA 4.0 (collection XML and the upstream `LICENSE`); the built PDF states it.
- **Figures:** raster only (300 files, 50 MB); no SVG.
- **Exercises:** none embedded, counted in the CNXML in both link schemes; no `exercises/` cache, so nothing for the maintainer to fetch.
- **Result:** built as PDF, EPUB and HTML on 2026-11-27; the final build log has no pandoc warning.

## What the book needed from the toolchain

**A root sign used as a tick mark.** A table of note-taking symbols in two modules holds a bare `√`. The converter writes it as `$\surd$`, which LaTeX sets and pandoc's math reader does not know: the first build's HTML and EPUB printed the TeX and the log had nine warnings. `openstax/tooling/tools/pandoc/preprocess.py` now puts the character back for the web editions (`tasks/reference/tooling/converters.md`, "Block quotations, reference notes and footnotes in titles"); the rebuilt web editions have no pandoc warning.

## Left as it is

The converter reports no fallback. The PDFs and HTML were not read page by page; that review is the maintainer's.

## Not done

The book needs the maintainer's public backup: `bash tools/mirror-upstreams.sh push college-success-bundle`.

## Recorded

`openstax/osbooks-college-success-bundle/CLAUDE.md` ("The books this folder builds"), the lists and counts in `openstax/CLAUDE.md` and the root `CLAUDE.md`, the inventory and its licence table, the converter quick reference and the umbrella's checklist. The survey table (`tasks/reference/openstax/upstream-book-repositories.md`) is refreshed once for the whole batch.
