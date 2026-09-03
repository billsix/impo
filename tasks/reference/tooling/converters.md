# The OpenStax converters — shared skeleton, the 5 historical versions, and the unified toolchain

**Reference doc — living, never archived.** What the CNXML→LaTeX (+ HTML/EPUB) converter does, how the 16
per-book source converters differed, and how impo's single shared toolchain relates to each. Read this before
touching `openstax/tooling/`. Companion *fix* task (the work that closed the gaps): [[openstax-converter-unification-gaps]].
Written 2026-09-03 from a full cross-repo diff; reflects the toolchain **after** the two-scheme exercise fix landed.

## Why this exists

The 16 OpenStax `latex`-branch source repos were assumed to share one converter. They did **not**:
`tools/cnxml2tex/convert.py` existed in **5 distinct versions**, with further divergence in `preprocess.py`,
`fetch_exercises.py`, `osbook.cls`, and `osbook-envs.sty`. impo hoisted **one** shared toolchain
(`openstax/tooling/`) — a superset. This doc records the common skeleton, every divergence, and where the shared
version stands, so a future session understands the whole landscape without re-diffing 16 repos or re-reading
2900+ lines. (An earlier survey wrongly claimed the converters were "byte-identical except the slug"; that claim
is corrected here and was the reason for the whole investigation.)

