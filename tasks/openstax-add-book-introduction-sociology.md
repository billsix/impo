# Added `osbooks-introduction-sociology` to impo (one book)

**Done 2026-11-27** (agent; part of `tasks/openstax-add-remaining-english-books.md`. William Emerison Six <billsix@gmail.com>, 2026-11-27: "you can make a branch, temporarily turn off gpg signing, and start working on all of them (minus the business ones for now)").

## What was added

`openstax/osbooks-introduction-sociology/`, created with `tools/add-book.sh introduction-sociology "Introduction to Sociology 3e"` and pinned at the upstream head `ab8839c5c5340cb4dffbc310699da450549deb20`. It builds one book:

| Book | Collection | Shape | PDF | Web pages |
|---|---|---|---|---|
| *Introduction to Sociology 3e* | `introduction-sociology-3e` | 96 modules in 21 chapters; one level of nesting | 828 pages | 119 |

- **Licence:** CC BY-NC-SA 4.0 (collection XML and the upstream `LICENSE`); the built PDF states it.
- **Figures:** raster only (642 files, 107 MB); no SVG.
- **Exercises:** none embedded, counted in the CNXML in both link schemes; no `exercises/` cache, so nothing for the maintainer to fetch.
- **Result:** built as PDF, EPUB and HTML on 2026-11-27; the final build log has no pandoc warning.

## What the book needed from the toolchain

**Empty labels.** The book puts an empty `<label/>` on 437 notes and solutions, which tells OpenStax's web edition to print no label there. The converter set nothing for them, which is right, but listed each one in its "Unknown/fallback elements" report. An empty label is known markup since this book (`tasks/reference/tooling/converters.md`, "Block quotations, reference notes and footnotes in titles"); the generated LaTeX is the same before and after.

## Left as it is

In module `m90145` a quiz question points at another exercise ("the experiment noted in …") and the PDF prints "??" there, because the converter gives exercises no label. The same gap affects 1,193 exercises in 14 book folders, so it has its own task: `tasks/openstax-links-to-exercises-print-question-marks.md`. The converter reports no fallback. The PDF and HTML were not read page by page; that review is the maintainer's.

## Not done

The book needs the maintainer's public backup: `bash tools/mirror-upstreams.sh push introduction-sociology`.

## Recorded

`openstax/osbooks-introduction-sociology/CLAUDE.md` ("The books this folder builds"), the lists and counts in `openstax/CLAUDE.md` and the root `CLAUDE.md`, the inventory and its licence table, the converter quick reference and the umbrella's checklist. The survey table (`tasks/reference/openstax/upstream-book-repositories.md`) is refreshed once for the whole batch.
