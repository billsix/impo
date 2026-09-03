# osbooks-calculus-bundle — OpenStax Calculus (bundle) (imps)

An imps OpenStax-family book on the shared-toolchain contract. Read the family
doc [`../CLAUDE.md`](../CLAUDE.md) first (the fetch → apply-overlay → build model,
the content/copyright rules) and the shared toolchain it points at,
[`../tooling/`](../tooling). This file records only what is specific to *this book*.

## What lives here (thin per-book folder)

No OpenStax content and no toolchain are committed — both are pulled in on demand:

- `fetch.sh` — clones the pinned pristine OpenStax content into `checkout/` (gitignored).
- `apply.sh` — overlays `../tooling/` onto `checkout/` (and copies a committed
  `exercises/` cache in, if this book has one).
- `Makefile` — builds the image from `../tooling/Dockerfile` (context `../tooling`) and
  runs it against `checkout/` mounted at the fixed path `/book`.
- `README.md`, `.gitignore`.

## The pin

`fetch.sh` pins **`9b6c28b21c723a10ac045bad22b34377b3ff3f89`** — the merge-base where the
maintainer's `latex` port branch diverged from OpenStax's `main` (the pristine
content the port was made against), from the survey table in
`tasks/openstax-populate-books.md`. Canonical upstream:
`https://github.com/openstax/osbooks-calculus-bundle`. Fallback mirror if GitHub is
unreachable: `pi@192.168.0.186:/mnt/usbdrive2/gitRepos/openstax/**/osbooks-calculus-bundle.git`.

## This book (from the survey; build-time facts pending)

- **Delta size:** 53 port-branch files; **small download cache**
  (per the `tasks/openstax-populate-books.md` survey table).
- **No `os-embed` exercises** (0 in both schemes — confirmed 2026-09-03); 3 collection masters
  (calculus-volume-1/2/3).
- **Ships a per-book theme override:** `bookstyle.tex` (PDF: `\setmainfont{TeX Gyre Termes}` + a navy palette)
  and `bookstyle-web.css` (HTML/EPUB: the same navy `:root` + Times body). These restore the maintainer's
  calculus look over the default Roboto-Slab + teal; the shared `osbook.cls`/`html.sh`/`epub.sh` load them via
  the per-book theme hook (see `../CLAUDE.md`). Edit these here for calculus styling — not the shared toolchain.
- **Book specifics — single- vs multi-collection, subcollection nesting depth,
  whether `os-embed` exercises are actually present, and SVG vs raster figures —
  are verified on the first build**, not asserted here. The converter auto-detects
  collection structure and nesting; only the *downloaded* exercise images (not
  upstream `media/` figures) belong in a committed `exercises/` cache.

## Build

```
./fetch.sh        # pristine OpenStax content -> checkout/  (idempotent)
./apply.sh        # overlay ../tooling/ onto checkout/      (idempotent)
make image        # build the shared toolchain image once
make dist         # PDF + EPUB + chunked HTML  (convert runs as needed)
```

`pdf`/`html`/`epub` depend on the `checkout/latex/.converted` stamp, so the
converter auto-runs when the CNXML changed. Nested podman: `PODMAN_RUN_FLAGS`
auto-applies `--cgroups=disabled` under a `NESTED_PODMAN=1` sandbox, empty on a
normal host; threaded into every `run`, never `build`.

## Changing the toolchain

Edit `../tooling/` once (shared by every book), then re-run `./apply.sh` here to
pick it up. Do not edit the generated LaTeX or the overlaid copies inside
`checkout/` — a reconvert or a re-apply overwrites them.
