# Add `osbooks-principles-marketing` to impo (one book): built, waiting for its exercise cache

**Status:** blocked
**Blocked on:** the maintainer running `make -C openstax/osbooks-principles-marketing fetch-exercises` (the fetch identifies itself to OpenStax's server with his contact address, so it is his to run).
**Recheck:** `ls openstax/osbooks-principles-marketing/checkout/exercises/*.json | wc -l` prints about 662 (one file per distinct exercise) and not an error.
**Part of:** `tasks/openstax-add-remaining-english-books.md`
**Priority:** 6
**Difficulty:** 2
**Created:** 2026-11-26 (William Emerison Six <billsix@gmail.com>: "I want to add all of the ones you said … make a task per book").

## BLUF

`openstax/osbooks-principles-marketing/` was added on 2026-11-28 and builds one book as PDF, EPUB and HTML, but each of its 662 embedded exercises prints as a placeholder, because the exercise cache has not been fetched. Done means the cache is committed with its `COPYRIGHT` notice, the folder is rebuilt with the exercises in, and this task is archived.

## Context

**Read first:** "Adding a book" in `openstax/CLAUDE.md` (step 2 is what remains) and the umbrella `tasks/openstax-add-remaining-english-books.md`.

## What was added

`openstax/osbooks-principles-marketing/`, created with `tools/add-book.sh principles-marketing "Principles of Marketing"` and pinned at the upstream head `a6d7372579d13e0a733954953c4613867f018a48`. It builds one book:

| Book | Collection | Shape | PDF | Web pages |
|---|---|---|---|---|
| *Principles of Marketing* | `principles-marketing` | 132 modules in 19 chapters, from "Marketing and Customer Value" to "Sustainable Marketing: The New Paradigm"; two levels of nesting (units, then chapters) | 831 pages | 24 |

- **Licence:** CC BY-NC-SA 4.0 (collection XML and the upstream `LICENSE`); the built PDF states it.
- **Figures:** raster only (237 files, 62 MB); no SVG.
- **Exercises:** 662 embedded links, all in the `#exercise/<nickname>` scheme and none in the `#ost/api/ex/<id>` scheme (counted in the CNXML).
- **Result so far:** built as PDF, EPUB and HTML on 2026-11-28, without the exercises. The page counts above will grow when they are in.

## What the book needed from the toolchain

One converter fix. A display equation whose only row is a table (the customer lifetime value formula in module `m00018`, followed by line-break marks) was wrapped in `aligned` with an alignment tab at its `=`, which fell inside the table's `array` and stopped the PDF ("Extra alignment tab"). `render_equation` in `openstax/tooling/tools/cnxml2tex/convert.py` now leaves a single row as it is.

## Left as it is

The converter reports these fallbacks, where the element's text is kept: `inline:cite` (893), `inline:note` (893), `inline:para` (4). The PDF and HTML were not read page by page; that review is the maintainer's.

## Plan (what remains)

- [ ] Maintainer: `make -C openstax/osbooks-principles-marketing fetch-exercises`, which writes `openstax/osbooks-principles-marketing/checkout/exercises/`.
- [ ] Agent: copy its `*.json` and `media/` (not `media-derived/`) to `openstax/osbooks-principles-marketing/exercises/`, add the notice (`cp ../tooling/templates/exercises-COPYRIGHT exercises/COPYRIGHT`), `./apply.sh && make dist`, and commit the cache with its notice.
- [ ] Agent: correct the page counts and the exercise lines in the folder's `CLAUDE.md`, the inventory and `tasks/reference/tooling/converters.md`; tick the umbrella; archive this task.
- [ ] Maintainer: the public backup, `bash tools/mirror-upstreams.sh push principles-marketing`.

## Recorded so far

`openstax/osbooks-principles-marketing/CLAUDE.md` ("The books this folder builds"), the list in `openstax/CLAUDE.md`, the inventory and its licence table, the per-book table in `tasks/reference/tooling/converters.md`, and the umbrella's checklist. The survey table (`tasks/reference/openstax/upstream-book-repositories.md`) is refreshed once for the whole 2026-11-28 batch.

## Open questions

None.
