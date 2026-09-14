# OpenStax — LaTeX ports of OpenStax textbooks, under impo

This is the sole family in **impo** (see the repo-root `../CLAUDE.md`). It carries the maintainer's
**hand-owned LaTeX/PDF/EPUB/HTML port toolchain** for OpenStax open textbooks, on top of pristine,
pinned OpenStax content — the same idea as impo's sibling **imps** (the N64 PC-ports carrier), but for
books instead of games. One folder per book (`osbooks-<subject>/`), plus a **single shared toolchain**
at `openstax/tooling/` (see below).

## How this family differs from N64 (read this first)

1. **All personal, never upstreamed.** A LaTeX conversion is not something OpenStax would merge, so —
   unlike the N64 family's "upstreaming is the goal" ranking — there is **no upstream-submission
   tier** here. Every change is a permanent personal patch, replayed onto newer OpenStax content
   pins over time.
2. **The delta is a SHARED toolchain, not a per-book patch series.** One book-agnostic converter
   (`convert.py` auto-detects nesting; generated LaTeX is never hand-edited), hoisted so each book
   folder stays thin. It is a **feature-detecting superset** merging the 5 historical per-book
   converter versions — history, the divergences, and unification gaps:
   `tasks/reference/tooling/converters.md`.
3. **"apply" = overlay the shared toolchain, not `git am`.** Because the delta is a shared file set
   (not upstream-code hunks), a book's `apply.sh` **copies `../tooling/` onto the fetched upstream
   checkout** rather than replaying patches. Everything else (fetch a pinned pristine upstream, build
   from the applied checkout, gitignore the checkout) is the same imps/impo carrier shape.

## The content model — downloaded → commit; generated → ignore

(The maintainer's own policy, lifted from the book repos into the family contract.)

- **Pinned upstream = the OpenStax content** — a book's `collections/`, `modules/`, `media/` (the
  CNXML source + original figures). Cloned at a pinned commit by `fetch.sh`; **gitignored** in imps
  (never committed — it's OpenStax's, and it regenerates from the pin).
- **The toolchain (`openstax/tooling/`)** — the maintainer's converter, LaTeX document class +
  style, pandoc templates, entrypoint scripts, container build, and tests. Committed once.
