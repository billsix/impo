# Add `osbooks-world-history` to impo (2 books): built, waiting for its exercises

**Status:** blocked
**Blocked on:** the maintainer running `make -C openstax/osbooks-world-history fetch-exercises` (the fetch identifies itself to OpenStax's server with his contact address, so it is his to run)
**Recheck:** `ls openstax/osbooks-world-history/checkout/exercises/*.json | wc -l` — cleared when it prints a number near 1,158
**Part of:** `tasks/openstax-add-remaining-english-books.md`
**Priority:** 5
**Difficulty:** 2 (what is left is a fetch, a rebuild and the record)
**Created:** 2026-11-26 (William Emerison Six <billsix@gmail.com>: "I want to add all of the ones you said … make a task per book"). Built 2026-11-27 (agent).

## BLUF

`openstax/osbooks-world-history/` is committed and builds 2 books as PDF, EPUB and HTML, but without the 1,158 practice exercises the source embeds: they come from OpenStax's exercise server, and that fetch is the maintainer's. Done means the exercise cache is committed with its `COPYRIGHT` notice, the book is rebuilt with the exercises in it, and this task is archived.

## Context

**Read first:** `openstax/CLAUDE.md` ("Adding a book", and "The content model" for the exercise cache) and `openstax/osbooks-world-history/CLAUDE.md`.

### What was added on 2026-11-27

`openstax/osbooks-world-history/`, created with `tools/add-book.sh world-history "World History"` and pinned at the upstream head `c0dd82697bc2c7cd355c942e778f215762768c43`. It builds 2 books:

| Book | Collection | Shape | PDF | Web pages |
|---|---|---|---|---|
| *World History Volume 1, to 1500* | `world-history-volume-1` | 85 modules in 17 chapters and 4 units; two levels of nesting | 918 pages | 23 |
| *World History Volume 2, from 1400* | `world-history-volume-2` | 80 modules in 15 chapters and 3 units; two levels of nesting | 864 pages | 20 |

- **Licence:** CC BY-NC-SA 4.0 (collection XML and the upstream `LICENSE`); the built PDF states it.
- **Figures:** raster only (909 files, 345 MB, both volumes together); no SVG.
- **Exercises:** 1,158 embedded links, counted in the CNXML: all in the `#exercise/<nickname>` scheme, none in `#ost/api/ex/<id>`. With no cache the converter leaves each one out and reports it as `exercise-uncached`.
- **Result:** built as PDF, EPUB and HTML on 2026-11-27, without the exercises.

### What the book needed from the toolchain

Nothing of its own. Its 131 block quotations are set off by the converter change made for U.S. History the same day (`tasks/reference/tooling/converters.md`, "Block quotations, reference notes and footnotes in titles"); the built HTML of the two volumes has 131 `<blockquote>` elements.

### Left as it is

The 8 embedded frames are dropped, as in every book (`tasks/openstax-embedded-frame-links-are-dropped.md`). The web editions have 23 and 20 pages, because a book with two levels of nesting is split per chapter. The converter reports no fallback besides the uncached exercises. The PDF and HTML were not read page by page; that review is the maintainer's.

## Plan (what is left)

- [ ] **Maintainer:** `make -C openstax/osbooks-world-history fetch-exercises` (needs the network; it writes `openstax/osbooks-world-history/checkout/exercises/` and its `COPYRIGHT` notice). If `checkout/` is missing: `./fetch.sh && ./apply.sh` in that folder first.
- [ ] Copy the cache to `openstax/osbooks-world-history/exercises/` as the other exercise books have it (compare `openstax/osbooks-physics/exercises/` and that folder's `apply.sh`, which copies a committed cache into the checkout), and commit it with its `COPYRIGHT` notice.
- [ ] `./apply.sh && make convert`; the converter's report should no longer list `exercise-uncached` (a few exercises missing from the server is normal; record the count). Then `make dist`.
- [ ] Update the exercise facts and page counts in `openstax/osbooks-world-history/CLAUDE.md` and `tasks/reference/openstax/book-inventory.md`, and the per-book table in `tasks/reference/tooling/converters.md`.
- [ ] Rewrite this task as a done-record, archive it, and tick it in the umbrella.
- [ ] **Maintainer:** the public backup, `bash tools/mirror-upstreams.sh push world-history`.

## Recorded so far

`openstax/osbooks-world-history/CLAUDE.md` ("The books this folder builds"), the list in `openstax/CLAUDE.md`, the inventory and its licence table, and the umbrella's checklist. The survey table (`tasks/reference/openstax/upstream-book-repositories.md`) is refreshed once for the whole 2026-11-27 batch.

## Open questions

None.
