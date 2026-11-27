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
| *Pharmacology for Nurses* | `pharmacology` | 203 modules in 40 chapters grouped into 11 units; two levels of nesting | 1,244 pages | 53 |
| *Nutrition for Nurses* | `nutrition` | 93 modules in 20 chapters grouped into 9 units; two levels of nesting | 520 pages | 31 |
| *Population Health for Nurses* | `population-health` | 185 modules in 35 chapters grouped into 7 units; two levels of nesting | 1,374 pages | 44 |

- **Licence:** CC BY-NC-SA 4.0 (collection XML and upstream `LICENSE`).
- **Exercises:** 1,156 embedded links, all in the `#exercise/<nickname>` scheme (none in
  `#ost/api/ex/`). **Not fetched yet**: there is no `exercises/` cache, so each one is
  left out of the built book and counted by the converter as `exercise-uncached`. The
  maintainer runs `make fetch-exercises` here (it identifies itself with his contact
  address); `../../tasks/openstax-add-book-nursing-external-bundle.md` holds what follows.
- **Figures:** raster only (419 files, 142 MB); no SVG.
- **Exercises per book:** Pharmacology for Nurses 472, Nutrition for Nurses 304, Population Health for Nurses 380.
- **Tables:** 714, most of them prose (drug classes, dosages, nursing implications). In the PDF such a table is scaled down, some until they cannot be read, and one with a link runs off the page (`../../tasks/openstax-pdf-prose-tables-shrink-or-run-off-the-page.md`).
- **Coloured table text:** 3,375 `<span class="blue-text">` wrappers, set like the text around them.
- **Embedded frames:** 248 point at outside pages (58, 6 and 184 in the three books); each is a labelled link (`../../tasks/reference/tooling/converters.md`, "Outside pages embedded in frames").
- **Web editions:** 53, 31 and 44 pages. With two levels of nesting the HTML is split per chapter, so each page is long.
- **Characters missing from the PDF:** `⅓`, `₁` and `₆` in Nutrition for Nurses (`../../tasks/openstax-pdf-characters-missing-from-the-body-font.md`).
- **Still falling back** (the converter's report): none besides the 1,156 `exercise-uncached`.

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
