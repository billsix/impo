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
2. **The delta is a SHARED toolchain, not a per-book patch series.** The maintainer's converter is
   fully automatic and **book-agnostic** (`convert.py` auto-detects a book's subcollection nesting;
   `fetch_exercises.py` is bundle-agnostic; the generated LaTeX is never hand-edited). Surveyed
   2026-09-02: across all 16 books the toolchain file-set is identical and the core files
   (`convert.py`, `fetch_exercises.py`, `osbook.cls`) are **byte-identical**; the only per-book
   variation was the hardcoded book slug in three scripts. So the toolchain is hoisted to
   `openstax/tooling/` **once** and each book folder is thin — carrying 16 near-identical copies as
   patches would be a maintenance smell.
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

- `tools/cnxml2tex/convert.py` — CNXML + Presentation-MathML → LaTeX; auto-discovers structure.
- `tools/cnxml2tex/fetch_exercises.py` — the redownload script (the one networked step).
- `tools/pandoc/` — templates + `xref.lua` + web CSS (HTML/EPUB editions).
- `tools/tests/` — converter unit tests (`make test`).
- `latex/osbook.cls`, `osbook-envs.sty`, `osbook-defer.sty` — the house document class + pedagogical
  environments + per-chapter exercise numbering / answer key.
- `entrypoint/*.sh` — `convert`/`pdf`/`html`/`epub`/`fetch-exercises`/`shell`/`format` (all use `/book`).
- `Dockerfile` — Fedora 44 + TeX Live + `python3-lxml` + pandoc + `rsvg-convert`.
- `pyproject.toml`, `templates/exercises-COPYRIGHT`.

**Changing the toolchain:** edit it here once; each book picks it up on its next `apply.sh`. This is
the whole reason it's shared — one place to maintain the converter and the house style.

## Adding a book

1. `mkdir openstax/osbooks-<subject>`; write `fetch.sh` with the upstream URL + the pin (the
   merge-base where the maintainer's `latex` branch diverged from OpenStax's `main`).
2. `apply.sh` overlays `../tooling/`; `Makefile`/`README`/`CLAUDE.md` from the anatomy-physiology
   template.
3. `make dist` to build; if the book has `os-embed` exercises, `make fetch-exercises` once and commit
   `exercises/` **with its COPYRIGHT NOTICE**.

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
- `osbooks-physics/` — **no `os-embed` exercises** (0 nicknames → no exercise cache); large delta is
  upstream `media/` figures. Likewise `osbooks-college-algebra-bundle/`, `osbooks-prealgebra-bundle/`,
  `osbooks-calculus-bundle/` (all 0 os-embed → no caches).
- `osbooks-introduction-python-programming/` — **has committed exercises cache** (613 questions,
  no images; convert → `introduction-python-programming.tex`, 115 modules).
- `osbooks-algebra-1/` — **committed exercise cache** (932 JSON + 288 images) with `COPYRIGHT`, plus
  SVG figures (convert → `algebra-1.tex`, 976 modules).
- `osbooks-organic-chemistry/`, `osbooks-contemporary-mathematics/` — **committed exercise caches**
  (organic-chemistry 1959 JSON + 2076 images; contemporary-mathematics 3073 JSON + 578 images), each
  with its `COPYRIGHT` NOTICE (green-lit + fetched 2026-09-02 — see `tasks/openstax-populate-books.md`).
- `osbooks-biology-bundle/` — large *figure* book but **no `os-embed` exercises** (0 nicknames → no
  exercise cache); its large delta is upstream `media/` figures, not downloadable practice exercises.
