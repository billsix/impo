# Added `osbooks-principles-accounting-bundle` to impo (2 books)

**Done 2026-11-28** (agent; part of `tasks/openstax-add-remaining-english-books.md`. William Emerison Six <billsix@gmail.com>, 2026-11-28: "work them all, do the work, commit, archive, commit, next").

## What was added

`openstax/osbooks-principles-accounting-bundle/`, created with `tools/add-book.sh principles-accounting-bundle "Principles of Accounting"` and pinned at the upstream head `2165bf6454c0279c1284e19ac7febc101f7956ad`. It builds 2 books:

| Book | Collection | Shape | PDF | Web pages |
|---|---|---|---|---|
| *Principles of Accounting, Volume 1: Financial Accounting* | `principles-financial-accounting` | 104 modules in 16 chapters, from "Role of Accounting in Society" to "Statement of Cash Flows"; one level of nesting | 1,081 pages | 122 |
| *Principles of Accounting, Volume 2: Managerial Accounting* | `principles-managerial-accounting` | 81 modules in 13 chapters, from "Accounting as a Tool for Managers" to "Sustainability Reporting"; one level of nesting | 783 pages | 96 |

- **Licence:** CC BY-NC-SA 4.0 (collection XML and the upstream `LICENSE`); the built PDF states it.
- **Figures:** raster only (2,034 files, 659 MB); no SVG.
- **Exercises:** none embedded, counted in the CNXML in both link schemes; no `exercises/` cache, so nothing for the maintainer to fetch.
- **Result:** built as PDF, EPUB and HTML on 2026-11-28.

## What the book needed from the toolchain

Nothing: it converted and built in one pass with the toolchain as it stood.

## Left as it is

The PDF and HTML were not read page by page; that review is the maintainer's.

## Not done

The book needs the maintainer's public backup: `bash tools/mirror-upstreams.sh push principles-accounting-bundle`.

## Recorded

`openstax/osbooks-principles-accounting-bundle/CLAUDE.md` ("The books this folder builds"), the list in `openstax/CLAUDE.md`, the inventory and its licence table, the per-book table in `tasks/reference/tooling/converters.md`, and the umbrella's checklist. The survey table (`tasks/reference/openstax/upstream-book-repositories.md`) is refreshed once for the whole 2026-11-28 batch.
