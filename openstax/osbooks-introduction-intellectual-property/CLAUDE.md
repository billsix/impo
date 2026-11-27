# osbooks-introduction-intellectual-property — OpenStax Introduction to Intellectual Property (impo)

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

`fetch.sh` pins **`6dad5479f5a7974df9a2dcb01f4ce9a970658029`**, the head of OpenStax's default branch
when the book was added (2026-11-27). The pin moves at every sync; `fetch.sh` is the source
of truth. Canonical upstream: `https://github.com/openstax/osbooks-introduction-intellectual-property`. Fallback, tried
automatically by `fetch.sh` when the upstream does not provide the pin:
`https://github.com/billsix/osbooks-introduction-intellectual-property`, the maintainer's public mirror.

## The books this folder builds

One collection, `introduction-intellectual-property` (OpenStax *Introduction to Intellectual Property*): 54 modules in 5 chapters; one level of nesting. Built as PDF (233 pages), EPUB and HTML
(61 web pages) on 2026-11-27, the day it was added.

- **Licence:** CC BY 4.0 (collection XML and upstream `LICENSE`).
- **Exercises:** 185 embedded links to 185 exercises, all in the `#exercise/<nickname>`
  scheme. All 185 are in the committed cache `exercises/` (no images; with its `COPYRIGHT`
  notice), fetched by the maintainer on 2026-11-27, and are in the built book.
- **Figures:** raster only (191 files, 42 MB); no SVG.
- **Block quotations:** 31, set off as such.
- **Embedded frames:** 9 point at outside pages (simulations, videos). Each is a labelled link in all
  three editions (`../../tasks/reference/tooling/converters.md`, "Outside pages embedded in frames").
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

Edit `../tooling/` once (shared by every book), then re-run `./apply.sh` here to
pick it up. Do not edit the generated LaTeX or the overlaid copies inside
`checkout/` — a reconvert or a re-apply overwrites them.
