# Trench Elementary Differential Equations — HTML + EPUB editions

**Status:** DONE (2026-09-19) — base editions build AND are **restyled to the OpenStax house theme**
(route a). `make html` → a chunked, Furo-like site (`checkout/output/html/index.html`: index + 11 pages =
Preface + 10 chapters, split **per chapter** so the left bar lists chapters and the right "On this page"
bar lists that chapter's sections; breadcrumb, big Prev/Next, teal palette, native MathML, 154 figures
resolving). `make epub` → a valid EPUB3 with the same
theme CSS injected. See "## DONE — Furo restyle (route a, 2026-09-19)" for what shipped. Not archived
per the maintainer's standing "don't archive any tasks" instruction.
**Depends on:** `add-trench-differential-equations-book.md` — satisfied (the PDF pipeline exists). NOTE
the web path does **not** actually read the osbook master: it feeds the *pristine* `TRENCH_DIFFEQ.tex`
through `tools/web_preprocess.py` into a simple `\documentclass{book}` `bookW.tex` that make4ht
compiles. So the dependency is only on the fetched source + the phase-3 figures, not on osbook.cls.
**Priority:** 4 (the maintainer asked for the Furo restyle 2026-09-19; base editions already ship)
**Difficulty:** 6
Created 2026-09-19 (William Emerison Six <billsix@gmail.com>).

## DONE — full-book HTML + EPUB via make4ht/tex4ebook (2026-09-19)

The final pipeline **abandoned pandoc for make4ht/tex4ebook** (real LaTeX engines via tex4ht), because
pandoc's LaTeX *parser* could not handle Trench's raw-TeX primitives and custom macros without an
open-ended macro-rewriting effort, whereas make4ht runs the actual LaTeX. The one insight that made
this cheap: make4ht chokes on the heavy `osbook.cls` (memoir + fontspec + unicode-math — it timed out),
but a **simple `\documentclass{book}` web input compiles fast** — so the web edition takes a wholly
separate path from the PDF.

