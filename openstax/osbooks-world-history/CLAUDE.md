# osbooks-world-history — OpenStax World History (impo)

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

`fetch.sh` pins **`c0dd82697bc2c7cd355c942e778f215762768c43`**, the head of OpenStax's default branch
when the book was added (2026-11-27). The pin moves at every sync; `fetch.sh` is the source
of truth. Canonical upstream: `https://github.com/openstax/osbooks-world-history`. Fallback, tried
automatically by `fetch.sh` when the upstream does not provide the pin:
`https://github.com/billsix/osbooks-world-history`, the maintainer's public mirror.

## The books this folder builds

2 collections, built as PDF, EPUB and HTML on 2026-11-27, the day the folder was added:

| Book | Collection | Shape | PDF | Web pages |
|---|---|---|---|---|
| *World History Volume 1, to 1500* | `world-history-volume-1` | 85 modules in 17 chapters and 4 units; two levels of nesting | 918 pages | 23 |
| *World History Volume 2, from 1400* | `world-history-volume-2` | 80 modules in 15 chapters and 3 units; two levels of nesting | 864 pages | 20 |

- **Licence:** CC BY-NC-SA 4.0 (collection XML and upstream `LICENSE`).
- **Exercises:** 1,158 embedded links, all in the `#exercise/<nickname>` scheme (none in
  `#ost/api/ex/`). **Not fetched yet**: there is no `exercises/` cache, so each one is
  left out of the built book and counted by the converter as `exercise-uncached`. The
  maintainer runs `make fetch-exercises` here (it identifies itself with his contact
  address); `../../tasks/openstax-add-book-world-history.md` holds what follows.
- **Figures:** raster only (909 files, 345 MB, both volumes together); no SVG.
- **Exercises per volume:** 589 links in volume 1 and 569 in volume 2.
- **Block quotations:** 131 in the two volumes, set off as such.
- **Embedded frames:** 8 point at outside pages (simulations, videos). Each is a labelled link in all
  three editions (`../../tasks/reference/tooling/converters.md`, "Outside pages embedded in frames").
- **Web editions:** 23 and 20 pages. With two levels of nesting the HTML is split per chapter, as in the other unit-nested books, so each page is long.
- **Still falling back** (the converter's report): none besides the 1,158 `exercise-uncached`.

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
