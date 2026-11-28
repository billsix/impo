# Add `osbooks-principles-finance` to impo (one book): built, waiting for its exercise cache

**Status:** blocked
**Blocked on:** the maintainer running `make -C openstax/osbooks-principles-finance fetch-exercises` (the fetch identifies itself to OpenStax's server with his contact address, so it is his to run).
**Recheck:** `ls openstax/osbooks-principles-finance/checkout/exercises/*.json | wc -l` prints about 580 (one file per distinct exercise) and not an error.
**Part of:** `tasks/openstax-add-remaining-english-books.md`
**Priority:** 6
**Difficulty:** 2
**Created:** 2026-11-26 (William Emerison Six <billsix@gmail.com>: "I want to add all of the ones you said … make a task per book").

## BLUF

`openstax/osbooks-principles-finance/` was added on 2026-11-28 and builds one book as PDF, EPUB and HTML, but each of its 580 embedded exercises prints as a placeholder, because the exercise cache has not been fetched. Done means the cache is committed with its `COPYRIGHT` notice, the folder is rebuilt with the exercises in, and this task is archived.

## Context

**Read first:** "Adding a book" in `openstax/CLAUDE.md` (step 2 is what remains) and the umbrella `tasks/openstax-add-remaining-english-books.md`.

## What was added

`openstax/osbooks-principles-finance/`, created with `tools/add-book.sh principles-finance "Principles of Finance 2e"` and pinned at the upstream head `e3e5135ae36e21282d7afb4cccd5ce09f421d830`. It builds one book:

| Book | Collection | Shape | PDF | Web pages |
|---|---|---|---|---|
| *Principles of Finance 2e* | `principles-finance-2e` | 131 modules in 20 chapters, from "Introduction to Finance" to "Risk Management and the Financial Manager"; one level of nesting | 739 pages | 153 |

- **Licence:** CC BY-NC-SA 4.0 (collection XML and the upstream `LICENSE`); the built PDF states it.
- **Figures:** raster only (278 files, 31 MB); no SVG.
- **Exercises:** 580 embedded links, all in the `#exercise/<nickname>` scheme and none in the `#ost/api/ex/<id>` scheme (counted in the CNXML).
- **Result so far:** built as PDF, EPUB and HTML on 2026-11-28, without the exercises. The page counts above will grow when they are in.

## What the book needed from the toolchain

Nothing: it converted and built in one pass with the toolchain as it stood.

## Left as it is

The PDF and HTML were not read page by page; that review is the maintainer's.

## Plan (what remains)

- [ ] Maintainer: `make -C openstax/osbooks-principles-finance fetch-exercises`, which writes `openstax/osbooks-principles-finance/checkout/exercises/`.
- [ ] Agent: copy its `*.json` and `media/` (not `media-derived/`) to `openstax/osbooks-principles-finance/exercises/`, add the notice (`cp ../tooling/templates/exercises-COPYRIGHT exercises/COPYRIGHT`), `./apply.sh && make dist`, and commit the cache with its notice.
- [ ] Agent: correct the page counts and the exercise lines in the folder's `CLAUDE.md`, the inventory and `tasks/reference/tooling/converters.md`; tick the umbrella; archive this task.
- [ ] Maintainer: the public backup, `bash tools/mirror-upstreams.sh push principles-finance`.

## Recorded so far

`openstax/osbooks-principles-finance/CLAUDE.md` ("The books this folder builds"), the list in `openstax/CLAUDE.md`, the inventory and its licence table, the per-book table in `tasks/reference/tooling/converters.md`, and the umbrella's checklist. The survey table (`tasks/reference/openstax/upstream-book-repositories.md`) is refreshed once for the whole 2026-11-28 batch.

## Open questions

None.
