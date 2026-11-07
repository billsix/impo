# One `make` target per book + an all-books build, then a GitHub Pages publish path

**Status:** proposed — needs go-ahead (William Emerison Six <billsix@gmail.com>, 2026-11-07)
**Priority:** 4
**Difficulty:** 4

## BLUF

Give impo a **root `Makefile`** with one target per book (e.g. `make anatomy-physiology`) that
builds that book's HTML, PDF, and EPUB in one command, the way modelviewprojection's `make docs`
builds its book. Add `make all-books` (backed by a script, generalizing
`tools/build-web-editions.sh` to all three formats and both families) to build every book. Then
publish. **The size research below rules out the obvious "one GitHub Pages site with everything":**
the built outputs total about **4 GB** (mostly EPUBs; biology alone is 789 MB), and a GitHub Pages
site is capped at **1 GB**. The workable shape is **HTML on Pages, PDF/EPUB as GitHub Release
assets**. Done = the per-book + all-books targets work, and the publish step is chosen and wired
(this task supersedes the "where to publish" half of `tasks/openstax-publish-books.md`).

## Context

- Read first: `CLAUDE.md` (families, `tools/`), `openstax/CLAUDE.md`, `trench/CLAUDE.md`,
  `tasks/openstax-publish-books.md` (the existing publish decision, whose open questions this task
  answers with data), and `tasks/openstax-ia-crossref-links.md` (parked until books have stable
  URLs).
- **Today:** every book folder has its own Makefile. OpenStax books have `pdf`, `html`, `epub`, and
  `dist` (= all three). **Trench has `pdf`/`html`/`epub` but no `dist`.** Add one so every book
  answers the same target. There is no root `Makefile`. `tools/build-web-editions.sh` loops over
  the 16 OpenStax books for `html epub` only (non-fatal per book, logs to `$LOGDIR`).
- Bundles produce several books each (the biology bundle produces `concepts-biology`, `biology-2e`,
  and `biology-ap-courses`), so "a target per book" means **a target per book folder** (17: 16
  OpenStax + 1 Trench). Each target builds every book in its bundle.
- The modelviewprojection precedent (github.com/billsix/modelviewprojection): `make docs` builds
  HTML+PDF+EPUB into `./output/`, and `release-book-assets` stages standalone PDF/EPUB/HTML-zip for
  a GitHub Release. Its Pages decision is still open in that repo's
  `tasks/release-book-github-pages-decision.md`, which also explains GitHub Pages in plain terms.

## Size measurements (2026-11-07, existing `checkout/output/` dirs, `du`)

- Total of the 16 OpenStax outputs: **~4 GB**. The largest are biology-bundle 789 MB,
  chemistry-bundle 492 MB, and anatomy-physiology 414 MB.
- Most of it is **EPUB** (biology-2e.epub 392 MB). The chunked **HTML dirs total only ~253 MB**
  across all books (biology-2e HTML 6.3 MB).
- **To verify:** the HTML dirs look too small to contain the figures. Check whether the web edition
  references images outside `output/<book>/` (e.g. the checkout's `media/`). If so, the published
  site must copy them in, and the real HTML size will be larger. **This number decides whether one
  combined Pages site fits under 1 GB.**

## GitHub Pages facts (researched 2026-11-07)

- Pages = free static hosting at `https://billsix.github.io/<repo>/`. Limits (docs.github.com
  "GitHub Pages limits"): **published site ≤ 1 GB**, source repo recommended ≤ 1 GB, deploy timeout
  10 min, soft bandwidth 100 GB/month.
- **Automated:** a GitHub Actions workflow builds and then runs `actions/upload-pages-artifact` +
  `actions/deploy-pages` (artifact must be < 10 GB, recommended < 1 GB). Building 17 books with
  TeX Live in CI is slow and heavy, so automation would more likely deploy pre-built HTML than
  build in CI.
- **Manual (the analogue of geometricalgebra's `make upload` to PyPI):** build locally, then push
  the HTML to a `gh-pages` branch with **`ghp-import -n -o -p <dir>`** (`-n` writes `.nojekyll`, `-o`
  keeps a single commit so the branch never accumulates history, `-p` pushes). Set the repo's Pages
  source to "Deploy from branch: gh-pages". This can be a `make publish-pages` target, run by the
  maintainer on the host, with no CI and no tokens beyond normal git push rights.
- **PDF/EPUB downloads:** attach them to a GitHub Release (`gh release upload`). Release assets are
  not part of the Pages site, so they don't count against its 1 GB. The site's landing page links to
  them.
- A **separate repo** for the site (e.g. `billsix/openstax-books`) keeps the large `gh-pages` branch
  out of impo's own clone. Pages from impo itself would add every published HTML snapshot to impo's
  object store (mitigated, not removed, by `-o`).

## Plan

1. Add `dist` to the Trench Makefile. Add a root `Makefile` with a target per book folder
   (generated from the folder list via a pattern rule, not 17 hand-written stanzas), `all-books`,
   and `help`.
2. Generalize `tools/build-web-editions.sh` → `tools/build-books.sh [formats] [book…]` covering both
   families and `pdf html epub`, keeping its non-fatal PASS/FAIL report. Keep the old name working
   (a shim) or update its references.
3. Measure the real self-contained HTML size (resolve the "To verify" item above).
4. Add `make publish-pages` (manual ghp-import to the chosen repo) and `make publish-downloads`
   (`gh release upload` of PDFs/EPUBs), per the answers below.
5. Update `tasks/openstax-publish-books.md` (close or narrow it) and un-park the IA cross-link task
   once URLs exist.

## Open questions

1. Publish mechanism: (a) **manual `make publish-pages`** (ghp-import from the maintainer's host,
   the PyPI-style flow) or (b) **automated GitHub Actions** deploy on push/tag? *Recommend (a): the
   books need a TeX Live container and a lot of build time, and a manual push matches how
   geometricalgebra publishes.*
2. Site home: (a) **a separate repo** (e.g. `billsix/openstax-books`, one combined site with a path per
   book) or (b) **impo's own `gh-pages`**? *Recommend (a), to keep impo's clone small.*
3. PDF/EPUB: publish them as GitHub Release assets linked from the site? *Recommend yes. They are
   about 4 GB and cannot go on Pages.*
