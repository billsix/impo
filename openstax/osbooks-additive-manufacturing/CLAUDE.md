# osbooks-additive-manufacturing — OpenStax Additive Manufacturing Essentials (impo)

An impo OpenStax-family book on the shared-toolchain contract. Read the family
doc [`../CLAUDE.md`](../CLAUDE.md) first (the fetch → apply-overlay → build model,
the content/copyright rules) and the shared toolchain it points at,
[`../tooling/`](../tooling). This file records only what is specific to *this book*.

## What lives here (thin per-book folder)

No OpenStax content and no toolchain are committed — both are pulled in on demand:

- `fetch.sh` — fetches the pinned pristine OpenStax content into `checkout/` (gitignored).
- `apply.sh` — overlays `../tooling/` onto `checkout/` (and copies a committed
  `exercises/` cache in, if this book has one).
- `Makefile` — builds the image from `../tooling/Dockerfile` (context `../tooling`) and
  runs it against `checkout/` mounted at the fixed path `/book`.
- `README.md`, `.gitignore`.

## The pin

`fetch.sh` pins **`461b9c36ac439a4797fbfe2e41d8f9b1dbf90610`**, the head of OpenStax's default branch
when the book was added (2026-11-27). The pin moves at every sync; `fetch.sh` is the source
of truth. Canonical upstream: `https://github.com/openstax/osbooks-additive-manufacturing`. Fallback, tried
automatically by `fetch.sh` when the upstream does not provide the pin:
`https://github.com/billsix/osbooks-additive-manufacturing`, the maintainer's public mirror.

## The books this folder builds

One collection, `additive-manufacturing-essentials` (OpenStax *Additive Manufacturing Essentials*): 42 modules in 8 chapters, from "Fundamentals of Additive Manufacturing" to "The Business of Additive Manufacturing"; one level of nesting. Built as PDF (259 pages), EPUB and HTML
(52 web pages) on 2026-11-27, the day it was added.

- **Licence:** CC BY-NC-SA 4.0 (collection XML and upstream `LICENSE`).
- **Exercises:** 122 embedded links to 120 exercises (2 of the links repeat an exercise), all in the `#exercise/<nickname>`
  scheme. All 120 are in the committed cache `exercises/` (no images; with its `COPYRIGHT`
  notice), fetched by the maintainer on 2026-11-27, and are in the built book.
- **Figures:** raster only (70 files, 20 MB); no SVG.
- **Still falling back** (the converter's report): none.

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
