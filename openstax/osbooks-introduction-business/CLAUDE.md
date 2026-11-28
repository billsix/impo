# osbooks-introduction-business — OpenStax Introduction to Business 2e (impo)

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

`fetch.sh` pins **`2a839877ab89a207c9b9e501df438173013fa45c`**, the head of OpenStax's default branch
when the book was added (2026-11-28). The pin moves at every sync; `fetch.sh` is the source
of truth. Canonical upstream: `https://github.com/openstax/osbooks-introduction-business`. Fallback, tried
automatically by `fetch.sh` when the upstream does not provide the pin:
`https://github.com/billsix/osbooks-introduction-business`, the maintainer's public mirror.

## The books this folder builds

One collection, `introduction-business-2e` (OpenStax *Introduction to Business 2e*): 153 modules in 17 chapters, from "Understanding Economic Systems and Business" to "Your Career in Business"; one level of nesting; PDF 842 pages, 172 web pages.
Built as PDF, EPUB and HTML on 2026-11-28, the day it was added.

- **Licence:** CC BY-NC-SA 4.0 (collection XML). The upstream `LICENSE` file is the text of CC BY 4.0, but the collection XML declares CC BY-NC-SA 4.0, and so does the book's preface on openstax.org (https://openstax.org/books/introduction-business-2e/pages/preface, read 2026-11-28). The converter reads the collection, so the built book states CC BY-NC-SA 4.0. The survey table reads the `LICENSE` file and shows CC BY 4.0 for this repository.
- **Exercises:** none embedded (no `os-embed` links in either scheme), so there is no
  `exercises/` cache.
- **Figures:** raster only (197 files, 237 MB); no SVG.

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
