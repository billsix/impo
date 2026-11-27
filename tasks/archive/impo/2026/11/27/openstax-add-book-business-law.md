# Added `osbooks-business-law` to impo (one book)

**Done 2026-11-27** (agent; part of `tasks/openstax-add-remaining-english-books.md`. William Emerison Six <billsix@gmail.com>, 2026-11-27: "for each book, do the work, commit, archive, commit").

## What was added

`openstax/osbooks-business-law/`, created with `tools/add-book.sh business-law "Business Law I Essentials 2e"` and pinned at the upstream head `0502c9f293fdb7745b76c4d7855d49acdaf8098b`. It builds one book:

| Book | Collection | Shape | PDF | Web pages |
|---|---|---|---|---|
| *Business Law I Essentials 2e* | `business-law-i-essentials-2e` | 47 modules in 14 chapters, from "American Law, Legal Reasoning, and the Legal System" to "Securities Regulation"; one level of nesting | 181 pages | 63 |

- **Licence:** CC BY-NC-SA 4.0 (collection XML and the upstream `LICENSE`); the built PDF states it.
- **Figures:** raster only (66 files, 12 MB); no SVG.
- **Exercises:** none embedded, counted in the CNXML in both link schemes; no `exercises/` cache, so nothing for the maintainer to fetch.
- **Result:** built as PDF, EPUB and HTML on 2026-11-27.

## What the book needed from the toolchain

Nothing: it converted and built in one pass with the toolchain as it stood.

## Left as it is

The converter reports eight `inline:span` fallbacks (the span's text is kept), a kind the other books also report. The PDF and HTML were not read page by page; that review is the maintainer's.

## Not done

The book needs the maintainer's public backup: `bash tools/mirror-upstreams.sh push business-law`.

## Recorded

`openstax/osbooks-business-law/CLAUDE.md` ("The books this folder builds"), the list in `openstax/CLAUDE.md`, the inventory and its licence table, and the umbrella's checklist. The survey table (`tasks/reference/openstax/upstream-book-repositories.md`) is refreshed once for the whole 2026-11-27 batch.
