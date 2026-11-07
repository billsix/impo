# One `make` call per book (and for all books), release downloads on tag push, manual Pages publish

**Status:** in progress (authorized batch, 2026-11-07) — `make publish-pages` deferred by the
maintainer; everything else is in scope (William Emerison Six <billsix@gmail.com>, 2026-11-07)
**Priority:** 4
**Difficulty:** 5

## BLUF

Make impo build its books the way modelviewprojection does: **one command**. `make <book>` builds
that book's HTML, PDF, and EPUB, and `make books` builds all 17 book folders. Then publish in two
parts. (1) **Pushing a version tag** (`v*`) runs a GitHub Actions job that builds every book and
attaches the PDFs and EPUBs to a GitHub Release, like mvp's `release.yml`. (2) The HTML web editions
go to **GitHub Pages by a manual `make publish-pages`** run on the maintainer's host. Everything
cannot go on Pages, because the outputs total about 4 GB (mostly EPUBs) and a Pages site is capped
at 1 GB. Done = both make targets work locally, the tag workflow produces a Release with every
PDF/EPUB attached, and `make publish-pages` publishes the HTML (once open question 2 is answered).

## Decisions (William Emerison Six <billsix@gmail.com>, 2026-11-07)

1. **Pages publishing is manual**: `make publish-pages`, run on the host (ghp-import), like
   geometricalgebra's manual PyPI upload. No CI deploys the website.
2. **`make publish-pages` is deferred** (and with it the question of where the website's files
   live: a separate repo, or a `gh-pages` branch in impo). The mvp-style build target is still
   required: `make books` builds every book's HTML/PDF/EPUB into one output tree, the way
   modelviewprojection's `make docs` does.
3. **PDFs/EPUBs become GitHub Release assets, built and attached by a CI job on tag push.** The
   maintainer asked for help with the mechanism; the design is below.
4. **The model is modelviewprojection:** one `make` call builds a book's three formats
   (github.com/billsix/modelviewprojection: `make docs` → HTML+PDF+EPUB; `release.yml` on `v*`
   tags runs `make release-artifacts` and attaches `dist/*` with `softprops/action-gh-release@v2`).

## Context

- Read first: `CLAUDE.md`, `openstax/CLAUDE.md`, `trench/CLAUDE.md`,
  `tasks/openstax-publish-books.md` (the older publish task; this task answers its open questions
  and narrows it to the cross-book-link work), `tasks/openstax-ia-crossref-links.md` (parked until
  stable URLs exist).
- **Today:** each book folder has its own Makefile. OpenStax books have `pdf`/`html`/`epub`/`dist`.
  **Trench has `pdf`/`html`/`epub` but no `dist`.** There is no root `Makefile`.
  `tools/build-web-editions.sh` builds `html epub` for the 16 OpenStax books only (non-fatal per
  book, logs to `$LOGDIR`).
- One folder can produce several books (biology-bundle → `concepts-biology`, `biology-2e`,
  `biology-ap-courses`), so the targets are **per book folder** (17: 16 OpenStax + 1 Trench).
- **Sizes (2026-11-07, `du` of existing `checkout/output/`):** ~4 GB total across the OpenStax
  folders, mostly EPUB (biology-2e.epub 392 MB). HTML dirs total ~253 MB, which looks too small to
  include the figures. **Verify** whether the web edition references images outside
  `output/<book>/`. If it does, the published site must copy them in.

## Limits that shaped the design (researched 2026-11-07)

