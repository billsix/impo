# Add `osbooks-nursing-external-bundle` to impo (3 books): built, waiting for its exercises

**Status:** blocked
**Blocked on:** the maintainer running `make -C openstax/osbooks-nursing-external-bundle fetch-exercises` (the fetch identifies itself to OpenStax's server with his contact address, so it is his to run)
**Recheck:** `ls openstax/osbooks-nursing-external-bundle/checkout/exercises/*.json | wc -l` — cleared when it prints a number near 1156
**Part of:** `tasks/openstax-add-remaining-english-books.md`
**Priority:** 5
**Difficulty:** 2 (what is left is a fetch, a rebuild and the record)
**Created:** 2026-11-26 (William Emerison Six <billsix@gmail.com>: "I want to add all of the ones you said … make a task per book"). Built 2026-11-27 (agent; William Emerison Six <billsix@gmail.com>, 2026-11-27: "you can make a branch, temporarily turn off gpg signing, and start working on all of them (minus the business ones for now)").

## BLUF

`openstax/osbooks-nursing-external-bundle/` is committed and builds 3 books as PDF, EPUB and HTML, but without the 1,156 practice exercises the source embeds: they come from OpenStax's exercise server, and that fetch is the maintainer's. Done means the exercise cache is committed with its `COPYRIGHT` notice, the book is rebuilt with the exercises in it, and this task is archived.

## Context

**Read first:** `openstax/CLAUDE.md` ("Adding a book", and "The content model" for the exercise cache) and `openstax/osbooks-nursing-external-bundle/CLAUDE.md`.

### What was added on 2026-11-27

`openstax/osbooks-nursing-external-bundle/`, created with `tools/add-book.sh nursing-external-bundle "Nursing (Pharmacology, Nutrition and Population Health for Nurses)"` and pinned at the upstream head `128c6c3e0ee66850bd8cbb3aa02be736f10db74e`. It builds 3 books:

| Book | Collection | Shape | PDF | Web pages |
|---|---|---|---|---|
| *Pharmacology for Nurses* | `pharmacology` | 203 modules in 40 chapters grouped into 11 units; two levels of nesting | 1,244 pages | 53 |
| *Nutrition for Nurses* | `nutrition` | 93 modules in 20 chapters grouped into 9 units; two levels of nesting | 520 pages | 31 |
| *Population Health for Nurses* | `population-health` | 185 modules in 35 chapters grouped into 7 units; two levels of nesting | 1,374 pages | 44 |

- **Licence:** CC BY-NC-SA 4.0 (collection XML and the upstream `LICENSE`); the built PDF states it.
- **Figures:** raster only (419 files, 142 MB); no SVG.
- **Exercises:** 1,156 embedded links, counted in the CNXML: all in the `#exercise/<nickname>` scheme, none in `#ost/api/ex/<id>`. With no cache the converter leaves each one out and reports it as `exercise-uncached`.
- **Result:** built as PDF, EPUB and HTML on 2026-11-27, without the exercises; the build log has no pandoc warning.

### What the book needed from the toolchain

**A paragraph of only line breaks.** The preface of Population Health for Nurses holds a `<para>` with eight `<newline/>`s and nothing else, used as vertical space. It became a run of line breaks with no line to end, and the first build of that book stopped ("There's no line here to end"); the other two books built. `cleanup_latex` now drops such a run. **Coloured spans.** The books wrap table text in `<span class="blue-text">` 3,375 times; the converter set the words correctly and listed each span in its fallback report, and a span is known markup now. Both are in `tasks/reference/tooling/converters.md`, "Block quotations, reference notes and footnotes in titles"; no other fetched book converts differently.

### Left as it is

**The tables are the weak point of these three PDFs.** The books hold 714 tables and most are prose. The converter's columns do not wrap, so a wide table is scaled down to the page width: Table 3.33 of Pharmacology for Nurses is at about half size, and Table 7.12 of Population Health for Nurses (PDF page 1371) is a hairline. The HTML and EPUB set the same tables normally. It affects books impo already built too and has its own task: `tasks/openstax-pdf-prose-tables-shrink-or-run-off-the-page.md`. Nutrition for Nurses also loses `⅓`, `₁` and `₆` in the PDF (`tasks/openstax-pdf-characters-missing-from-the-body-font.md`). The repository holds 492 module folders and the three collections list 481. The converter reports no fallback besides the uncached exercises. The PDFs and HTML were not read page by page; that review is the maintainer's.

## Plan (what is left)

- [ ] **Maintainer:** `make -C openstax/osbooks-nursing-external-bundle fetch-exercises` (needs the network; it writes `openstax/osbooks-nursing-external-bundle/checkout/exercises/`). If `checkout/` is missing: `./fetch.sh && ./apply.sh` in that folder first.
- [ ] Copy the cache's `*.json` and `media/` (not `media-derived/`) to `openstax/osbooks-nursing-external-bundle/exercises/`, add the notice (`cp openstax/tooling/templates/exercises-COPYRIGHT openstax/osbooks-nursing-external-bundle/exercises/COPYRIGHT`; the fetch does not write it), and commit the cache with its notice.
- [ ] `./apply.sh && make convert`; the converter's report should no longer list `exercise-uncached` (a few exercises missing from the server is normal; record the count). Then `make dist`.
- [ ] Update the exercise facts and page counts in `openstax/osbooks-nursing-external-bundle/CLAUDE.md` and `tasks/reference/openstax/book-inventory.md`, and the per-book table in `tasks/reference/tooling/converters.md`.
- [ ] Rewrite this task as a done-record, archive it, and tick it in the umbrella.
- [ ] **Maintainer:** the public backup, `bash tools/mirror-upstreams.sh push nursing-external-bundle`.

## Recorded so far

`openstax/osbooks-nursing-external-bundle/CLAUDE.md` ("The books this folder builds"), the lists and counts in `openstax/CLAUDE.md` and the root `CLAUDE.md`, the inventory and its licence table, the converter quick reference and the umbrella's checklist. The survey table (`tasks/reference/openstax/upstream-book-repositories.md`) is refreshed once for the whole batch.

## Open questions

None.
