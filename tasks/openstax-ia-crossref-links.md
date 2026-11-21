# Hyperlink "(IA x.y.z)" learning-objective cross-references — done, inside the cross-book task

**Closed 2026-11-21:** implemented by `tasks/archive/impo/2026/11/21/openstax-cross-book-references.md`,
which generalized it to every link between books. Mechanism and findings:
`tasks/reference/tooling/cross-book-links.md`.

## Record

- Parked 2026-09-03 because the books had no published URLs; un-parked when
  `tasks/archive/impo/2026/11/21/openstax-publish-books.md` fixed the site layout
  (`https://billsix.github.io/impo/<book>/`).
- The corequisite-support material in `osbooks-college-algebra-bundle` tags learning objectives with
  literal text "(IA x.y.z)" = Intermediate Algebra 2e section x.y, objective z. The 2026-11-21 scan
  found 161 tags (67 distinct) in 47 modules, all in that bundle.
- Implemented as this task's design (b) + (c): a configurable base URL (`SITE_BASE` /
  `OSBOOK_SITE_BASE` in `crossbook.py`), plain text when a section is not indexed. The link goes to the
  section page (objectives have no anchors). It is emitted in the LaTeX, so the PDF and EPUB carry the
  absolute URL and the web edition a relative one (the PDF/EPUB question this task left open).
- **Correction to this task's 2026-09-03 finding:** "(IA 8.2.1) → 058/059 Simplify Expressions with
  Roots" used the web edition's numbering, which counts each chapter's "Introduction" module as x.1 and
  so runs one ahead of OpenStax's numbering that the tags use. IA 8.2 is *Simplify Radical
  Expressions* (the objective "use the product property to simplify radical expressions" is its first);
  the cross-book page index renumbers to OpenStax's numbers.
