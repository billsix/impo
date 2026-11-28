# osbooks-nursing-external-bundle — OpenStax Nursing (Pharmacology, Nutrition and Population Health for Nurses) (impo)

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

`fetch.sh` pins **`128c6c3e0ee66850bd8cbb3aa02be736f10db74e`**, the head of OpenStax's default branch
when the book was added (2026-11-27). The pin moves at every sync; `fetch.sh` is the source
of truth. Canonical upstream: `https://github.com/openstax/osbooks-nursing-external-bundle`. Fallback, tried
automatically by `fetch.sh` when the upstream does not provide the pin:
`https://github.com/billsix/osbooks-nursing-external-bundle`, the maintainer's public mirror.

## The books this folder builds

3 collections, built as PDF, EPUB and HTML on 2026-11-27, the day the folder was added:

| Book | Collection | Shape | PDF | Web pages |
|---|---|---|---|---|
| *Pharmacology for Nurses* | `pharmacology` | 203 modules in 40 chapters grouped into 11 units; two levels of nesting | 1,568 pages | 53 |
| *Nutrition for Nurses* | `nutrition` | 93 modules in 20 chapters grouped into 9 units; two levels of nesting | 622 pages | 31 |
| *Population Health for Nurses* | `population-health` | 185 modules in 35 chapters grouped into 7 units; two levels of nesting | 1,653 pages | 44 |

- **Licence:** CC BY-NC-SA 4.0 (collection XML and upstream `LICENSE`).
- **Exercises:** 1,156 embedded links to 1,156 exercises, all in the `#exercise/<nickname>`
  scheme. All 1,156 are in the committed cache `exercises/` (no images; with its `COPYRIGHT`
  notice), fetched by the maintainer on 2026-11-27, and are in the built book.
- **Figures:** raster only (419 files, 142 MB); no SVG.
- **Exercises per book:** Pharmacology for Nurses 472, Nutrition for Nurses 304, Population Health for Nurses 380.
- **Tables:** 714, most of them prose (drug classes, dosages, nursing implications). 657 are set with wrapping columns, and those standing on their own break across pages (`../../tasks/reference/tooling/converters.md`, "Tables of prose"); before 2026-11-27's change they were scaled down until some could not be read.
- **Coloured table text:** 3,375 `<span class="blue-text">` wrappers, set like the text around them.
- **Embedded frames:** 248 point at outside pages (58, 6 and 184 in the three books); each is a labelled link (`../../tasks/reference/tooling/converters.md`, "Outside pages embedded in frames").
- **Web editions:** 53, 31 and 44 pages. With two levels of nesting the HTML is split per chapter, so each page is long.
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
