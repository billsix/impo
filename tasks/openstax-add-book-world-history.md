# Added `osbooks-world-history` to impo (2 books)

**Done 2026-11-27** (agent, with the exercise fetch run by the maintainer; part of `tasks/openstax-add-remaining-english-books.md`. William Emerison Six <billsix@gmail.com>, 2026-11-27: "for each book, do the work, commit, archive, commit").

## What was added

`openstax/osbooks-world-history/`, created with `tools/add-book.sh world-history "World History"` and pinned at the upstream head `c0dd82697bc2c7cd355c942e778f215762768c43`. It builds 2 books:

| Book | Collection | Shape | PDF | Web pages |
|---|---|---|---|---|
| *World History Volume 1, to 1500* | `world-history-volume-1` | 85 modules in 17 chapters and 4 units; two levels of nesting | 928 pages | 23 |
| *World History Volume 2, from 1400* | `world-history-volume-2` | 80 modules in 15 chapters and 3 units; two levels of nesting | 872 pages | 20 |

- **Licence:** CC BY-NC-SA 4.0 (collection XML and the upstream `LICENSE`); the built PDF states it.
- **Figures:** raster only (909 files, 345 MB, both volumes together); no SVG.
- **Exercises:** 1,158 embedded links to 1,158 exercises, all in the `#exercise/<nickname>` scheme, none in `#ost/api/ex/<id>`. The maintainer ran `make fetch-exercises` on 2026-11-27; all 1,158 are in the committed cache `openstax/osbooks-world-history/exercises/` (4 images) with its `COPYRIGHT` notice.
- **Result:** built as PDF, EPUB and HTML on 2026-11-27 with the exercises in; the converter reports no `exercise-uncached` and the build log has no pandoc warning.

## What the book needed from the toolchain

Nothing of its own. Its 131 block quotations are set off by the converter change made for U.S. History the same day (`tasks/reference/tooling/converters.md`, "Block quotations, reference notes and footnotes in titles"); the built HTML of the two volumes has 131 `<blockquote>` elements.

## Left as it is

Its 8 embedded frames were dropped in the first build and are labelled links since the fix of the same day (`tasks/archive/impo/2026/11/27/openstax-embedded-frame-links-are-dropped.md`). The web editions have 23 and 20 pages, because a book with two levels of nesting is split per chapter. The converter reports no fallback. The PDF and HTML were not read page by page; that review is the maintainer's.

## Not done

The book needs the maintainer's public backup: `bash tools/mirror-upstreams.sh push world-history`.

## Recorded

`openstax/osbooks-world-history/CLAUDE.md` ("The books this folder builds"), the list in `openstax/CLAUDE.md`, the inventory and its licence table, the survey table and the umbrella's checklist.
