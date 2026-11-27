# Added `osbooks-college-physics-bundle` to impo (2 books)

**Done 2026-11-26** (agent; part of `tasks/openstax-add-remaining-english-books.md`, in the mathematics and physics group the maintainer asked for first).

## What was added

`openstax/osbooks-college-physics-bundle/`, created with `tools/add-book.sh college-physics-bundle "College Physics"` and pinned at the upstream head `66fcef29596e3a32818162b837dd0c85b754cbad`. It builds two books of 283 modules each, 34 chapters, sharing 248 modules (318 distinct):

| Book | Collection | PDF |
|---|---|---|
| *College Physics 2e* | `college-physics-2e` | 2,552 pages |
| *College Physics for AP® Courses 2e* | `college-physics-ap-courses-2e` | 2,595 pages |

- **Licence:** CC BY-NC-SA 4.0 (both collection XML files and the upstream `LICENSE`); the built PDF states it.
- **Exercises:** none embedded in either book, counted in the CNXML in both link schemes; no `exercises/` cache, so nothing for the maintainer to fetch. (The high-school `osbooks-physics` does embed exercises; this bundle does not.)
- **Figures:** raster only, 472 MB of media.
- **Result:** both books built as PDF, EPUB and HTML (319 web pages each) on 2026-11-26, in one pass with no converter change.

It is the algebra-based college text, between `osbooks-physics` (high school) and `osbooks-university-physics-bundle` (calculus-based), both of which impo already built.

## Defects found in the output, each with its own task

- **Twelve formulas with a degree sign** come out with literal braces in the PDF and as raw TeX in the HTML and EPUB (72 pandoc warnings): `tasks/archive/impo/2026/11/27/openstax-degree-sign-inside-math-text-is-escaped.md` (fixed 2026-11-27).
- **Eighteen embedded simulation links are missing** (frames pointing at openstax.org). The converter drops such frames in every book that has them: `tasks/openstax-embedded-frame-links-are-dropped.md`.

Neither stopped the build. The converter's report listed only inline fallbacks (`inline:label` 806, `inline:space` 90, `inline:span` 6).

## Not done

The PDFs and HTML were not read page by page; that review is the maintainer's. The book needs his public backup: `bash tools/mirror-upstreams.sh push college-physics-bundle`.

## Recorded

`openstax/osbooks-college-physics-bundle/CLAUDE.md`, the list in `openstax/CLAUDE.md`, the inventory and its licence table, the survey table, and the umbrella's checklist.
