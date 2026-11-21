# Review the math-ladder prerequisites map, then map physics and the sciences

**Status:** proposed — needs go-ahead (step 1 is the maintainer's review)
**Priority:** 6
**Difficulty:** 6
**Created:** 2026-11-21 (follow-on of `tasks/archive/impo/2026/11/21/openstax-cross-book-references.md`)

## BLUF

The "Prerequisites" boxes are built and the math-ladder map is drafted (303 entries, from section
titles), but the decision was that the maintainer reviews the ladder map before physics and the
sciences are mapped. Done = the ladder map reviewed (entries kept, changed or dropped), then the
same kind of map for the physics books and the sciences, built and link-checked.

## Context

- Mechanism, data format, book codes and findings: `tasks/reference/tooling/cross-book-links.md`.
- The data: `openstax/tooling/tools/cnxml2tex/crossbook/prerequisites.txt`. Print the review list
  (book, section and title on both sides) with
  `python3 openstax/tooling/tools/cnxml2tex/crossbook.py --check`.
- A new target book needs its page index: build it (`make html` in its folder), then
  `python3 tools/cnxml2tex/crossbook_index.py ../osbooks-<folder>/checkout/output/<book>` from
  `openstax/tooling/`, and a book code in `crossbook.py` `BOOKS`.

## Plan

1. **[MAINTAINER]** Read the review list; mark entries to drop or change (edit the file, or list
   them in this task).
2. Physics: `osbooks-physics` (high-school Physics) → `osbooks-university-physics-bundle` (volumes
   1–3, with Calculus 1–3 as math prerequisites). Draft, review, build.
3. Sciences (chemistry, biology, microbiology, anatomy-physiology, organic chemistry): draft per
   chain (e.g. organic chemistry ← chemistry 2e; microbiology and anatomy-physiology ← biology 2e),
   review, build.
4. Rebuild the affected folders (`make <folder>`), stage the sites (`DRY_RUN=1 make publish-pages`)
   and run `python3 openstax/tooling/tools/pandoc/check_links.py output/pages`.
