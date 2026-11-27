# Add `osbooks-introduction-anthropology` to impo (one book): built, waiting for its exercises

**Status:** blocked
**Blocked on:** the maintainer running `make -C openstax/osbooks-introduction-anthropology fetch-exercises` (the fetch identifies itself to OpenStax's server with his contact address, so it is his to run)
**Recheck:** `ls openstax/osbooks-introduction-anthropology/checkout/exercises/*.json | wc -l` — cleared when it prints a number near 150
**Part of:** `tasks/openstax-add-remaining-english-books.md`
**Priority:** 5
**Difficulty:** 2 (what is left is a fetch, a rebuild and the record)
**Created:** 2026-11-26 (William Emerison Six <billsix@gmail.com>: "I want to add all of the ones you said … make a task per book"). Built 2026-11-27 (agent; William Emerison Six <billsix@gmail.com>, 2026-11-27: "you can make a branch, temporarily turn off gpg signing, and start working on all of them (minus the business ones for now)").

## BLUF

`openstax/osbooks-introduction-anthropology/` is committed and builds one book as PDF, EPUB and HTML, but without the 150 practice exercises the source embeds: they come from OpenStax's exercise server, and that fetch is the maintainer's. Done means the exercise cache is committed with its `COPYRIGHT` notice, the book is rebuilt with the exercises in it, and this task is archived.

## Context

**Read first:** `openstax/CLAUDE.md` ("Adding a book", and "The content model" for the exercise cache) and `openstax/osbooks-introduction-anthropology/CLAUDE.md`.

### What was added on 2026-11-27

`openstax/osbooks-introduction-anthropology/`, created with `tools/add-book.sh introduction-anthropology "Introduction to Anthropology"` and pinned at the upstream head `e466666414f1900a783141339dc5ef3106dba5dd`. It builds one book:

| Book | Collection | Shape | PDF | Web pages |
|---|---|---|---|---|
| *Introduction to Anthropology* | `introduction-anthropology` | 121 modules in 20 chapters; one level of nesting | 873 pages | 143 |

- **Licence:** CC BY-NC-SA 4.0 (collection XML and the upstream `LICENSE`); the built PDF states it.
- **Figures:** raster only (350 files; `media/` is 130 MB). `media/Interactive/` holds 197 more files, 24 of them SVG icons; no module references an SVG.
- **Exercises:** 150 embedded links, counted in the CNXML: all in the `#exercise/<nickname>` scheme, none in `#ost/api/ex/<id>`. With no cache the converter leaves each one out and reports it as `exercise-uncached`.
- **Result:** built as PDF, EPUB and HTML on 2026-11-27, without the exercises; the build log has no pandoc warning.

### What the book needed from the toolchain

Nothing: it converted and built in one pass.

### Left as it is

The converter reports no fallback besides the uncached exercises. The PDF and HTML were not read page by page; that review is the maintainer's.

## Plan (what is left)

- [ ] **Maintainer:** `make -C openstax/osbooks-introduction-anthropology fetch-exercises` (needs the network; it writes `openstax/osbooks-introduction-anthropology/checkout/exercises/`). If `checkout/` is missing: `./fetch.sh && ./apply.sh` in that folder first.
- [ ] Copy the cache's `*.json` and `media/` (not `media-derived/`) to `openstax/osbooks-introduction-anthropology/exercises/`, add the notice (`cp openstax/tooling/templates/exercises-COPYRIGHT openstax/osbooks-introduction-anthropology/exercises/COPYRIGHT`; the fetch does not write it), and commit the cache with its notice.
- [ ] `./apply.sh && make convert`; the converter's report should no longer list `exercise-uncached` (a few exercises missing from the server is normal; record the count). Then `make dist`.
- [ ] Update the exercise facts and page counts in `openstax/osbooks-introduction-anthropology/CLAUDE.md` and `tasks/reference/openstax/book-inventory.md`, and the per-book table in `tasks/reference/tooling/converters.md`.
- [ ] Rewrite this task as a done-record, archive it, and tick it in the umbrella.
- [ ] **Maintainer:** the public backup, `bash tools/mirror-upstreams.sh push introduction-anthropology`.

## Recorded so far

`openstax/osbooks-introduction-anthropology/CLAUDE.md` ("The books this folder builds"), the lists and counts in `openstax/CLAUDE.md` and the root `CLAUDE.md`, the inventory and its licence table, the converter quick reference and the umbrella's checklist. The survey table (`tasks/reference/openstax/upstream-book-repositories.md`) is refreshed once for the whole batch.

## Open questions

None.
