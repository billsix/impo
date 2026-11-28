# Added `osbooks-principles-economics-bundle` to impo (5 books)

**Done 2026-11-28** (agent; part of `tasks/openstax-add-remaining-english-books.md`. William Emerison Six <billsix@gmail.com>, 2026-11-28: "work them all, do the work, commit, archive, commit, next").

## What was added

`openstax/osbooks-principles-economics-bundle/`, created with `tools/add-book.sh principles-economics-bundle "Principles of Economics"` and pinned at the upstream head `cf93bf19bbbca7d1324c2d31af0e81740ae3e5f5`. It builds 5 books:

| Book | Collection | Shape | PDF | Web pages |
|---|---|---|---|---|
| *Principles of Economics 3e* | `principles-economics-3e` | 182 modules in 34 chapters, from "Welcome to Economics!" to "Globalization and Protectionism"; one level of nesting | 1,229 pages | 218 |
| *Principles of Macroeconomics 3e* | `principles-macroeconomics-3e` | 119 modules in 21 chapters, from "Welcome to Economics!" to "Globalization and Protectionism"; one level of nesting | 788 pages | 142 |
| *Principles of Microeconomics 3e* | `principles-microeconomics-3e` | 100 modules in 20 chapters, from "Welcome to Economics!" to "Globalization and Protectionism"; one level of nesting | 723 pages | 122 |
| *Principles of Macroeconomics for AP® Courses 2e* | `principles-macroeconomics-ap-courses-2e` | 104 modules in 18 chapters, from "Welcome to Economics!" to "Macroeconomic Policy Around the World"; one level of nesting | 702 pages | 124 |
| *Principles of Microeconomics for AP® Courses 2e* | `principles-microeconomics-ap-courses-2e` | 98 modules in 20 chapters, from "Welcome to Economics!" to "Globalization and Protectionism"; one level of nesting | 717 pages | 120 |

- **Licence:** CC BY-NC-SA 4.0 (collection XML and the upstream `LICENSE`); the built PDF states it.
- **Figures:** raster only (811 files, 161 MB); no SVG.
- **Exercises:** none embedded, counted in the CNXML in both link schemes; no `exercises/` cache, so nothing for the maintainer to fetch.
- **Result:** built as PDF, EPUB and HTML on 2026-11-28.

## What the book needed from the toolchain

Nothing: it converted and built in one pass with the toolchain as it stood.

## Left as it is

The PDF and HTML were not read page by page; that review is the maintainer's.

## Not done

The book needs the maintainer's public backup: `bash tools/mirror-upstreams.sh push principles-economics-bundle`.

## Recorded

`openstax/osbooks-principles-economics-bundle/CLAUDE.md` ("The books this folder builds"), the list in `openstax/CLAUDE.md`, the inventory and its licence table, the per-book table in `tasks/reference/tooling/converters.md`, and the umbrella's checklist. The survey table (`tasks/reference/openstax/upstream-book-repositories.md`) is refreshed once for the whole 2026-11-28 batch.
