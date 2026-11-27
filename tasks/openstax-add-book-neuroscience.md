# Add `osbooks-neuroscience` to impo (one book): built, waiting for its exercises

**Status:** blocked
**Blocked on:** the maintainer running `make -C openstax/osbooks-neuroscience fetch-exercises` (the fetch identifies itself to OpenStax's server with his contact address, so it is his to run)
**Recheck:** `ls openstax/osbooks-neuroscience/checkout/exercises/*.json | wc -l` — cleared when it prints a number near 568
**Part of:** `tasks/openstax-add-remaining-english-books.md`
**Priority:** 5
**Difficulty:** 2 (what is left is a fetch, a rebuild and the record)
**Created:** 2026-11-26 (William Emerison Six <billsix@gmail.com>: "I want to add all of the ones you said … make a task per book"). Built 2026-11-27 (agent).

## BLUF

`openstax/osbooks-neuroscience/` is committed and builds one book as PDF, EPUB and HTML, but without the 568 practice exercises the source embeds: they come from OpenStax's exercise server, and that fetch is the maintainer's. Done means the exercise cache is committed with its `COPYRIGHT` notice, the book is rebuilt with the exercises in it, and this task is archived.

## Context

**Read first:** `openstax/CLAUDE.md` ("Adding a book", and "The content model" for the exercise cache) and `openstax/osbooks-neuroscience/CLAUDE.md`.

### What was added on 2026-11-27

`openstax/osbooks-neuroscience/`, created with `tools/add-book.sh neuroscience "Introduction to Behavioral Neuroscience"` and pinned at the upstream head `6164a769d700843059a11fdd5e505e1c0efe1443`. It builds one book:

| Book | Collection | Shape | PDF | Web pages |
|---|---|---|---|---|
| *Introduction to Behavioral Neuroscience* | `introduction-behavioral-neuroscience` | 106 modules in 19 chapters; one level of nesting | 1,114 pages | 127 |

- **Licence:** CC BY-NC-SA 4.0 (collection XML and the upstream `LICENSE`); the built PDF states it.
- **Figures:** raster only (541 files, 310 MB); no SVG. One file name holds an en dash (`Image-12.04_Stress–critical-periods.png`).
- **Exercises:** 568 embedded links, counted in the CNXML: all in the `#exercise/<nickname>` scheme, none in `#ost/api/ex/<id>`. With no cache the converter leaves each one out and reports it as `exercise-uncached`.
- **Result:** built as PDF, EPUB and HTML on 2026-11-27, without the exercises.

### What the book needed from the toolchain

**A UTF-8 locale for pandoc.** The first HTML build stopped with "File media/Image-12.04_Stress–critical-periods.png not found in resource path", and the EPUB build before it had left the same figure out with only a warning. The file exists; its name holds an en dash, and in the image's POSIX locale pandoc cannot decode such a name. `openstax/tooling/entrypoint/html.sh` and `epub.sh` now set `LANG=C.UTF-8`. No other fetched book has a non-ASCII figure name (checked in every checkout's `media/`), so no other book's output changes. After the change the HTML build passed with the figure in it and the build log has no pandoc warning.

### Left as it is

The 40 embedded frames were dropped in that first build; since later the same day each is a labelled link (`tasks/archive/impo/2026/11/27/openstax-embedded-frame-links-are-dropped.md`). The converter reports no fallback besides the uncached exercises. The PDF and HTML were not read page by page; that review is the maintainer's.

## Plan (what is left)

- [ ] **Maintainer:** `make -C openstax/osbooks-neuroscience fetch-exercises` (needs the network; it writes `openstax/osbooks-neuroscience/checkout/exercises/` and its `COPYRIGHT` notice). If `checkout/` is missing: `./fetch.sh && ./apply.sh` in that folder first.
- [ ] Copy the cache to `openstax/osbooks-neuroscience/exercises/` as the other exercise books have it (compare `openstax/osbooks-physics/exercises/` and that folder's `apply.sh`, which copies a committed cache into the checkout), and commit it with its `COPYRIGHT` notice.
- [ ] `./apply.sh && make convert`; the converter's report should no longer list `exercise-uncached` (a few exercises missing from the server is normal; record the count). Then `make dist`.
- [ ] Update the exercise facts and page counts in `openstax/osbooks-neuroscience/CLAUDE.md` and `tasks/reference/openstax/book-inventory.md`, and the per-book table in `tasks/reference/tooling/converters.md`.
- [ ] Rewrite this task as a done-record, archive it, and tick it in the umbrella.
- [ ] **Maintainer:** the public backup, `bash tools/mirror-upstreams.sh push neuroscience`.

## Recorded so far

`openstax/osbooks-neuroscience/CLAUDE.md` ("The books this folder builds"), the list in `openstax/CLAUDE.md`, the inventory and its licence table, and the umbrella's checklist. The survey table (`tasks/reference/openstax/upstream-book-repositories.md`) is refreshed once for the whole 2026-11-27 batch.

## Open questions

None.
