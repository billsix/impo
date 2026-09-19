# trench/elementary-differential-equations — Trench *Elementary Differential Equations* (impo)

A restyle of William F. Trench's open-source **Elementary Differential Equations** into the same
OpenStax house look as the impo OpenStax books. Read the family doc [`../CLAUDE.md`](../CLAUDE.md)
first (why this is a separate `trench/` family, and that it **reuses the OpenStax toolchain** rather
than a CNXML converter), then the shared toolchain it points at,
[`../../openstax/tooling/`](../../openstax/tooling). This file records only what is specific to *this
book*.

> **Status: all three editions build.** `make pdf` (osbook-styled PDF), `make html` and `make epub`
> (the MathML web editions) all work. Plans/rationale:
> [`../../tasks/add-trench-differential-equations-book.md`](../../tasks/add-trench-differential-equations-book.md)
> (PDF) and [`../../tasks/trench-differential-equations-html-epub.md`](../../tasks/trench-differential-equations-html-epub.md)
> (web).

## What lives here (thin per-book folder)

No source and no toolchain are committed — both are pulled in on demand:

- `fetch.sh` — clones the pinned pristine Trench LaTeX source into `checkout/` (gitignored).
- `apply.sh` — overlays the OpenStax house style (`osbook.cls`+`osbook-envs`+`osbook-defer`, copied
  from `../../openstax/tooling/latex/`) and, from phase 2, the `latex/trench-osbook.sty` shim.
- `Makefile` — builds the shared image from `../../openstax/tooling` and runs it against `checkout/`
  mounted at `/book`.
- `latex/` — this book's native toolchain delta: the phase-2 `trench-osbook.sty` shim (the PDF path).
- `tools/` — this book's build scripts: `normalize_master.py` (PDF preamble transform),
  `eps2pdf.sh` (EPS→PDF for the PDF), and the **web-edition** set — `web_preprocess.py`, `eps2png.sh`,
  `build_web.sh`, `pandoc-defs.tex`, `over_to_frac.py`, `split_html.py` (chunk + theme the HTML),
  `trench-web.css` (the CSS adapter) (see "Web editions" below). `tools/*.py` are
  **gated by `make image`**: it builds the shared image, then runs `ruff` + `ty` over them
  (`check-tools`, config in `tools/pyproject.toml` — the shared image's baked ty/pytest gate covers
  only openstax/tooling's own tools, not these). A dirty tool fails `make image`, hence pdf/html/epub.
- `README.md`, `.gitignore`.

## The source (native LaTeX, not CNXML)

- Upstream: **https://github.com/billsix/differentialEquationsTrench**, pin
  **`a7c17e34ee0326ff97824d166a1dc91547f8f2e7`** (HEAD, 2026-09-19).
- Three standalone masters in the checkout: `TRENCH_DIFFEQ.tex` (main, this task),
  `TRENCH_DIFFEQ_BV.tex` (boundary-value) + `TRENCH_DIFFEQ_STUDENT_MANUAL.tex` (both a follow-on
  task, `../../tasks/add-trench-bv-and-student-manual.md`), plus `wtrench.sty` and `EPS/` (206 EPS
  figures).
- **License: CC BY-NC-SA 3.0 Unported** (AIM Open Textbook Initiative; Free Edition 1.01, Dec 2013,
  William F. Trench, Trinity University) — **different from the OpenStax books' CC BY 4.0**. It is
  the author's content, **not the maintainer's**; the front-matter license page must state 3.0.

## The restyle approach (why it's a shim, not a converter)

Trench's book is a monolithic `book`-class document that fakes its sectioning (`\chaptertitle`/
`\newsection`, manual counters, hand-typed TOC) and carries a bespoke exercise/answer system, all in
`wtrench.sty`. So there is no CNXML to convert; instead a **compatibility shim**
(`latex/trench-osbook.sty`, phase 2) maps its macros onto `osbook.cls`+envs/defer, a deterministic
transform normalizes the master preamble, EPS→PDF runs for lualatex (phase 3), and the license page
is set for CC BY-NC-SA 3.0 (phase 4). **Aesthetics only — the mathematical content is unchanged.**
Full mapping table + phases: the task doc.

## Figure gotcha — two fixes keep figures placed correctly (do not undo)

Trench's figures come from an EPS/dvips/PCTeX pipeline that misplaces them under lualatex in **two**
ways (both reported by the maintainer 2026-09-19); two steps fix it, and both must stay:

1. **Vertical offset / caption overlap → strip `bb=`.** The source stamps the *same*
   `\includegraphics[bb=-78 148 689 643,...]` on every figure. `epstopdf` already crops each PDF to
   its own box at origin (0,0), so re-declaring that non-zero-origin `bb` offsets the image
   down-and-right over its caption. `tools/normalize_master.py` **strips `bb=`** from every
   `\includegraphics`; graphicx then uses each PDF's MediaBox (`width`/`height`/`keepaspectratio`
   still size it). **Do not re-introduce the EPS bounding boxes.**
2. **Horizontal offset (looks shoved right) → `pdfcrop`.** Each EPS BoundingBox carries *asymmetric*
   dead whitespace (fig010101: ~100pt left vs ~57pt right), so even a `\centering`'d figure sits
   right-of-center. `tools/eps2pdf.sh` runs **`pdfcrop --margins 2`** after `epstopdf` to trim each
   PDF to its true ink bounds, so `\centering` actually centers the drawing.

Verified visually (Figure 1.1, logistic-equation plot: sits under its caption and fills the column).

## Web editions (HTML + EPUB) — a SEPARATE path from the PDF (do not merge them)

