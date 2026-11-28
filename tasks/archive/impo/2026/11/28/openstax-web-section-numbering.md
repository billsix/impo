# Section numbers match OpenStax's: chapter openers and prefaces are unnumbered

**Done 2026-11-28** (agent. Created 2026-11-21 by William Emerison Six <billsix@gmail.com> from a finding of
`tasks/archive/impo/2026/11/21/openstax-cross-book-references.md`; his go-ahead 2026-11-28: "for those three
tasks you mention, make a branch, temporarily turn gpg signing off, do them in the order you'd like").

## What was wrong

In a chapter that opens with an unnumbered module, impo counted that module as section x.1, so every later
section was one higher than OpenStax's: OpenStax's 8.2 appeared as 8.3. The task described it for the web
edition; the PDF contents had the same numbers ("1.1 Introduction"), and the preface printed as "0.1
Preface". The EPUB shows no section numbers and was not affected.

## What changed

- **The converter leaves OpenStax's unnumbered modules unnumbered**
  (`openstax/tooling/tools/cnxml2tex/convert.py`). OpenStax marks a chapter's opening module and a book's
  preface on the module's `<document>` element (`class="introduction"`, `class="preface"`).
  `is_unnumbered_module` reads the class and `module_heading` writes the heading starred, kept in the
  contents and in the running head; `render_section` stars the headings inside such a module. All three
  formats are built from that LaTeX, so they agree. Mechanics: `tasks/reference/tooling/converters.md`,
  "Modules OpenStax does not number".
- **The cross-book page index reads the sitemap's own numbers**
  (`openstax/tooling/tools/cnxml2tex/crossbook_index.py`): its renumbering step and the title test behind it
  are gone; the opener keeps the key `x.0`.
- **Prealgebra 2e chapter 11 was wrong in the index and is corrected.** Its opener is titled "Graphs", which
  the old title test (a first module titled "Introduction…") did not recognise, so the committed index had
  the chapter one too high. Regenerating the ten indexes changed that one file. The eleven entries of
  `crossbook/prerequisites.txt` that cite "PA 11.x" had been written against the wrong numbers and were
  shifted down by one, which keeps every reviewed target the same section (checked by title with
  `crossbook.py --check`: "Elementary Algebra 2e §4.1 Use the Rectangular Coordinate System ← Prealgebra 2e
  §11.1 Use the Rectangular Coordinate System", and the other ten).

## Why the class attribute and not the title

`tasks/adhoc/openstax-web-section-numbering/survey_openers.py` (deleted with the archive commit) compared the
two tests over the 71 collections of the 45 fetched folders. The class attribute selects 1,196 modules, each
the first module of a chapter and none anywhere else. The title test selects 850 and misses 346: 175 openers
with other titles ("Why It Matters" 49, "Why This Chapter?" 31, "Connection for AP® Courses" 32, "Thinking
Ahead" 29, "What Does Psychology Say?" 17, "Chapter Scenario" 15, and two single ones), and 171
Introductions that hold sections of their own. It never selects a module the class does not.

## Verification (2026-11-28)

- `tools/compare-converter-output.sh`: 1,166 of 8,441 generated LaTeX files differ, in all 45 folders; every
  changed line is a sectioning line (a module heading, or a starred heading inside an unnumbered module).
- *Business Ethics*, read after the change: the PDF contents list "Preface" and each "Introduction" without a
  number and the first section of chapter 1 as 1.1; the web sitemap gives the same numbers and the side
  navigation shows "Introduction" and "1.1  Being a Professional of Integrity"; the page file names and ids
  are unchanged (`004-mod:m68350.html`).
- All 45 folders rebuilt as PDF, EPUB and HTML (`tools/build-after-sync.sh`): every step passed.
- The Prealgebra bundle was rebuilt again with the corrected index and map, and the cross-book link check
  (`openstax/tooling/tools/pandoc/check_links.py`) over the ten math sites reports 0 broken links.
- The toolchain gate (`make -C openstax/tooling type-check`) passes.

## Left as it is

- **Appendices.** The modules after a book's last chapter are OpenStax's appendices A, B, C; impo still
  numbers them as sections of the last chapter (199 modules in 48 collections). Its own task:
  `tasks/openstax-appendix-modules-are-numbered-as-sections.md`.
- **Books with units.** Where a collection nests chapters inside units, impo numbers unit.chapter.section;
  OpenStax numbers chapters through the whole book. Not looked at here.
- **A reference to an opener.** An empty link to an unnumbered module prints the chapter's number ("Chapter
  1") in the PDF, since the module has no number of its own.
- The PDFs and HTML were not read page by page; that review is the maintainer's.

## Recorded

`tasks/reference/tooling/cross-book-links.md` ("Facts the work established"),
`tasks/reference/tooling/converters.md` ("Modules OpenStax does not number").
