# Add `osbooks-introduction-intellectual-property` to impo (one book): built, waiting for its exercises

**Status:** blocked
**Blocked on:** the maintainer running `make -C openstax/osbooks-introduction-intellectual-property fetch-exercises` (the fetch identifies itself to OpenStax's server with his contact address, so it is his to run)
**Recheck:** `ls openstax/osbooks-introduction-intellectual-property/checkout/exercises/*.json | wc -l` — cleared when it prints a number near 185
**Part of:** `tasks/openstax-add-remaining-english-books.md`
**Priority:** 6
**Difficulty:** 2 (what is left is a fetch, a rebuild and the record)
**Created:** 2026-11-26 (William Emerison Six <billsix@gmail.com>: "I want to add all of the ones you said … make a task per book"). Built 2026-11-27 (agent).

## BLUF

`openstax/osbooks-introduction-intellectual-property/` is committed and builds one book as PDF, EPUB and HTML, but without the 185 practice exercises the source embeds: they come from OpenStax's exercise server, and that fetch is the maintainer's. Done means the exercise cache is committed with its `COPYRIGHT` notice, the book is rebuilt with the exercises in it, and this task is archived.

## Context

**Read first:** `openstax/CLAUDE.md` ("Adding a book", and "The content model" for the exercise cache) and `openstax/osbooks-introduction-intellectual-property/CLAUDE.md`.

### What was added on 2026-11-27

`openstax/osbooks-introduction-intellectual-property/`, created with `tools/add-book.sh introduction-intellectual-property "Introduction to Intellectual Property"` and pinned at the upstream head `6dad5479f5a7974df9a2dcb01f4ce9a970658029`. It builds one book:

| Book | Collection | Shape | PDF | Web pages |
|---|---|---|---|---|
| *Introduction to Intellectual Property* | `introduction-intellectual-property` | 54 modules in 5 chapters; one level of nesting | 226 pages | 61 |

- **Licence:** CC BY 4.0 (collection XML and the upstream `LICENSE`); the built PDF states it.
- **Figures:** raster only (191 files, 42 MB); no SVG.
- **Exercises:** 185 embedded links, counted in the CNXML: all in the `#exercise/<nickname>` scheme, none in `#ost/api/ex/<id>`. With no cache the converter leaves each one out and reports it as `exercise-uncached`.
- **Result:** built as PDF, EPUB and HTML on 2026-11-27, without the exercises.

### What the book needed from the toolchain

Nothing of its own. Its 31 block quotations are set off by the converter change made for U.S. History the same day (`tasks/reference/tooling/converters.md`, "Block quotations, reference notes and footnotes in titles"); the built HTML has 31 `<blockquote>` elements. It is under CC BY 4.0, which the converter read from the collection XML.

### Left as it is

The CNXML holds 185 exercise links and the converter reports 183 as uncached; the two it does not count were not traced, and the count after the fetch will show whether anything is missing. The 9 embedded frames were dropped in that first build; since later the same day each is a labelled link (`tasks/archive/impo/2026/11/27/openstax-embedded-frame-links-are-dropped.md`). The PDF and HTML were not read page by page; that review is the maintainer's.

## Plan (what is left)

- [ ] **Maintainer:** `make -C openstax/osbooks-introduction-intellectual-property fetch-exercises` (needs the network; it writes `openstax/osbooks-introduction-intellectual-property/checkout/exercises/` and its `COPYRIGHT` notice). If `checkout/` is missing: `./fetch.sh && ./apply.sh` in that folder first.
- [ ] Copy the cache to `openstax/osbooks-introduction-intellectual-property/exercises/` as the other exercise books have it (compare `openstax/osbooks-physics/exercises/` and that folder's `apply.sh`, which copies a committed cache into the checkout), and commit it with its `COPYRIGHT` notice.
- [ ] `./apply.sh && make convert`; the converter's report should no longer list `exercise-uncached` (a few exercises missing from the server is normal; record the count). Then `make dist`.
- [ ] Update the exercise facts and page counts in `openstax/osbooks-introduction-intellectual-property/CLAUDE.md` and `tasks/reference/openstax/book-inventory.md`, and the per-book table in `tasks/reference/tooling/converters.md`.
- [ ] Rewrite this task as a done-record, archive it, and tick it in the umbrella.
- [ ] **Maintainer:** the public backup, `bash tools/mirror-upstreams.sh push introduction-intellectual-property`.

## Recorded so far

`openstax/osbooks-introduction-intellectual-property/CLAUDE.md` ("The books this folder builds"), the list in `openstax/CLAUDE.md`, the inventory and its licence table, and the umbrella's checklist. The survey table (`tasks/reference/openstax/upstream-book-repositories.md`) is refreshed once for the whole 2026-11-27 batch.

## Open questions

None.
