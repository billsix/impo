# Added `osbooks-introduction-intellectual-property` to impo (one book)

**Done 2026-11-27** (agent, with the exercise fetch run by the maintainer; part of `tasks/openstax-add-remaining-english-books.md`. William Emerison Six <billsix@gmail.com>, 2026-11-27: "for each book, do the work, commit, archive, commit").

## What was added

`openstax/osbooks-introduction-intellectual-property/`, created with `tools/add-book.sh introduction-intellectual-property "Introduction to Intellectual Property"` and pinned at the upstream head `6dad5479f5a7974df9a2dcb01f4ce9a970658029`. It builds one book:

| Book | Collection | Shape | PDF | Web pages |
|---|---|---|---|---|
| *Introduction to Intellectual Property* | `introduction-intellectual-property` | 54 modules in 5 chapters; one level of nesting | 232 pages | 61 |

- **Licence:** CC BY 4.0 (collection XML and the upstream `LICENSE`); the built PDF states it.
- **Figures:** raster only (191 files, 42 MB); no SVG.
- **Exercises:** 185 embedded links to 185 exercises, all in the `#exercise/<nickname>` scheme, none in `#ost/api/ex/<id>`. The maintainer ran `make fetch-exercises` on 2026-11-27; all 185 are in the committed cache `openstax/osbooks-introduction-intellectual-property/exercises/` (no images) with its `COPYRIGHT` notice.
- **Result:** built as PDF, EPUB and HTML on 2026-11-27 with the exercises in; the converter reports no `exercise-uncached` and the build log has no pandoc warning.

## What the book needed from the toolchain

Nothing of its own. Its 31 block quotations are set off by the converter change made for U.S. History the same day (`tasks/reference/tooling/converters.md`, "Block quotations, reference notes and footnotes in titles"); the built HTML has 31 `<blockquote>` elements. It is under CC BY 4.0, which the converter read from the collection XML.

## Left as it is

Its 9 embedded frames were dropped in the first build and are labelled links since the fix of the same day (`tasks/archive/impo/2026/11/27/openstax-embedded-frame-links-are-dropped.md`). The first build's report counted 183 uncached exercises against 185 links; with the cache in place none is uncached. The converter reports no fallback. The PDF and HTML were not read page by page; that review is the maintainer's.

## Not done

The book needs the maintainer's public backup: `bash tools/mirror-upstreams.sh push introduction-intellectual-property`.

## Recorded

`openstax/osbooks-introduction-intellectual-property/CLAUDE.md` ("The books this folder builds"), the list in `openstax/CLAUDE.md`, the inventory and its licence table, the survey table and the umbrella's checklist.
