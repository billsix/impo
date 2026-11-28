# osbooks-life-liberty-and-pursuit-happiness — OpenStax Life, Liberty, and the Pursuit of Happiness (impo)

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

`fetch.sh` pins **`acb6fbe2744dd112187b6aff5946cfe969410fca`**, the head of OpenStax's default branch
when the book was added (2026-11-27). The pin moves at every sync; `fetch.sh` is the source
of truth. Canonical upstream: `https://github.com/openstax/osbooks-life-liberty-and-pursuit-happiness`. Fallback, tried
automatically by `fetch.sh` when the upstream does not provide the pin:
`https://github.com/billsix/osbooks-life-liberty-and-pursuit-happiness`, the maintainer's public mirror.

## The books this folder builds

One collection, `life-liberty-and-pursuit-happiness` (OpenStax *Life, Liberty, and the Pursuit of Happiness*): 532 modules in 16 chapters grouped into 8 units by period, from "1491–1763" to "1980–Present"; two levels of nesting. Built as PDF (3,360 pages), EPUB and HTML
(26 web pages) on 2026-11-27, the day it was added.

- **Licence:** CC BY 4.0 (collection XML and upstream `LICENSE`).
- **Exercises:** 1,896 embedded links to 1,895 exercises (1 of the links repeat an exercise), all in the `#exercise/<nickname>`
  scheme. All 1,895 are in the committed cache `exercises/` (95 images; with its `COPYRIGHT`
  notice), fetched by the maintainer on 2026-11-27, and are in the built book.
- **Figures:** raster only (893 files, 331 MB); no SVG.
- **Web edition:** 26 pages for 532 modules. With two levels of nesting the HTML is split per chapter, as in the other unit-nested books (Biology 2e: 57 pages), so each page is long.
- **Embedded frames:** 33 point at outside pages (simulations, videos). Each is a labelled link in all
  three editions (`../../tasks/reference/tooling/converters.md`, "Outside pages embedded in frames").
- **Still falling back** (the converter's report): `inline:label` (32).

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
