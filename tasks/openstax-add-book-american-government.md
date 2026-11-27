# Added `osbooks-american-government` to impo (one book)

**Done 2026-11-27** (agent; part of `tasks/openstax-add-remaining-english-books.md`. William Emerison Six <billsix@gmail.com>, 2026-11-27: "for each book, do the work, commit, archive, commit").

## What was added

`openstax/osbooks-american-government/`, created with `tools/add-book.sh american-government "American Government 4e"` and pinned at the upstream head `a2677245241954039c7ebc996e82a8f3b0b4376f`. It builds one book:

| Book | Collection | Shape | PDF | Web pages |
|---|---|---|---|---|
| *American Government 4e* | `american-government-4e` | 100 modules in 17 chapters grouped into 5 units; two levels of nesting | 918 pages | 24 |

- **Licence:** CC BY-NC-SA 4.0 (collection XML and the upstream `LICENSE`); the built PDF states it.
- **Figures:** raster only (335 files, 169 MB); no SVG.
- **Exercises:** none embedded, counted in the CNXML in both link schemes; no `exercises/` cache, so nothing for the maintainer to fetch.
- **Result:** built as PDF, EPUB and HTML on 2026-11-27.

## What the book needed from the toolchain

**Reference notes.** The book cites a source 1,342 times as `<cite><note class="reference">source</note></cite>` in the middle of a sentence. The converter printed the source's text inline, so the first build (902 pages) had a bibliographic entry inside nearly every paragraph. Each is now a footnote; the 9 inside figure captions follow in parentheses, since a footnote cannot be relied on there (`tasks/reference/tooling/converters.md`, "Block quotations, reference notes and footnotes in titles"). Read back from the build: 1,333 `\footnote` in the generated LaTeX and 1,333 footnote references in the HTML. The PDF is 918 pages. Its 19 block quotations are set off by the change U.S. History needed.

## Left as it is

The web edition has 24 pages for 100 modules, because a book with two levels of nesting is split per chapter (the same holds for the other unit-nested books). The converter reports no fallback. The PDF and HTML were not read page by page; that review is the maintainer's.

## Not done

The book needs the maintainer's public backup: `bash tools/mirror-upstreams.sh push american-government`.

## Recorded

`openstax/osbooks-american-government/CLAUDE.md` ("The books this folder builds"), the list in `openstax/CLAUDE.md`, the inventory and its licence table, and the umbrella's checklist. The survey table (`tasks/reference/openstax/upstream-book-repositories.md`) is refreshed once for the whole 2026-11-27 batch.
