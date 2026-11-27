# osbooks-college-success-bundle — OpenStax College Success (impo)

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

`fetch.sh` pins **`cca7cd1d4ab230f2e2cb6131ed7e161d50548f07`**, the head of OpenStax's default branch
when the book was added (2026-11-27). The pin moves at every sync; `fetch.sh` is the source
of truth. Canonical upstream: `https://github.com/openstax/osbooks-college-success-bundle`. Fallback, tried
automatically by `fetch.sh` when the upstream does not provide the pin:
`https://github.com/billsix/osbooks-college-success-bundle`, the maintainer's public mirror.

## The books this folder builds

3 collections, built as PDF, EPUB and HTML on 2026-11-27, the day the folder was added:

| Book | Collection | Shape | PDF | Web pages |
|---|---|---|---|---|
| *College Success 2e* | `college-success-2e` | 75 modules in 12 chapters; one level of nesting | 468 pages | 89 |
| *College Success Concise* | `college-success-concise` | 44 modules in 8 chapters; one level of nesting | 294 pages | 54 |
| *Preparing for College Success* | `preparing-for-college-success` | 49 modules in 9 chapters; one level of nesting | 325 pages | 60 |

- **Licence:** CC BY-NC-SA 4.0 (collection XML and upstream `LICENSE`).
- **Exercises:** none embedded, counted in the CNXML in both link schemes; no `exercises/` cache.
- **Figures:** raster only (300 files, 50 MB); no SVG.
- **Shared modules:** the three collections list 168 modules between them and the repository holds 125, so some are shared.
- **Block quotations:** 41, 13 and 14 `<quote>` elements in the three books, the ones holding paragraphs set off as such.
- **Tick marks:** a table of note-taking symbols uses a bare `√`; the web editions show the character (`../../tasks/reference/tooling/converters.md`, "Block quotations, reference notes and footnotes in titles").
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
