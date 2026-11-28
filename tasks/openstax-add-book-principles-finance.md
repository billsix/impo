# Added `osbooks-principles-finance` to impo (one book)

**Done 2026-11-28** (agent, with the exercise fetch run by the maintainer; part of `tasks/openstax-add-remaining-english-books.md`. William Emerison Six <billsix@gmail.com>, 2026-11-28: "work them all, do the work, commit, archive, commit, next", and after his fetch the same day: "fetched all three, do the work").

## What was added

`openstax/osbooks-principles-finance/`, created with `tools/add-book.sh principles-finance "Principles of Finance 2e"` and pinned at the upstream head `e3e5135ae36e21282d7afb4cccd5ce09f421d830`. It builds one book:

| Book | Collection | Shape | PDF | Web pages |
|---|---|---|---|---|
| *Principles of Finance 2e* | `principles-finance-2e` | 131 modules in 20 chapters, from "Introduction to Finance" to "Risk Management and the Financial Manager"; one level of nesting | 746 pages | 153 |

- **Licence:** CC BY-NC-SA 4.0 (collection XML and the upstream `LICENSE`); the built PDF states it.
- **Figures:** raster only (278 files, 31 MB); no SVG.
- **Exercises:** 580 embedded links to 580 exercises, all in the `#exercise/<nickname>` scheme, none in `#ost/api/ex/<id>`. The maintainer ran `make fetch-exercises` on 2026-11-28; all 580 are in the committed cache `openstax/osbooks-principles-finance/exercises/` (17 images) with its `COPYRIGHT` notice, copied in from `openstax/tooling/templates/exercises-COPYRIGHT` because the fetch does not write it.
- **Result:** built as PDF, EPUB and HTML on 2026-11-28: 746 pages with the exercises in (739 without). The converter reports no `exercise-uncached`. The first build of the day, without the exercises, is the commit that added the folder.

## What the book needed from the toolchain

Nothing: it converted and built in one pass with the toolchain as it stood.

## Left as it is

The PDF and HTML were not read page by page; that review is the maintainer's.

## Not done

The book needs the maintainer's public backup: `bash tools/mirror-upstreams.sh push principles-finance`.

## Recorded

`openstax/osbooks-principles-finance/CLAUDE.md` ("The books this folder builds"), the lists and counts in `openstax/CLAUDE.md` and the root `CLAUDE.md`, the inventory and its licence table, the converter quick reference, the survey table and the umbrella's checklist.
