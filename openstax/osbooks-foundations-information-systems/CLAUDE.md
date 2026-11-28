# osbooks-foundations-information-systems — OpenStax Foundations of Information Systems (impo)

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

`fetch.sh` pins **`057882c68a7867af80c42e86937d3a2454bfd86a`**, the head of OpenStax's default branch
when the book was added (2026-11-27). The pin moves at every sync; `fetch.sh` is the source
of truth. Canonical upstream: `https://github.com/openstax/osbooks-foundations-information-systems`. Fallback, tried
automatically by `fetch.sh` when the upstream does not provide the pin:
`https://github.com/billsix/osbooks-foundations-information-systems`, the maintainer's public mirror.

## The books this folder builds

One collection, `foundations-information-systems` (OpenStax *Foundations of Information Systems*): 59 modules in 12 chapters; one level of nesting. Built as PDF (640 pages), EPUB and HTML
(73 web pages) on 2026-11-27, the day it was added.

- **Licence:** CC BY-NC-SA 4.0 (collection XML and upstream `LICENSE`).
- **Exercises:** 410 embedded links to 410 exercises, all in the `#exercise/<nickname>`
  scheme. All 410 are in the committed cache `exercises/` (1 image; with its `COPYRIGHT`
  notice), fetched by the maintainer on 2026-11-27, and are in the built book.
- **Figures:** raster only (181 files, 28 MB); no SVG.
- **Markup this book brought to the converter:** a `<footnote>` inside a note's title, which stopped LaTeX; it is given in parentheses since the day the book was added (`../../tasks/reference/tooling/converters.md`, "Block quotations, reference notes and footnotes in titles").
- **Still falling back** (the converter's report): `inline:item` (8) and `inline:list` (1).

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
