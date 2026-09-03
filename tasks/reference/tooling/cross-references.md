# Cross-references & internal links in the OpenStax web edition — how they work, and what can't be auto-linked

**Reference doc — living, never archived.** How the toolchain turns OpenStax cross-references into links (PDF and
HTML), what is and isn't linked, and why auto-linking the *literal-text* references is not viable as things stand.
Written 2026-09-03 from the internal-ref investigation (archived task:
`tasks/archive/impo/2026/09/03/openstax-html-autolink-internal-refs.md`). Companion: `converters.md` (the
converter itself), and `openstax/CLAUDE.md`.

## How a cross-reference becomes a link

OpenStax CNXML marks a real cross-reference as `<link target-id="…" [document="…"]>`. The pipeline:

1. **Converter** (`tools/cnxml2tex/convert.py`): a `<link target-id>` → `\cref{<module-scoped label>}` (see
   `link_label()` / `_ALL_TARGETS`, and the inline-link handler ~line 1440). The target's `\label` is emitted on
   the figure/section/theorem/etc.
2. **PDF**: `cleveref` resolves `\cref{…}` to the numbered, hyperlinked reference ("Figure 3.1", "Equation (3.2)")
   at LaTeX time. Works out of the box.
3. **HTML**: pandoc does NOT run LaTeX, so `\cref` would be inert — **`tools/pandoc/xref.lua` handles it**: a
   first pass records `labels[id] = "Figure 3.1"` from the numbered environments/figures, and a **second pass
   rewrites each `\cref` link into a real `pandoc.Link`** whose text is the target's number (`xref.lua:131-135`).
   Verified: **no raw `\cref{}` survives in the built HTML** — properly-marked cross-refs ARE hyperlinks.

So: **any reference the source author marked up with `<link>` is already a working link in both PDF and HTML.**
Nothing to do there.

## What is NOT linked: literal-text references (and why auto-linking them isn't viable)

Some references are written as **plain text** in the CNXML — "as discussed in Section 1.5", "the street map in
Figure 10.6" — with no `<link>`. These render as text. The 2026-09-03 investigation asked whether they can be
auto-linked. Findings (all 16 books' built HTML):

- **The scale is misleading.** ~24,100 occurrences of `<Kind> N` text look unlinked, but **~99% are LABELS, not
  references** — figure captions ("Figure 1.1."), example headings ("Example 1.1.") — the item itself, which must
  never become a self-link. They sit in `envhead`/caption spans. Excluding those, the real prose references are
  **~335** total (Section 182, Figure 84, Example 30, Table 26, Equation 13), concentrated in
  organic-chemistry (138, many low-value changelog notes), writing-guide (89), contemporary-mathematics (54).
- **They can't be resolved safely.** A prototype linker (`build_xref_links.py`, see below) — two passes, lxml
  text-node-only rewriting, "only link when the number resolves in this book" safety net — was **safe** (0
  broken/empty hrefs, 0 labels turned into links, no mangling) but resolved **~1–4 refs per book**, because:
  - **Section refs use a different numbering than the sitemap.** writing-guide prose says "Section 9.6", but its
    sitemap sections are numbered `9`, `9.0.1`, … — there is no `9.6`. The literal-text scheme ≠ the structural
    scheme, so the number can't be mapped to a page.
  - **Figures have no `id` anchor in the HTML.** `<div class="calcfig">` carries no id, so a "Figure 10.6" prose
    ref has nothing to point at — the figure→anchor map came back empty on contemporary-mathematics.
- **Decision: not shipped.** A build step that links 1–4 refs per book isn't worth its cost, and the
  properly-referenced links already work. The `(IA x.y.z)` *cross-book* refs are a separate, deliberately-parked
  case (`tasks/openstax-ia-crossref-links.md`).

## The prototype, and what a revival would need

`build_xref_links.py` (kept at `tasks/adhoc/openstax-autolink-internal-refs/`, first committed in `9390245`) is a
correct, safe linker held back only by the two data problems above. To make literal-text auto-linking worthwhile,
the toolchain would first need:

1. **Stable `id`s on every figure / table / example / equation** (so figure-style refs have a target). This is a
   converter/xref.lua change: emit the `\label` id onto the rendered element in a form pandoc keeps as an `id`.
2. **Section-number reconciliation** — a map from the literal-text section scheme (e.g. "9.6") to the actual
   section pages, since the prose numbering doesn't match the sitemap's. May be book-specific and is the harder
   half.

Both are non-trivial for a ~335-ref payoff; revisit only if the converter grows figure ids for another reason.

## Rules of thumb

- A reference that should be a link and isn't is almost always because **the CNXML used plain text, not
  `<link>`** — an upstream authoring gap, not a converter bug. Don't "fix" it by regex-linking text; the
  numbering/anchor mismatches make that unreliable (above).
- When touching `xref.lua`, keep the two-pass shape: you can only rewrite a `\cref` after the label→number map is
  built from the whole collection.
- Cross-*book* references (a different book entirely, e.g. `(IA x.y.z)` = Intermediate Algebra) can't be links
  until the books are published at known URLs — see `tasks/openstax-publish-books.md`.
