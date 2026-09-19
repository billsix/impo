# Publish the OpenStax books (PDF / HTML / EPUB) — decide where, then wire cross-book links

**Status:** proposed — needs go-ahead
**Priority:** 5
**Difficulty:** 5

## BLUF

The 16 OpenStax books build cleanly in all three formats (PDF, chunked HTML web edition, EPUB), but nothing is
**published** anywhere yet. This task is to decide **where and how to publish them** at known, stable URLs, and —
once that's settled — to **wire up the cross-book links** that only make sense with a real publish target,
starting with the `(IA x.y.z)` Intermediate-Algebra references (see [[openstax-ia-crossref-links]]). "Done" =
a chosen publishing target + a repeatable publish step, and the cross-book references turned into working links.

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
3. **Cross-book links (the payoff)** — once a base-URL scheme exists, implement [[openstax-ia-crossref-links]]
   option (b): a configurable base URL per target book, and turn `(IA x.y.z)` (and any other inter-book refs
   found) into `<a href>`s. Then decide the PDF/EPUB behaviour for those refs (a `\href`/URL, or leave plain) per
   that task's "PDF and EPUB" note.

## Open questions

1. **Publishing target** — GitHub Pages, the self-hosted Pi, or another static host? And **one combined site**
   (all 16 books under one domain — simplest for cross-book links) or **one site per book**? *Recommend a single
   combined site (one domain, `/<book>/…` per book) — it makes the cross-book URLs trivial and stable.*
2. **What formats to publish** — HTML web edition always; also offer the PDF + EPUB as downloads from each book's
   landing page? *Recommend yes — build once, link the artifacts.*
3. **Scope of cross-book linking** — just the `(IA x.y.z)` corequisite references, or sweep for other inter-book
   references too once a base URL exists? *Recommend start with IA (known, verified), then grep for other
   patterns.*
