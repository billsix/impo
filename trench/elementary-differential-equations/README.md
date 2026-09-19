# Trench *Elementary Differential Equations* — LaTeX restyle (impo)

A restyle of William F. Trench's open-source **Elementary Differential Equations** into the same
house look as the impo OpenStax books, built on the pinned pristine LaTeX source with the shared
toolchain in [`../../openstax/tooling/`](../../openstax/tooling). See [`../CLAUDE.md`](../CLAUDE.md)
for the `trench/` family model and [`CLAUDE.md`](./CLAUDE.md) for this book's facts.

All three editions build: the osbook-styled **PDF**, and the **HTML** + **EPUB** web editions (native
MathML). Plans: [`../../tasks/archive/impo/2026/09/19/add-trench-differential-equations-book.md`](../../tasks/archive/impo/2026/09/19/add-trench-differential-equations-book.md)
(PDF), [`../../tasks/archive/impo/2026/09/19/trench-differential-equations-html-epub.md`](../../tasks/archive/impo/2026/09/19/trench-differential-equations-html-epub.md)
(web).

## Build

```sh
./fetch.sh        # [HOST] clone pinned Trench LaTeX source into checkout/  (gitignored)
./apply.sh        # [HOST] overlay the OpenStax house style (+ shim) onto checkout/
make image        # build the shared toolchain container image once
make pdf          # typeset the osbook-styled PDF        -> checkout/output/TRENCH_DIFFEQ-osbook.pdf
make html         # build the HTML web edition (themed)  -> checkout/output/html/index.html
make epub         # build the EPUB web edition (themed)  -> checkout/output/epub/bookW.epub
make help         # list all targets
```

The web editions (`html`/`epub`) take a **separate** path from the PDF: they feed the *pristine*
`TRENCH_DIFFEQ.tex` through `tools/web_preprocess.py` into a simple `book`-class `bookW.tex` that
**make4ht/tex4ebook** compile (real LaTeX, math as MathML) — they do not use `osbook.cls`. The HTML is
then **chunked and restyled to the OpenStax house theme** (`tools/split_html.py` + the shared
`osbook-web.css`/`osbook-web.js`/`build_nav.py`, read from `../../openstax/tooling/tools/pandoc`): a
navigable per-chapter site (left bar = chapters, right "On this page" bar = that chapter's sections),
teal palette, and Prev/Next. Both reuse the phase-3
figures (`make figures`, run automatically). See the book [`CLAUDE.md`](./CLAUDE.md) for the pipeline
and its gotchas.

Nested podman: `PODMAN_RUN_FLAGS` auto-applies `--cgroups=disabled` inside a `NESTED_PODMAN=1`
sandbox and expands empty on a normal host.

## Content & license

The Trench source (the `.tex` masters, `wtrench.sty`, `EPS/`) is fetched at a pin into `checkout/`
and is **not** part of this repository — it is © William F. Trench, **CC BY-NC-SA 3.0** (AIM Open
Textbook Initiative), sourced from <https://github.com/billsix/differentialEquationsTrench>. The
restyle toolchain (the shim + the shared `../../openstax/tooling/`) is the maintainer's, MIT (see the
repo `LICENSE`). Design details: [`../CLAUDE.md`](../CLAUDE.md).