`make html`/`make epub` do **not** use `osbook.cls`. That class (memoir + fontspec + unicode-math) is
too heavy for tex4ht — make4ht times out on it. Instead the web path (`tools/build_web.sh`, one
container pass) feeds the **pristine** `TRENCH_DIFFEQ.tex` through `tools/web_preprocess.py` into a
plain `\documentclass{book}` `bookW.tex` that **make4ht** (HTML) / **tex4ebook** (EPUB) compile fast,
with math as native **MathML**. Pandoc was tried first and abandoned — its LaTeX *parser* can't handle
Trench's raw-TeX primitives; make4ht runs the real engine. Full rationale + the pandoc spike:
[`../../tasks/trench-differential-equations-html-epub.md`](../../tasks/trench-differential-equations-html-epub.md).

Pipeline steps (all in `build_web.sh`):
1. `tools/eps2png.sh` rasterizes the cropped `EPS-pdf/*.pdf` (from `make figures`) to PNG at 120 dpi
   with **ghostscript** — tex4ht embeds PNG in HTML, not PDF/EPS, and poppler's `pdftoppm` is not in
   the image.
2. `tools/web_preprocess.py` keeps Preface..end, rewrites sectioning to real `\chapter`/`\section` as
   **text** (a macro that expands to sectioning breaks the reader), strips comments, and prepends the
   needed packages + `tools/pandoc-defs.tex`. The pristine source is never modified.
3. `make4ht -u bookW.tex "mathml"` (HTML) or `tex4ebook -f epub3 bookW.tex "mathml"` (EPUB) compile the
   real LaTeX to a **single** `bookW.html` (tex4ht CSS) / a chunked `.epub`, math as native MathML.
4. **RESTYLE to the OpenStax house theme** (route a — see the task doc):
   - **HTML:** `tools/split_html.py` splits `bookW.html` at the `h2.chapterHead` boundaries into
     `index.html` + `NNN-<slug>.html` **per-chapter** pages (11: Preface + 10 chapters; the chapter's
     `h3.sectionHead` sections stay on the page as the right "On this page" bar), wraps each in the
     shared chunked-template layout, and synthesizes `sitemap.json`; then the **shared assets**
     (`osbook-web.css`, `osbook-web.js`, `build_nav.py`) — reused UNCHANGED from
     `../../openstax/tooling/tools/pandoc`, read via the `/osbook-assets` RO mount — apply the theme and
     inject the left book-TOC. `tools/trench-web.css` reconciles tex4ht's `bookW.css` with osbook-web.css.
   - **EPUB:** the tex4ebook epub is unzipped, `osbook-web.css`+`trench-web.css` are appended into its
     stylesheet, and it is repackaged (mimetype first + STORED).
   Output → `checkout/output/html/` (index.html + pages + `EPS-png/`) and `checkout/output/epub/bookW.epub`.

Gotchas that are load-bearing (do not undo):
- **`make4ht -u`, NOT `-um`.** `-m` takes a MODE argument, so `-um FILE` swallows `FILE` as the mode
  and treats `"mathml"` as the (missing) input file. `"mathml"` is make4ht's 2nd positional (the
  tex4ht.sty option), not a filename.
- **The theme assets are read via the `/osbook-assets` RO mount** (Makefile `FILES_TO_MOUNT`), not a
  vendored copy — single source of truth, no drift. A repo symlink into the sibling `openstax/` tree
  can't resolve (separate container mounts), so the mount is the working equivalent.
- **Figure `<img>` srcs are `EPS-png/*.png`** (make4ht graphicspath prefers PNG), so `build_web.sh` copies
  the PNGs to `output/html/EPS-png/` — the dir name must match the src, or figures 404.
- **`web_preprocess.py` and `normalize_master.py` strip both `\setcounter{chapter}{N}` and
  `\setcounter{section}{N}`** so chapters number 1–10 and every chapter's sections auto-number from .1
  (chapter 2 was 2.2–2.7, fixed to 2.1–2.6, 2026-09-19). The correct numbers come from `\newsection`'s
  first arg; auto-numbering matches it once the manual setters are gone.
- **`split_html.py` + `trench-web.css` restyle WITHOUT re-rendering math** — the MathML from make4ht is
  copied verbatim; only the page shell/CSS changes.
- **`pandoc-defs.tex` is what makes the whole book compile 0-error** — ~60 custom-macro definitions
  (2.09 math fonts, the missing counters, the ch2–10 matrix macros, bookmark no-ops, `\def\endproof{}`
  because `\newcommand` refuses `\end…` names). The `definition` env must NOT have a trailing `\ `
  after `#1` (the source writes `\begin{definition}\color{blue}…` unbraced). `\thissection` is defined
  by the body, so the defs must not define it.
- **EPUB needs `zip`+`tidy`** — added to `../../openstax/tooling/Dockerfile` (own layer). `zip` packs
  the `.epub`; `tidy` cleans the XHTML.
- **`over_to_frac.py` is not on the critical path** — make4ht compiles `\over` natively, so
  `web_preprocess.py --frac` is not passed. It's kept, validated, for a future pandoc/MathML path.

## Build

```
./fetch.sh        # pristine Trench source -> checkout/  (idempotent)
./apply.sh        # overlay osbook.cls (+ the phase-2 shim) onto checkout/
make image        # build the shared toolchain image once (from ../../openstax/tooling)
make pdf          # typeset the osbook-styled PDF          -> checkout/output/TRENCH_DIFFEQ-osbook.pdf
make html         # build the HTML web edition (Furo theme) -> checkout/output/html/index.html
make epub         # build the EPUB web edition (themed)      -> checkout/output/epub/bookW.epub
```

Nested podman: `PODMAN_RUN_FLAGS` auto-applies `--cgroups=disabled` under a `NESTED_PODMAN=1`
sandbox, empty on a normal host; threaded into every `run`, never `build`.
