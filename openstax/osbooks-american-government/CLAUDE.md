# osbooks-american-government — OpenStax American Government (impo)

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

`fetch.sh` pins **`a2677245241954039c7ebc996e82a8f3b0b4376f`**, the head of OpenStax's default branch
when the book was added (2026-11-27). The pin moves at every sync; `fetch.sh` is the source
of truth. Canonical upstream: `https://github.com/openstax/osbooks-american-government`. Fallback, tried
automatically by `fetch.sh` when the upstream does not provide the pin:
`https://github.com/billsix/osbooks-american-government`, the maintainer's public mirror.

## The books this folder builds

One collection, `american-government-4e` (OpenStax *American Government 4e*): 100 modules in 17 chapters grouped into 5 units; two levels of nesting. Built as PDF (922 pages), EPUB and HTML
(24 web pages) on 2026-11-27, the day it was added.

- **Licence:** CC BY-NC-SA 4.0 (collection XML and upstream `LICENSE`).
- **Exercises:** none embedded (no `os-embed` links in either scheme), so there is no
  `exercises/` cache.
- **Figures:** raster only (335 files, 169 MB); no SVG.
- **Reference notes:** 1,342 sources cited as `<cite><note class="reference">`; 1,333 are footnotes and the 9 in figure captions follow in parentheses (`../../tasks/reference/tooling/converters.md`, "Block quotations, reference notes and footnotes in titles").
- **Block quotations:** 19, set off as such.
- **Web edition:** 24 pages for 100 modules. With two levels of nesting the HTML is split per chapter, as in the other unit-nested books, so each page is long.
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
