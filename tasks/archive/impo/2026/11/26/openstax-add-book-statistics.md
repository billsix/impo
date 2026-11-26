# Added `osbooks-statistics` to impo (one book)

**Done 2026-11-26** (agent; part of `tasks/openstax-add-remaining-english-books.md`. William Emerison Six <billsix@gmail.com>, 2026-11-26: "let's start with the math and physics books, do all of those ports one at time, commiting when done, archiving, committing").

## What was added

`openstax/osbooks-statistics/`, created with `tools/add-book.sh statistics "Statistics"` and pinned at the upstream head `7dea80ae2800386d470b11f6528962f9c4992d15`. It builds one book, OpenStax *Statistics*:

| | |
|---|---|
| Collection | `statistics`: 101 modules in 13 chapters, one level of nesting |
| Licence | CC BY 4.0 (collection XML and upstream `LICENSE`); the built PDF states it on the licence page and in "About This Edition" |
| Exercises | none embedded, counted in the CNXML in both link schemes; no `exercises/` cache, so nothing for the maintainer to fetch |
| Figures | raster only (about 700 files, 54 MB) |
| Result | PDF (1,042 pages), EPUB and HTML, built 2026-11-26 |

## What the book needed from the converter

1. **A crash.** `render_table` took `int()` of a table's `cols` attribute; one table has `cols=""`. A value that is not a number now counts as undeclared and the observed row width decides.
2. **Content MathML.** Six modules write some formulas in the dialect that says what a formula means (`<m:apply><m:divide/>…`), not how it looks. The converter fell back on it and printed the operands run together: the median example `(6.8 + 7.2) / 2 = 7` came out as bare numbers, and the sample mean lost its bar. `mml()` now renders `<cn>`, `<ci>`, `<apply>` and the older `<reln>` (`tasks/reference/tooling/converters.md`, "Content MathML"). Read back from the generated LaTeX: `\frac{6.8 + 7.2}{2} = 7` and `\overline{x}`.

## Proof that the other books were not disturbed

The maintainer asked for this while the work was under way ("please make sure the updates don't break the other mathml stuff we do in this repo").

- Every existing book was converted twice, with the committed converter and with the changed one, and the generated LaTeX compared file by file: **15 books identical** (977, 199, 200, 577, 137, 178, 142, 120, 116, 160, 343, 101, 274, 325 and 189 files).
- **Psychology 2e differed in one file, and the difference is a repair.** A memory exercise asks the reader to unscramble "AETPL"; the source writes those letters as a Content MathML identifier, and every edition impo had built printed nothing there. They now appear. Psychology was rebuilt.
- The older `<reln>` form and `<infinity/>` were added after that comparison; no existing book contains either (checked in every checkout), so they cannot change their output. After them the converter reports no MathML fallback at all for Statistics.
- The toolchain gate (`make -C openstax/tooling type-check`: ruff, the annotation checker, ty, pytest) passes with seven new tests, 54 in all.

## Left as they are

The converter still reports `inline:label` (586), `inline:item` (15), `inline:cite` and `inline:cite-title` (4 each), `inline:div` and `inline:list` (1 each) as fallbacks in this book. The same kinds are reported for the books impo already builds. The PDF and HTML were not read page by page; that review is the maintainer's.

## Recorded

`openstax/osbooks-statistics/CLAUDE.md` ("The books this folder builds"), the list in `openstax/CLAUDE.md`, the inventory and its licence table, the survey table (Statistics now "built in impo"), and the umbrella's checklist. The book still needs the maintainer's public backup: `bash tools/mirror-upstreams.sh push statistics`.
