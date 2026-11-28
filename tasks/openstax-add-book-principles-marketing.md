# Added `osbooks-principles-marketing` to impo (one book)

**Done 2026-11-28** (agent, with the exercise fetch run by the maintainer; part of `tasks/openstax-add-remaining-english-books.md`. William Emerison Six <billsix@gmail.com>, 2026-11-28: "work them all, do the work, commit, archive, commit, next", and after his fetch the same day: "fetched all three, do the work").

## What was added

`openstax/osbooks-principles-marketing/`, created with `tools/add-book.sh principles-marketing "Principles of Marketing"` and pinned at the upstream head `a6d7372579d13e0a733954953c4613867f018a48`. It builds one book:

| Book | Collection | Shape | PDF | Web pages |
|---|---|---|---|---|
| *Principles of Marketing* | `principles-marketing` | 132 modules in 19 chapters, from "Marketing and Customer Value" to "Sustainable Marketing: The New Paradigm"; two levels of nesting (units, then chapters) | 852 pages | 24 |

- **Licence:** CC BY-NC-SA 4.0 (collection XML and the upstream `LICENSE`); the built PDF states it.
- **Figures:** raster only (237 files, 62 MB); no SVG.
- **Exercises:** 662 embedded links to 662 exercises, all in the `#exercise/<nickname>` scheme, none in `#ost/api/ex/<id>`. The maintainer ran `make fetch-exercises` on 2026-11-28; all 662 are in the committed cache `openstax/osbooks-principles-marketing/exercises/` (no images) with its `COPYRIGHT` notice, copied in from `openstax/tooling/templates/exercises-COPYRIGHT` because the fetch does not write it.
- **Result:** built as PDF, EPUB and HTML on 2026-11-28: 852 pages with the exercises in (831 without). The converter reports no `exercise-uncached`. The first build of the day, without the exercises, is the commit that added the folder.

## What the book needed from the toolchain

One converter fix. A display equation whose only row is a table (the customer lifetime value formula in module `m00018`, followed by line-break marks) was wrapped in `aligned` with an alignment tab at its `=`, which fell inside the table's `array` and stopped the PDF ("Extra alignment tab"). `render_equation` in `openstax/tooling/tools/cnxml2tex/convert.py` now leaves a single row as it is.

## Left as it is

The converter reports these fallbacks, where the element's text is kept: `inline:cite` (893), `inline:note` (893), `inline:para` (4). The PDF and HTML were not read page by page; that review is the maintainer's.

## Not done

The book needs the maintainer's public backup: `bash tools/mirror-upstreams.sh push principles-marketing`.

## Recorded

`openstax/osbooks-principles-marketing/CLAUDE.md` ("The books this folder builds"), the lists and counts in `openstax/CLAUDE.md` and the root `CLAUDE.md`, the inventory and its licence table, the converter quick reference, the survey table and the umbrella's checklist.
