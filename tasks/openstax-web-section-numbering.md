# Number the web edition's sections the way OpenStax does

**Status:** proposed — needs go-ahead
**Priority:** 4
**Difficulty:** 4
**Created:** 2026-11-21 (William Emerison Six <billsix@gmail.com>), from a finding of
`tasks/archive/impo/2026/11/21/openstax-cross-book-references.md`.

## BLUF

In every chapter that opens with an "Introduction" module, the HTML web edition numbers the sections one
higher than OpenStax does: the pandoc sitemap counts the Introduction as x.1, OpenStax leaves it
unnumbered, so OpenStax's 8.2 appears as 8.3. A reader comparing with the printed book, or following a
"(IA 8.2.1)" reference by number, lands on the wrong section. Done = the web edition's section numbers
match OpenStax's (the opener unnumbered or x.0) in every book, and the PDF/EPUB agree.

## Context

- Read first: `tasks/reference/tooling/cross-book-links.md` ("Facts the work established": the
  off-by-one, and the rule the cross-book index already uses — a chapter's first module whose title
  starts with "Introduction" and has no subsections is the unnumbered opener).
- The cross-book page index (`openstax/tooling/tools/cnxml2tex/crossbook_index.py`) already renumbers
  this way, so links are right; only the numbers shown to readers are off.
- The HTML leg: `openstax/tooling/entrypoint/html.sh` (pandoc chunked output, its sitemap and nav). Check
  whether the PDF (LaTeX `\section` numbering) and EPUB have the same off-by-one before choosing where to
  fix it (the converter, so all three formats agree, or the HTML leg only).
- After the fix, the committed `crossbook/index/*.json` may no longer need its renumbering step; keep the
  two consistent.

## Plan

1. Measure: for one book (e.g. `osbooks-prealgebra-bundle`), compare the section numbers in the HTML nav,
   the PDF and the EPUB against OpenStax's own (openstax.org table of contents).
2. Fix at the right layer; rebuild the math-ladder books; rerun the cross-book link check (0 broken).
3. Update `tasks/reference/tooling/cross-book-links.md`.
