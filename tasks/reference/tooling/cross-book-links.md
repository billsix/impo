# Links between books — "(IA x.y.z)" references and "Prerequisites" boxes

**Reference doc — living.** How the converter links one book to another, where the data lives,
and what the 2026-11-21 scan of the books found. Built in
`tasks/archive/impo/2026/11/21/openstax-cross-book-references.md` (which absorbed
`tasks/archive/impo/2026/11/21/openstax-ia-crossref-links.md`). Within-book references are a
different mechanism: `tasks/reference/tooling/cross-references.md`.

## The mechanism (`openstax/tooling/tools/cnxml2tex/crossbook.py`)

- **Emitted in the LaTeX**, by `convert.py`'s `convert_module`, so all three editions get them:
  1. `link_ia_references` turns the literal text `(IA 8.2.1)` (Intermediate Algebra 2e section 8.2,
     objective 1) into `(\href{<url of IA 8.2>}{IA 8.2.1})`; a section not in the index stays text.
  2. `prerequisites_box(module)` opens a section with a `prerequisites` box (osbook-envs.sty; titled
     by xref.lua; styled with the other titled boxes in osbook-web.css) of
     "Review: <book> §x.y <title>" links. The OpenStax prose is not changed.
- **Every link is absolute** on the published site, `SITE_BASE` =
  `https://billsix.github.io/impo/` (`OSBOOK_SITE_BASE` overrides): the PDF and EPUB keep it (there
  is no shared PDF to `\ref` into, and inter-EPUB links are unreliable), and `entrypoint/html.sh`
  rewrites `href="<SITE_BASE>` to `href="../` in the web edition, so on the site the links are
  relative and resolve between books (`tasks/reference/openstax/publishing.md`). In a downloaded
  `<book>-html.zip` they point at sibling directories that are not in the zip.
- **Page index, committed:** `crossbook/index/<book>.json` maps each **official** section number
  to `{module, page, title}`. A book folder's build container mounts only its own checkout, so the
  target book's `sitemap.json` is not available at convert time; the index is generated once from
  the built sites (`python3 tools/cnxml2tex/crossbook_index.py ../osbooks-*/checkout/output/<book>`
  from `openstax/tooling/`) and committed, which removes the build-order dependency between book
  folders. Re-run it after a pin bump or a converter change that renumbers pages, then check with
  `python3 openstax/tooling/tools/pandoc/check_links.py <dir with the built sites>`.
- **The prerequisites map, reviewed data:** `crossbook/prerequisites.txt`, one line per source
  section: `SRC x.y  TGT a.b [TGT c.d ...]` with book codes PA (Prealgebra 2e), EA (Elementary
  Algebra 2e), IA (Intermediate Algebra 2e), CA (College Algebra 2e), PC (Precalculus 2e), C1–C3
  (Calculus Volumes 1–3). `python3 openstax/tooling/tools/cnxml2tex/crossbook.py --check` validates
  every entry and prints the review list with titles on both sides.

## Facts the work established

- **The books' section numbers are OpenStax's** (since 2026-11-28). OpenStax does not number a chapter's
  opening module or a book's preface, and marks them on the module's `<document>` element
  (`class="introduction"`, `class="preface"`). The converter stars their headings
  (`is_unnumbered_module`, `module_heading` in `convert.py`), so the PDF contents and the web edition's
  sitemap number the sections that follow from x.1, and the page index reads the sitemap's numbers as they
  are, keeping the opener under `x.0`. The IA tags use OpenStax's numbers: "(IA 8.2.1) Use the product
  property to simplify radical expressions" is section 8.2 *Simplify Radical Expressions*. Until that date
  the opener was counted as x.1, every later section was one higher than OpenStax's, and the index
  renumbered by a title test (a first module titled "Introduction…" with no subsections). That test missed
  346 of the 1,196 openers in the 71 collections fetched on 2026-11-28 (titles such as "Why It Matters" and
  "Thinking Ahead", and Introductions that hold sections); the class attribute marks only a chapter's first
  module, in every one of them. Record: `tasks/archive/impo/2026/11/28/openstax-web-section-numbering.md`.
- **Modules are shared between books**: College Algebra 2e shares 32 modules with Precalculus 2e (and
  with the corequisite and Algebra & Trigonometry editions), Calculus Volume 2 shares 21 with Volume 1
  (its chapters 1–2 are Volume 1's chapters 5–6) and Volume 3 shares 9 with Volume 2. A box belongs
  to a module, so it lists the union of what any book section built from that module declares, once,
  never the module itself.
- **Appendices fold into the last chapter** in the web edition's numbering (Calculus Volume 1 "6.10
  Table of Integrals", Prealgebra "11.6 Cumulative Review"); harmless, but they carry numbers there.
- **Explicit references in the CNXML (scan of all 16 folders, 2026-11-21):** 161 `(IA x.y.z)` tags,
  all in `osbooks-college-algebra-bundle`: 81 distinct (module, tag) pairs in 47 modules, 67 distinct
  tags, every one resolving to an indexed IA section; 17 "Calculus Volume N" mentions, all in each calculus volume's own preface (self-
  references, not linked); no other book named another. The scan was a `grep -rEo` over every checkout's `modules/*/index.cnxml` for these patterns
  (one-shot script, removed with the task's archive).
- **The draft map (303 entries, 294 modules)** covers the math ladder: Elementary Algebra ←
  Prealgebra, Intermediate ← Elementary, College Algebra ← Intermediate, Calculus 1 ← College
  Algebra and Precalculus (trigonometry, limits), Calculus 2 ← 1, Calculus 3 ← 1–2. It was drafted
  from section titles and awaits the maintainer's review; physics and the sciences are not mapped.