**Source of truth for the originals:** each source repo's `latex` branch at `/foo/opt/openstax/osbooks-<subject>`
(an **upstream-only, read-only** checkout — the `latex` branch is the maintainer's own work; never edit it). Read
with `git -C <repo> cat-file -p latex:<path>`. All `file:line` anchors below point at impo's maintained copy under
`openstax/tooling/` (that's what you edit); line numbers drift — the function names and section titles are the
stable anchors.

## The shared skeleton — `openstax/tooling/tools/cnxml2tex/convert.py` (~2930 lines)

Book-agnostic: `ROOT` is always `/book`; per-book structure is **auto-derived**, so the same converter serves every
book. Major phases (section banners in the file):

| ~line | phase | what it does |
|------|------|------|
| 48 | per-book configuration | auto-derives collection/subcollection nesting; no hardcoded slug |
| 120 | text escaping | LaTeX special-char escaping |
| 352 | MathML → LaTeX | Presentation-MathML → math; includes the obsolete-font map (see gap #4) at ~757 |
| 1191 | continued-equality promotion | `a=b=c` chains → aligned display |
| 1375 | inline content | `inline()` (1378), `inline_element()` (1390) |
| 1484 | labels | module-scoped label state (CNXML reuses `fs-id`s across modules) |
| 1558 | source-line wrapping | wraps prose in the emitted `.tex` for readable diffs |
| 1655 | block content | `block_element()` (2055), `inline_block()` (2204) |
| 1761 | **injected os-embed exercises** | `_os_embed_nickname()` (1778), `render_injected_exercise()` (2013), `render_exercise()` (2367) |
| 2631 | label discovery | which ids are referenced (so only those get `\label`) |
| 2643 | module conversion | `convert_module()` (2653) |
| 2748 | collection assembly | `convert_collection()` (2751) — Phase 2 |
| 2912 | entry | `main()` (2913) |

## The 5 historical `convert.py` versions and their deltas

Verified by hashing `latex:tools/cnxml2tex/convert.py` across all 16 repos. 12 books shared one version; four
diverged. impo's converter (2930 lines) is larger than every original — a merged superset.

| Version | Books | What it added over the majority | In impo now? |
|------|------|------|------|
| **majority** (2856 ln) | the other 12 | — the base | — |
| **physics** (2863) | physics | 2nd os-embed URL scheme `#ost/api/ex/<id>` → query `tag:<id>` | ✅ (fixed 2026-09-03) |
| **organic** (2873) | organic-chemistry | `_pdfsafe(title)` — wrap math-in-headings in `\texorpdfstring` (else hyperref aborts on `$…$` in a PDF bookmark) | ✅ (build-all fix #2) |
| **python** (2906) | introduction-python-programming | `render_code_block` — multi-line `<code>` → a verbatim block env (inline `\texttt` can't hold a paragraph) | ✅ (build-all fix #1, as `oscode`) |
| **biology** (2889) | biology-bundle | `_pdfsafe` **and** the 2nd os-embed scheme (union of organic + physics) | ✅ (both) |

### The two os-embed exercise schemes (the subtle one)

OpenStax practice exercises are referenced in CNXML as `<link class="os-embed" url="…">`, sole content of a
`<para>`. **Two URL schemes exist:**

- `#exercise/<nickname>` — most books; API query `nickname:<nickname>` (e.g. anatomy would use this if it had any).
- `#ost/api/ex/<id>` — **physics and biology only**; API query `tag:<id>` (e.g. `k12phys-ch04-ex017`,
  `apbio-ch01-ex001`). The trailing token is the cache key (`exercises/<key>.json`) either way.

The unified converter originally recognized only the first scheme, so **physics (846 exercises) and biology
silently rendered zero** — the "physics/biology have 0 exercises" reading was the bug hiding itself. Both
`convert.py` (`_os_embed_nickname`, and the inline-link fallback at ~1425) and `fetch_exercises.py`
(`discover_targets` → `nickname:`/`tag:` queries, `fetch_one(key, query)`) now handle both. Unit tests:
`tools/tests/test_helpers.py::test_os_embed_{nickname,tag}_scheme`.

## The other divergent files

| File | versions | who diverged | what it was | impo |
|------|------|------|------|------|
| `tools/pandoc/preprocess.py` | 2 | python | rename `codeblock`→`verbatim` so pandoc (HTML/EPUB) reads the code env | ⚠️ impo uses the majority; the env is now `oscode`, so HTML/EPUB code blocks for python still need an `oscode`→verbatim rename (open, task [[openstax-html-exercise-rendering]] / gap #6) |
| `tools/cnxml2tex/fetch_exercises.py` | 2 | physics, biology | `discover_targets` — both `nickname:` and `tag:` queries | ✅ (fixed 2026-09-03) |
| `latex/osbook.cls` | 3 | organic+biology; calculus | organic/biology: `\DeclareOldFontCommand{\rm…\mathrm}` (+`\bf\it\sf\tt\cal`) — robust obsolete-font fix for chem formulae. calculus: `\setmainfont{TeX Gyre Termes}` (Times) + a **blue** palette | ⚠️ impo uses majority `.cls`; the `{\rm}` case is handled a different way in `convert.py` (~757, `{\rm X}`→`{\mathrm X}` substitution, build-all fix #3) — less general than the `.cls` form; the calculus font+palette is **missing** (calculus builds with the generic Roboto-Slab+teal theme) — open, gap #5 |
| `latex/osbook-envs.sty` | 2 | python | the code env | ✅ impo has `oscode` (new hash; build-all fix #1) |
| `latex/osbook-defer.sty` | 1 | — | identical across all 16 | ✅ (confirmed same) |

## The unification model (the reusable lesson)

Divergences split into two kinds, unified differently:

- **Logic divergences** (exercise schemes, math-in-titles, code blocks) → fold **all** variants into one
  feature-detecting converter. This is how the physics/biology originals already modeled the two schemes
  (`discover_targets` returning both queries). The right answer is a superset, not "pick one."
- **Presentation divergences** (calculus's Times+blue theme) → do **not** belong in a universal converter. The
  clean unification is a **per-book style hook**: `osbook.cls` `\InputIfFileExists{book-style.tex}`, defaulting to
  the shared Roboto-Slab+teal theme, so a book can override only its font+palette. (Proposed in gap #5, not yet
  built.)

## Per-book quick reference

Figure format and os-embed scheme are the durable facts; exercise counts are as of 2026-09-03.

| Book | collections | os-embed scheme | exercises cached | figures |
|------|------|------|------|------|
| anatomy-physiology | 1 | none | 0 | raster |
| astronomy | 1 | none (survey) | 0 | raster |
| algebra-1 | 1 | `#exercise/` | 932 | SVG |
| organic-chemistry | 1 | `#exercise/` | 1959 | raster+exercise imgs |
| contemporary-mathematics | 1 | `#exercise/` | 3073 | mixed |
| introduction-python-programming | 1 | `#exercise/` | 613 | none |
| writing-guide | 1 | `#exercise/` | 182 (0 img) | — |
| **physics** | 1 | **`#ost/api/ex/`** | **846** (fixed 2026-09-03) | raster |
| **biology-bundle** | 3 | **`#ost/api/ex/`** | (re-fetching 2026-09-03) | raster |
| chemistry-bundle | 2 | none/survey | 0 | — |
| calculus-bundle | 3 | none | 0 | — (wants Times+blue theme, gap #5) |
| college-algebra-bundle | 4 | survey | 0 | — |
| prealgebra-bundle | 3 | survey | 0 | — |
| university-physics-bundle | 3 | survey | 0 | — |
| microbiology | 1 | survey | 0 | — |
| psychology | 1 | survey | 0 | — |

("survey" = the scheme wasn't re-audited on the raw CNXML for that book; verify on first exercise-bearing build,
the same way physics/biology turned out to have `#ost/api/ex/`.)

## See also

- [[openstax-converter-unification-gaps]] — the fix task (gap table, plan, status).
- [[openstax-html-exercise-rendering]] — HTML/EPUB presentation of exercises (collapsible answers; the `oscode`
  HTML rename, gap #6, is tracked here).
- `openstax/CLAUDE.md` — the family contract (had the "byte-identical" error this doc corrects).
