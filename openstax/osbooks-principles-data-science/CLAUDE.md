# osbooks-principles-data-science — OpenStax Principles of Data Science (impo)

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

`fetch.sh` pins **`cc5a81d59c7d9b8b153a2297098e89dfaca7b2d3`**, the head of OpenStax's default branch
when the book was added (2026-11-26). The pin moves at every sync; `fetch.sh` is the source
of truth. Canonical upstream: `https://github.com/openstax/osbooks-principles-data-science`. Fallback, tried
automatically by `fetch.sh` when the upstream does not provide the pin:
`https://github.com/billsix/osbooks-principles-data-science`, the maintainer's public mirror.

## The books this folder builds

One collection, `principles-data-science` (OpenStax *Principles of Data Science*): 59 modules in 10 chapters grouped into 4 units, from "Introducing Data Science and Data Collection" to "Maintaining a Professional and Ethical Data Science Practice"; two levels of nesting. Built as PDF (600 pages), EPUB and HTML
(16 web pages) on 2026-11-27, the day it was added.

- **Licence:** CC BY-NC-SA 4.0 (collection XML and upstream `LICENSE`).
- **Exercises:** 136 embedded links, all in the `#exercise/<nickname>` scheme (none in
  `#ost/api/ex/`). **Not fetched yet**: there is no `exercises/` cache, so each one is
  left out of the built book and counted by the converter as `exercise-uncached`. The
  maintainer runs `make fetch-exercises` here (it identifies itself with his contact
  address); `../../tasks/openstax-add-book-principles-data-science.md` holds what follows.
- **Figures:** raster only (232 files, 40 MB); no SVG.
- **Code:** 166 `<code class="python">` blocks, many holding one line wrapped in line breaks; each is a listing since the day the book was added (`../../tasks/reference/tooling/converters.md`, "One line of code wrapped in line breaks").
- **Web edition:** 16 pages for 59 modules. With two levels of nesting the HTML is split per chapter, as in the other unit-nested books, so each page is long.
- **Still falling back** (the converter's report): `inline:span` (815) and `inline:para` (3).

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
