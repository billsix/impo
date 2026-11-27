# osbooks-us-history — OpenStax U.S. History (impo)

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

`fetch.sh` pins **`c05b860a035ff59a2ca1fd44339ef86694e09b57`**, the head of OpenStax's default branch
when the book was added (2026-11-27). The pin moves at every sync; `fetch.sh` is the source
of truth. Canonical upstream: `https://github.com/openstax/osbooks-us-history`. Fallback, tried
automatically by `fetch.sh` when the upstream does not provide the pin:
`https://github.com/billsix/osbooks-us-history`, the maintainer's public mirror.

## The books this folder builds

One collection, `us-history` (OpenStax *U.S. History*): 177 modules in 32 chapters; one level of nesting. Built as PDF (1,309 pages), EPUB and HTML
(211 web pages) on 2026-11-27, the day it was added.

- **Licence:** CC BY-NC-SA 4.0 (collection XML and upstream `LICENSE`).
- **Exercises:** none embedded (no `os-embed` links in either scheme), so there is no
  `exercises/` cache.
- **Figures:** raster only (607 files, 326 MB); no SVG.
- **Block quotations:** 97 `<quote>` elements hold paragraphs (speeches, letters, documents). They are set off as block quotations since the day the book was added (`../../tasks/reference/tooling/converters.md`, "Block quotations, reference notes and footnotes in titles").
- **Still falling back** (the converter's report): `inline:label` (303).

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
