# OpenStax book inventory — per-book status, counts, and build history

**Reference doc — living, updated in place as books get built.** The per-book status inventory
(build-verified dates, exercise/image counts, os-embed scheme post-mortems, structural facts) for
the books under `openstax/osbooks-<subject>/` (the original sixteen, and those added since 2026-11-26). Moved out of `openstax/CLAUDE.md` (2026-09-13) so
the family contract stays lean; this is the durable detail behind the lean book list there. Each
book also has its own `osbooks-<subject>/CLAUDE.md` with its pin and book-specific facts. The
converter-side per-book quick reference (figure format, os-embed scheme, exercise counts) lives in
`tasks/reference/tooling/converters.md`.

## Books

- `osbooks-anatomy-physiology/` — OpenStax **Anatomy & Physiology 2e**. Single-collection, two
  subcollection levels, **no** `os-embed` exercises, raster figures (no SVG step). The **pilot** for
  this family's shared-toolchain contract. Details: `osbooks-anatomy-physiology/CLAUDE.md`.

The other 15 books were scaffolded on the pilot pattern (2026-09-02); each carries the thin
per-book folder and a `CLAUDE.md` with its pin. Build-verified so far: **astronomy**,
**algebra-1**, **introduction-python-programming** (image + `make convert` generate the LaTeX
master; python-programming's 613-exercise download cache is fetched, committed, and injection-
verified). The rest are structure-verified only (`bash -n`, and the generic pattern is proven).
Per-book structural facts (collection layout, nesting, real exercise/figure presence) are
confirmed on each book's first build.

- `osbooks-astronomy/` — Astronomy 2e (single-collection; convert → `astronomy-2e.tex`, 199 modules).
- `osbooks-chemistry-bundle/`, `osbooks-microbiology/`, `osbooks-psychology/`,
  `osbooks-university-physics-bundle/` — the other toolchain-only (no-download) books.
- `osbooks-college-algebra-bundle/`, `osbooks-prealgebra-bundle/`, `osbooks-calculus-bundle/` —
  small download caches (survey).
- `osbooks-writing-guide/` — **committed exercise cache** (182 JSON, 0 images) with `COPYRIGHT`.
- `osbooks-physics/` — **committed exercise cache** (846 JSON + 31 images) with `COPYRIGHT`. Uses the
  **`#ost/api/ex/<id>`** os-embed scheme (fetched by tag), not `#exercise/` — it was wrongly read as
  "0 exercises" until the converter learned that scheme (2026-09-03; see the archived converter-gaps task).
  `osbooks-college-algebra-bundle/`, `osbooks-prealgebra-bundle/`, `osbooks-calculus-bundle/` are genuine
  0-os-embed (confirmed in both schemes) → no caches.
- `osbooks-introduction-python-programming/` — **has committed exercises cache** (613 questions,
  no images; convert → `introduction-python-programming.tex`, 115 modules).
- `osbooks-algebra-1/` — **committed exercise cache** (932 JSON + 288 images) with `COPYRIGHT`, plus
  SVG figures (convert → `algebra-1.tex`, 976 modules).
- `osbooks-organic-chemistry/`, `osbooks-contemporary-mathematics/` — **committed exercise caches**
  (organic-chemistry 1959 JSON + 2076 images; contemporary-mathematics 3073 JSON + 578 images), each
  with its `COPYRIGHT` NOTICE (green-lit + fetched 2026-09-02 — see `tasks/archive/impo/2026/09/03/openstax-populate-books.md`).
- `osbooks-biology-bundle/` — **committed exercise cache** (2337 JSON + 359 images) with `COPYRIGHT`, across
  all 3 volumes. Like physics, it uses the **`#ost/api/ex/<id>`** scheme (fetched by tag), so it too was wrongly
  read as "0 exercises" before the 2026-09-03 converter fix. (Its `\unicode[…]{x…}` Greek in exercise math also
  drove a converter fix — see `tasks/reference/tooling/converters.md`.) The three books are `biology-2e`,
  `biology-ap-courses-2e` (renamed upstream from `biology-ap-courses` at the 2026-11 pin) and
  `concepts-biology`; only the AP book embeds exercises: 2350 referenced, 13 not in the cache (four in
  `apbio-ch06`, nine in `apbio-ch10`), unchanged by the rename. Detail: `openstax/osbooks-biology-bundle/CLAUDE.md`.
- `osbooks-prealgebra-bundle/` — four books since the 2026-11 pin: `prealgebra-2e`, `elementary-algebra-2e`,
  `intermediate-algebra-2e` and the new `healthcare-foundations` (30 modules), all built 2026-11-26.
- `osbooks-statistics/` — *Statistics*, added 2026-11-26 with `tools/add-book.sh` (the first book added
  after the original sixteen): 101 modules, 13 chapters, no embedded exercises, raster figures; 1,042-page
  PDF. It needed two converter fixes (an empty table `cols` attribute; Content MathML).
- `osbooks-introductory-statistics-bundle/` — two books added 2026-11-26: *Introductory Statistics 2e*
  (102 modules) and *Introductory Business Statistics 2e* (77 modules); no embedded exercises, raster figures.
- `osbooks-college-physics-bundle/` — two books added 2026-11-26: *College Physics 2e* and *College Physics
  for AP® Courses 2e*, 283 modules each (248 shared); no embedded exercises, raster figures.
