# osbooks-principles-of-management-bundle — OpenStax Principles of Management (impo)

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

`fetch.sh` pins **`f2b749648a176dbe114dbc4e35ec20c030be4713`**, the head of OpenStax's default branch
when the book was added (2026-11-28). The pin moves at every sync; `fetch.sh` is the source
of truth. Canonical upstream: `https://github.com/openstax/osbooks-principles-of-management-bundle`. Fallback, tried
automatically by `fetch.sh` when the upstream does not provide the pin:
`https://github.com/billsix/osbooks-principles-of-management-bundle`, the maintainer's public mirror.

## The books this folder builds

2 collections over 192 modules on disk (the books share modules):

- `principles-management` (OpenStax *Principles of Management*): 132 modules in 18 chapters, from "Managing and Performing" to "Management of Technology and Innovation"; one level of nesting; PDF 767 pages, 152 web pages.
- `organizational-behavior` (OpenStax *Organizational Behavior*): 121 modules in 19 chapters, from "Management and Organizational Behavior" to "Entrepreneurship"; one level of nesting; PDF 783 pages, 142 web pages.

Built as PDF, EPUB and HTML on 2026-11-28, the day it was added.

- **Licence:** CC BY-NC-SA 4.0 (collection XML and upstream `LICENSE`).
- **Exercises:** none embedded (no `os-embed` links in either scheme), so there is no
  `exercises/` cache.
- **Figures:** raster only (278 files, 82 MB); no SVG.
- **Still falling back** (the converter's report): `inline:para` (4), `inline:equation` (2).

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
