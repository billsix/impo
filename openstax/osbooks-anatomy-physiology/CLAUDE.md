# osbooks-anatomy-physiology — OpenStax Anatomy & Physiology 2e (imps pilot book)

The **pilot** for the imps OpenStax family's shared-toolchain contract. Read the family
doc `../CLAUDE.md` first (the fetch → apply-overlay → build model, the content/copyright
rules) and the shared toolchain it points at, `../tooling/`. This file records only what is
specific to *this book*.

## What lives here (thin per-book folder)

This folder carries **no** OpenStax content and **no** toolchain — both are pulled in on
demand:

- `fetch.sh` — clones the pinned pristine OpenStax content into `checkout/` (gitignored).
- `apply.sh` — overlays `../tooling/` onto `checkout/` (copies `tools/`, `latex/` house
  `.cls`/`.sty`, `entrypoint/`, `pyproject.toml`, `templates/` beside the CNXML).
- `Makefile` — builds the image from `../tooling/Dockerfile` (context `../tooling`) and runs
  it against `checkout/` mounted at the fixed path `/book`.
- `README.md`, `.gitignore`.

The whole build product regenerates from the pin + the shared toolchain, so nothing under
`checkout/` (content, overlaid toolchain, generated LaTeX, `output/`) is committed.

## The pin

`fetch.sh` pins **`716383a4c6c16037b14d75a156c65145e75e895e`** — the merge-base where the
maintainer's `latex` port branch diverged from OpenStax's `main`, i.e. the pristine content
the port was made against. It is `main`/`HEAD` of the canonical repo
`https://github.com/openstax/osbooks-anatomy-physiology`, verified fetchable there
(`git ls-remote`, 2026-09-02). Fallback mirror if GitHub is unreachable:
`pi@192.168.0.186:/mnt/usbdrive2/gitRepos/openstax/science/osbooks-anatomy-physiology.git`.

## This book (facts that shape the port)

- **Single-collection** → the converter emits **one** master
  (`checkout/latex/anatomy-and-physiology-2e.tex`) from
  `collections/anatomy-and-physiology-2e.collection.xml`.
- **Subcollection nesting: two levels** → `\chapter`/`\section`/`\subsection`. `convert.py`
  auto-detects the depth (`_max_subcol_depth()`); nesting is the main structural risk, so
  spot-check one chapter's sectioning before trusting a bulk convert.
- **No `os-embed` exercises** → `make fetch-exercises` is a no-op; the target exists only for
  parity with books that have them. There is no committed `exercises/` cache here.
- **Raster figures (jpg/png)** → `pdflatex` and `pandoc` embed these directly, so **no
  SVG→PDF/PNG rasterization step runs** for this book (the SVG paths in the toolchain scripts
  are guarded and simply find nothing to convert).
- **Target size:** ~1849 pp (6 chapters, 28 sections, ~198 modules), 0 LaTeX errors / 0
  undefined references at the pin (per the maintainer's original port). Cheat sheets are out
  of scope.

## Build

```
./fetch.sh        # pristine OpenStax content -> checkout/  (idempotent)
./apply.sh        # overlay ../tooling/ onto checkout/      (idempotent)
make image        # build the shared toolchain image once
make dist         # PDF + EPUB + chunked HTML  (convert runs as needed)
# or individually: make convert | pdf | html | epub
```

`pdf`/`html`/`epub` depend on the `checkout/latex/.converted` stamp, so they auto-run the
converter when the CNXML changed — you never run `make convert` by hand. Nested podman:
`PODMAN_RUN_FLAGS` auto-applies `--cgroups=disabled` when driven from a `NESTED_PODMAN=1`
sandbox and is empty on a normal host; it is threaded into every `run`, never `build`.

## Changing the toolchain

Edit `../tooling/` once (it is shared by every book), then re-run `./apply.sh` here to pick
it up. Do not edit the generated LaTeX or the overlaid copies inside `checkout/` — a
reconvert or a re-apply overwrites them.
