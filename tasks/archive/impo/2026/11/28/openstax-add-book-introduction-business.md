# Added `osbooks-introduction-business` to impo (one book)

**Done 2026-11-28** (agent; part of `tasks/openstax-add-remaining-english-books.md`. William Emerison Six <billsix@gmail.com>, 2026-11-28: "work them all, do the work, commit, archive, commit, next").

## What was added

`openstax/osbooks-introduction-business/`, created with `tools/add-book.sh introduction-business "Introduction to Business 2e"` and pinned at the upstream head `2a839877ab89a207c9b9e501df438173013fa45c`. It builds one book:

| Book | Collection | Shape | PDF | Web pages |
|---|---|---|---|---|
| *Introduction to Business 2e* | `introduction-business-2e` | 153 modules in 17 chapters, from "Understanding Economic Systems and Business" to "Your Career in Business"; one level of nesting | 842 pages | 172 |

- **Licence:** CC BY-NC-SA 4.0 (collection XML); the built PDF states it. The upstream `LICENSE` file is the text of CC BY 4.0, but the collection XML declares CC BY-NC-SA 4.0, and so does the book's preface on openstax.org (https://openstax.org/books/introduction-business-2e/pages/preface, read 2026-11-28). The converter reads the collection, so the built book states CC BY-NC-SA 4.0. The survey table reads the `LICENSE` file and shows CC BY 4.0 for this repository.
- **Figures:** raster only (197 files, 237 MB); no SVG.
- **Exercises:** none embedded, counted in the CNXML in both link schemes; no `exercises/` cache, so nothing for the maintainer to fetch.
- **Result:** built as PDF, EPUB and HTML on 2026-11-28.

## What the book needed from the toolchain

Nothing: it converted and built in one pass with the toolchain as it stood.

## Left as it is

The PDF and HTML were not read page by page; that review is the maintainer's.

## Not done

The book needs the maintainer's public backup: `bash tools/mirror-upstreams.sh push introduction-business`.

## Recorded

`openstax/osbooks-introduction-business/CLAUDE.md` ("The books this folder builds"), the list in `openstax/CLAUDE.md`, the inventory and its licence table, the per-book table in `tasks/reference/tooling/converters.md`, and the umbrella's checklist. The survey table (`tasks/reference/openstax/upstream-book-repositories.md`) is refreshed once for the whole 2026-11-28 batch.
