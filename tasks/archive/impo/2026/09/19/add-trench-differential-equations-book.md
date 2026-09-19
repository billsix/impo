# Add the Trench "Elementary Differential Equations" book to impo, in OpenStax house style

**Status:** COMPLETE 2026-09-19 — phases 1–5 done; builds to a clean **673-page** osbook-styled PDF via
`make pdf` (wider per-book measure; Overfull \hbox 578→97, big ones 59→1). The remaining non-blocking
maintainer visual review + minor polish are spun out to `trench-pdf-review-and-polish.md` so this build
task can close.
**Priority:** 4
**Difficulty:** 8 (large, multi-phase: LaTeX restyle of a 1.6MB custom-class book + build wiring)
Created 2026-09-19 (William Emerison Six <billsix@gmail.com>).
**Book folder:** `trench/elementary-differential-equations/` (new sibling family `trench/`).

> **Decisions (William Emerison Six <billsix@gmail.com>, 2026-09-19):**
> 1. **Location/name:** new **sibling family folder `trench/`** (the author's name), holding the book at
>    `trench/elementary-differential-equations/`. Not under `openstax/`.
> 2. **Tooling (maintainer deferred to my recommendation):** **reuse the OpenStax toolchain in place** —
>    `trench/`'s book builds the shared image from `../../openstax/tooling` and its `apply.sh` overlays
>    the osbook LaTeX layer (`osbook.cls`+`osbook-envs`+`osbook-defer`) plus the trench shim. **No
>    refactor of the 16 existing books.** The cleaner "promote a shared `tooling/` to the repo root" is
>    deferred as a future cleanup (revisit if/when a third family appears) — not worth touching 16
>    working books to add one.
> 3. **Scope:** **main book (`TRENCH_DIFFEQ.tex`) → PDF only** in this task. Follow-ons below.
> 4. **Fidelity:** **full osbook restyle — aesthetics only.** The mathematical content, prose,
>    equations, examples, and exercises stay **identical**; only their *presentation* (fonts, colors,
>    chapter/section/theorem/exercise styling, TOC) changes. One honest caveat: swapping the faked
>    sectioning and bespoke exercise system for osbook's real ones may change how numbering is
>    *rendered/labeled* — not the content, but its label form (e.g. how "Theorem 2.3.4" is styled).
> 5. **HTML/EPUB:** PDF-only first cut; deferred to a separate gated task.
>
> **Follow-on tasks (created 2026-09-19, sequenced after this one via `Depends on`, not `blocked` —
> internal sequence, within our control, per the task-doc convention):**
> - `add-trench-bv-and-student-manual.md` — the boundary-value variant + student solutions manual;
>   depends on this task.
> - `trench-differential-equations-html-epub.md` — HTML + EPUB via the reused pandoc legs; depends on
>   this task's PDF.

## BLUF

Bring William F. Trench's open-source *Elementary Differential Equations* (LaTeX source at
https://github.com/billsix/differentialEquationsTrench, pinned) into impo so it builds and reads in
the **same house style as the OpenStax books** (the `osbook.cls` look), using the same
fetch/apply/Makefile/Dockerfile per-book pattern. The source is **not** CNXML, so this is **not** a
CNXML-style re-emit converter: the realistic approach (both codebases analyzed 2026-09-19) is to
**fetch the pristine Trench `.tex`, then overlay a LaTeX compatibility shim** that swaps its custom
`book`+`wtrench.sty` styling for `osbook.cls` + `osbook-envs`/`osbook-defer`, plus a build that
converts its 206 EPS figures to PDF and drops the dvips pipeline. "Done" (phase 1) = the main book
compiles under the OpenStax toolchain to a PDF whose chapters/theorems/examples/exercises/figures
render in osbook style with cross-references intact. Several architecture decisions gate the work —
see Open questions; nothing is built until those are answered and a go-ahead is given.

## Context — the two codebases (analyzed 2026-09-19)

### Target: impo's OpenStax build (what "house style" is, and what a book must provide)

The uniform look is produced by **two layers** (`openstax/CLAUDE.md`, `openstax/tooling/`):
- **The LaTeX house style** — `openstax/tooling/latex/osbook.cls` (memoir + lualatex/fontspec, teal
  palette, golden-ratio geometry, colored chapter titles; metadata setters
  `\setOSbooktitle/\setOSbooksubtitle` and `\OSfrontmatter` for half-title/title/**CC-license
  page**/TOC at `osbook.cls:212-264`; per-book theme hook `\InputIfFileExists{osbook-bookstyle.tex}`
  at `:57`), plus `osbook-envs.sty` (pedagogical envs: `theorem/corollary/lemma/definition/example`,
  titled boxes, callouts, `calcfig`) and `osbook-defer.sty` (per-chapter `exercise` numbering,
  inline `solution`, deferred back-of-book answer key via `\printanswerkey`).
- **The structural skeleton** — the converter's `build_master()`
  (`tooling/tools/cnxml2tex/convert.py:2899-2932`) emits the master every book needs:
  `\documentclass[letter]{osbook}` + `\usepackage{osbook-envs}\usepackage{osbook-defer}` +
  `\setOSbooktitle{…}` + `\setOSbooksubtitle{Formatted by Bill Six}` + `\OSfrontmatter` + body in
  osbook environments + `\printanswerkey` + `\end{document}`.

Per-book folder contract (`openstax/CLAUDE.md:59-116`; template = `osbooks-physics/`,
`osbooks-anatomy-physiology/`): `fetch.sh` (`PIN_SHA=` + `UPSTREAM_URL=`, git clone at pin —
**source-agnostic**), `apply.sh` (overlay `../tooling/` onto gitignored `checkout/`), thin `Makefile`
(`image`/`convert`/`pdf`/`html`/`epub`/`dist`; `PODMAN_RUN_FLAGS` on `run` only), `CLAUDE.md`,
`README.md`, `.gitignore` (`checkout/`, `output/`, `*.tar`). Content model: fetched content →
gitignored `checkout/`; generated `.tex`/rasterized figures → gitignored.

**Reuse vs replace for a non-CNXML book** (agent-verified):
- **Reuse as-is:** the whole LaTeX house-style layer (`osbook.cls` + the two `.sty`), the `Dockerfile`
  TeX Live/pandoc/rsvg/fonts base, `fetch.sh`, the `Makefile` image/mount scaffolding, `.gitignore`,
  and — importantly — the **entire pandoc HTML/EPUB pipeline**, because pandoc reads the *generated
  LaTeX* (`pandoc -f latex`), so HTML+EPUB come nearly free once a valid osbook `.tex` exists.
- **Replace/adapt (the four CNXML-coupled seams):** `convert.py`+`convert.sh`; the Makefile
  `CNXML_SOURCES`/`.converted` stamp; the Dockerfile's `python3-lxml` + `ty`/`pytest` converter gate
  (`Dockerfile:84-88`); and the **master-discovery via `collections/*.collection.xml`** in
  `pdf.sh:42` / `html.sh:41` / `epub.sh:49` (must instead find the Trench master `.tex`).

### Source: Trench *Elementary Differential Equations* (billsix/differentialEquationsTrench)

Pin **`a7c17e34ee0326ff97824d166a1dc91547f8f2e7`** (HEAD as of 2026-09-19). 212 files: 3 standalone
`.tex` (`TRENCH_DIFFEQ.tex` 1.6MB main; `TRENCH_DIFFEQ_BV.tex` boundary-value variant;
`TRENCH_DIFFEQ_STUDENT_MANUAL.tex`), `wtrench.sty` (132 lines), 206 `.eps` + 2 `.m` in `EPS/`. **No
build tooling, no LICENSE file.** License is inline: **CC BY-NC-SA 3.0**, AIM Open Textbook
Initiative, "Free Edition 1.01 (December 2013)", "no charges for profit beyond printing costs"
(`TRENCH_DIFFEQ.tex:130-142,157-173`).

Why it's far from a drop-in (this is the heart of the task):
- **`\documentclass[dvips]{book}`** + EPS figures ⇒ classic latex→dvips pipeline; osbook is
  lualatex/fontspec. Needs EPS→PDF (206 files, hard-coded bounding boxes) and dvips options dropped.
- **Sectioning is FAKED** — the book essentially never uses `\chapter`/`\section`. It calls custom
  `\chaptertitle{n}{title}` (10×) and `\newsection`/`\sectiontitle` (55/54×) that set counters by
  hand (`wtrench.sty:27-79`), and the **TOC is hand-typed** (no `\tableofcontents`). So osbook's
  chapter/section styling and auto-TOC have nothing to bind to until this is redefined.
- **Bespoke look + envs in `wtrench.sty`:** `theorem`/`example` via `\newtheorem`, `definition`
  sharing the theorem counter (`:114-117`), an exercise/answer system (`exerciselist`, `\exer`,
  **1424 `\answer`** page-refs, `\Cex/\CGex/\Lex` tech badges), list envs `alist/Alist/rmlist`,
  hand-drawn QED boxes, colored `\sectiontitle`, and `\renewcommand{\part}` (`:42`, collides with
  book/memoir `\part`). Geometry is double-set (wtrench 5in vs main file `geometry[a4paper]`).
- amsmath/amsbsy/amsfonts, **no amsthm**, no tikz/pstricks, no fontspec, no bibliography, no real
  `\index` use. Heavy `eqnarray`/`array` (dated but portable).

## Approach (decided by analysis; confirm as open question 4)

**Shim/patch the pristine `.tex`, do NOT re-emit content through a converter.** A full re-emit would
have to reverse-engineer the faked sectioning, the shared theorem/definition counter, the 1424-ref
answer web, and 155 bounding-box'd figures — high risk of silently breaking numbering/cross-refs.
Instead the maintainer's delta is a **LaTeX compatibility layer** overlaid at apply-time:

1. A shim style/preamble (call it `trench-osbook.sty`) that, loaded after `osbook.cls`, **redefines
   Trench's macros to osbook equivalents** — mapping table below.
2. A small **preprocessing patch** to the fetched master (the parts a `.sty` can't fix): change
   `\documentclass[dvips]{book}` → `\documentclass[letter]{osbook}`, remove `\usepackage{wtrench}`
   (replaced by the shim) and the dvips/geometry/`\renewcommand{\part}` lines, inject
   `\usepackage{osbook-envs}\usepackage{osbook-defer}` + `\setOSbooktitle{Elementary Differential
   Equations}\setOSbooksubtitle{Formatted by Bill Six}` and `\OSfrontmatter`/`\printanswerkey`
   scaffolding, and neutralize the hand-typed title/TOC. Carry this as a committed patch or a
   deterministic `sed`/python transform in the book's `apply`/`convert` step (this is the "converter"
   the request asked for — a LaTeX→LaTeX normalizer, not CNXML→LaTeX).
3. Build changes: EPS→PDF (epstopdf over `EPS/*.eps`) before lualatex; master-discovery pointed at
   the Trench master instead of `collections/*.collection.xml`.

### Macro-mapping surface (the shim's core — from `wtrench.sty` → osbook)

| Trench (`wtrench.sty`) | osbook target | Note |
| --- | --- | --- |
| `\chaptertitle{n}{t}` (`:77`) | real `\chapter{t}` | recovers osbook chapter style + TOC entry |
| `\newsection`+`\sectiontitle` (`:27,74`) | real `\section{t}` | drop manual counter resets; let osbook number |
| `theorem`,`example` (`:10-11`) | `osbook-envs` `theorem`/`example` | keep names; decide numbering scheme |
| `definition` (`:114`, shares thm counter) | `osbook-envs` `definition` | decide: keep shared counter or independent |
| `exerciselist`/`\exer`/`\answer` | `osbook-defer` `exercise`/`solution`/`answer`+`\printanswerkey` | preserve the 1424 label/pageref web — highest-risk item |
| `alist`/`Alist`/`rmlist` | enumerate variants (enumitem) | sub-part lists |
| `\proof`/`\bbox`/`\solution` | amsthm-style proof / osbook | QED boxes restyled |
| `\Cex/\CGex/\Lex` tech badges | keep, restyle to osbook accent | 407 uses |
| `\renewcommand{\part}` (`:42`) | **delete** | collides with memoir/osbook |
| wtrench geometry (`:1-8`) | **delete** | osbook owns geometry |
| `tindex` | osbook/memoir index or drop | 1 use |
| color/math shorthands (`\R \E \dst \boxit …`) | keep in shim | harmless helpers |

## Phased plan

- **Phase 0 — decisions.** DONE 2026-09-19 (see the Decisions block above): family `trench/`, reuse
  OpenStax tooling in place, main book → PDF only, full aesthetics-only restyle.
- **Phase 1 — scaffold the book folder** at `trench/elementary-differential-equations/`. **DONE
  2026-09-19.** Created: `fetch.sh` (pin `a7c17e3…`), `apply.sh` (overlays `osbook.cls`+envs+defer
  from `../../openstax/tooling/latex/`; the phase-2 shim is copied when present), `Makefile` (image
  from `../../openstax/tooling`; `figures`/`pdf` are honest phase-3/5 stubs that `@false`; no CNXML
  seams), `CLAUDE.md`/`README.md`/`.gitignore`/`latex/.keep`, the family `trench/CLAUDE.md`, and the
  root `CLAUDE.md` two-family index. **Smoke-tested:** `make help` parses; `./fetch.sh` clones the
  pinned source (HEAD matches `a7c17e3…`; 3 `.tex` + `wtrench.sty` + `EPS/`); `./apply.sh` drops the
  osbook class into `checkout/`. (No Dockerfile — reuses `../../openstax/tooling/Dockerfile`; its
  baked CNXML converter is unused by trench but harmless.)
- **Phase 2 — the shim + preprocessing patch.** **DONE 2026-09-19.** Created
  `latex/trench-osbook.sty` (keeps Trench's helper macros; remaps `\chaptertitle`→`\chapter`,
  `\newsection`→`\section`, gobbles `\sectiontitle`; overrides the `\proof`/`\solution`/`definition`
  clashes; drops geometry/fonts/`\numberwithin`) and `tools/normalize_master.py` (swaps the
  book/dvips preamble for an osbook preamble loading `osbook-envs`+the shim+metadata, drops the manual
  `\setcounter{chapter}` lines; writes a sibling `-osbook.tex`, never mutating the source). Wired as
  `make normalize`. **Validated:** a representative test doc compiles cleanly under lualatex (exit 0,
  PDF, no errors) and renders in osbook style — `CHAPTER 1`, auto-numbered `1.1` sections, boxed
  `Theorem 1.1`/`Example 1.2`/`Definition 1.3`, run-in `Proof.`/`Solution.`/`Remark.`, matrices,
  inline `\part`, exercise lists. **Note (aesthetics-only consequence):** theorem/example/definition
  now share one **chapter-based** counter (osbook's uniform scheme) rather than Trench's section-based
  `X.Y.Z` — the intended restyle, content unchanged. The full-book compile + its error tail is Phase 5
  (needs Phase 3 EPS→PDF); the shim is expected to grow there.
- **Phase 3 — figures & engine.** **DONE 2026-09-19.** Created `tools/eps2pdf.sh` (epstopdf over
  `checkout/EPS/*.eps` → `checkout/EPS-pdf/*.pdf`, idempotent, batch-failure-propagating), wired as
  `make figures` (mounts `tools/` at `/toolsrc`; `pdf` now depends on `figures`). The dvips/geometry
  drop was already handled by the phase-2 preamble swap. **Validated:** all **206** EPS converted
  (status 0, incl. `cover.pdf`); a test doc `\includegraphics{exer010301}` resolves to
  `./EPS-pdf/exer010301.pdf` and embeds under lualatex (exit 0). `EPS-pdf/` is on the normalized
  master's `\graphicspath` and is gitignored (regenerable, under `checkout/`).
- **Phase 4 — front matter & license.** **DONE 2026-09-19.** Chose the general fix (impl. OQ1 (a)):
  **parameterized the shared `openstax/tooling/latex/osbook.cls`** with three backward-compatible
  setters — `\setOSbooklicense`, `\setOSbookdedication`, `\setOSbookpublisher` — whose DEFAULTS
  reproduce the OpenStax CC BY-NC-SA 4.0 page verbatim (verified: a bare-osbook doc still renders
  OpenStax + CC-4.0, so the 16 existing books are unchanged). The transform now cuts the hand
  title/license/dedication/TOC at the `\pdfbookmark[0]{Preface}` marker (preserving the **Preface**
  prose + all chapters) and injects `\OSfrontmatter` with Trench's **CC BY-NC-SA 3.0 + AIM** license,
  the **TO BEVERLY** dedication, and an empty publisher (no false "OpenStax" imprint). Also unblocked
  a body-wide issue found here: the shim re-enables the old LaTeX 2.09 font declarations
  (`\bf`/`\it`/`\sc`/…) that memoir disables. **Validated:** the front matter compiles (exit 0) and
  renders osbook title, the CC-3.0 license page, the dedication, the auto-TOC, and the preserved
  preface. NOTE: this is a **shared-class change** (also gives the OpenStax colophon a proper
  per-book license setter — see `openstax-book-subtitle-attribution.md`).
- **Phase 5 — build & verify.** **DONE 2026-09-19.** Wired `make pdf` (image → normalize → figures →
  `latexmk -pdflua` into `checkout/output/`). Iterated the full-book compile from **2467 → 0 errors**
  over a few cycles; the shim grew to cover the real book: `\DeclareOldFontCommand` (the 2.09 fonts
  work in **math** too, ~2060 errors), `\RequirePackage{float}` (`[H]`, 51), a `tindex` index env,
  `\part` made math-safe, `\thissection` left to the body, and one body-fixup in the transform
  (`\enlargethispage{1\in}`→`1in`, a source typo). **Result: a clean 762-page PDF, 0 LaTeX errors**,
  latexmk exit 0. Only **4 undefined references remain — pre-existing danglers in Trench's own source**
  (`exer:11.2.30`, `eq:12.2.1`, `eq:12.2.23` → chapters 11–12, which exist only in the boundary-value
  edition, not this 10-chapter main book); fixing them would change content, so out of scope.

- **Figure placement fix (2026-09-19, maintainer-reported).** Figures rendered offset down/right over
  their captions: Trench stamps the same EPS `bb=-78 148 689 643` on every `\includegraphics`, but
  `epstopdf` already crops each PDF to its own box, so the transform now **strips `bb=`** and lets
  graphicx use each PDF's MediaBox. Verified visually (Figure 1.1). Gotcha documented in the book
  `CLAUDE.md`.

## Build-warnings review (2026-09-19, autonomous session — for maintainer review)

The maintainer flagged "a ton of warnings." Full triage of the `make pdf` log (0 errors, 761 pp):

**Fixed this session:**
- **Figure right-overflow** → capped figure width at `\linewidth` via `adjustbox`'s `max width`
  (shim loads `[export]{adjustbox}`; transform injects `max width=\linewidth` into every
  `\includegraphics`). Verified visually: Figure 1.1 now fits the column.
- **`\l` in math (6 warnings: 3 "invalid in math" + 3 "missing character ł")** → a source typo for
  `\ell`; transform replaces a bare `\l` with `\ell`. Now 0.

**Wide display equations off the right — FIXED (maintainer chose option (a), 2026-09-19).** Trench's
dense math/arrays were typeset for a wider measure than osbook's 5 in, so ~59 equations ran >50 pt
(up to ~2.4 in) off the page. **The shim now widens the text block to ~6.5 in for THIS book only**
(`\setlrmarginsandblock{1in}{1in}{*}` + `\setulmarginsandblock{1.1in}{1.3in}{*}` +
`\checkandfixthelayout`; deliberately drops osbook's golden-ratio proportion, scoped to the trench
family via the shim — the shared `osbook.cls` and the OpenStax books are untouched). Result:
**Overfull \hbox 578 → 97; the >50 pt "real" ones 59 → 1** (a single intrinsically-huge equation),
**Overfull \vbox 0** (no vertical overflow — the taller block still fits the 11 in page), 673 pp,
0 errors. Verified visually (page layout uses the page well, equations fit, margins balanced). The
remaining ~97 are the small/invisible line-breaking noise (<10–50 pt).

**Other warnings — cosmetic / source-content, left as-is:** `\over` primitive (1, works),
`table:4.1.1` label multiply-defined (1, a Trench source bug — a content fix), `mdframed` bad page
breaks in theorem/definition boxes (6), hyperref PDF-bookmark token warnings (4), `unicode-math`
informational (2). None affect correctness.

## Minor polish + review — MOVED OUT (2026-09-19)

The maintainer visual review and the cosmetic polish items (Preface pagination, license-page wording,
empty PDF metadata title, the 4 source danglers, `definition` numbering) are now their own task,
`trench-pdf-review-and-polish.md`, so this build task can close. **Follow-ons (separate tasks, gated on
this one):** the BV variant + student manual (`add-trench-bv-and-student-manual.md`), and the HTML+EPUB
web editions (`trench-differential-equations-html-epub.md`, done).

> This task (phases 1–5) is itself big enough that it may warrant splitting into **step-tasks**
> (umbrella + per-phase children) at execution — see `~/.claude/reference/task-doc-conventions.md`.
> Left as one doc for now so the whole shape is reviewable; propose the split when picking it up if
> phases 2–5 each grow commit boundaries.

## Risks / watch-items

- **Cross-reference integrity** is the top risk: 1424 `\answer` page-refs + faked sectioning mean a
  careless sectioning swap silently renumbers or breaks refs. Verify by diffing structure, not by eye
  alone.
- **HTML/EPUB via pandoc** is not guaranteed — Trench's `eqnarray`/custom envs may not translate;
  treat as stretch, PDF is the phase-1 deliverable.
- **License accuracy** — Trench is CC BY-NC-SA **3.0** (not the OpenStax 4.0); the front matter and
  any colophon must state 3.0 + the AIM/no-profit clause. (Note: this also touches the pre-existing
  osbook.cls colophon license question flagged in `openstax-book-subtitle-attribution.md`.)
- **EPS bounding boxes** are hard-coded; epstopdf should preserve them, but spot-check figure sizing.

## Provenance

- Upstream: https://github.com/billsix/differentialEquationsTrench @
  `a7c17e34ee0326ff97824d166a1dc91547f8f2e7` (HEAD, 2026-09-19).
- License: CC BY-NC-SA 3.0 Unported; AIM Open Textbook Initiative; Free Edition 1.01 (Dec 2013),
  William F. Trench, Trinity University.

## Open questions

All five original questions were resolved 2026-09-19 — see the Decisions block at the top (family
`trench/`; reuse OpenStax tooling in place; main book → PDF only; full aesthetics-only restyle;
HTML/EPUB deferred). Two implementation sub-decisions remain, both deferrable to execution:

1. ~~**License-page mechanism.**~~ **RESOLVED 2026-09-19: (a)** — added `\setOSbooklicense` +
   `\setOSbookdedication` + `\setOSbookpublisher` to the shared `osbook.cls` (backward-compatible
   defaults). Also gives the OpenStax colophon a per-book license setter.
2. **`definition` numbering.** Trench shares one counter across theorem/definition; osbook may number
   them independently. Recommendation: match Trench (shared) to keep the book's internal references
   stable; revisit only if it looks wrong. Decide at phase 2.
