# Added `osbooks-entrepreneurship` to impo (one book)

**Done 2026-11-28** (agent; part of `tasks/openstax-add-remaining-english-books.md`. William Emerison Six <billsix@gmail.com>, 2026-11-28: "work them all, do the work, commit, archive, commit, next").

## What was added

`openstax/osbooks-entrepreneurship/`, created with `tools/add-book.sh entrepreneurship "Entrepreneurship"` and pinned at the upstream head `2ac8635c0711ea3754336ce8a4042bbe8a009801`. It builds one book:

| Book | Collection | Shape | PDF | Web pages |
|---|---|---|---|---|
| *Entrepreneurship* | `entrepreneurship` | 79 modules in 15 chapters, from "The Entrepreneurial Perspective" to "Next Steps"; one level of nesting | 805 pages | 96 |

- **Licence:** CC BY-NC-SA 4.0 (collection XML and the upstream `LICENSE`); the built PDF states it.
- **Figures:** raster only (222 files, 156 MB); no SVG.
- **Exercises:** none embedded, counted in the CNXML in both link schemes; no `exercises/` cache, so nothing for the maintainer to fetch.
- **Result:** built as PDF, EPUB and HTML on 2026-11-28.

## What the book needed from the toolchain

One converter fix. A section title carries a footnote ("Business Model Canvas" in module `m71178`, an attribution of CC BY material), and a footnote in a heading stopped the PDF when the title travelled to the contents ("Use of \@xfootnote doesn't match its definition"). `render_section` in `openstax/tooling/tools/cnxml2tex/convert.py` now gives such a heading a short form without the footnote for the contents and running heads; the footnote still prints under the heading.

## Left as it is

The PDF and HTML were not read page by page; that review is the maintainer's.

## Not done

The book needs the maintainer's public backup: `bash tools/mirror-upstreams.sh push entrepreneurship`.

## Recorded

`openstax/osbooks-entrepreneurship/CLAUDE.md` ("The books this folder builds"), the list in `openstax/CLAUDE.md`, the inventory and its licence table, the per-book table in `tasks/reference/tooling/converters.md`, and the umbrella's checklist. The survey table (`tasks/reference/openstax/upstream-book-repositories.md`) is refreshed once for the whole 2026-11-28 batch.
