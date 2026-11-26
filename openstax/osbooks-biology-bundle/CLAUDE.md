# osbooks-biology-bundle — OpenStax Biology (bundle) (imps)

An imps OpenStax-family book on the shared-toolchain contract. Read the family
doc [`../CLAUDE.md`](../CLAUDE.md) first (the fetch → apply-overlay → build model,
the content/copyright rules) and the shared toolchain it points at,
[`../tooling/`](../tooling). This file records only what is specific to *this book*.

## What lives here (thin per-book folder)

No OpenStax content and no toolchain are committed — both are pulled in on demand:

- `fetch.sh` — clones the pinned pristine OpenStax content into `checkout/` (gitignored).
- `apply.sh` — overlays `../tooling/` onto `checkout/` (and copies a committed
  `exercises/` cache in, if this book has one).
- `Makefile` — builds the image from `../tooling/Dockerfile` (context `../tooling`) and
  runs it against `checkout/` mounted at the fixed path `/book`.
- `README.md`, `.gitignore`.

## The pin

`fetch.sh` pins **`bc1be223bd23a00cc68efb6195dc183f4e1e228a`**, the head of OpenStax's default branch
at the last sync (the pin moves at every sync; `fetch.sh` is the source of truth).
The port was first made against `1e74a23833550e6bbe3aa3450c50c9ecb74f3a66` — the merge-base where the
maintainer's `latex` port branch diverged from OpenStax's `main` (the pristine
content the port was made against), from the survey table in
`tasks/archive/impo/2026/09/03/openstax-populate-books.md`. Canonical upstream:
`https://github.com/openstax/osbooks-biology-bundle`. Fallback mirror if GitHub is
unreachable: `pi@192.168.0.186:/mnt/usbdrive2/gitRepos/openstax/**/osbooks-biology-bundle.git`.

## The books this folder builds (verified by the 2026-11-26 build)

Three collections, each built as PDF, EPUB and HTML: `biology-2e` (259 modules),
`biology-ap-courses-2e` (209) and `concepts-biology` (107). Upstream renamed
`biology-ap-courses` to `biology-ap-courses-2e` between the 2026-10 and 2026-11
pins, so the output files and the published address carry the new name.

Only Biology for AP Courses has embedded exercises. The rename did not touch them:
the same 2350 exercises are referenced at both pins. The committed cache holds 2337;
13 are not in it (`apbio-ch06-ex039`, `-ex040`, `-ex064`, `-ex065` and nine in
`apbio-ch10`), so those print "Practice exercise available in the online edition"
or nothing. Another 101 references exist only inside XML comments in the CNXML and
are not part of the book. The cache files carry `book-slug:biology-ap-courses` tags
from when they were fetched; the converter looks an exercise up by its nickname
(`exercises/<nickname>.json`), so the tags do not matter to the build.

## This book (from the survey; build-time facts pending)

- **Delta size:** 2723 port-branch files; **has os-embed exercises (large cache)**
  (per the `tasks/archive/impo/2026/09/03/openstax-populate-books.md` survey table).
- **Book specifics — single- vs multi-collection, subcollection nesting depth,
  whether `os-embed` exercises are actually present, and SVG vs raster figures —
  are verified on the first build**, not asserted here. The converter auto-detects
  collection structure and nesting; only the *downloaded* exercise images (not
  upstream `media/` figures) belong in a committed `exercises/` cache.

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
