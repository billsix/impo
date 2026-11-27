# Added `osbooks-us-history` to impo (one book)

**Done 2026-11-27** (agent; part of `tasks/openstax-add-remaining-english-books.md`. William Emerison Six <billsix@gmail.com>, 2026-11-27: "for each book, do the work, commit, archive, commit").

## What was added

`openstax/osbooks-us-history/`, created with `tools/add-book.sh us-history "U.S. History"` and pinned at the upstream head `c05b860a035ff59a2ca1fd44339ef86694e09b57`. It builds one book:

| Book | Collection | Shape | PDF | Web pages |
|---|---|---|---|---|
| *U.S. History* | `us-history` | 177 modules in 32 chapters; one level of nesting | 1,308 pages | 211 |

- **Licence:** CC BY-NC-SA 4.0 (collection XML and the upstream `LICENSE`); the built PDF states it.
- **Figures:** raster only (607 files, 326 MB); no SVG.
- **Exercises:** none embedded, counted in the CNXML in both link schemes; no `exercises/` cache, so nothing for the maintainer to fetch.
- **Result:** built as PDF, EPUB and HTML on 2026-11-27.

## What the book needed from the toolchain

**Block quotations.** The book quotes its sources at length: 97 `<quote>` elements hold one or more paragraphs. The converter treated every `<quote>` as a few words inside a sentence, so a speech of several paragraphs was run into the paragraph before it between one pair of quotation marks. A quote that holds paragraphs is now a LaTeX `quote` environment (`_is_block_quote` in `openstax/tooling/tools/cnxml2tex/convert.py`; `tasks/reference/tooling/converters.md`, "Block quotations, reference notes and footnotes in titles"). The built HTML has 97 `<blockquote>` elements. The change also repaired block quotations in six books impo already built (Algebra 1, Astronomy 2e, Organic Chemistry, Physics, Psychology 2e, Writing Guide), which were rebuilt; the comparison is in the converter commit.

## Left as it is

The converter reports 303 `inline:label` fallbacks, a kind the other books also report. The PDF and HTML were not read page by page; that review is the maintainer's.

## Not done

The book needs the maintainer's public backup: `bash tools/mirror-upstreams.sh push us-history`.

## Recorded

`openstax/osbooks-us-history/CLAUDE.md` ("The books this folder builds"), the list in `openstax/CLAUDE.md`, the inventory and its licence table, and the umbrella's checklist. The survey table (`tasks/reference/openstax/upstream-book-repositories.md`) is refreshed once for the whole 2026-11-27 batch.
