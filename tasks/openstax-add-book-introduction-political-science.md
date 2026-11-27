# Add `osbooks-introduction-political-science` to impo (one book): built, waiting for its exercises

**Status:** blocked
**Blocked on:** the maintainer running `make -C openstax/osbooks-introduction-political-science fetch-exercises` (the fetch identifies itself to OpenStax's server with his contact address, so it is his to run)
**Recheck:** `ls openstax/osbooks-introduction-political-science/checkout/exercises/*.json | wc -l` — cleared when it prints a number near 308
**Part of:** `tasks/openstax-add-remaining-english-books.md`
**Priority:** 5
**Difficulty:** 2 (what is left is a fetch, a rebuild and the record)
**Created:** 2026-11-26 (William Emerison Six <billsix@gmail.com>: "I want to add all of the ones you said … make a task per book"). Built 2026-11-27 (agent).

## BLUF

`openstax/osbooks-introduction-political-science/` is committed and builds one book as PDF, EPUB and HTML, but without the 308 practice exercises the source embeds: they come from OpenStax's exercise server, and that fetch is the maintainer's. Done means the exercise cache is committed with its `COPYRIGHT` notice, the book is rebuilt with the exercises in it, and this task is archived.

## Context

**Read first:** `openstax/CLAUDE.md` ("Adding a book", and "The content model" for the exercise cache) and `openstax/osbooks-introduction-political-science/CLAUDE.md`.

### What was added on 2026-11-27

`openstax/osbooks-introduction-political-science/`, created with `tools/add-book.sh introduction-political-science "Introduction to Political Science"` and pinned at the upstream head `61afbf50d27ba833feb64b66ba06a5384e9f371c`. It builds one book:

| Book | Collection | Shape | PDF | Web pages |
|---|---|---|---|---|
| *Introduction to Political Science* | `introduction-political-science` | 107 modules in 16 chapters grouped into 5 units; two levels of nesting | 753 pages | 23 |

- **Licence:** CC BY-NC-SA 4.0 (collection XML and the upstream `LICENSE`); the built PDF states it.
- **Figures:** raster only (229 files, 97 MB). `media/Interactive/` also holds a case-study bundle with 22 SVG icons that no module references.
- **Exercises:** 308 embedded links, counted in the CNXML: all in the `#exercise/<nickname>` scheme, none in `#ost/api/ex/<id>`. With no cache the converter leaves each one out and reports it as `exercise-uncached`.
- **Result:** built as PDF, EPUB and HTML on 2026-11-27, without the exercises.

### What the book needed from the toolchain

Nothing of its own. It relies on two converter changes made for books added the same day: its 1,522 reference notes (`<cite><note class="reference">`) are footnotes, 1,508 of them, with the 14 in captions, table cells and titles in parentheses (the change American Government needed), and its 33 block quotations are set off (the change U.S. History needed). Both are in `tasks/reference/tooling/converters.md`, "Block quotations, reference notes and footnotes in titles".

### Left as it is

The 115 embedded frames (videos), more than in any other book, were dropped in that first build; since later the same day each is a labelled link (`tasks/archive/impo/2026/11/27/openstax-embedded-frame-links-are-dropped.md`). The web edition has 23 pages for 107 modules, because a book with two levels of nesting is split per chapter. The converter reports no fallback besides the uncached exercises. The PDF and HTML were not read page by page; that review is the maintainer's.

## Plan (what is left)

- [ ] **Maintainer:** `make -C openstax/osbooks-introduction-political-science fetch-exercises` (needs the network; it writes `openstax/osbooks-introduction-political-science/checkout/exercises/` and its `COPYRIGHT` notice). If `checkout/` is missing: `./fetch.sh && ./apply.sh` in that folder first.
- [ ] Copy the cache to `openstax/osbooks-introduction-political-science/exercises/` as the other exercise books have it (compare `openstax/osbooks-physics/exercises/` and that folder's `apply.sh`, which copies a committed cache into the checkout), and commit it with its `COPYRIGHT` notice.
- [ ] `./apply.sh && make convert`; the converter's report should no longer list `exercise-uncached` (a few exercises missing from the server is normal; record the count). Then `make dist`.
- [ ] Update the exercise facts and page counts in `openstax/osbooks-introduction-political-science/CLAUDE.md` and `tasks/reference/openstax/book-inventory.md`, and the per-book table in `tasks/reference/tooling/converters.md`.
- [ ] Rewrite this task as a done-record, archive it, and tick it in the umbrella.
- [ ] **Maintainer:** the public backup, `bash tools/mirror-upstreams.sh push introduction-political-science`.

## Recorded so far

`openstax/osbooks-introduction-political-science/CLAUDE.md` ("The books this folder builds"), the list in `openstax/CLAUDE.md`, the inventory and its licence table, and the umbrella's checklist. The survey table (`tasks/reference/openstax/upstream-book-repositories.md`) is refreshed once for the whole 2026-11-27 batch.

## Open questions

None.