- **Downloaded content → committed cache.** Some books embed `os-embed` practice exercises;
  `tooling/tools/cnxml2tex/fetch_exercises.py` pulls them (questions only — the API withholds answer
  keys) into a book's `exercises/` cache (JSON + localized images under `exercises/media/`). This is
  the **one networked step**; it is run occasionally and its output is **committed like source**, so
  a build never touches the network and *a book always has all of its content* (offline-reproducible,
  even if OpenStax's servers are down). Re-run `make fetch-exercises` to refresh.
- **Generated → gitignored.** The converter's `latex/*.tex` masters + `latex/sections/`, the SVG→PDF
  rasterizations, and everything under `output/` are build artifacts — regenerated from committed
  source, never committed.

## Copyright / licensing (IMPORTANT — mark it clearly)

The two layers have two different owners, and imps must not blur them:

- **The toolchain is the maintainer's** — MIT, like the rest of impo (see `../LICENSE`).
- **The OpenStax content is NOT the maintainer's.** The pinned CNXML/`media`, **and any downloaded
  `exercises/` (problem sets) and their images, are © OpenStax and the respective authors, licensed
  CC BY 4.0** — carried here for reproducibility, not authored here. This mirrors imps' README note
  that upstream fragments in `patches/` stay under the upstream license.
- **Every committed download cache carries a `COPYRIGHT` NOTICE** at its root
  (`openstax/tooling/templates/exercises-COPYRIGHT` is the template `fetch_exercises` writes/keeps):
  "© OpenStax, licensed CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/); sourced from
  https://openstax.org — not owned by this repository's maintainer." So no one browsing imps mistakes
  those blobs for the maintainer's.

## Per-book folder contract

`openstax/osbooks-<subject>/` holds only what is book-specific:

- `fetch.sh` — clone the pinned OpenStax content into `checkout/` (gitignored); the upstream URL +
  `PIN_SHA` (the commit the maintainer's port was made against) live here, SHA commented with its
  date. Sets `commit.gpgsign false` in the checkout (sandbox signing fails). Idempotent.
- `apply.sh` — overlay `../tooling/` onto `checkout/` (the "apply" step; see above). Guarded/idempotent.
- `build.sh` / `Makefile` — the container build: `make image` (from `../tooling/Dockerfile`), then
  `make convert`/`pdf`/`html`/`epub`/`dist` running the toolchain against `checkout/` mounted at the
  fixed path `/book`. `PODMAN_RUN_FLAGS` threaded into every `run` (never `build`), per the sandbox
  nested-podman convention.
- `exercises/` — the committed download cache **+ its `COPYRIGHT` NOTICE**, for books that have
  `os-embed` exercises (many don't — e.g. anatomy-physiology has none).
- `CLAUDE.md` — this book's facts (single- vs multi-collection, nesting depth, whether it has
  exercises, figure format, page count / build status) and a pointer to the shared toolchain.
- `README.md` — commands-forward: fetch → apply → `make dist`.
- `.gitignore` — `checkout/`, `output/`, generated `latex/*.tex`+`latex/sections/`, and the
  rasterized `*-derived`/`*.pdf` figures.

## The shared toolchain (`openstax/tooling/`)

Book-agnostic; the book is always mounted at the fixed path **`/book`** so nothing hardcodes a slug.

- `tools/cnxml2tex/convert.py` — CNXML + Presentation-MathML → LaTeX; auto-discovers structure. Handles BOTH
  os-embed exercise schemes (`#exercise/<nickname>` and `#ost/api/ex/<id>` — physics/biology).
- `tools/cnxml2tex/fetch_exercises.py` — the redownload script (the one networked step); fetches by nickname or tag.
- `tools/pandoc/` — the HTML/EPUB leg: `xref.lua` (cross-ref → numbered link rewrite), `preprocess.py`,
  `chunked-template.html` + `osbook-web.css` (the Furo-style layout), plus the web-edition nav — `build_nav.py`
  (injects the collapsible book TOC into each page at build time, from `sitemap.json`) and `osbook-web.js`
  (right "On this page" TOC + scrollspy + chapter/mobile toggles).
- `tools/tests/` — converter unit tests (`make test`).
- `latex/osbook.cls`, `osbook-envs.sty`, `osbook-defer.sty` — the house document class + pedagogical
  environments + per-chapter exercise numbering / answer key.
- **Per-book theme override (optional):** a book may ship `bookstyle.tex` (PDF font/palette, loaded by
  `osbook.cls` via `\InputIfFileExists{osbook-bookstyle.tex}`) and/or `bookstyle-web.css` (HTML/EPUB, appended to
  `osbook-web.css` so its `:root` wins); `apply.sh` copies both into the checkout. Default is Roboto-Slab + teal;
  **calculus** ships both (TeX Gyre Termes + navy). No-op for books without them.
- `entrypoint/*.sh` — `convert`/`pdf`/`html`/`epub`/`fetch-exercises`/`shell`/`format` (all use `/book`).
- `Dockerfile` — Fedora 44 + TeX Live + `python3-lxml` + pandoc + `rsvg-convert`.
- `pyproject.toml`, `templates/exercises-COPYRIGHT`.

**Changing the toolchain:** edit it here once; each book picks it up on its next `apply.sh`. This is
the whole reason it's shared — one place to maintain the converter and the house style.

**Reference docs** (`tasks/reference/tooling/`, read before touching the toolchain): **`converters.md`** — the
converter landscape (the 5 historical per-book converter versions merged into one, gap analysis); and
**`cross-references.md`** — how cross-refs become links (PDF cleveref / HTML xref.lua), and why literal-text
internal references can't be reliably auto-linked.

## Adding a book

1. `mkdir openstax/osbooks-<subject>`; write `fetch.sh` with the upstream URL + the pin (the
   merge-base where the maintainer's `latex` branch diverged from OpenStax's `main`).
2. `apply.sh` overlays `../tooling/`; `Makefile`/`README`/`CLAUDE.md` from the anatomy-physiology
   template.
3. `make dist` to build; if the book has `os-embed` exercises, `make fetch-exercises` once and commit
   `exercises/` **with its COPYRIGHT NOTICE**.

## Books

One thin `openstax/osbooks-<subject>/` folder per book (16 total); each carries its own `CLAUDE.md`
with its pin and book-specific facts. **anatomy-physiology** is the pilot for this family's
shared-toolchain contract.

- `osbooks-anatomy-physiology/` — Anatomy & Physiology 2e (pilot)
- `osbooks-astronomy/` — Astronomy 2e
- `osbooks-algebra-1/` — Algebra 1
- `osbooks-organic-chemistry/` — Organic Chemistry
- `osbooks-contemporary-mathematics/` — Contemporary Mathematics
- `osbooks-introduction-python-programming/` — Introduction to Python Programming
- `osbooks-writing-guide/` — Writing Guide
- `osbooks-physics/` — Physics
- `osbooks-biology-bundle/` — Biology (3 volumes)
- `osbooks-chemistry-bundle/` — Chemistry
- `osbooks-calculus-bundle/` — Calculus (Times + navy theme)
- `osbooks-college-algebra-bundle/` — College Algebra
- `osbooks-prealgebra-bundle/` — Prealgebra
- `osbooks-university-physics-bundle/` — University Physics
- `osbooks-microbiology/` — Microbiology
- `osbooks-psychology/` — Psychology

Per-book status (build-verified dates, exercise/image counts, os-embed scheme post-mortems, structural
facts): `tasks/reference/openstax/book-inventory.md`. Figure format + os-embed scheme + exercise counts
also in `tasks/reference/tooling/converters.md` (per-book quick reference).
