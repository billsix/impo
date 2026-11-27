# Added `osbooks-introduction-philosophy` to impo (one book)

**Done 2026-11-27** (agent, with the exercise fetch run by the maintainer; part of `tasks/openstax-add-remaining-english-books.md`. William Emerison Six <billsix@gmail.com>, 2026-11-27: "you can make a branch, temporarily turn off gpg signing, and start working on all of them (minus the business ones for now)").

## What was added

`openstax/osbooks-introduction-philosophy/`, created with `tools/add-book.sh introduction-philosophy "Introduction to Philosophy"` and pinned at the upstream head `a0dbb585086d0302a9e509c0aa50f2ef436c3613`. It builds one book:

| Book | Collection | Shape | PDF | Web pages |
|---|---|---|---|---|
| *Introduction to Philosophy 2e* | `introduction-philosophy-2e` | 66 modules in 12 chapters; one level of nesting | 521 pages | 80 |

- **Licence:** CC BY-NC-SA 4.0 (collection XML and the upstream `LICENSE`); the built PDF states it.
- **Figures:** raster only (130 files; `media/` is 118 MB). `media/Interactive/` holds 525 more files, 127 of them SVG icons; no module references an SVG.
- **Exercises:** 228 embedded links to 228 exercises, all in the `#exercise/<nickname>` scheme, none in `#ost/api/ex/<id>`. The maintainer ran `make fetch-exercises` on 2026-11-27; all 228 are in the committed cache `openstax/osbooks-introduction-philosophy/exercises/` (no images) with its `COPYRIGHT` notice, copied in from `openstax/tooling/templates/exercises-COPYRIGHT` because the fetch does not write it.
- **Result:** built as PDF, EPUB and HTML on 2026-11-27 with the exercises in; the converter reports no `exercise-uncached` and the build log has no pandoc warning. The first build of the day, without the exercises, is the commit that added the folder.

## What the book needed from the toolchain

**A quotation that holds a list.** In module `m00034` the three numbered premises of an argument are quoted as a `<quote>` holding an enumerated list and no paragraph. The converter set off a quote only when it held paragraphs, so this one stayed inline: the three premises ran together between quotation marks with their numbers lost, and the converter reported `inline:list` and `inline:item`. A quote holding a list is a block quotation now (`_is_block_quote` in `openstax/tooling/tools/cnxml2tex/convert.py`; `tasks/reference/tooling/converters.md`, "Block quotations, reference notes and footnotes in titles"). The same change restored lists in five section files of Algebra 1 and one of Foundations of Information Systems, which were rebuilt; the other 34 fetched book folders converted to identical LaTeX.

## Left as it is

The PDF leaves out six characters the body font has no glyph for (`ǐ`, `ʿ`, `Ḥ`, `ṇ`, `Ṣ`, `ṣ`, nine places in Chinese, Arabic and Sanskrit names); the HTML and EPUB have them. Every book impo builds has this gap, so it has its own task: `tasks/archive/impo/2026/11/27/openstax-pdf-characters-missing-from-the-body-font.md`. The converter reports no fallback. The PDF and HTML were not read page by page; that review is the maintainer's.

## Not done

The book needs the maintainer's public backup: `bash tools/mirror-upstreams.sh push introduction-philosophy`.

## Recorded

`openstax/osbooks-introduction-philosophy/CLAUDE.md` ("The books this folder builds"), the lists and counts in `openstax/CLAUDE.md` and the root `CLAUDE.md`, the inventory and its licence table, the converter quick reference, the survey table and the umbrella's checklist.
