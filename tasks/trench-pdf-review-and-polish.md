# Trench Elementary Differential Equations — PDF maintainer review + minor polish

**Status:** open — needs maintainer visual review + optional minor polish. Split out of
`tasks/archive/impo/2026/09/19/add-trench-differential-equations-book.md` (2026-09-19) so that task (the build — phases 1–5, DONE)
could be archived; these are the non-blocking follow-ups.
**Priority:** 6 (polish; the PDF already builds clean and is usable)
**Difficulty:** 2

## BLUF

The Trench *Elementary Differential Equations* PDF builds clean (673 pp, Overfull \hbox 578→97 with the
>50 pt "real" ones 59→1, Overfull \vbox 0) via `make pdf`. What remains is **a maintainer visual
review** (eyes on the rendered PDF) plus a few **cosmetic polish** items, none of which block the build.
"Done" = the maintainer has skimmed the PDF and either accepted it or filed specific fixes, and the
polish items below are done or explicitly declined.

## Maintainer visual review (the main item)

Skim the built PDF (`trench/elementary-differential-equations/checkout/output/TRENCH_DIFFEQ-osbook.pdf`)
for anything that looks wrong that the automated checks can't catch: figure placement/sizing, equation
breaks, the title/license/colophon front matter, chapter/section headings, the answer key. File specific
fixes if any surface; otherwise accept.

## Minor polish (cosmetic; none block the build)

- **Preface pagination.** The Preface renders in `\mainmatter` (arabic page numbers) rather than
  front-matter roman, because `\OSfrontmatter` ends with `\mainmatter` and chapter 1 resets to page 1. A
  cosmetic pagination nicety; would need osbook.cls front/main-matter sequencing (osbook-wide, not
  trench-specific).
- **License-page wording.** "Typeset … in the OpenStax house style" is deliberate but could be softened
  for a non-OpenStax book. (Partly addressed already by the "About This Edition" colophon, which states
  the impo/Bill Six provenance + CC BY-NC-SA 3.0 explicitly.)
- **Empty PDF metadata title.** osbook.cls doesn't set `pdftitle`, so the PDF's document-properties title
  is blank — an osbook-wide nicety (add `\hypersetup{pdftitle=…}` from the `\setOSbooktitle` value), not
  trench-specific.
- **4 source "dangler" cross-references.** A few references in the source point at the boundary-value
  edition; resolving them needs a content decision (e.g. cross-link the BV edition once it exists —
  `add-trench-bv-and-student-manual.md`).
- **`definition` numbering (deferred sub-decision).** Trench shares one counter across
  theorem/definition; osbook may number them independently. Recommendation: match Trench (shared counter)
  to keep the book's internal references stable; revisit only if it looks wrong in the review above.

## Related

- `tasks/archive/impo/2026/09/19/add-trench-differential-equations-book.md` — the build task this was split from (phases 1–5, DONE).
- `add-trench-bv-and-student-manual.md` — the BV variant + student manual (gated follow-on; the dangler
  cross-refs relate to it).
- `tasks/archive/impo/2026/09/19/trench-differential-equations-html-epub.md` — the web editions (done); the license/colophon wording is
  shared with the PDF.
