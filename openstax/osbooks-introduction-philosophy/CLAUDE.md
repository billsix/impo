# osbooks-introduction-philosophy — OpenStax Introduction to Philosophy (impo)

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

`fetch.sh` pins **`a0dbb585086d0302a9e509c0aa50f2ef436c3613`**, the head of OpenStax's default branch
when the book was added (2026-11-27). The pin moves at every sync; `fetch.sh` is the source
of truth. Canonical upstream: `https://github.com/openstax/osbooks-introduction-philosophy`. Fallback, tried
automatically by `fetch.sh` when the upstream does not provide the pin:
`https://github.com/billsix/osbooks-introduction-philosophy`, the maintainer's public mirror.

## The books this folder builds

One collection, `introduction-philosophy-2e` (OpenStax *Introduction to Philosophy 2e*): 66 modules in 12 chapters; one level of nesting. Built as PDF (533 pages), EPUB and HTML
(80 web pages) on 2026-11-27, the day it was added.

- **Licence:** CC BY-NC-SA 4.0 (collection XML and upstream `LICENSE`).
- **Exercises:** 228 embedded links, all in the `#exercise/<nickname>` scheme (none in
  `#ost/api/ex/`). **Not fetched yet**: there is no `exercises/` cache, so each one is
  left out of the built book and counted by the converter as `exercise-uncached`. The
  maintainer runs `make fetch-exercises` here (it identifies itself with his contact
  address); `../../tasks/openstax-add-book-introduction-philosophy.md` holds what follows.
- **Figures:** raster only (130 files; `media/` is 118 MB). `media/Interactive/` holds 525 more files, 127 of them SVG icons; no module references an SVG.
- **Unused modules:** the repository holds 76 module folders and the collection lists 66.
- **Block quotations:** 33, set off as such; one holds a numbered list and no paragraph (`../../tasks/reference/tooling/converters.md`, "Block quotations, reference notes and footnotes in titles").
- **Characters missing from the PDF:** `ǐ`, `ʿ`, `Ḥ`, `ṇ`, `Ṣ`, `ṣ`, in Chinese, Arabic and Sanskrit names, which the body font has no glyph for (`../../tasks/openstax-pdf-characters-missing-from-the-body-font.md`).
- **Still falling back** (the converter's report): none besides the 228 `exercise-uncached`.

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
