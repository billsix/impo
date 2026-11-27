# Add `osbooks-foundations-information-systems` to impo (one book): built, waiting for its exercises

**Status:** blocked
**Blocked on:** the maintainer running `make -C openstax/osbooks-foundations-information-systems fetch-exercises` (the fetch identifies itself to OpenStax's server with his contact address, so it is his to run)
**Recheck:** `ls openstax/osbooks-foundations-information-systems/checkout/exercises/*.json | wc -l` — cleared when it prints a number near 410
**Part of:** `tasks/openstax-add-remaining-english-books.md`
**Priority:** 5
**Difficulty:** 2 (what is left is a fetch, a rebuild and the record)
**Created:** 2026-11-26 (William Emerison Six <billsix@gmail.com>: "I want to add all of the ones you said … make a task per book"). Built 2026-11-27 (agent).

## BLUF

`openstax/osbooks-foundations-information-systems/` is committed and builds one book as PDF, EPUB and HTML, but without the 410 practice exercises the source embeds: they come from OpenStax's exercise server, and that fetch is the maintainer's. Done means the exercise cache is committed with its `COPYRIGHT` notice, the book is rebuilt with the exercises in it, and this task is archived.

## Context

**Read first:** `openstax/CLAUDE.md` ("Adding a book", and "The content model" for the exercise cache) and `openstax/osbooks-foundations-information-systems/CLAUDE.md`.

### What was added on 2026-11-27

`openstax/osbooks-foundations-information-systems/`, created with `tools/add-book.sh foundations-information-systems "Foundations of Information Systems"` and pinned at the upstream head `057882c68a7867af80c42e86937d3a2454bfd86a`. It builds one book:

| Book | Collection | Shape | PDF | Web pages |
|---|---|---|---|---|
| *Foundations of Information Systems* | `foundations-information-systems` | 59 modules in 12 chapters; one level of nesting | 609 pages | 73 |

- **Licence:** CC BY-NC-SA 4.0 (collection XML and the upstream `LICENSE`); the built PDF states it.
- **Figures:** raster only (181 files, 28 MB); no SVG.
- **Exercises:** 410 embedded links, counted in the CNXML: all in the `#exercise/<nickname>` scheme, none in `#ost/api/ex/<id>`. With no cache the converter leaves each one out and reports it as `exercise-uncached`.
- **Result:** built as PDF, EPUB and HTML on 2026-11-27, without the exercises.

### What the book needed from the toolchain

**A footnote in a note's title.** The first PDF build stopped with "Use of \@item doesn't match its definition": module `m00014` has a note titled "The Rise of Data and AI Ethics" with a `<footnote>` in the title, and the title is the optional argument of the note's box. Such a footnote is now given in parentheses after the title (`tasks/reference/tooling/converters.md`, "Block quotations, reference notes and footnotes in titles"). Two of its sections also hold block quotations with lists inside, which the change made for U.S. History keeps as lists.

### Left as it is

The converter reports `inline:item` (8) and `inline:list` (1) fallbacks. The PDF and HTML were not read page by page; that review is the maintainer's.

## Plan (what is left)

- [ ] **Maintainer:** `make -C openstax/osbooks-foundations-information-systems fetch-exercises` (needs the network; it writes `openstax/osbooks-foundations-information-systems/checkout/exercises/` and its `COPYRIGHT` notice). If `checkout/` is missing: `./fetch.sh && ./apply.sh` in that folder first.
- [ ] Copy the cache to `openstax/osbooks-foundations-information-systems/exercises/` as the other exercise books have it (compare `openstax/osbooks-physics/exercises/` and that folder's `apply.sh`, which copies a committed cache into the checkout), and commit it with its `COPYRIGHT` notice.
- [ ] `./apply.sh && make convert`; the converter's report should no longer list `exercise-uncached` (a few exercises missing from the server is normal; record the count). Then `make dist`.
- [ ] Update the exercise facts and page counts in `openstax/osbooks-foundations-information-systems/CLAUDE.md` and `tasks/reference/openstax/book-inventory.md`, and the per-book table in `tasks/reference/tooling/converters.md`.
- [ ] Rewrite this task as a done-record, archive it, and tick it in the umbrella.
- [ ] **Maintainer:** the public backup, `bash tools/mirror-upstreams.sh push foundations-information-systems`.

## Recorded so far

`openstax/osbooks-foundations-information-systems/CLAUDE.md` ("The books this folder builds"), the list in `openstax/CLAUDE.md`, the inventory and its licence table, and the umbrella's checklist. The survey table (`tasks/reference/openstax/upstream-book-repositories.md`) is refreshed once for the whole 2026-11-27 batch.

## Open questions

None.
