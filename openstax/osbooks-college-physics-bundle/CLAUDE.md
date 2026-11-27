# osbooks-college-physics-bundle — OpenStax College Physics (impo)

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

`fetch.sh` pins **`66fcef29596e3a32818162b837dd0c85b754cbad`**, the head of OpenStax's default branch
when the book was added (2026-11-26). The pin moves at every sync; `fetch.sh` is the source
of truth. Canonical upstream: `https://github.com/openstax/osbooks-college-physics-bundle`. Fallback, tried
automatically by `fetch.sh` when the upstream does not provide the pin:
`https://github.com/billsix/osbooks-college-physics-bundle`, the maintainer's public mirror.

## The books this folder builds

Two collections of 283 modules each, 34 chapters, one level of nesting. They share 248
modules; each has 35 of its own (318 distinct modules in the folder):

- `college-physics-2e` (*College Physics 2e*): algebra-based physics.
- `college-physics-ap-courses-2e` (*College Physics for AP® Courses 2e*): the same course
  arranged for AP Physics 1 and 2.

Where these sit beside the other physics books impo builds: `osbooks-physics` is the
high-school text, this is the algebra-based college text, and
`osbooks-university-physics-bundle` is the calculus-based one.

Facts from the first build (2026-11-26):

- **Licence:** CC BY-NC-SA 4.0 (both collection XML files and the upstream `LICENSE`).
- **Exercises:** none embedded in either book (no `os-embed` links in either scheme;
  unlike `osbooks-physics`, which uses the `#ost/api/ex/` scheme), so there is no
  `exercises/` cache.
- **Figures:** raster only (about 1,440 references per book, 472 MB of media); no SVG.
- **Embedded frames:** 18 point at openstax.org simulation links. The converter emits
  nothing for them, as in the other books
  (`../../tasks/openstax-embedded-frame-links-are-dropped.md`).
- **Still falling back** (the converter's report, both books together): `inline:label`
  (806), `inline:space` (90), `inline:span` (6).
- **PDFs:** 2,552 pages (2e) and 2,595 pages (AP), built 2026-11-26 and rebuilt 2026-11-27 with the multi-character
  operator fix (formulas such as "cal/g·ºC").

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
