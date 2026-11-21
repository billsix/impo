# Find the references between books by scanning their content, and make them relative links

**Status:** proposed — needs go-ahead (decisions recorded 2026-11-21; no open questions)
**Priority:** 6
**Difficulty:** 8 (a survey across 16 book folders, then a build-order dependency and a link pass)
**Created:** 2026-11-21 (William Emerison Six <billsix@gmail.com>)

## BLUF

The books build on each other: Calculus 1 assumes algebra and prealgebra, the physics books build on
earlier physics, Calculus 3 assumes Calculus 1 and 2. Scan the books' content to find those
references, both the **explicit** ones (text that names another book or section, like the corequisite
books' `(IA x.y.z)`) and the **implicit** prerequisites (a section that uses a topic another book
teaches), and turn them into **relative links that resolve** on the published site. Done = a
reference map per book pair, the explicit references linked in the HTML web edition, the implicit
ones shown as "Review: <book> §x.y" links where the maintainer approves them, and no broken link
(checked by a link checker over the built site).

## Context

- Read first: `CLAUDE.md`, `openstax/CLAUDE.md`, `tasks/openstax-publish-books.md` (fixes the site
  layout `/<book>/<page>.html` these links rely on), `tasks/openstax-ia-crossref-links.md` (parked:
  the `(IA x.y.z)` case, already designed: the CNXML pattern, the IA `sitemap.json` lookup from
  section number to page, and the PDF/EPUB note). This task takes that one up and generalizes it.
  Archive it into this one (or close it as covered) when this task starts.
- Books (`tasks/reference/openstax/book-inventory.md`): the math ladder in `osbooks-prealgebra-bundle`
  (prealgebra, elementary algebra, intermediate algebra), `osbooks-algebra-1`,
  `osbooks-college-algebra-bundle`, `osbooks-calculus-bundle` (Calculus vol 1–3),
  `osbooks-contemporary-mathematics`; physics in `osbooks-physics` and
  `osbooks-university-physics-bundle` (vol 1–3); and the science books (chemistry, biology,
  microbiology, anatomy-physiology, organic-chemistry) whose prerequisites run across each other.
- **Relative links:** with every book on one site, a link from one book to another is
  `../<other-book>/<page>.html`, built from the target book's `sitemap.json` (section number →
  page). So the target book must be built first, a new build-order dependency between book folders.
  With no target configured or built, leave plain text, as the IA task decided.
- The scan has two parts that need different methods:
  1. **Explicit references** — grep the CNXML for named book/section patterns (`(IA x.y.z)`, "see
     Calculus Volume 1", "Prerequisite", "Be Prepared" boxes that cite another book). Mechanical;
     a discovery script under `tasks/adhoc/openstax-cross-book-references/` with a committed
     worklog (`data/`).
  2. **Implicit prerequisites** — match each section's topics to the section that teaches them in an
     earlier book (e.g. Calculus 1 §1.1 functions → College Algebra ch. 3). Needs judgment (by hand
     or AI-assisted), so the result is a reviewed mapping file, not a regex.
- PDF and EPUB: a cross-book link there can only be an absolute URL (`\href`), since no shared PDF
  exists (the IA task's note). Decisions: absolute URLs.

## Plan

1. Explicit references: discovery script + worklog; count per book pair.
2. Implicit prerequisites: draft the map for one chain first (prealgebra → algebra → college
   algebra → calculus 1–3), for review, before doing physics and the sciences.
3. Write the mappings as data (per book, `section → [(target book, section)]`) in the toolchain,
   and a pass in the HTML leg (pandoc lua filter or a post-process like `build_nav.py`) that emits
   the links.
4. Build-order in `tools/build-books.sh`: target books first.
5. Link-check the built combined site; then the PDF/EPUB decision.

## Decisions (William Emerison Six <billsix@gmail.com>, 2026-11-21: "go with your recommendations")

- **Implicit prerequisites too:** new "Review: <book> §x.y" links, starting with the math ladder (prealgebra → algebra → college algebra → calculus 1–3), reviewed by the maintainer before physics and the sciences.
- **Added links go in a "Prerequisites" box** at the top of each section; the OpenStax prose is unchanged.
- **PDF/EPUB:** absolute `\href` URLs to the published site, once `tasks/openstax-publish-books.md` fixes its URL.
