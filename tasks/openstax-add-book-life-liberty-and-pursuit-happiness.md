# Add `osbooks-life-liberty-and-pursuit-happiness` to impo (one book): built, waiting for its exercises

**Status:** blocked
**Blocked on:** the maintainer running `make -C openstax/osbooks-life-liberty-and-pursuit-happiness fetch-exercises` (the fetch identifies itself to OpenStax's server with his contact address, so it is his to run)
**Recheck:** `ls openstax/osbooks-life-liberty-and-pursuit-happiness/checkout/exercises/*.json | wc -l` — cleared when it prints a number near 1,896
**Part of:** `tasks/openstax-add-remaining-english-books.md`
**Priority:** 5
**Difficulty:** 2 (what is left is a fetch, a rebuild and the record)
**Created:** 2026-11-26 (William Emerison Six <billsix@gmail.com>: "I want to add all of the ones you said … make a task per book"). Built 2026-11-27 (agent).

## BLUF

`openstax/osbooks-life-liberty-and-pursuit-happiness/` is committed and builds one book as PDF, EPUB and HTML, but without the 1,896 practice exercises the source embeds: they come from OpenStax's exercise server, and that fetch is the maintainer's. Done means the exercise cache is committed with its `COPYRIGHT` notice, the book is rebuilt with the exercises in it, and this task is archived.

## Context

**Read first:** `openstax/CLAUDE.md` ("Adding a book", and "The content model" for the exercise cache) and `openstax/osbooks-life-liberty-and-pursuit-happiness/CLAUDE.md`.

### What was added on 2026-11-27

`openstax/osbooks-life-liberty-and-pursuit-happiness/`, created with `tools/add-book.sh life-liberty-and-pursuit-happiness "Life, Liberty, and the Pursuit of Happiness"` and pinned at the upstream head `acb6fbe2744dd112187b6aff5946cfe969410fca`. It builds one book:

| Book | Collection | Shape | PDF | Web pages |
|---|---|---|---|---|
| *Life, Liberty, and the Pursuit of Happiness* | `life-liberty-and-pursuit-happiness` | 532 modules in 16 chapters grouped into 8 units by period, from "1491–1763" to "1980–Present"; two levels of nesting | 2,484 pages | 26 |

- **Licence:** CC BY 4.0 (collection XML and the upstream `LICENSE`); the built PDF states it.
- **Figures:** raster only (893 files, 331 MB); no SVG.
- **Exercises:** 1,896 embedded links, counted in the CNXML: all in the `#exercise/<nickname>` scheme, none in `#ost/api/ex/<id>`. With no cache the converter leaves each one out and reports it as `exercise-uncached`.
- **Result:** built as PDF, EPUB and HTML on 2026-11-27, without the exercises.

### What the book needed from the toolchain

Nothing: it converted and built in one pass with the toolchain as it stood. It is one of the few books under CC BY 4.0 (with `osbooks-physics`, `osbooks-statistics` and `osbooks-introduction-intellectual-property`); the converter read that from the collection XML.

### Left as it is

The web edition has 26 pages for 532 modules, because a book with two levels of nesting is split per chapter (the same holds for the other unit-nested books). The 33 embedded frames (videos) are dropped, as in every book (`tasks/openstax-embedded-frame-links-are-dropped.md`). The converter reports 32 `inline:label` fallbacks. The PDF and HTML were not read page by page; that review is the maintainer's.

## Plan (what is left)

- [ ] **Maintainer:** `make -C openstax/osbooks-life-liberty-and-pursuit-happiness fetch-exercises` (needs the network; it writes `openstax/osbooks-life-liberty-and-pursuit-happiness/checkout/exercises/` and its `COPYRIGHT` notice). If `checkout/` is missing: `./fetch.sh && ./apply.sh` in that folder first.
- [ ] Copy the cache to `openstax/osbooks-life-liberty-and-pursuit-happiness/exercises/` as the other exercise books have it (compare `openstax/osbooks-physics/exercises/` and that folder's `apply.sh`, which copies a committed cache into the checkout), and commit it with its `COPYRIGHT` notice.
- [ ] `./apply.sh && make convert`; the converter's report should no longer list `exercise-uncached` (a few exercises missing from the server is normal; record the count). Then `make dist`.
- [ ] Update the exercise facts and page counts in `openstax/osbooks-life-liberty-and-pursuit-happiness/CLAUDE.md` and `tasks/reference/openstax/book-inventory.md`, and the per-book table in `tasks/reference/tooling/converters.md`.
- [ ] Rewrite this task as a done-record, archive it, and tick it in the umbrella.
- [ ] **Maintainer:** the public backup, `bash tools/mirror-upstreams.sh push life-liberty-and-pursuit-happiness`.

## Recorded so far

`openstax/osbooks-life-liberty-and-pursuit-happiness/CLAUDE.md` ("The books this folder builds"), the list in `openstax/CLAUDE.md`, the inventory and its licence table, and the umbrella's checklist. The survey table (`tasks/reference/openstax/upstream-book-repositories.md`) is refreshed once for the whole 2026-11-27 batch.

## Open questions

None.
