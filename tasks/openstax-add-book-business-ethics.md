# Add `osbooks-business-ethics` to impo (one book): built, waiting for its exercise cache

**Status:** blocked
**Blocked on:** the maintainer running `make -C openstax/osbooks-business-ethics fetch-exercises` (the fetch identifies itself to OpenStax's server with his contact address, so it is his to run).
**Recheck:** `ls openstax/osbooks-business-ethics/checkout/exercises/*.json | wc -l` prints about 196 (one file per distinct exercise) and not an error.
**Part of:** `tasks/openstax-add-remaining-english-books.md`
**Priority:** 6
**Difficulty:** 2
**Created:** 2026-11-26 (William Emerison Six <billsix@gmail.com>: "I want to add all of the ones you said … make a task per book").

## BLUF

`openstax/osbooks-business-ethics/` was added on 2026-11-28 and builds one book as PDF, EPUB and HTML, but each of its 196 embedded exercises prints as a placeholder, because the exercise cache has not been fetched. Done means the cache is committed with its `COPYRIGHT` notice, the folder is rebuilt with the exercises in, and this task is archived.

## Context

**Read first:** "Adding a book" in `openstax/CLAUDE.md` (step 2 is what remains) and the umbrella `tasks/openstax-add-remaining-english-books.md`.

## What was added

`openstax/osbooks-business-ethics/`, created with `tools/add-book.sh business-ethics "Business Ethics"` and pinned at the upstream head `37c6dbe07bd93b5ead10942092a348d60d5dfd30`. It builds one book:

| Book | Collection | Shape | PDF | Web pages |
|---|---|---|---|---|
| *Business Ethics* | `business-ethics` | 61 modules in 11 chapters, from "Why Ethics Matter" to "Epilogue: Why Ethics Still Matter"; one level of nesting | 449 pages | 74 |

- **Licence:** CC BY-NC-SA 4.0 (collection XML and the upstream `LICENSE`); the built PDF states it.
- **Figures:** raster only (100 files, 50 MB); no SVG.
- **Exercises:** 196 embedded links, all in the `#exercise/<nickname>` scheme and none in the `#ost/api/ex/<id>` scheme (counted in the CNXML).
- **Result so far:** built as PDF, EPUB and HTML on 2026-11-28, without the exercises. The page counts above will grow when they are in.

## What the book needed from the toolchain

Nothing: it converted and built in one pass with the toolchain as it stood.

## Left as it is

The converter reports these fallbacks, where the element's text is kept: `inline:cite` (525), `inline:note` (525). The PDF and HTML were not read page by page; that review is the maintainer's.

## Plan (what remains)

- [ ] Maintainer: `make -C openstax/osbooks-business-ethics fetch-exercises`, which writes `openstax/osbooks-business-ethics/checkout/exercises/`.
- [ ] Agent: copy its `*.json` and `media/` (not `media-derived/`) to `openstax/osbooks-business-ethics/exercises/`, add the notice (`cp ../tooling/templates/exercises-COPYRIGHT exercises/COPYRIGHT`), `./apply.sh && make dist`, and commit the cache with its notice.
- [ ] Agent: correct the page counts and the exercise lines in the folder's `CLAUDE.md`, the inventory and `tasks/reference/tooling/converters.md`; tick the umbrella; archive this task.
- [ ] Maintainer: the public backup, `bash tools/mirror-upstreams.sh push business-ethics`.

## Recorded so far

`openstax/osbooks-business-ethics/CLAUDE.md` ("The books this folder builds"), the list in `openstax/CLAUDE.md`, the inventory and its licence table, the per-book table in `tasks/reference/tooling/converters.md`, and the umbrella's checklist. The survey table (`tasks/reference/openstax/upstream-book-repositories.md`) is refreshed once for the whole 2026-11-28 batch.

## Open questions

None.
