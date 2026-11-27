# Add `osbooks-lifespan-development` to impo (one book): built, waiting for its exercises

**Status:** blocked
**Blocked on:** the maintainer running `make -C openstax/osbooks-lifespan-development fetch-exercises` (the fetch identifies itself to OpenStax's server with his contact address, so it is his to run)
**Recheck:** `ls openstax/osbooks-lifespan-development/checkout/exercises/*.json | wc -l` — cleared when it prints a number near 872
**Part of:** `tasks/openstax-add-remaining-english-books.md`
**Priority:** 5
**Difficulty:** 2 (what is left is a fetch, a rebuild and the record)
**Created:** 2026-11-26 (William Emerison Six <billsix@gmail.com>: "I want to add all of the ones you said … make a task per book"). Built 2026-11-27 (agent; William Emerison Six <billsix@gmail.com>, 2026-11-27: "you can make a branch, temporarily turn off gpg signing, and start working on all of them (minus the business ones for now)").

## BLUF

`openstax/osbooks-lifespan-development/` is committed and builds one book as PDF, EPUB and HTML, but without the 872 practice exercises the source embeds: they come from OpenStax's exercise server, and that fetch is the maintainer's. Done means the exercise cache is committed with its `COPYRIGHT` notice, the book is rebuilt with the exercises in it, and this task is archived.

## Context

**Read first:** `openstax/CLAUDE.md` ("Adding a book", and "The content model" for the exercise cache) and `openstax/osbooks-lifespan-development/CLAUDE.md`.

### What was added on 2026-11-27

`openstax/osbooks-lifespan-development/`, created with `tools/add-book.sh lifespan-development "Lifespan Development"` and pinned at the upstream head `ebed4ae43c261041030f752eb49d92d0411608db`. It builds one book:

| Book | Collection | Shape | PDF | Web pages |
|---|---|---|---|---|
| *Lifespan Development* | `lifespan-development` | 100 modules in 17 chapters; one level of nesting | 1,415 pages | 119 |

- **Licence:** CC BY-NC-SA 4.0 (collection XML and the upstream `LICENSE`); the built PDF states it.
- **Figures:** raster only (450 files, 79 MB); no SVG.
- **Exercises:** 872 embedded links, counted in the CNXML: all in the `#exercise/<nickname>` scheme, none in `#ost/api/ex/<id>`. With no cache the converter leaves each one out and reports it as `exercise-uncached`.
- **Result:** built as PDF, EPUB and HTML on 2026-11-27, without the exercises; the build log has no pandoc warning.

### What the book needed from the toolchain

Nothing: it converted and built in one pass.

### Left as it is

The PDF leaves out two characters the body font has no glyph for, `ɡ` (two places, for a plain g) and `ɛ` (once, in "APOE ɛ4"); the HTML and EPUB have them. Every book impo builds has this gap, so it has its own task: `tasks/openstax-pdf-characters-missing-from-the-body-font.md`. The converter reports no fallback besides the uncached exercises. The PDF and HTML were not read page by page; that review is the maintainer's.

## Plan (what is left)

- [ ] **Maintainer:** `make -C openstax/osbooks-lifespan-development fetch-exercises` (needs the network; it writes `openstax/osbooks-lifespan-development/checkout/exercises/`). If `checkout/` is missing: `./fetch.sh && ./apply.sh` in that folder first.
- [ ] Copy the cache's `*.json` and `media/` (not `media-derived/`) to `openstax/osbooks-lifespan-development/exercises/`, add the notice (`cp openstax/tooling/templates/exercises-COPYRIGHT openstax/osbooks-lifespan-development/exercises/COPYRIGHT`; the fetch does not write it), and commit the cache with its notice.
- [ ] `./apply.sh && make convert`; the converter's report should no longer list `exercise-uncached` (a few exercises missing from the server is normal; record the count). Then `make dist`.
- [ ] Update the exercise facts and page counts in `openstax/osbooks-lifespan-development/CLAUDE.md` and `tasks/reference/openstax/book-inventory.md`, and the per-book table in `tasks/reference/tooling/converters.md`.
- [ ] Rewrite this task as a done-record, archive it, and tick it in the umbrella.
- [ ] **Maintainer:** the public backup, `bash tools/mirror-upstreams.sh push lifespan-development`.

## Recorded so far

`openstax/osbooks-lifespan-development/CLAUDE.md` ("The books this folder builds"), the lists and counts in `openstax/CLAUDE.md` and the root `CLAUDE.md`, the inventory and its licence table, the converter quick reference and the umbrella's checklist. The survey table (`tasks/reference/openstax/upstream-book-repositories.md`) is refreshed once for the whole batch.

## Open questions

None.
