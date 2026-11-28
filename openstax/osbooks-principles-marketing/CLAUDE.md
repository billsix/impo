# osbooks-principles-marketing — OpenStax Principles of Marketing (impo)

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

`fetch.sh` pins **`a6d7372579d13e0a733954953c4613867f018a48`**, the head of OpenStax's default branch
when the book was added (2026-11-28). The pin moves at every sync; `fetch.sh` is the source
of truth. Canonical upstream: `https://github.com/openstax/osbooks-principles-marketing`. Fallback, tried
automatically by `fetch.sh` when the upstream does not provide the pin:
`https://github.com/billsix/osbooks-principles-marketing`, the maintainer's public mirror.

## The books this folder builds

One collection, `principles-marketing` (OpenStax *Principles of Marketing*): 132 modules in 19 chapters, from "Marketing and Customer Value" to "Sustainable Marketing: The New Paradigm"; two levels of nesting (units, then chapters); PDF 831 pages, 24 web pages.
Built as PDF, EPUB and HTML on 2026-11-28, the day it was added.

- **Licence:** CC BY-NC-SA 4.0 (collection XML and upstream `LICENSE`).
- **Exercises:** 662 embedded links, all in the `#exercise/<nickname>` scheme. **Not cached yet:** the maintainer runs `make fetch-exercises` here, and until then the books print a placeholder for each.
- **Figures:** raster only (237 files, 62 MB); no SVG.
- **Still falling back** (the converter's report): `inline:cite` (893), `inline:note` (893), `inline:para` (4).

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
