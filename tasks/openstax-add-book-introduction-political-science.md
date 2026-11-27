# Added `osbooks-introduction-political-science` to impo (one book)

**Done 2026-11-27** (agent, with the exercise fetch run by the maintainer; part of `tasks/openstax-add-remaining-english-books.md`. William Emerison Six <billsix@gmail.com>, 2026-11-27: "for each book, do the work, commit, archive, commit").

## What was added

`openstax/osbooks-introduction-political-science/`, created with `tools/add-book.sh introduction-political-science "Introduction to Political Science"` and pinned at the upstream head `61afbf50d27ba833feb64b66ba06a5384e9f371c`. It builds one book:

| Book | Collection | Shape | PDF | Web pages |
|---|---|---|---|---|
| *Introduction to Political Science* | `introduction-political-science` | 107 modules in 16 chapters grouped into 5 units; two levels of nesting | 763 pages | 23 |

- **Licence:** CC BY-NC-SA 4.0 (collection XML and the upstream `LICENSE`); the built PDF states it.
- **Figures:** raster only (229 files, 97 MB). `media/Interactive/` also holds a case-study bundle with 22 SVG icons that no module references.
- **Exercises:** 308 embedded links to 308 exercises, all in the `#exercise/<nickname>` scheme, none in `#ost/api/ex/<id>`. The maintainer ran `make fetch-exercises` on 2026-11-27; all 308 are in the committed cache `openstax/osbooks-introduction-political-science/exercises/` (no images) with its `COPYRIGHT` notice.
- **Result:** built as PDF, EPUB and HTML on 2026-11-27 with the exercises in; the converter reports no `exercise-uncached` and the build log has no pandoc warning.

## What the book needed from the toolchain

Nothing of its own. It relies on two converter changes made for books added the same day: its 1,522 reference notes (`<cite><note class="reference">`) are footnotes, 1,508 of them, with the 14 in captions, table cells and titles in parentheses (the change American Government needed), and its 33 block quotations are set off (the change U.S. History needed). Both are in `tasks/reference/tooling/converters.md`, "Block quotations, reference notes and footnotes in titles".

## Left as it is

Its 115 embedded frames (videos), more than in any other book, were dropped in the first build and are labelled links since the fix of the same day (`tasks/archive/impo/2026/11/27/openstax-embedded-frame-links-are-dropped.md`). The web edition has 23 pages for 107 modules, because a book with two levels of nesting is split per chapter. The converter reports no fallback. The PDF and HTML were not read page by page; that review is the maintainer's.

## Not done

The book needs the maintainer's public backup: `bash tools/mirror-upstreams.sh push introduction-political-science`.

## Recorded

`openstax/osbooks-introduction-political-science/CLAUDE.md` ("The books this folder builds"), the list in `openstax/CLAUDE.md`, the inventory and its licence table, the survey table and the umbrella's checklist.
