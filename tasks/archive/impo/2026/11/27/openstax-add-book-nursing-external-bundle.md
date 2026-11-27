# Added `osbooks-nursing-external-bundle` to impo (3 books)

**Done 2026-11-27** (agent, with the exercise fetch run by the maintainer; part of `tasks/openstax-add-remaining-english-books.md`. William Emerison Six <billsix@gmail.com>, 2026-11-27: "you can make a branch, temporarily turn off gpg signing, and start working on all of them (minus the business ones for now)").

## What was added

`openstax/osbooks-nursing-external-bundle/`, created with `tools/add-book.sh nursing-external-bundle "Nursing (Pharmacology, Nutrition and Population Health for Nurses)"` and pinned at the upstream head `128c6c3e0ee66850bd8cbb3aa02be736f10db74e`. It builds 3 books:

| Book | Collection | Shape | PDF | Web pages |
|---|---|---|---|---|
| *Pharmacology for Nurses* | `pharmacology` | 203 modules in 40 chapters grouped into 11 units; two levels of nesting | 1,267 pages | 53 |
| *Nutrition for Nurses* | `nutrition` | 93 modules in 20 chapters grouped into 9 units; two levels of nesting | 537 pages | 31 |
| *Population Health for Nurses* | `population-health` | 185 modules in 35 chapters grouped into 7 units; two levels of nesting | 1,400 pages | 44 |

- **Licence:** CC BY-NC-SA 4.0 (collection XML and the upstream `LICENSE`); the built PDF states it.
- **Figures:** raster only (419 files, 142 MB); no SVG.
- **Exercises:** 1,156 embedded links to 1,156 exercises, all in the `#exercise/<nickname>` scheme, none in `#ost/api/ex/<id>`. The maintainer ran `make fetch-exercises` on 2026-11-27; all 1,156 are in the committed cache `openstax/osbooks-nursing-external-bundle/exercises/` (no images) with its `COPYRIGHT` notice, copied in from `openstax/tooling/templates/exercises-COPYRIGHT` because the fetch does not write it.
- **Result:** built as PDF, EPUB and HTML on 2026-11-27 with the exercises in; the converter reports no `exercise-uncached` and the build log has no pandoc warning. The first build of the day, without the exercises, is the commit that added the folder.

## What the book needed from the toolchain

**A paragraph of only line breaks.** The preface of Population Health for Nurses holds a `<para>` with eight `<newline/>`s and nothing else, used as vertical space. It became a run of line breaks with no line to end, and the first build of that book stopped ("There's no line here to end"); the other two books built. `cleanup_latex` now drops such a run. **Coloured spans.** The books wrap table text in `<span class="blue-text">` 3,375 times; the converter set the words correctly and listed each span in its fallback report, and a span is known markup now. Both are in `tasks/reference/tooling/converters.md`, "Block quotations, reference notes and footnotes in titles"; no other fetched book converts differently.

## Left as it is

**The tables are the weak point of these three PDFs.** The books hold 714 tables and most are prose. The converter's columns do not wrap, so a wide table is scaled down to the page width: Table 3.33 of Pharmacology for Nurses is at about half size, and Table 7.12 of Population Health for Nurses (PDF page 1371) is a hairline. The HTML and EPUB set the same tables normally. It affects books impo already built too and has its own task: `tasks/archive/impo/2026/11/27/openstax-pdf-prose-tables-shrink-or-run-off-the-page.md`. Nutrition for Nurses also loses `⅓`, `₁` and `₆` in the PDF (`tasks/archive/impo/2026/11/27/openstax-pdf-characters-missing-from-the-body-font.md`). The repository holds 492 module folders and the three collections list 481. The converter reports no fallback. The PDFs and HTML were not read page by page; that review is the maintainer's.

## Not done

The book needs the maintainer's public backup: `bash tools/mirror-upstreams.sh push nursing-external-bundle`.

## Recorded

`openstax/osbooks-nursing-external-bundle/CLAUDE.md` ("The books this folder builds"), the lists and counts in `openstax/CLAUDE.md` and the root `CLAUDE.md`, the inventory and its licence table, the converter quick reference, the survey table and the umbrella's checklist.