- **GitHub Pages:** published site ≤ 1 GB, deploy ≤ 10 min (docs.github.com, "GitHub Pages
  limits"). This rules out putting the 4 GB of downloads on Pages.
- **GitHub Releases:** each asset < 2 GiB, ≤ 1000 assets per release, **no limit on total release
  size** (docs.github.com, "About releases"). The largest file, biology-2e.epub at 392 MB, fits
  easily.
- **GitHub Actions (hosted runners):** each *job* may run ≤ 6 hours; the free plan allows 20
  concurrent jobs. So the tag workflow runs **one job per book folder** (a matrix): every book
  gets its own 6-hour budget and its own disk, and they run in parallel. **Verify:** the runner's
  free disk (the Fedora + TeX Live image plus one book's output must fit, and a "free disk space"
  step may be needed), that `podman` is present on `ubuntu-latest` (the book Makefiles call
  podman), and that impo is public. Private-repo Actions minutes are metered, and 17 TeX builds
  per tag would use them quickly.

## Design

**Local (the mvp-style one call):**
- Root `Makefile`: a pattern rule so `make anatomy-physiology` (the folder slug without
  `osbooks-`), `make elementary-differential-equations`, etc. each runs that folder's `make dist`.
  Also `make books` (all folders, via the script), `make list-books`, and `help`. No 17
  hand-written stanzas: derive the list from `openstax/osbooks-*/` + `trench/*/`.
- Add `dist` to the Trench Makefile so every folder answers the same target.
- `tools/build-books.sh [book…]` generalizes `build-web-editions.sh` to all three formats and both
  families, keeping the non-fatal PASS/FAIL summary. Keep `build-web-editions.sh` as a two-line
  shim (or update its references in `CLAUDE.md`).
- `make release-assets BOOK=<slug>` copies that folder's PDFs + EPUBs into `dist/` with
  unambiguous names (`<book>.pdf`, `<book>.epub`).

**CI on tag push (`.github/workflows/release.yml`, a thin wrapper over make, like mvp):**
1. Trigger: `push: tags: ['v*']`.
2. Job `books` (matrix over the 17 folder slugs, `fail-fast: false`): checkout → `make <slug>` →
   `make release-assets BOOK=<slug>` → `actions/upload-artifact` of `dist/`.
3. Job `release` (`needs: books`, `permissions: contents: write`): `actions/download-artifact`
   (merge all) → `softprops/action-gh-release@v2` with `files: dist/*`.
4. Each matrix job builds the shared toolchain image itself. If that dominates the run time,
   build it once in a first job and pass it to the others as a `podman save` artifact.
5. The maintainer cuts a release by `git tag vX.Y.Z && git push github vX.Y.Z`. This is the only
   step the workflow needs from him, and it only runs on GitHub (it cannot be tested locally until
   the first tag push).

**Pages (manual, host):** `make publish-pages` collects every book's HTML dir (plus figures, per
the verify item) into one staging dir with an index page linking each book and its Release
downloads, then runs `ghp-import -n -o -p` (`-n` writes `.nojekyll`; `-o` keeps a single commit on
the branch so it does not grow with every publish; `-p` pushes). Where it pushes depends on open
question 2. Because the tag job already builds the HTML, adding an automatic Pages deploy to it
later would be one extra step, if the maintainer ever wants that.

## Plan

1. Root `Makefile` + Trench `dist` + `tools/build-books.sh`; build one book end to end with
   `make <slug>`, and record per-book build times here (they size the CI expectation).
2. Resolve the HTML-figures verify item and measure the real site size.
3. `make release-assets` + `.github/workflows/release.yml`; dry-run the make side locally
   (`make <slug> release-assets`) for two books.
4. Maintainer pushes a test tag (e.g. `v0.0.1`) and checks the Release. Fix whatever only GitHub
   reveals (disk, podman, timing).
5. `make publish-pages` once open question 2 is answered; then narrow
   `tasks/openstax-publish-books.md` to the cross-book links and un-park the IA-link task.

## Deferred (not in this task's scope)

- **`make publish-pages`** (manual ghp-import to GitHub Pages). When it is picked up, the first
  question is where the website's files live: (a) a new repo used only for the website (e.g.
  `billsix/openstax-books`, served at `billsix.github.io/openstax-books/`), or (b) a `gh-pages`
  branch inside impo (served at `billsix.github.io/impo/`, but every clone of impo then also
  downloads the website). The recommendation was (a), to keep impo small.