- `osbooks-business-law/` — *Business Law I Essentials 2e* (47 modules, 181-page PDF), added 2026-11-27: no embedded exercises; raster figures; built in one pass with no toolchain change.
- `osbooks-additive-manufacturing/` — *Additive Manufacturing Essentials* (42 modules, 246-page PDF), added 2026-11-27: 120 embedded exercises, all cached 2026-11-27; raster figures; built in one pass with no toolchain change.
- `osbooks-life-liberty-and-pursuit-happiness/` — *Life, Liberty, and the Pursuit of Happiness* (532 modules, 2,484-page PDF), added 2026-11-27: 1,896 embedded exercises, not fetched yet (`tasks/openstax-add-book-life-liberty-and-pursuit-happiness.md`); raster figures; CC BY 4.0; built in one pass with no toolchain change.
- `osbooks-us-history/` — *U.S. History* (177 modules, 1,308-page PDF), added 2026-11-27: no embedded exercises; raster figures; it brought block quotations to the converter (97 of them).
- `osbooks-american-government/` — *American Government 4e* (100 modules, 918-page PDF), added 2026-11-27: no embedded exercises; raster figures; it brought reference notes to the converter (1,342, now footnotes).
- `osbooks-foundations-information-systems/` — *Foundations of Information Systems* (59 modules, 615-page PDF), added 2026-11-27: 410 embedded exercises, all cached 2026-11-27; raster figures; it brought a footnote in a note's title to the converter.
- `osbooks-neuroscience/` — *Introduction to Behavioral Neuroscience* (106 modules, 1-page PDF), added 2026-11-27: 568 embedded exercises, all cached 2026-11-27; raster figures; one figure's file name holds an en dash, which needed a UTF-8 locale in the HTML and EPUB scripts.
- `osbooks-introduction-political-science/` — *Introduction to Political Science* (107 modules, 763-page PDF), added 2026-11-27: 308 embedded exercises, all cached 2026-11-27; raster figures; 1,522 reference notes, now footnotes; 115 embedded video frames, dropped as in every book.
- `osbooks-introduction-intellectual-property/` — *Introduction to Intellectual Property* (54 modules, 232-page PDF), added 2026-11-27: 185 embedded exercises, all cached 2026-11-27; raster figures; CC BY 4.0; 31 block quotations.
- `osbooks-world-history/` — *World History Volume 1, to 1500* (85 modules, 928-page PDF); *World History Volume 2, from 1400* (80 modules, 872-page PDF), added 2026-11-27: 1,158 embedded exercises, all cached 2026-11-27; raster figures; 131 block quotations.
- `osbooks-principles-data-science/` — *Principles of Data Science* (59 modules, 600-page PDF), added 2026-11-27: 136 embedded exercises, all cached 2026-11-27; raster figures; it brought one-line code blocks wrapped in line breaks to the converter.

## Licences (read from each book's own source, 2026-11-26)

The licence of a book is what its source declares: the `<md:license url="…">` of each collection XML, and
the upstream repository's `LICENSE` file. Re-read both at every sync; the converter fails on a collection
whose licence it does not know.

| Book folder | Declared licence | Upstream `LICENSE` file in the checkout |
|---|---|---|
| osbooks-algebra-1 | CC BY-NC-SA 4.0 | none (files copied in without git) |
| osbooks-anatomy-physiology | CC BY-NC-SA 4.0 | yes |
| osbooks-astronomy | CC BY-NC-SA 4.0 | yes |
| osbooks-biology-bundle (3 books) | CC BY-NC-SA 4.0 | yes |
| osbooks-calculus-bundle (3 books) | CC BY-NC-SA 4.0 | yes |
| osbooks-chemistry-bundle (2 books) | CC BY-NC-SA 4.0 | yes |
| osbooks-college-algebra-bundle (4 books) | CC BY-NC-SA 4.0 | yes |
| osbooks-contemporary-mathematics | CC BY-NC-SA 4.0 | none |
| osbooks-introduction-python-programming | CC BY-NC-SA 4.0 | none |
| osbooks-microbiology | CC BY-NC-SA 4.0 | yes |
| osbooks-organic-chemistry | CC BY-NC-SA 4.0 | yes |
| **osbooks-physics** | **CC BY 4.0** | yes |
| osbooks-prealgebra-bundle (4 books) | CC BY-NC-SA 4.0 | yes |
| osbooks-psychology | CC BY-NC-SA 4.0 | yes |
| osbooks-statistics | CC BY 4.0 | yes |
| osbooks-introductory-statistics-bundle (2 books) | CC BY-NC-SA 4.0 | yes |
| osbooks-college-physics-bundle (2 books) | CC BY-NC-SA 4.0 | yes |
| osbooks-university-physics-bundle (3 books) | CC BY-NC-SA 4.0 | yes |
| osbooks-writing-guide | CC BY-NC-SA 4.0 | none |
| osbooks-business-law | CC BY-NC-SA 4.0 | yes |
| osbooks-additive-manufacturing | CC BY-NC-SA 4.0 | yes |
| osbooks-life-liberty-and-pursuit-happiness | CC BY 4.0 | yes |
| osbooks-us-history | CC BY-NC-SA 4.0 | yes |
| osbooks-american-government | CC BY-NC-SA 4.0 | yes |
| osbooks-foundations-information-systems | CC BY-NC-SA 4.0 | yes |
| osbooks-neuroscience | CC BY-NC-SA 4.0 | yes |
| osbooks-introduction-political-science | CC BY-NC-SA 4.0 | yes |
| osbooks-introduction-intellectual-property | CC BY 4.0 | yes |
| osbooks-world-history (2 books) | CC BY-NC-SA 4.0 | yes |
| osbooks-principles-data-science | CC BY-NC-SA 4.0 | yes |

Every collection inside a bundle declares the same licence as its siblings. No module file carries licence
metadata. The exercise caches are a separate case: see "Copyright / licensing" in `openstax/CLAUDE.md`.
