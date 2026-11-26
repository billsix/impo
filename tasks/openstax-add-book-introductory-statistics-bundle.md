# Added `osbooks-introductory-statistics-bundle` to impo (2 books)

**Done 2026-11-26** (agent; part of `tasks/openstax-add-remaining-english-books.md`, in the mathematics and physics group the maintainer asked for first).

## What was added

`openstax/osbooks-introductory-statistics-bundle/`, created with `tools/add-book.sh introductory-statistics-bundle "Introductory Statistics"` and pinned at the upstream head `24e9884724b13baba2b8879d03103cccafc7e25d`. It builds two books that share none of their 179 modules:

| Book | Collection | Modules | PDF |
|---|---|---|---|
| *Introductory Statistics 2e* | `introductory-statistics-2e` | 102, in 13 chapters | 1,009 pages |
| *Introductory Business Statistics 2e* | `introductory-business-statistics-2e` | 77, in 13 chapters | 759 pages |

- **Licence:** CC BY-NC-SA 4.0 (both collection XML files and the upstream `LICENSE`); the built PDF states it.
- **Exercises:** none embedded in either book, counted in the CNXML in both link schemes; no `exercises/` cache, so nothing for the maintainer to fetch.
- **Figures:** raster only (91 MB).
- **Result:** both books built as PDF, EPUB and HTML on 2026-11-26, in one pass.

## What it needed

Nothing from the converter. The fixes made for Statistics the same day covered it: this bundle has one Content MathML formula, which converted. The converter's report listed only the usual inline fallbacks (`inline:label` 745, `inline:cite-title` 17, `inline:item` 15, `inline:cite` 13, `inline:div` and `inline:list` 1 each).

One fix to the scaffold tool: the upstream `LICENSE` file has Windows line endings, so `tools/add-book.sh` did not recognise its first line and wrote a generic phrase into the README. The tool now strips carriage returns and takes the first non-blank line; the README was corrected. (That fix was committed with the Statistics book.)

## Not done

The PDFs and HTML were not read page by page; that review is the maintainer's. The book needs his public backup: `bash tools/mirror-upstreams.sh push introductory-statistics-bundle`.

## Recorded

`openstax/osbooks-introductory-statistics-bundle/CLAUDE.md`, the list in `openstax/CLAUDE.md`, the inventory and its licence table, the survey table, and the umbrella's checklist.
