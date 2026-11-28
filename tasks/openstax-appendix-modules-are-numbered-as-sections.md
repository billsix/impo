# Letter the appendix modules the way OpenStax does

**Status:** proposed — needs go-ahead
**Priority:** 6
**Difficulty:** 4
**Created:** 2026-11-28 (agent), a finding of
`tasks/archive/impo/2026/11/28/openstax-web-section-numbering.md`.
**Source:** that task's "Left as it is".

## BLUF

The modules a collection lists after its last chapter are OpenStax's appendices, lettered A, B, C on
openstax.org. impo converts each as one more numbered section of the last chapter: in *Business Ethics*
the three appendices print as sections 11.6, 11.7 and 11.8 of the epilogue, in the PDF contents and in
the web edition's side navigation. Done means those modules sit outside the last chapter, lettered or
unnumbered as OpenStax has them, in the PDF, the HTML and the EPUB of every book, and the cross-book link
check still reports no broken link.

## Context

- Read first: `tasks/reference/tooling/converters.md` ("Modules OpenStax does not number": the rule for
  chapter openers and prefaces, and why the label must follow the heading at once) and
  `tasks/reference/tooling/cross-book-links.md` (the page index is built from the web edition's sitemap;
  moving pages needs `crossbook_index.py` re-run).
- Size, counted 2026-11-28 in the collection XML of the 71 fetched collections: 48 collections list
  modules after their last chapter, 199 modules in all (astronomy-2e has 13).
- The marker is not reliable on its own: 145 module files in the fetched repositories carry
  `class="appendix"` on `<document>`, and
  *Business Ethics* marks one of its three appendices that way (`m66996`) and not the other two
  (`m66992`, `m66993`). The position in the collection (a module at the top level, after the last
  `<col:subcollection>`) selects all of them.
- Where the code is: `convert_collection` in `openstax/tooling/tools/cnxml2tex/convert.py` puts a
  top-level module into `main_lines` as a plain `\subfile`, so it continues the last `\chapter`. A module
  file is shared by every collection of a bundle, so a rule keyed on position belongs in the master file
  the collection writes (for instance `\appendix` before the first such module and a chapter-level
  heading per module), not in the module file.

## Plan

1. Compare three books with openstax.org's table of contents (one with lettered appendices, one whose
   trailing modules are an index or references, one bundle), to settle what each kind should print.
2. Emit the appendix part in the master file; check the PDF contents, the web sitemap and the EPUB
   navigation of those three books.
3. Run `tools/compare-converter-output.sh`, rebuild every book, regenerate the cross-book page index
   (appendix pages move) and run the link check.

## Open questions

None yet; step 1 may raise one (whether an index or a references module counts as an appendix).
