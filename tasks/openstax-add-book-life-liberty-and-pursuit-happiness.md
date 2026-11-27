# Added `osbooks-life-liberty-and-pursuit-happiness` to impo (one book)

**Done 2026-11-27** (agent, with the exercise fetch run by the maintainer; part of `tasks/openstax-add-remaining-english-books.md`. William Emerison Six <billsix@gmail.com>, 2026-11-27: "for each book, do the work, commit, archive, commit").

## What was added

`openstax/osbooks-life-liberty-and-pursuit-happiness/`, created with `tools/add-book.sh life-liberty-and-pursuit-happiness "Life, Liberty, and the Pursuit of Happiness"` and pinned at the upstream head `acb6fbe2744dd112187b6aff5946cfe969410fca`. It builds one book:

| Book | Collection | Shape | PDF | Web pages |
|---|---|---|---|---|
| *Life, Liberty, and the Pursuit of Happiness* | `life-liberty-and-pursuit-happiness` | 532 modules in 16 chapters grouped into 8 units by period, from "1491–1763" to "1980–Present"; two levels of nesting | 2 pages | 26 |

- **Licence:** CC BY 4.0 (collection XML and the upstream `LICENSE`); the built PDF states it.
- **Figures:** raster only (893 files, 331 MB); no SVG.
- **Exercises:** 1,896 embedded links to 1,895 exercises (1 of the links repeat an exercise), all in the `#exercise/<nickname>` scheme, none in `#ost/api/ex/<id>`. The maintainer ran `make fetch-exercises` on 2026-11-27; all 1,895 are in the committed cache `openstax/osbooks-life-liberty-and-pursuit-happiness/exercises/` (95 images) with its `COPYRIGHT` notice.
- **Result:** built as PDF, EPUB and HTML on 2026-11-27 with the exercises in; the converter reports no `exercise-uncached` and the build log has no pandoc warning.

## What the book needed from the toolchain

Nothing: it converted and built in one pass with the toolchain as it stood. It is one of the few books under CC BY 4.0 (with `osbooks-physics`, `osbooks-statistics` and `osbooks-introduction-intellectual-property`); the converter read that from the collection XML.

## Left as it is

Its 33 embedded frames (videos) were dropped in the first build and are labelled links since the fix of the same day (`tasks/archive/impo/2026/11/27/openstax-embedded-frame-links-are-dropped.md`). The web edition has 26 pages for 532 modules, because a book with two levels of nesting is split per chapter. The exercise cache is the largest in impo so far (66 MB, 95 images). The converter reports 32 `inline:label` fallbacks. The PDF and HTML were not read page by page; that review is the maintainer's.

## Not done

The book needs the maintainer's public backup: `bash tools/mirror-upstreams.sh push life-liberty-and-pursuit-happiness`.

## Recorded

`openstax/osbooks-life-liberty-and-pursuit-happiness/CLAUDE.md` ("The books this folder builds"), the list in `openstax/CLAUDE.md`, the inventory and its licence table, the survey table and the umbrella's checklist.
