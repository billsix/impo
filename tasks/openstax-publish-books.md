# Publish the OpenStax books (PDF / HTML / EPUB) — decide where, then wire cross-book links

**Status:** proposed — needs go-ahead (open questions below; updated 2026-11-21 with the maintainer's
billsix.github.io request)
**Priority:** 5
**Difficulty:** 5

## BLUF

The 16 OpenStax books build cleanly in all three formats (PDF, chunked HTML web edition, EPUB), but nothing is
**published** anywhere yet. This task is to decide **where and how to publish them** at known, stable URLs, and —
once that's settled — to **wire up the cross-book links** that only make sense with a real publish target,
starting with the `(IA x.y.z)` Intermediate-Algebra references (see [[openstax-ia-crossref-links]]). "Done" =
a chosen publishing target + a repeatable publish step, and the cross-book references turned into working links.

## Request (William Emerison Six <billsix@gmail.com>, 2026-11-21)

Consider publishing on **billsix.github.io**. Publish every book as a viewable HTML web edition,
plus the PDF, the EPUB and a **zipped HTML** download, with links to all three at the **beginning
of the online HTML** (the book's landing page). Also find the references *between* books by
scanning their content (calculus → algebra/prealgebra, physics → earlier physics, Calculus 3 →
Calculus 1 and 2) and make them **relative links that resolve**. That part is big enough to be its
own task: `tasks/openstax-cross-book-references.md`. This task supplies the stable URL layout it
needs.

- **What this changes:** the target is now named (GitHub Pages, the user site billsix.github.io,
  i.e. the `billsix/billsix.github.io` repo, or a project site `billsix.github.io/<repo>/`), the
  zipped-HTML format is new, and the download links go at the top of each book's first page.
- **Gotcha: the size cap.** A Pages site is capped at 1 GB, and the outputs are about 4 GB, mostly
  EPUBs (`tasks/impo-make-target-per-book-and-publish.md`, "Limits that shaped the design"). The
  HTML (~253 MB, to be re-measured with figures) can go on Pages; the PDFs, EPUBs and HTML zips
  have to be **GitHub Release assets** (already built by that task's `release.yml` on a tag push)
  and the landing-page links point at the release download URLs. Putting the zips on Pages would
  bust the cap.
- **Relationship to `tasks/impo-make-target-per-book-and-publish.md`:** that task builds the
  release assets and deferred `make publish-pages`. This task now owns `make publish-pages`
  (ghp-import or a push to the Pages repo, run by hand on the host, per that task's decision 1).

## Context

- Build story is complete: `tasks/archive/impo/2026/09/03/build-all-books.md` (28 PDFs + 28 HTML sites + 28 EPUBs, all clean); the HTML
  web edition has the full Furo-style nav (archived `openstax-html-*` tasks). Outputs land in each book's
  gitignored `checkout/output/` (PDF, `output/<slug>/` chunked HTML site, `<slug>.epub`).
- The books cross-reference each other. The known case: corequisite-support books tag objectives with
  `(IA x.y.z)` = Intermediate Algebra section x.y (a **different** book). Those can't be linked until every book
  has a stable published URL. There may be other inter-book references to sweep for once a base URL exists.
- Licensing note carries through: the toolchain is the maintainer's (MIT), the OpenStax content + exercises are
  CC BY — a published site must keep the attribution/`COPYRIGHT` notices visible (see `openstax/CLAUDE.md`).

## What this task decides / does

1. **Where to publish** — pick a target and a per-book URL scheme. Options to weigh:
   - **GitHub Pages** (per-book repo, or one repo with a path per book) — free, static, fits the chunked HTML;
     each book at `https://<user>.github.io/<book>/…` (the toolchain already `touch`es `.nojekyll` for Pages).
   - The maintainer's **self-hosted box** (the Pi that already serves the git remotes) or another static host.
   - A single combined site (all books under one domain/path) vs. one site per book. A combined site makes
     cross-book links simplest (stable relative/absolute paths).
2. **A repeatable publish step** — a `make publish` / script that builds and pushes each book's HTML (and PDF/EPUB
   downloads) to the chosen target. Decide what's published: HTML site always; PDF + EPUB as downloadable
   artifacts linked from each book's landing page.
3. **Cross-book links** — moved to `tasks/openstax-cross-book-references.md` (2026-11-21), which
   covers the `(IA x.y.z)` references of `tasks/openstax-ia-crossref-links.md` and every other
   reference between books. This task only fixes the URL layout (`/<book>/<page>.html` on one
   site) that its relative links rely on.
4. **Downloads at the top of each book** — the landing page gets links to the PDF, EPUB and zipped
   HTML (`<book>-html.zip`, a new `dist` output) on the GitHub Release.

## Open questions

1. **Which Pages site:** (a) the user site `billsix.github.io` itself (books at
   `billsix.github.io/<book>/`, shared with anything else already there), or (b) a project site from
   a new repo, e.g. `billsix.github.io/openstax/<book>/`, or (c) a `gh-pages` branch of impo
   (`billsix.github.io/impo/<book>/`)? *Recommend (b): one combined site keeps cross-book links
   relative and stable, and it doesn't fill the user site's 1 GB budget.*
2. **Downloads as Release assets:** OK for the PDF, EPUB and zipped HTML to live on the GitHub
   Release (linked from each book's landing page), since all of them together won't fit under the
   1 GB Pages cap? *Recommend yes.*
3. **Download links' place:** a box at the top of the book's first page only, or a bar on every
   page? *Recommend the first page (what you asked for), plus one "Downloads" item in the side nav.*