**The pipeline (all in one container pass, `tools/build_web.sh html|epub`):**
1. `tools/eps2png.sh` — rasterize the cropped `EPS-pdf/*.pdf` (from `make figures`) to PNG at 120 dpi
   with ghostscript (poppler's `pdftoppm` is not in the image); tex4ht embeds PNG in HTML, not PDF/EPS.
2. `tools/web_preprocess.py` — `TRENCH_DIFFEQ.tex` → `bookW.tex`: keep Preface..end, rewrite sectioning
   to real `\chapter`/`\section` as **text**, strip comments, prepend the packages the body needs
   (`amsmath`/`xcolor`/`hyperref`/`graphicx`/`float` + `\graphicspath`) and `tools/pandoc-defs.tex`
   (the ~60 custom-macro definitions that made the whole book compile 0-error), wrap in
   `\documentclass{book}`. The pristine source is never modified.
3. `make4ht -u bookW.tex "mathml"` (HTML) or `tex4ebook -f epub3 bookW.tex "mathml"` (EPUB) — math as
   native MathML. Output collected to `checkout/output/<fmt>/` with figures under `.../EPS/`.

**What `pandoc-defs.tex` had to fix to reach 0 compile errors** (the long tail, all resolved): 2.09
font commands in math (`\DeclareOldFontCommand{\bf}`…); the missing counters
(`exercise`/`place`/`lcal`/`rm`); `\providecommand{\newsection}{}` (the answer key `\renewcommand`s it);
`\def\endproof{}` (`\newcommand` refuses `\end…` names); the matrix macros used in ch2–10
(`\col`/`\colfunc`/`\cthreebythree`/`\twochar`/`\threechar`/`\matfunc`/`\arraytext`); bookmark no-ops;
and the `definition` env written WITHOUT a trailing `\ ` after `#1` (the source writes
`\begin{definition}\color{blue}…` unbraced, so `#1` grabbed `\color` and the trailing space became its
arg → "Undefined color `\ '"). `\thissection` is defined by the body (line ~220), so the defs must NOT.

**`over_to_frac.py` — kept, but not on the critical path.** make4ht compiles `\over` natively, so the
brace-aware `{a\over b}`→`\frac` converter (`web_preprocess.py --frac`) is **not invoked** by the
current build. It is validated (whole book 4622→0 unresolved) and retained for a possible future
pandoc/MathML path; `build_web.sh` does not pass `--frac`.

**Build image change (authorized):** `openstax/tooling/Dockerfile` gained a `zip`+`tidy` layer —
tex4ebook needs `zip` to pack the `.epub` and `tidy` to clean the XHTML. Own RUN layer (after the
rsvg/fonts layers) so the big TeX layer stays cache-shared; harmless to the OpenStax books.

**Tools fully type-annotated** (locals + globals) per the maintainer's request: `web_preprocess.py`,
`over_to_frac.py`, `normalize_master.py`. `ty` clean and `ruff` clean under the project config
(`openstax/tooling/pyproject.toml`, which selects F/E402/I/TID/UP/B — the trench folder has no
pyproject of its own; the tools are checked against the shared one).

**Known cosmetic warnings (non-fatal):** tex4ht's luaxml DOM parser logs "Unbalanced Tag" on a few
chapters, then falls back to HTML DOM parsing and `tidy` (both succeed) — the outputs are complete and
valid. Not worth chasing.

**Reproduce:** `./fetch.sh && ./apply.sh && make figures && make html` (or `make epub`).

## DONE — Furo restyle (route a, 2026-09-19)

Implemented route (a): the make4ht monolithic HTML is post-processed into the OpenStax chunked theme
(the maintainer approved defaults 2026-09-19: shared assets by build-mount, teal, discretion on content
CSS; split granularity started per-section then changed to **per chapter** — see "Right 'On this page'
sidebar" below). What shipped:

- **`tools/split_html.py`** (NEW, type-annotated, ruff+ty gated) — splits `bookW.html` at the
  `h2.chapterHead` boundaries into `index.html` + `NNN-<slug>.html` **per-chapter** pages (the chapter's
  `h3.sectionHead` sections stay on the page as the right-bar subheadings), promotes each chapter heading
  to `<h1>`, wraps each in the shared chunked-template layout (left book-TOC slot, breadcrumb, Prev/Next,
  right on-this-page slot), and **synthesizes `sitemap.json`** (flat: chapters only) in the schema
  `build_nav.py` consumes.
- **Shared assets reused UNCHANGED** — `osbook-web.css`, `osbook-web.js`, `build_nav.py` from
  `openstax/tooling/tools/pandoc`, read via a **read-only build mount** (`/osbook-assets`, added to the
  Makefile's `FILES_TO_MOUNT`). A committed repo symlink into the sibling `openstax/` tree can't resolve
  in the build container (separate mounts), so the RO mount is the working "single source of truth, no
  drift" equivalent the maintainer wanted.
- **`tools/trench-web.css`** (NEW) — the small adapter loaded last: undoes tex4ht's `body{max-width:80ch}`
  so the 3-column `.layout` gets full width, centers `.minipage` figures, and a little polish. tex4ht's
  `bookW.css` (kept) supplies content typography (`.cmti`→italic, `.cmbx`→bold); osbook-web.css supplies
  the theme; trench-web.css reconciles the two.
- **`build_web.sh`** — the `html` case now runs `split_html.py` + copies the assets + runs `build_nav.py`;
  the `epub` case unzips the tex4ebook epub, appends `osbook-web.css`+`trench-web.css` into its
  stylesheet (the `.layout` grid rules are inert in a reader; palette/heading/figure/MathML rules apply),
  and repackages per EPUB rules (mimetype first + STORED). Figures: `<img>` srcs are `EPS-png/*.png`
  (make4ht graphicspath prefers PNG), copied to `output/html/EPS-png/`.
- **Chapter AND section numbering fixed** — `web_preprocess.py` and `normalize_master.py` strip both
  `\setcounter{chapter}{N}` and `\setcounter{section}{N}`, so chapters are 1–10 (not 2–11) and every
  chapter's sections auto-number consecutively from .1 (chapter 2 was 2.2–2.7, now 2.1–2.6). Details:
  `tasks/trench-section-numbering-decision.md` (RESOLVED 2026-09-19).

**Verified (structural, 2026-09-19):** `make html` → index + 11 pages (Preface + 10 chapters), no broken
internal links, left TOC injected into all pages, 154/154 figures resolve, MathML present (18k+ tags),
right "On this page" bar lists each chapter's sections, correct 1–10 chapter
numbering. `make epub` → valid EPUB3 (mimetype Stored/first), theme CSS injected, 154 figures, MathML.
**Not visually eyeballed in a browser** (no display in this session) — the maintainer should open
`checkout/output/html/index.html` and the epub to confirm the look; see open questions.

### Possible follow-ups (not blocking; noted for a future pass)
- **Boxed environments.** Trench's theorems/definitions/examples are plain bold run-in heads (its native
  print style), NOT semantic `<div class="theorem">` like the OpenStax converter emits, so osbook-web.css's
  boxed-env rules don't bind. Matching the OpenStax boxes would need pandoc-defs.tex to emit classed
  wrappers tex4ht can style — deferred (the run-in style is clean and true to the book).
- ~~Section-number quirk (chapter 2 → 2.2 start)~~ — FIXED 2026-09-19 (see the numbering bullet above +
  `tasks/trench-section-numbering-decision.md`).
- **Right "On this page" TOC is empty** — now an ACTIVE request (the maintainer, 2026-09-19: wants the
  diffeq book to have both a left and right sidebar like the OpenStax books). Full study + options below,
  "## Right 'On this page' sidebar — study + options".

## Right "On this page" sidebar — DONE via per-chapter split (2026-09-19)

**The request (maintainer, 2026-09-19):** the OpenStax web books show a **left** menubar (book TOC) AND a
**right** menubar ("On this page"); give the diffeq book the same gist. (The LEFT bar already worked;
`build_nav.py` injected the full book TOC. The RIGHT bar was empty.)

**Why it was empty.** `osbook-web.js` builds "On this page" from the page's own `h2/h3/h4[id]` and hides it
below 2. trench is only two levels deep (chapter → section; sections are monolithic — the heading map is 10
`h2.chapterHead` + 54 `h3.sectionHead`, zero `h4`), so the original **per-section** pages had exactly one
heading (the promoted `<h1>`) and nothing to sub-navigate. The section's landmarks (Example./Theorem./
Definition.) render as bare bold run-ins with no number/id/class (`\textbf{Example.}` via pandoc-defs), so
they aren't anchorable either.

**Decision (maintainer's call):** split **per CHAPTER**, not per section — *left = the chapter list, right
= the section subheadings*. Making the chapter the page turns its `h3.sectionHead` sections into the
on-page subheadings, so both bars fill from trench's REAL structure with no fragile heuristics.

**What changed (`split_html.py`, rewritten to per-chapter):** cut the monolithic HTML at `h2.chapterHead`
boundaries only (front matter = the Preface page). Each chapter page promotes its chapter heading to
`<h1>` and **leaves the `h3.sectionHead` sections in place** (they keep their tex4ht ids). Then:
- the **LEFT** book-TOC (`build_nav.py`, from `sitemap.json`) lists the **11 pages** (Preface + 10
  chapters); `sitemap.json` is now flat — chapters only, since sections are on-page, not sitemap nodes;
- the **RIGHT** "On this page" bar (`osbook-web.js`, from each page's `h3[id]`) lists that chapter's
  **sections** automatically.

Sections became `chapter.html#section-slug` anchors (deep links still work) instead of standalone pages;
chapter pages are correspondingly longer, which the right bar exists to navigate.

**Verified (2026-09-19):** `make html` → index + 11 pages (Preface + 10 chapters); left bar = 11 entries
(Preface, "1 Introduction" … "10 Linear Systems …"); a chapter page (Introduction) shows its sections in
the right bar (1.1, 1.2, 1.3); figures resolve; ruff+ty gate green.

**Rejected alternative — synthesizing in-section landmark anchors** (turn each Example./Theorem. run-in
into a numbered anchor to keep per-section pages with a populated right bar): not done — the run-ins carry
no number/id/class in the web output, so detection/numbering would be a fragile heuristic. If the
theorem-family environments are ever given real numbers/classes (the deferred "boxed environments"
follow-up), a per-section layout with landmark sub-nav could be revisited.

### Original research + plan (route a, as approved) — kept for reference

**Goal was:** make the trench HTML/EPUB look like the other 16 OpenStax books' web editions — the
Furo-like chunked theme (left collapsible book TOC, centered content column, right "On this page" TOC +
scrollspy, big Prev/Next footer, mobile hamburger drawer, teal palette). Researched 2026-09-19 (agent
sweep of `openstax/tooling` + git history + archived tasks); findings + `file:line` anchors below.

### How the OpenStax look is actually produced (it is NOT in pandoc)

The theme is a **pandoc `chunkedhtml`/`epub3` pipeline + 6 small asset files** under
`openstax/tooling/tools/pandoc/`. pandoc emits bare chunk pages + a `sitemap.json`; the *look* comes
entirely from the assets:

- **`entrypoint/html.sh`** — `pandoc -f latex -t chunkedhtml --split-level=2 --toc --toc-depth=2 --mathml
  --template=chunked-template.html --chunk-template="%n-%i.html" --lua-filter=xref.lua --css=osbook-web.css`
  (`html.sh:50-60`). `--split-level=2` = **one page per section** (1 = per chapter). Master discovery is
  the CNXML seam: it loops `collections/*.collection.xml` (`html.sh:41`) — a non-OpenStax book must
  replace this with single-master discovery.
- **`chunked-template.html`** — the page skeleton: `.layout` grid wrapper, `nav.book-toc` holding a
  `<!--BOOK-TOC-->` placeholder (`:39`), `main.content` with breadcrumb + `$body$` + `nav.prevnext`
  Prev/Next buttons (`:74-85`), `nav.page-toc` right sidebar (`:87`), mobile scrim, `osbook-web.js`.
- **`osbook-web.css`** — `:root` palette (`--os:#00507d` teal, `:6-11`), the **3-column Furo grid**
  `.layout{grid-template-columns:18rem minmax(0,1fr) 15rem}` (`:27-51`), sticky sidebars, collapsible
  left-TOC carets (CSS `::before` `▸`/`▾`, `:79-82`), responsive breakpoints (drop right TOC <1180px,
  hamburger drawer <900px, `:124-140`), and boxed theorem/definition/example envs (`:156-234`, mirroring
  the PDF mdframed).
- **`osbook-web.js`** — builds the right "On this page" TOC from the page's own `h2/h3/h4[id]`
  (`:14-37`), scrollspy via IntersectionObserver (`:40-58`), left-TOC caret toggle (`:61-69`), mobile
  drawer (`:72-83`). No deps; degrades with JS off. It does **not** build the left TOC.
- **`build_nav.py`** — injects the whole-book **left TOC** into each page's `<!--BOOK-TOC-->` at build
  time (not client-side: `file://` blocks `fetch`, and readers open these locally — archived task
  `openstax-html-sticky-sidebars.md`). Reads pandoc's **`sitemap.json`**; one `<li>` per PAGE (on-page
  anchors are dropped from the left tree, shown only in the right TOC, `:53-64`/`:104-113`).
- **`xref.lua`** (pandoc Lua filter — numbering + `\cref`→numbered links) and **`preprocess.py`**
  (CNXML-emitted-LaTeX sanitizer). **Neither is reusable for trench** — they're pandoc-only and assume
  the converter's output shape; trench's numbering/cross-refs already come from tex4ht's real-engine
  compile.
- **Per-book palette hook:** a book may ship `bookstyle-web.css`, appended after `osbook-web.css`
  (`html.sh:66`) so its `:root` wins (calculus = navy + Termes). This is the web twin of `bookstyle.tex`.
- **EPUB** (`entrypoint/epub.sh:52-61`): `pandoc -t epub3 --toc --mathml --lua-filter=xref.lua
  --css=osbook-web.css` — **no template, no build_nav, no JS**: the EPUB reader supplies nav from the
  `--toc` nav doc; only `osbook-web.css` (boxed envs + `details.answer` are CSS-only, so they work in a
  reader) is embedded.

### The gap — what the trench make4ht output has vs what the theme needs

Trench's `tools/build_web.sh` produces the web editions with **make4ht/tex4ebook (real tex4ht LaTeX
engine)**, deliberately NOT pandoc (pandoc can't parse Trench's raw TeX — see the history below). Its
output (verified on `checkout/bookW.html`, 8.1 MB):

- **Good:** semantic, splittable headings already exist — `<h2 class='chapterHead' id='<slug>'>` (10) and
  `<h3 class='sectionHead' id='<slug>'>` (54), clean slug ids. chapter=h2/section=h3 maps cleanly to what
  `osbook-web.js` scrollspy expects (`h2/h3[id]`). Native MathML (18 255 `<math>`).
- **Missing/mismatched:** ONE monolithic file (not chunked); **no `<nav>`, no TOC, no `sitemap.json`**
  (tex4ht emits none); body is drenched in tex4ht **CM-font presentational classes** (`cmti-10` ×11 123,
  `cmr-9`, `array-td`, `eqnarray-1..4`, `loglike`, …) that have **no relation** to osbook-web.css's
  semantic `.theorem`/`.definition`/`.example`/`.envhead`; figures at `EPS/*.png` not `media/`.

### Route (a) — post-process make4ht output, apply the osbook theme  ⟵ RECOMMENDED

Add a **post-make4ht stage** to `build_web.sh` (after the `make4ht` call, `build_web.sh:33`) — the
make4ht compile is unchanged, so the proven math/figure rendering is untouched:

1. **NEW splitter tool** (`tools/split_html.py`, Python) — parse `bookW.html`, cut at the
   `chapterHead`/`sectionHead` boundaries into per-section (or per-chapter) chunk pages named
   `NNN-<slug>.html` (zero-padded so ordering is stable and no name starts with `-`), wrap each chunk's
   content in the `chunked-template.html` layout (port its HTML into the splitter, since this path is not going
   through pandoc), compute **prev/next/up + breadcrumb** links itself, and drop the `<!--BOOK-TOC-->`
   placeholder into each page.
2. **Synthesize `sitemap.json`** from the heading tree, in the exact schema `build_nav.py` requires —
   `{"section":{"id","level","number","path","title"}, "subsections":[...]}` with `path="NNN-page.html#anchor"`
   and root `path:"index.html"` (`build_nav.py:28-46`, `:86-93`). Use Trench's own chapter/section numbers.
3. **Reuse UNCHANGED** (copy/symlink from `openstax/tooling/tools/pandoc/`): `osbook-web.css` (shell
   rules), `osbook-web.js` (works as-is given `h2/h3[id]`), and **`build_nav.py`** (works as-is given the
   synthesized `sitemap.json` + placeholders). Run `build_nav.py <outdir>` as the last step (as
   `html.sh:71` does).
4. **CSS reconciliation — the real judgment call (see open question 2).** osbook-web.css's *shell* rules
   (grid, sidebars, Prev/Next, palette, responsive) apply for free once the layout wrapper is in place;
   its *content-env* rules (`.theorem`/`.definition`/…) will NOT bind to tex4ht's `cm*`/`array-*` classes.
   Either (i) keep tex4ht's `bookW.css` for in-content typography and layer only the osbook **shell** CSS
   on top (fast; content won't look boxed like OpenStax), or (ii) write a trench `bookstyle-web.css` that
   maps/overrides the tex4ht classes onto the osbook palette (more work, closer match). Recommend (i)
   first (gets the Furo shell immediately), then (ii) incrementally.
5. **EPUB:** tex4ebook already emits a chunked EPUB3 with reader-supplied nav + MathML, so it is closer to
   done than the HTML. Restyle = **inject `osbook-web.css`** into the tex4ebook output's stylesheet (its
   XHTML uses the same tex4ht classes, so the same CSS decision as step 4 applies). No splitter/nav needed
   (the reader builds the TOC), matching how OpenStax's own EPUB drops the template/JS/build_nav.

**Pros:** reuses the working make4ht math/figure rendering (0-error compile, 18k MathML); no pandoc fight;
keeps the `pandoc-defs.tex` investment; gets the Furo shell + reuses 3 of the 4 theme assets unchanged.
**Cons/real work:** the splitter + `sitemap.json` synthesizer is the core new artifact; the CSS class
mismatch (tex4ht vs osbook semantic classes) means content-level styling is not free.

### Route (b) — make pandoc work, then run the exact OpenStax pipeline — REJECTED

Extend `pandoc-defs.tex`/rewrites until `pandoc -t chunkedhtml` parses the whole book, then run
`html.sh`/`epub.sh` unmodified (bar single-master discovery). **This is the route the project already
tried and abandoned** (see history below): pandoc chokes on Trench's raw-TeX primitives (`\vbox`/`\hbox`/
`\vrule`/`\kern`, a raw `\halign`, ~4700 `\over`) — the one-chapter spike worked but the full book didn't
scale, and it's open-ended macro-rewriting of unknown size. Only worth reopening if byte-for-byte
cross-book uniformity becomes a hard requirement; otherwise route (a) delivers the same *look* without the
parser fight. (A "make4ht-as-pandoc-normalizer" idea collapses into route (a): once make4ht has emitted
HTML/MathML, you're post-processing make4ht output, which *is* route (a).)

### Asset/script inventory for route (a)

- **Reuse unchanged** (copy or symlink from `openstax/tooling/tools/pandoc/`): `osbook-web.css`,
  `osbook-web.js`, `build_nav.py`.
- **Port into the splitter** (not reused directly — this path does not go through pandoc): the layout markup of
  `chunked-template.html`.
- **NOT reusable:** `xref.lua`, `preprocess.py` (pandoc-only).
- **New trench tools:** `tools/split_html.py` (splitter + `sitemap.json` synth + template wrap + prev/next
  + `<!--BOOK-TOC-->`), an optional `tools/bookstyle-web.css` (step 4-ii palette/class map). Add a
  post-make4ht stage to `build_web.sh`; add the EPUB CSS injection for the epub path. **All new `tools/*.py`
  are auto-gated** by `make image` (the `check-tools` ruff+ty gate added 2026-09-19) — annotate types
  generously per the standard.
- **Decide before building:** whether trench reuses the assets by **symlink into the checkout at build
  time** (like the shared osbook.cls overlay via `apply.sh`) or **vendors copies** into the trench
  `tools/`. Symlink keeps one source of truth (the assets are the maintainer's MIT toolchain); do the
  reference read of `openstax/CLAUDE.md`'s "Changing the toolchain" note first.

### Restyle decisions (taken 2026-09-19 by the maintainer) — all implemented

1. **Split granularity → per section initially, then changed to per CHAPTER** (2026-09-19, maintainer's
   call, so the left bar = chapters and the right "On this page" bar = that chapter's sections; trench is
   only 2 levels deep). See "Right 'On this page' sidebar — DONE via per-chapter split".
2. **Content-env CSS → shell + typography** (kept tex4ht `bookW.css` for content, osbook-web.css for the
   theme, trench-web.css to reconcile). Boxed envs deferred (see follow-ups) — Trench uses run-in heads.
3. **Asset delivery → read-only build mount** of `openstax/tooling/tools/pandoc` (a repo symlink into the
   sibling project can't resolve in a separate container mount; the RO mount is the driftless equivalent).
4. **Palette → OpenStax teal** (the shared default; no per-book `bookstyle-web.css`).

## Original plan + spike history (superseded by the above — kept as the honest record)

## BLUF

After the Trench main book builds to an osbook-styled **PDF** (task
`add-trench-differential-equations-book.md`), produce the **chunked HTML web edition and EPUB** for
it, reusing impo's existing pandoc pipeline. The leverage: OpenStax HTML/EPUB are built by running
`pandoc -f latex` over the *generated* osbook master (not the source), so once a valid osbook `.tex`
master exists, the same `html.sh`/`epub.sh` legs apply. The risk: Trench's dense, custom-macro LaTeX
(heavy `eqnarray`/`array`, the shim's redefinitions, faked-then-restyled sectioning) may not
translate cleanly, so the shim likely needs pandoc-friendly macro forms. "Done" = a navigable HTML
web edition and a valid EPUB, math and figures rendering, cross-references working.

## Context (cold-start)

The reusable web legs (`openstax/tooling/`): `entrypoint/html.sh` (chunked HTML via
`pandoc -t chunkedhtml` + `tools/pandoc/xref.lua`, `chunked-template.html`, `osbook-web.css`,
`build_nav.py`), `entrypoint/epub.sh` (`pandoc -t epub3`), and `tools/pandoc/preprocess.py`. These
consume the generated `latex/*.tex` — **not** CNXML — so they are source-independent *given a good
master*. The one CNXML-coupled seam is master-discovery via `collections/*.collection.xml`
(`html.sh:41`, `epub.sh:49`), which task 1 already adapts for trench's master.

**Read task 1 first** for the shim and the master's shape. Cross-references in the web edition go
through `\cref`→`xref.lua` (see `tasks/reference/tooling/cross-references.md`); the shim should emit
Trench's cross-refs in a form that path understands.

## Spike results (2026-09-19, one-chapter spike) — SUCCESS: HTML + EPUB both build

**Chapter 1 renders as good HTML end-to-end.** `defs.tex` (custom macros) + `--mathjax` produced an
**81 KB HTML page with 407 MathJax math spans, 87 cross-reference links, 3 section headings, 2 H1s,
19 figure `<img>`s**, and coherent text (verified by extraction: "Newton's Law of Cooling", inline
`\(T_m\)`, display `\[T'=-k(T-T_m)\]`). The pandoc path is **proven viable** for the web edition.

**The two blockers, both solved:**
1. **Sectioning must be TEXT-rewritten, not macro-defined.** pandoc silently empties the whole
   document (no error) if two macros both expand to sectioning (`\chapter` AND `\section`). Fix: the
   web preprocessor rewrites `\chaptertitle{X}`→`\chapter{X}`, `\newsection{a}{b}{c}`→`\section{c}`,
   `\sectiontitle{X}`→(removed) as text; `defs.tex` never defines sectioning.
2. **`%` comments in `defs.tex` break pandoc** (they contained `\chapter`/`\section`/`\newcommand`
   text and pandoc's reader chokes). Fix: strip `%` comments from the defs before feeding pandoc.
   (Lesson: much of the earlier "empty output" was these two, compounded by rapid file-state churn.)

**Third blocker: do the whole preprocess in ONE pass** — mixing host and container steps produced
maddeningly inconsistent "empty output" results (a file-crossing artifact, not real breakage). Doing
sectioning-rewrite + comment-strip + `\over`-convert + pandoc consistently in one place is reliable.

**BOTH editions build. `\over` converter is VALIDATED (no bug).** With the three fixes above:
- **HTML** (`--mathjax`, no `\over` conversion needed — MathJax renders `\over`): Chapter 1 → **81 KB,
  407 math spans, 87 links, 19 figures**, coherent text.
- **EPUB/MathML** (`\over`→`\frac` via `tools/over_to_frac.py`): converted Chapter 1 → **MathML 207 KB
  with 494 native `<math>` tags, and a valid 28 KB `.epub`**. (My earlier "the converter breaks
  pandoc" was the same host/container file gremlin — the converted chapter renders fine.)
- `over_to_frac.py` converts the whole book (**4622 → 0 unresolved**), correct on nested and
  **multi-line** cases; validated end-to-end through pandoc.

**Reusable pipeline built: `tools/web_preprocess.py`** — one command does sectioning-rewrite +
comment-strip + (`--frac`) `\over`→`\frac`, prepends the pandoc-defs, and emits a pandoc-ready
`*-web.tex` (source untouched). Verified: fresh Chapter 1 → 80 KB HTML + 28 KB EPUB in one pass.

**Remaining to a full edition** (bounded, no unknowns left): front matter (title/license/preface) for
the web; **EPS→PNG** for figures (the 19 `<img>`s are broken until then); a small math tail (~14/chapter,
mostly `\eqno{X}` → rewrite to `\tag{X}`, and `\left/…\right.`) that falls back to raw TeX under
MathML; wire the OpenStax chunked-HTML template + nav + CSS and `make html`/`make epub` targets; then
scale from Chapter 1 to all 10 chapters. **Committed spike artifacts:** `tools/over_to_frac.py`,
`tools/pandoc-defs.tex`, `tools/web_preprocess.py`.

**4. make4ht (tex4ht) comparison — NOT a free win either.** Ran `make4ht --lua` on a tiny
`osbook.cls`+shim doc: it **timed out (>260 s, exit 124) with no HTML produced**, and the mathml
extension flag needs different config. tex4ht struggles to compile this heavy memoir + fontspec +
unicode-math + mdframed class (each of its passes is slow, and it may be stuck). So a real-TeX-engine
render is plausible but needs real config/perf work, not turnkey. `LaTeXML` (the third option)
untried.

**Assessment (honest):** HTML/EPUB is a real project for this hand-written book, and **no tool is
turnkey** — each needs work:
- **pandoc + preprocess:** math is solved (the `\over` tool + `--mathjax`/`--mathml` both work); the
  cost is the custom-macro `defs.tex` (silent-failure debugging, but bounded — ~50 macros, structural
  ones rewritten as text). Upside: reuses the OpenStax web template (uniformity).
- **make4ht/LaTeXML:** no defs, no `\over` work (runs the real LaTeX), but this spike shows getting
  tex4ht to even compile `osbook.cls` is its own effort; LaTeXML unknown. Upside: highest fidelity;
  downside: won't match the OpenStax web template without work.

My lean, post-spike: **pandoc**, because its one hard blocker (`\over`) is now *solved* and its
remaining friction (defs) is tedious-but-bounded and reuses the OpenStax look — whereas the
real-engine tools traded that friction for a compile-the-class problem of unknown size. But it's a
real choice, not obvious. Committed spike artifacts: `tools/over_to_frac.py` (**keep — needed for the
pandoc/EPUB path either way**), `tools/pandoc-defs.tex` (WIP; only if pandoc is chosen).

**Recommended next step when picked up:** finish the pandoc `defs.tex` methodically (define macros in
small batches, testing after each so a silent-empty is caught immediately) + the sectioning/`\pageref`
text-rewrites in a `web_preprocess.py`, and render Chapter 1 end-to-end before scaling to all 10.

## Attempt log (2026-09-19, autonomous session — maintainer asked me to try it)

**Outcome: does not work out-of-the-box; needs a dedicated raw-TeX→pandoc sanitization pass.**
A direct `pandoc 3.7 -f latex -t html5 --mathml` on the completed `TRENCH_DIFFEQ-osbook.tex`
**failed** (exit 64):

```
Error at line 20729: unexpected \vbox / expecting \end{document}
```

Root cause: pandoc's LaTeX reader is not a TeX engine and chokes on the **low-level TeX primitives**
Trench's 2001 source uses everywhere — `\vbox`/`\hbox`/`\vrule`/`\hrule`/`\kern` (in `\bigbox`,
`\blankbox`, `\endproof`, tables), plus the shim/custom commands pandoc never sees (it doesn't load
`\usepackage{trench-osbook}`). The OpenStax books avoid this because their converter *emits*
pandoc-friendly LaTeX; Trench's hand-written source is the opposite.

So this task is **real work**, not a wiring job. What it needs (superset of the original plan below):
1. A **preprocessing pass** (a `tools/` script, LaTeX→LaTeX) that strips/replaces the raw TeX box
   primitives and the custom commands with pandoc-parseable equivalents — or a `defs.tex` fed to
   pandoc that redefines the shim macros in pandoc-expandable form (`\newcommand` pandoc can expand;
   raw `\vbox{}` it cannot, so those must be rewritten, not defined).
2. **EPS→PNG** for the web (pandoc embeds neither PDF nor EPS; phase-3 makes PDFs — add a PNG path).
3. Only then the reused `html.sh`/`epub.sh` pandoc invocation (adapted from single-master, not
   `collections/*.collection.xml`).

### Suggested approach (revised after testing, 2026-09-19)

**Recommendation: pandoc, math via `--mathjax`.** Testing flipped the earlier tex4ht lean: the thing
that looked like the dealbreaker — pandoc can't parse `\over` (used ~4700×) — was an artifact of
`--mathml` (which makes pandoc parse the math itself). With **`--mathjax`, pandoc passes the raw TeX
to MathJax, which renders `\over` natively — verified, zero preprocessing.** And pandoc reuses the
OpenStax web template (`chunked-template.html`/`osbook-web.css`/`build_nav.py`), so Trench's web
edition matches the other books. So preprocess a **separate** `TRENCH_DIFFEQ-web.tex` (PDF source
untouched) and run the OpenStax pandoc pipeline, adapted.

**Proven in a spike (2026-09-19):** a prepended defs file that redefines the custom macros makes
pandoc *expand* them — `\chaptertitle{X}` → `<h1>`, `\bigbox{X}` → passthrough (so the raw TeX box
primitives that live *inside* ~3 macros are absorbed for free); arrays → MathML/MathJax.

**Bounded work items:**
1. **`defs.tex`** redefining the ~60 custom macros (wtrench + the shim + the main-file preamble) to
   pandoc-friendly forms — sectioning → `\chapter`/`\section`, theorem/example/definition → simple
   blocks, exercise lists → `enumerate`, `\Cex`/badges → text, box macros → passthrough.
2. **`\pageref` → hyperlink** (maintainer-approved: drop the literal page number, link to the target).
   ~1462 refs, mostly via one macro (`\answer`); redefine it for the web path.
3. **EPS → PNG** for the web (pandoc embeds neither PDF nor EPS; phase-3 makes PDFs — add a PNG path,
   e.g. `pdftoppm`/`magick` from the cropped `EPS-pdf/`).
4. **Residual raw TeX:** ~20 box primitives (mostly absorbed by item 1) and **1 raw `\halign`** table
   — hand-handle that one.
5. Wire the reused `html.sh`/`epub.sh` pandoc invocation, adapted from a single master (not
   `collections/*.collection.xml`).

**Note — the maintainer's "sed line-by-line for `\over`" idea:** not needed for HTML (`--mathjax`
handles `\over`); and it would not be reliable even if needed — `\over` has ~84 brace-less/implicit-
group uses, plus multi-line and nested-brace cases, so `{a\over b}`→`\frac{a}{b}` needs a brace-aware
pass (Python), not sed. Keep this in reserve only for the MathML/EPUB path (below).

**EPUB math rendering — DECIDED (William Emerison Six <billsix@gmail.com>, 2026-09-19): (ii) MathML.**
Native/reliable in EPUB3 readers, worth the extra work. Consequence: EPUB is built with pandoc's
**MathML** output, which cannot parse `\over`, so this path **requires** a brace-aware
`\over`→`\frac` conversion — a `tools/` Python script (NOT sed: `\over` has ~84 brace-less/implicit,
plus multi-line and nested-brace cases), producing a committed intermediate the maintainer eyeballs
before the EPUB build (the source is pinned, so it's a one-time verify). **HTML stays on `--mathjax`**
(no `\over` work); only the **EPUB/MathML** path runs the `\over` converter. So the pipeline forks:
one preprocessed `*-web.tex` for HTML (`--mathjax`), and the same plus `\over`→`\frac` for EPUB
(`--mathml`) — or a single `*-web.tex` with `\over` already converted, used by both (MathJax renders
`\frac` fine too, so converting `\over`→`\frac` once and using it for BOTH is simpler — decide at
build time).

**Fallback:** if the item-1 macro-defs long tail proves painful, `make4ht`/`tex4ht` or `LaTeXML` run
the *actual* LaTeX (no defs, no `\over` issue) — at the cost of not matching the OpenStax web template.

**De-risk before committing:** spike ONE chapter through pandoc+`--mathjax`+defs, eyeball the HTML,
and separately try the `\over`→`\frac` script on that chapter for the MathML/EPUB question.

The PDF edition is complete and unaffected by any of this.

## Plan / watch-items

1. Run `make html` / `make epub` on the trench master; triage pandoc's LaTeX-reader failures.
2. **Figures:** EPS won't embed in HTML/EPUB — rasterize EPS→PNG (or PDF→PNG) for the web, mirroring
   how `pdf.sh`/`html.sh` rasterize SVG for the OpenStax books.
3. **Math:** confirm the chunked-HTML math renderer (MathJax/KaTeX per the template) handles Trench's
   `eqnarray`/`array`-heavy math; convert `eqnarray`→`align` in the shim if pandoc/MathJax struggles.
4. **Custom envs:** ensure the shim's theorem/example/definition/exercise redefinitions degrade to
   pandoc-parseable structures (or add `preprocess.py` rules).
5. Verify: navigation (`build_nav.py`), the answer key, and cross-refs in HTML; EPUB validates.

## Open questions

1. **Answer key in HTML/EPUB — RESOLVED by the make4ht path.** The web pipeline reads the *pristine*
   `TRENCH_DIFFEQ.tex` and compiles it whole (Preface..`\end{document}`), so the source's own answer
   material renders in place, exactly as the LaTeX lays it out — no separate web decision was needed.
   (The osbook deferred `\printanswerkey` machinery is PDF-only and not on the web path.)