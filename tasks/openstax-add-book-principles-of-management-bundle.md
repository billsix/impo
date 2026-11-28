# Added `osbooks-principles-of-management-bundle` to impo (2 books)

**Done 2026-11-28** (agent; part of `tasks/openstax-add-remaining-english-books.md`. William Emerison Six <billsix@gmail.com>, 2026-11-28: "work them all, do the work, commit, archive, commit, next").

## What was added

`openstax/osbooks-principles-of-management-bundle/`, created with `tools/add-book.sh principles-of-management-bundle "Principles of Management"` and pinned at the upstream head `f2b749648a176dbe114dbc4e35ec20c030be4713`. It builds 2 books:

| Book | Collection | Shape | PDF | Web pages |
|---|---|---|---|---|
| *Principles of Management* | `principles-management` | 132 modules in 18 chapters, from "Managing and Performing" to "Management of Technology and Innovation"; one level of nesting | 767 pages | 152 |
| *Organizational Behavior* | `organizational-behavior` | 121 modules in 19 chapters, from "Management and Organizational Behavior" to "Entrepreneurship"; one level of nesting | 783 pages | 142 |

- **Licence:** CC BY-NC-SA 4.0 (collection XML and the upstream `LICENSE`); the built PDF states it.
- **Figures:** raster only (278 files, 82 MB); no SVG.
- **Exercises:** none embedded, counted in the CNXML in both link schemes; no `exercises/` cache, so nothing for the maintainer to fetch.
- **Result:** built as PDF, EPUB and HTML on 2026-11-28.

## What the book needed from the toolchain

One converter fix. A figure file is named with two spaces in a row (`Exhibit 13-4 Typical Response  Patterns in Dyadic Power Relationships.png`); TeX reads a run of spaces as one, so the PDF build did not find the file. `_imgname` in `openstax/tooling/tools/cnxml2tex/convert.py` now writes each further space as `\space`, and `openstax/tooling/tools/pandoc/preprocess.py` turns it back for the web editions.

## Left as it is

The converter reports these fallbacks, where the element's text is kept: `inline:para` (4), `inline:equation` (2). The PDF and HTML were not read page by page; that review is the maintainer's.

## Not done

The book needs the maintainer's public backup: `bash tools/mirror-upstreams.sh push principles-of-management-bundle`.

## Recorded

`openstax/osbooks-principles-of-management-bundle/CLAUDE.md` ("The books this folder builds"), the list in `openstax/CLAUDE.md`, the inventory and its licence table, the per-book table in `tasks/reference/tooling/converters.md`, and the umbrella's checklist. The survey table (`tasks/reference/openstax/upstream-book-repositories.md`) is refreshed once for the whole 2026-11-28 batch.
