# Add the Trench "Elementary Differential Equations" book to impo, in OpenStax house style

**Status:** proposed — needs go-ahead + several architecture decisions (open questions below)
**Priority:** 4
**Difficulty:** 8 (large, multi-phase: LaTeX restyle of a 1.6MB custom-class book + build wiring)
Created 2026-09-19 (William Emerison Six <billsix@gmail.com>).

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

- **Phase 0 — decisions.** Resolve open questions 1–4 (family location/name, tooling sharing, scope,
  fidelity target). Nothing else starts until these are set.
- **Phase 1 — scaffold the book folder.** `fetch.sh` (pin `a7c17e3…`, URL as above), `apply.sh`
  (overlay the shared LaTeX layer + the shim), `Makefile`+`Dockerfile` (reuse the OpenStax base;
  swap the CNXML seams), `CLAUDE.md`/`README.md`/`.gitignore`.
- **Phase 2 — the shim + preprocessing patch.** Build `trench-osbook.sty` per the mapping table; the
  deterministic patch/transform of the master preamble + sectioning + title/TOC.
- **Phase 3 — figures & engine.** EPS→PDF step; confirm the 155 `\includegraphics` resolve; drop
  dvips/hyperref-dvips options.
- **Phase 4 — front matter & license.** A per-book license page for **CC BY-NC-SA 3.0 + AIM Open
  Textbook** (osbook.cls's `\OSfrontmatter` license page is written for CC BY-NC-SA 4.0 — needs a
  per-book override or an osbook.cls license-setter). Subtitle "Formatted by Bill Six" (consistent
  with the other books).
- **Phase 5 — build & verify.** Iterate to a clean lualatex compile; verify fidelity: all 10
  chapters, ~54 sections, 69 theorems, 250 examples, 52 exercise sets, 155 figures render; the answer
  key builds and its cross-refs resolve; page count and structure are sane. This is the "done" gate.
- **Phase 6 — stretch / follow-ups.** HTML+EPUB via the reused pandoc legs (risky — pandoc `-f latex`
  may choke on the dense custom macros; the shim should define macros in pandoc-friendly forms). Then
  the BV variant and the student solutions manual as sibling masters.

> This is big enough that it may warrant splitting into **step-tasks** (umbrella + per-phase children)
> at execution — see `~/.claude/reference/task-doc-conventions.md`. Left as one doc for now so the
> whole shape is reviewable; propose the split when picking it up if phases 2–5 each grow commit
> boundaries.

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

1. **Family location & name.** The master `CLAUDE.md` says a non-OpenStax book should be a **sibling
   family folder** (mirroring how imps carries `n64/`). Recommendation: a new family, e.g. **`aimath/`**
   (AIM open textbooks — Trench is one, and more could join), holding `aimath/differential-equations/`.
   OK — and what name (`aimath/`, `trench/`, `latex-textbooks/`)? Or do you want it under `openstax/`
   despite not being OpenStax?
2. **Tooling sharing.** The house style (`osbook.cls`+envs+defer), Dockerfile base, and pandoc legs
   live in `openstax/tooling/`. Recommendation: **promote the shared layer to a repo-level `tooling/`**
   both families use (clean, no drift) — a small refactor of the existing books' `apply.sh`
   references. Lighter alternatives: the new family references `../openstax/tooling` in place, or
   copies it (drift risk). Which?
3. **Scope.** Recommendation: **main book (`TRENCH_DIFFEQ.tex`) only for phase 1**; BV variant +
   student manual as follow-ups (phase 6). OK, or do you want all three from the start?
4. **Fidelity target.** You asked for "uniformity" — I read that as a **full osbook restyle** of
   sectioning/theorems/exercises (recommended). Confirm, vs. a lighter "osbook cover/fonts only, keep
   Trench's internal layout" (less work, less uniform).
5. **HTML/EPUB.** Attempt them via the reused pandoc pipeline (stretch, may need extra shim work), or
   **PDF-only** for the first cut? Recommendation: PDF-only first, HTML/EPUB as a follow-up once the
   master compiles.
