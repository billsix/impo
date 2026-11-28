# Added `osbooks-business-ethics` to impo (one book)

**Done 2026-11-28** (agent, with the exercise fetch run by the maintainer; part of `tasks/archive/impo/2026/11/28/openstax-add-remaining-english-books.md`. William Emerison Six <billsix@gmail.com>, 2026-11-28: "work them all, do the work, commit, archive, commit, next", and after his fetch the same day: "fetched all three, do the work").

## What was added

`openstax/osbooks-business-ethics/`, created with `tools/add-book.sh business-ethics "Business Ethics"` and pinned at the upstream head `37c6dbe07bd93b5ead10942092a348d60d5dfd30`. It builds one book:

| Book | Collection | Shape | PDF | Web pages |
|---|---|---|---|---|
| *Business Ethics* | `business-ethics` | 61 modules in 11 chapters, from "Why Ethics Matter" to "Epilogue: Why Ethics Still Matter"; one level of nesting | 449 pages | 74 |

- **Licence:** CC BY-NC-SA 4.0 (collection XML and the upstream `LICENSE`); the built PDF states it.
- **Figures:** raster only (100 files, 50 MB); no SVG.
- **Exercises:** 196 embedded links to 196 exercises, all in the `#exercise/<nickname>` scheme, none in `#ost/api/ex/<id>`. The maintainer ran `make fetch-exercises` on 2026-11-28; all 196 are in the committed cache `openstax/osbooks-business-ethics/exercises/` (no images) with its `COPYRIGHT` notice, copied in from `openstax/tooling/templates/exercises-COPYRIGHT` because the fetch does not write it.
- **Result:** built as PDF, EPUB and HTML on 2026-11-28: 449 pages, the same count as without the exercises. The converter reports no `exercise-uncached`. The first build of the day, without the exercises, is the commit that added the folder.

## What the book needed from the toolchain

Nothing: it converted and built in one pass with the toolchain as it stood.

## Left as it is

The converter reports these fallbacks, where the element's text is kept: `inline:cite` (525), `inline:note` (525). The PDF and HTML were not read page by page; that review is the maintainer's.

## Not done

The book needs the maintainer's public backup: `bash tools/mirror-upstreams.sh push business-ethics`.

## Recorded

`openstax/osbooks-business-ethics/CLAUDE.md` ("The books this folder builds"), the lists and counts in `openstax/CLAUDE.md` and the root `CLAUDE.md`, the inventory and its licence table, the converter quick reference, the survey table and the umbrella's checklist.
