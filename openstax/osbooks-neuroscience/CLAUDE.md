# osbooks-neuroscience — OpenStax Introduction to Behavioral Neuroscience (impo)

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

`fetch.sh` pins **`6164a769d700843059a11fdd5e505e1c0efe1443`**, the head of OpenStax's default branch
when the book was added (2026-11-27). The pin moves at every sync; `fetch.sh` is the source
of truth. Canonical upstream: `https://github.com/openstax/osbooks-neuroscience`. Fallback, tried
automatically by `fetch.sh` when the upstream does not provide the pin:
`https://github.com/billsix/osbooks-neuroscience`, the maintainer's public mirror.

## The books this folder builds

One collection, `introduction-behavioral-neuroscience` (OpenStax *Introduction to Behavioral Neuroscience*): 106 modules in 19 chapters; one level of nesting. Built as PDF (1,125 pages), EPUB and HTML
(127 web pages) on 2026-11-27, the day it was added.

- **Licence:** CC BY-NC-SA 4.0 (collection XML and upstream `LICENSE`).
- **Exercises:** 568 embedded links to 568 exercises, all in the `#exercise/<nickname>`
  scheme. All 568 are in the committed cache `exercises/` (no images; with its `COPYRIGHT`
  notice), fetched by the maintainer on 2026-11-27, and are in the built book.
- **Figures:** raster only (541 files, 310 MB); no SVG. One file name holds an en dash (`Image-12.04_Stress–critical-periods.png`).
- **What this book brought to the build scripts:** the figure with an en dash in its name. In the image's POSIX locale pandoc could not find it, so `html.sh` and `epub.sh` set `LANG=C.UTF-8` (`../../tasks/reference/tooling/converters.md`, "Block quotations, reference notes and footnotes in titles", last item).
- **Embedded frames:** 40 point at outside pages (simulations, videos). Each is a labelled link in all
  three editions (`../../tasks/reference/tooling/converters.md`, "Outside pages embedded in frames").
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
