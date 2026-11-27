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
  CNXML source + original figures). Fetched at a pinned commit by `fetch.sh`; **gitignored** in impo
  (never committed — it's OpenStax's, and the first sixteen books' figures alone were about 4.4 GB). It is
  **not** safe to say "it regenerates from the pin": `osbooks-algebra-1`'s upstream disappeared in
  2026-11. What keeps the source available is a **public mirror of each upstream repository under the
  maintainer's GitHub account** (`https://github.com/billsix/<name>`: unmodified, full history, upstream's
  `LICENSE` intact). `fetch.sh` tries the upstream first and the mirror second;
  `tools/mirror-upstreams.sh` updates the mirrors (`push`, the maintainer's) and checks that each holds
  its book's pin (`check`, anyone).
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
- **The OpenStax content is NOT the maintainer's**, and its licence is per book: whatever the book's own
  source declares, in each collection XML (`<md:license url="…">`) and in the upstream repository's
  `LICENSE` file. Read on 2026-11-26: **CC BY 4.0 for `osbooks-physics` and `osbooks-statistics`; CC BY-NC-SA
  4.0 for every other book folder** (table: `tasks/reference/openstax/book-inventory.md`). Until that date impo's
  docs said "CC BY 4.0" for all of it, which was wrong. The module files carry no licence metadata of their
  own, so a copy of the XML without its collection file and `LICENSE` is unmarked.
- **A built book is an adaptation and carries its source's licence.** The converter reads the licence from
  the collection XML (`licence_from_url` in `tools/cnxml2tex/convert.py`) and states it twice in every
  edition: on the class's licence page (`\setOSbooklicense`) and in the "About This Edition" colophon. A
  collection that declares no licence the converter knows fails the conversion.
- **Exercise caches:** each exercise's JSON names its copyright holders (Rice University in every file
  examined) and carries no licence field. OpenStax Exercises says many of its questions are under a
  Creative Commons Attribution licence and that each question has its own terms
  (https://exercises.openstax.org/copyright, read 2026-11-26). So the notice does not assert one licence.
- **Every committed download cache carries a `COPYRIGHT` NOTICE** at its root
  (`openstax/tooling/templates/exercises-COPYRIGHT` is the template `fetch_exercises` writes/keeps),
  saying whose the files are, where they came from and what is known about their terms. So no one
  browsing impo mistakes those blobs for the maintainer's.

## Per-book folder contract

`openstax/osbooks-<subject>/` holds only what is book-specific:

- `fetch.sh` — fetch the pinned OpenStax content into `checkout/` (gitignored). `UPSTREAM_URL`,
  `MIRROR_URL` (the maintainer's public backup, tried when the upstream does not provide the pin) and
  `PIN_SHA` live here; the pin is the upstream default-branch head at the last sync, or at the day the
  book was added. Sets `commit.gpgsign false` in the checkout (sandbox signing fails). Idempotent.
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

- `tools/cnxml2tex/convert.py` — CNXML + MathML (Presentation, and the Content dialect a few books mix
  in) → LaTeX; auto-discovers structure. Handles BOTH
  os-embed exercise schemes (`#exercise/<nickname>` and `#ost/api/ex/<id>` — physics/biology). Also emits an
  **"About This Edition" colophon** as the first front-matter unit (`\chapter*`, so it doesn't step the
  chapter counter) — impo link + build commit SHA/date (from `IMPO_COMMIT`/`IMPO_BUILD_DATE`, passed by each
  book Makefile's `IMPO_PROVENANCE`) + the licensing split (the book's own licence / MIT for the toolchain); it flows to all three editions
  via the shared master.
- `tools/cnxml2tex/fetch_exercises.py` — the redownload script (the one networked step); fetches by nickname or tag.
- `tools/cnxml2tex/crossbook.py` — links between books, emitted into the LaTeX by `convert.py`: "(IA x.y.z)"
  references become `\href`s, and math-ladder sections open with a reviewed "Prerequisites" box
  (`crossbook/prerequisites.txt`); targets resolve through the committed page index `crossbook/index/<book>.json`
  (written by `crossbook_index.py` from built sitemaps, OpenStax's own section numbers). Absolute URLs on the
  published site; `html.sh` makes them relative. Read `tasks/reference/tooling/cross-book-links.md` first.
- `tools/pandoc/` — the HTML/EPUB leg: `xref.lua` (cross-ref → numbered link rewrite), `preprocess.py`,
  `chunked-template.html` + `osbook-web.css` (the Furo-style layout), plus the web-edition nav — `build_nav.py`
  (injects the collapsible book TOC into each page at build time, from `sitemap.json`) and `osbook-web.js`
  (right "On this page" TOC + scrollspy + chapter/mobile toggles). `build_nav.py` also fills the "Downloads"
  box on each book's first page and the side-nav "Downloads" entry (GitHub Release assets);
  `site_files.py` lists the files a built site uses (for `<book>-html.zip`, which `html.sh` writes, and for the
  collected `output/<book>/`); `check_links.py` checks the local links of a directory of built sites.
  Publishing: `tasks/reference/openstax/publishing.md`.
- `tools/tests/` — converter unit tests (`make test`).
- `tools/check_local_annotations.py` — AST checker enforcing the house rule that every LOCAL and
  MODULE-LEVEL variable in `tools/*.py` carries an explicit annotation (`ty`/ruff only cover signatures).
  Ported from github.com/billsix/modelviewprojection. Part of the gate (below); do not add un-annotated
  `name = …` bindings to the tooling or the build fails. History: the one-time sweep is archived at
  `tasks/archive/impo/2026/09/20/annotate-tooling-python-types.md`.
- `latex/osbook.cls`, `osbook-envs.sty`, `osbook-defer.sty` — the house document class + pedagogical
  environments + per-chapter exercise numbering / answer key. Front-matter metadata setters:
  `\setOSbooktitle`/`\setOSbooksubtitle`/`\setOSbookversion`, plus (added 2026-09-19,
  backward-compatible) `\setOSbooklicense`/`\setOSbookdedication`/`\setOSbookpublisher` — defaults
  reproduce the OpenStax CC BY-NC-SA 4.0 page, so books that don't call them are unchanged; the
  sibling `trench/` family overrides them for a CC BY-NC-SA 3.0 book.
- **Per-book theme override (optional):** a book may ship `bookstyle.tex` (PDF font/palette, loaded by
  `osbook.cls` via `\InputIfFileExists{osbook-bookstyle.tex}`) and/or `bookstyle-web.css` (HTML/EPUB, appended to
  `osbook-web.css` so its `:root` wins); `apply.sh` copies both into the checkout. Default is Roboto-Slab + teal;
  **calculus** ships both (TeX Gyre Termes + navy). No-op for books without them.
- `entrypoint/*.sh` — `convert`/`pdf`/`html`/`epub`/`fetch-exercises`/`shell`/`format` (all use `/book`),
  plus `check-tools.sh` — the read-only gate (ruff check + the annotation checker + `ty check` + pytest)
  run BOTH by the Dockerfile build gate and the GitHub CI workflow (`.github/workflows/checks.yml`), so the
  two can't drift. `make format` runs the annotation checker too (after its ruff `--fix`/`ty`).
- **`openstax/tooling/Makefile`** — the toolchain's own Makefile (separate from the per-book ones): `make
  type-check` (alias `check`) builds a LEAN image (`WITH_TEXLIVE=0`, no TeX Live — fast) and runs
  `check-tools.sh` in it; `make shell`/`shell-exec` open the toolchain image. CI wraps `make type-check`.
  The `Dockerfile`'s `WITH_TEXLIVE` build-arg (default 1) gates the TeX Live/font/rsvg layer so the gate can
  build without it. Modeled on github.com/billsix/modelviewprojection.
- `Dockerfile` — Fedora 45 + TeX Live + `python3-lxml` + pandoc + `rsvg-convert` (+ `zip`/`tidy` in a
  separate layer, used only by the sibling `trench/` family's make4ht/tex4ebook web editions — inert
  for the OpenStax books).
- `pyproject.toml`, `templates/exercises-COPYRIGHT`.

**Changing the toolchain:** edit it here once; each book picks it up on its next `apply.sh`. This is
the whole reason it's shared — one place to maintain the converter and the house style.

**Reference docs** (`tasks/reference/tooling/`, read before touching the toolchain): **`converters.md`** — the
converter landscape (the 5 historical per-book converter versions merged into one, gap analysis);
**`cross-references.md`** — how cross-refs become links (PDF cleveref / HTML xref.lua), and why literal-text
internal references can't be reliably auto-linked; **`cross-book-links.md`** — links between books (the IA
references, the Prerequisites boxes, the page index and its official-numbering rule); and **`web-editions-mobile.md`** — the web theme's
mobile/responsive layer (osbook-web.css/.js): the apply.sh-before-build propagation trap, the MathML
horizontal-overflow root cause + fix, the drawer/on-this-page behaviour, and how to verify with a real
headless browser (read before touching osbook-web.css/.js).

## Adding a book

1. `bash tools/add-book.sh <name> "<Title>"` (from the repo root; `<name>` without the `osbooks-`
   prefix). It creates `openstax/osbooks-<name>/` from `tools/book-template/`: `fetch.sh` pinned at the
   upstream default-branch head with the mirror fallback, `apply.sh`, `Makefile`, `README.md`,
   `CLAUDE.md`, `.gitignore`. Change a template, not a generated folder, when the pattern changes.
2. In the new folder: `./fetch.sh && ./apply.sh`, then `make convert` and `make dist`. Count the embedded
   exercise links in the CNXML in **both** schemes (`#exercise/<nickname>`, `#ost/api/ex/<id>`); if there
   are any, the maintainer runs `make fetch-exercises` (it identifies itself with his contact address) and
   `exercises/` is committed **with its COPYRIGHT NOTICE**.
3. Record the book: "The books this folder builds" in its `CLAUDE.md`, the list below, the inventory and
   its licence table (`tasks/reference/openstax/book-inventory.md`), and refresh the survey
   (`python3 tools/survey-upstream-books.py`).
4. The maintainer adds it to his public backups (`tools/mirror-upstreams.sh push <name>`).

## Books

One thin `openstax/osbooks-<subject>/` folder per book (24 total; more are being added, see
`tasks/openstax-add-remaining-english-books.md`); each carries its own `CLAUDE.md`
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
- `osbooks-biology-bundle/` — Biology (3 books: `biology-2e`, `biology-ap-courses-2e`, `concepts-biology`)
- `osbooks-chemistry-bundle/` — Chemistry
- `osbooks-calculus-bundle/` — Calculus (Times + navy theme)
- `osbooks-college-algebra-bundle/` — College Algebra
- `osbooks-prealgebra-bundle/` — Prealgebra (4 books: `prealgebra-2e`, `elementary-algebra-2e`,
  `intermediate-algebra-2e`, `healthcare-foundations`)
- `osbooks-university-physics-bundle/` — University Physics
- `osbooks-microbiology/` — Microbiology
- `osbooks-psychology/` — Psychology
- `osbooks-statistics/` — Statistics (added 2026-11-26)
- `osbooks-introductory-statistics-bundle/` — Introductory Statistics (2 books: `introductory-statistics-2e`,
  `introductory-business-statistics-2e`; added 2026-11-26)
- `osbooks-college-physics-bundle/` — College Physics (2 books: `college-physics-2e`,
  `college-physics-ap-courses-2e`; added 2026-11-26)
- `osbooks-business-law/` — Business Law I Essentials 2e (added 2026-11-27)
- `osbooks-additive-manufacturing/` — Additive Manufacturing Essentials (added 2026-11-27)
- `osbooks-life-liberty-and-pursuit-happiness/` — Life, Liberty, and the Pursuit of Happiness (added 2026-11-27)
- `osbooks-us-history/` — U.S. History (added 2026-11-27)
- `osbooks-american-government/` — American Government 4e (added 2026-11-27)

Per-book status (build-verified dates, exercise/image counts, os-embed scheme post-mortems, structural
facts): `tasks/reference/openstax/book-inventory.md`. Figure format + os-embed scheme + exercise counts
also in `tasks/reference/tooling/converters.md` (per-book quick reference).
