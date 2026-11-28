# osbooks-physics — OpenStax Physics (imps)

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

`fetch.sh` pins **`56e71824e73e371c0d20eb68a77611aa438b5f89`**, the head of OpenStax's default branch
at the last sync (the pin moves at every sync; `fetch.sh` is the source of truth).
The port was first made against `cbf75cb4a18223a788868244be73affe932ef680` — the merge-base where the
maintainer's `latex` port branch diverged from OpenStax's `main` (the pristine
content the port was made against), from the survey table in
`tasks/archive/impo/2026/09/03/openstax-populate-books.md`. Canonical upstream:
`https://github.com/openstax/osbooks-physics`. Fallback, tried automatically by `fetch.sh` when the upstream does not
provide the pin: `https://github.com/billsix/osbooks-physics`, the maintainer's public mirror.

## This book (from the survey; build-time facts pending)

- **Delta size:** 904 port-branch files; **has os-embed exercises (downloads)**
  (per the `tasks/archive/impo/2026/09/03/openstax-populate-books.md` survey table).
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

Edit `../tooling/` once (shared by every book). Every build target here runs
`./apply.sh` first, so the next `make` picks the edit up. Do not edit the
generated LaTeX or the overlaid copies inside `checkout/` — a reconvert or a
re-apply overwrites them.
