# Add `osbooks-principles-data-science` to impo (one book): built, waiting for its exercises

**Status:** blocked
**Blocked on:** the maintainer running `make -C openstax/osbooks-principles-data-science fetch-exercises` (the fetch identifies itself to OpenStax's server with his contact address, so it is his to run)
**Recheck:** `ls openstax/osbooks-principles-data-science/checkout/exercises/*.json | wc -l` — cleared when it prints a number near 136
**Part of:** `tasks/openstax-add-remaining-english-books.md`
**Priority:** 4
**Difficulty:** 2 (what is left is a fetch, a rebuild and the record)
**Created:** 2026-11-26 (William Emerison Six <billsix@gmail.com>: "I want to add all of the ones you said … make a task per book"). Built 2026-11-27 (agent).

## BLUF

`openstax/osbooks-principles-data-science/` is committed and builds one book as PDF, EPUB and HTML, but without the 136 practice exercises the source embeds: they come from OpenStax's exercise server, and that fetch is the maintainer's. Done means the exercise cache is committed with its `COPYRIGHT` notice, the book is rebuilt with the exercises in it, and this task is archived.

## Context

**Read first:** `openstax/CLAUDE.md` ("Adding a book", and "The content model" for the exercise cache) and `openstax/osbooks-principles-data-science/CLAUDE.md`.

### What was added on 2026-11-27

`openstax/osbooks-principles-data-science/`, created with `tools/add-book.sh principles-data-science "Principles of Data Science"` and pinned at the upstream head `cc5a81d59c7d9b8b153a2297098e89dfaca7b2d3`. It builds one book:

| Book | Collection | Shape | PDF | Web pages |
|---|---|---|---|---|
| *Principles of Data Science* | `principles-data-science` | 59 modules in 10 chapters grouped into 4 units, from "Introducing Data Science and Data Collection" to "Maintaining a Professional and Ethical Data Science Practice"; two levels of nesting | 600 pages | 16 |

- **Licence:** CC BY-NC-SA 4.0 (collection XML and the upstream `LICENSE`); the built PDF states it.
- **Figures:** raster only (232 files, 40 MB); no SVG.
- **Exercises:** 136 embedded links, counted in the CNXML: all in the `#exercise/<nickname>` scheme, none in `#ost/api/ex/<id>`. With no cache the converter leaves each one out and reports it as `exercise-uncached`.
- **Result:** built as PDF, EPUB and HTML on 2026-11-27, without the exercises.

### What the book needed from the toolchain

**One line of code wrapped in line breaks.** The first PDF build stopped with "Paragraph ended before \text@command was complete": the book writes many one-line code samples as `<code class="python">` with a blank line before the code, and the converter put that blank line inside a `\texttt{}`. Such a block standing between paragraphs is now a one-line listing, and inside a sentence it is inline code with the breaks trimmed (`tasks/reference/tooling/converters.md`, "One line of code wrapped in line breaks"). The change also repaired code blocks in Introduction to Python Programming (30 section files), which was rebuilt.

### Left as it is

x The PDF and HTML were not read page by page; that review is the maintainer's.

## Plan (what is left)

- [ ] **Maintainer:** `make -C openstax/osbooks-principles-data-science fetch-exercises` (needs the network; it writes `openstax/osbooks-principles-data-science/checkout/exercises/` and its `COPYRIGHT` notice). If `checkout/` is missing: `./fetch.sh && ./apply.sh` in that folder first.
- [ ] Copy the cache to `openstax/osbooks-principles-data-science/exercises/` as the other exercise books have it (compare `openstax/osbooks-physics/exercises/` and that folder's `apply.sh`, which copies a committed cache into the checkout), and commit it with its `COPYRIGHT` notice.
- [ ] `./apply.sh && make convert`; the converter's report should no longer list `exercise-uncached` (a few exercises missing from the server is normal; record the count). Then `make dist`.
- [ ] Update the exercise facts and page counts in `openstax/osbooks-principles-data-science/CLAUDE.md` and `tasks/reference/openstax/book-inventory.md`, and the per-book table in `tasks/reference/tooling/converters.md`.
- [ ] Rewrite this task as a done-record, archive it, and tick it in the umbrella.
- [ ] **Maintainer:** the public backup, `bash tools/mirror-upstreams.sh push principles-data-science`.

## Recorded so far

`openstax/osbooks-principles-data-science/CLAUDE.md` ("The books this folder builds"), the list in `openstax/CLAUDE.md`, the inventory and its licence table, and the umbrella's checklist. The survey table (`tasks/reference/openstax/upstream-book-repositories.md`) is refreshed once for the whole 2026-11-27 batch.

## Open questions

None.
