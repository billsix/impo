# Hyperlink "(IA x.y.z)" learning-objective cross-references in the web edition

**Status:** PARKED 2026-09-03 — leave the references as plain text for now (maintainer's call)
**Priority:** 8
**Difficulty:** 5
**Parked because:** the reference points to a *different* book, and the OpenStax books aren't published at known
URLs yet, so there's no stable link target. **Revisit when** the books are hosted at known URLs — then implement
option (b): a configurable IA base URL + the section lookup below (both already worked out here). Until then the
`(IA x.y.z)` text stays as-is (harmless, just not clickable).

## BLUF

The corequisite-support books (e.g. **College Algebra with Corequisite Support**, in
`osbooks-college-algebra-bundle`) tag each Learning Objective with its match in OpenStax's **Intermediate
Algebra** book, shown as literal text like **"(IA 8.2.1)"** — which is opaque to a reader. `IA` = *Intermediate
Algebra*; `8.2.1` = that book's chapter 8, section 2, objective 1. Make these references **hyperlinks** in the
HTML to the corresponding Intermediate Algebra section. The catch: Intermediate Algebra is a **separate book**
(`intermediate-algebra-2e`, in `osbooks-prealgebra-bundle`), so this is a **cross-book** link whose URL depends
on how the books are deployed — that's the decision to make first. Also note (below) what to do for PDF/EPUB.
"Done" = "(IA x.y.z)" renders as a link to IA section x.y in the HTML edition (all corequisite books), with the
PDF/EPUB behaviour decided.

## Context / findings (verified 2026-09-03)

- **What it is:** `IA` = Intermediate Algebra. `(IA 8.2.1)` → IA section **8.2** ("Simplify Expressions with
  Roots"), objective 1 = "Use the product property to simplify radical expressions" — matches the objective text
  it annotates. Confirmed against the IA book's own section numbering.
- **In the source it's LITERAL TEXT**, not a `<link>` — e.g. `Graph exponential functions. (IA 10.2.1)</item>`
  in the college-algebra-bundle CNXML. So there is no existing target to resolve; we parse the text pattern
  `\(IA\s+\d+(?:\.\d+)*\)`.
- **Target lives in another book/site.** IA is `intermediate-algebra-2e` under `osbooks-prealgebra-bundle`. Its
  sitemap maps section numbers to pages cleanly, e.g. `8.2 -> 058-mod:m81444.html`, `10.2 -> 078-…`,
  `3.5 -> 023-…`. So `IA x.y` → a real IA page is a simple lookup built from the IA book's `sitemap.json`.
- **Granularity:** the `.z` objective sub-part has no per-objective anchor in the IA HTML; link to the **section
  (x.y) page** — that's the useful, reliable target.

## Design (HTML) — pending the cross-book-URL decision

1. Build an **IA lookup** `x.y -> page-url` from `intermediate-algebra-2e`'s `sitemap.json` (a small generated
   JSON, or computed at build time). Requires the IA book to be built first (a build-order dependency between
   two book folders — new for this toolchain).
2. In the HTML leg (a pandoc lua filter, or a post-process pass like `build_nav.py`), replace each `(IA x.y.z)`
   text with `(<a href="<IA base>/<page>">IA x.y.z</a>)`.
3. Scope it to the corequisite/college-algebra books (the ones that use the notation) — or make it generic and a
   no-op where the IA lookup/base isn't configured.

## THE decision to make first: how to form the cross-book URL

Intermediate Algebra is a different site, so the link target depends on deployment. Options:
- **(a) Relative path to a co-located build** — e.g. `../../../osbooks-prealgebra-bundle/checkout/output/intermediate-algebra-2e/<page>`. Works only if both books are built and served with that exact tree; **fragile** (the checkout/output dirs are gitignored build artifacts, and a hosted site won't have that layout).
- **(b) A configurable base URL** — a per-repo/per-book setting like `IA_BASE=https://<host>/intermediate-algebra/`; the filter prepends it. Robust for hosting; needs the maintainer to set where IA is published. **(Recommended.)**
- **(c) No link when unresolved** — if no IA base is configured (or IA isn't built), leave the text as-is (today's behaviour), so nothing breaks.

Recommend **(b) + (c)**: a configurable IA base URL, degrade to plain text when unset — no broken links, works
for whatever hosting the maintainer chooses.

## Note: PDF and EPUB (think about later — do not implement yet)

- **PDF:** a cross-book link can only be a *URL* (there's no shared PDF to `\ref` into). Options: make `(IA x.y.z)`
  a `\href` to the same configurable IA base URL (clickable in a PDF viewer), or leave it as text. A within-PDF
  `\ref` is impossible unless IA is bound into the same document (it isn't). Likely: `\href` to the URL, or leave
  plain.
- **EPUB:** same as HTML but the IA book is a *different* EPUB — an inter-EPUB link isn't reliable across readers.
  Likely: link to the configurable web URL (opens a browser), or leave plain.
- Decide these once the HTML approach + IA base URL are settled; they share the same lookup and base-URL config.

## Resolved / dependency

- **Decision (2026-09-03):** parked — leave as plain text; not publishing at known URLs yet (open questions
  below resolved by this).
- **Unblocked by publishing.** This becomes actionable once the books are published at known URLs — tracked in
  **[[openstax-publish-books]]** (`tasks/openstax-publish-books.md`), which will settle where they live and then
  set the IA base URL. When that lands, implement option (b) here.
