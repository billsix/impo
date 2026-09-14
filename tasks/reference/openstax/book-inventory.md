# OpenStax book inventory — per-book status, counts, and build history

**Reference doc — living, updated in place as books get built.** The per-book status inventory
(build-verified dates, exercise/image counts, os-embed scheme post-mortems, structural facts) for
the 16 books under `openstax/osbooks-<subject>/`. Moved out of `openstax/CLAUDE.md` (2026-09-13) so
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
  with its `COPYRIGHT` NOTICE (green-lit + fetched 2026-09-02 — see `tasks/openstax-populate-books.md`).
- `osbooks-biology-bundle/` — **committed exercise cache** (2337 JSON + 359 images) with `COPYRIGHT`, across
  all 3 volumes. Like physics, it uses the **`#ost/api/ex/<id>`** scheme (fetched by tag), so it too was wrongly
  read as "0 exercises" before the 2026-09-03 converter fix. (Its `\unicode[…]{x…}` Greek in exercise math also
  drove a converter fix — see `tasks/reference/tooling/converters.md`.)
</content>
</invoke>
