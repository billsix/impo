# osbooks-introductory-statistics-bundle — OpenStax Introductory Statistics (impo)

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

`fetch.sh` pins **`24e9884724b13baba2b8879d03103cccafc7e25d`**, the head of OpenStax's default branch
when the book was added (2026-11-26). The pin moves at every sync; `fetch.sh` is the source
of truth. Canonical upstream: `https://github.com/openstax/osbooks-introductory-statistics-bundle`. Fallback, tried
automatically by `fetch.sh` when the upstream does not provide the pin:
`https://github.com/billsix/osbooks-introductory-statistics-bundle`, the maintainer's public mirror.

## The books this folder builds

Two collections, sharing none of their 179 modules:

- `introductory-statistics-2e` (*Introductory Statistics 2e*): 102 modules in 13 chapters.
- `introductory-business-statistics-2e` (*Introductory Business Statistics 2e*): 77 modules
  in 13 chapters.

Both have one level of nesting. Facts from the first build (2026-11-26):

- **Licence:** CC BY-NC-SA 4.0 (both collection XML files and the upstream `LICENSE`).
- **Exercises:** none embedded in either book (no `os-embed` links in either scheme), so
  there is no `exercises/` cache.
- **Figures:** raster only (91 MB of JPEG/PNG); no SVG.
- **Content MathML:** one formula, in Introductory Statistics 2e; handled by the converter.
- **Still falling back** (the converter's report, both books together): `inline:label` (745),
  `inline:cite-title` (17), `inline:item` (15), `inline:cite` (13), `inline:div` and
  `inline:list` (1 each).

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
