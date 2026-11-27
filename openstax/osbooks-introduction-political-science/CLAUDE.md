# osbooks-introduction-political-science — OpenStax Introduction to Political Science (impo)

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

`fetch.sh` pins **`61afbf50d27ba833feb64b66ba06a5384e9f371c`**, the head of OpenStax's default branch
when the book was added (2026-11-27). The pin moves at every sync; `fetch.sh` is the source
of truth. Canonical upstream: `https://github.com/openstax/osbooks-introduction-political-science`. Fallback, tried
automatically by `fetch.sh` when the upstream does not provide the pin:
`https://github.com/billsix/osbooks-introduction-political-science`, the maintainer's public mirror.

## The books this folder builds

One collection, `introduction-political-science` (OpenStax *Introduction to Political Science*): 107 modules in 16 chapters grouped into 5 units; two levels of nesting. Built as PDF (763 pages), EPUB and HTML
(23 web pages) on 2026-11-27, the day it was added.

- **Licence:** CC BY-NC-SA 4.0 (collection XML and upstream `LICENSE`).
- **Exercises:** 308 embedded links to 308 exercises, all in the `#exercise/<nickname>`
  scheme. All 308 are in the committed cache `exercises/` (no images; with its `COPYRIGHT`
  notice), fetched by the maintainer on 2026-11-27, and are in the built book.
- **Figures:** raster only (229 files, 97 MB). `media/Interactive/` also holds a case-study bundle with 22 SVG icons that no module references.
- **Reference notes:** 1,522 sources cited as `<cite><note class="reference">`; 1,508 are footnotes and the 14 in captions, table cells and titles follow in parentheses (`../../tasks/reference/tooling/converters.md`, "Block quotations, reference notes and footnotes in titles").
- **Block quotations:** 33, set off as such.
- **Embedded frames:** 115 point at outside pages (simulations, videos). Each is a labelled link in all
  three editions (`../../tasks/reference/tooling/converters.md`, "Outside pages embedded in frames").
- **Web edition:** 23 pages for 107 modules. With two levels of nesting the HTML is split per chapter, as in the other unit-nested books, so each page is long.
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
