# Auto-link literal-text internal references (Figure/Table/Example/Section/Equation N) in the HTML

**Status:** PROTOTYPED, NOT SHIPPED 2026-09-03 — the literal-text refs can't be reliably resolved; not worth a build step. See "Outcome".
**Priority:** 8
**Difficulty:** 5

**Durable write-up:** `tasks/reference/tooling/cross-references.md` (how cross-refs work + this investigation +
what a revival needs). The prototype `build_xref_links.py` is kept under `tasks/adhoc/` (not deleted — it's the
revival starting point the reference doc points at).

## Outcome (2026-09-03) — built a safe linker, but it can't resolve the refs; parked

Built `build_xref_links.py` (a two-pass, lxml-based, safety-netted linker — kept at
`tasks/adhoc/openstax-autolink-internal-refs/build_xref_links.py`) and tested it on the ref-heavy books. It is
**safe** (0 broken/empty hrefs, 0 labels/captions turned into links, no HTML mangling), but **recall is
near-zero** because the literal-text refs don't resolve to real targets:

- **Section refs** use a numbering the sitemap doesn't carry: writing-guide prose says "Section 9.6", but its
  sitemap sections are numbered `9`, `9.0.1`, … — no `9.6`. So `Section 9.6` matches nothing (correctly left as
  text). Only ~1 per book resolves.
- **Figure refs** have no target: figures render without an `id` anchor in the HTML (the `<div class="calcfig">`
  has none), so there's nothing to link to — the figure map came back **empty** on contemporary-mathematics.

**Decision: don't ship** a build step that links ~1–4 refs per book. The properly-marked-up cross-references
(`<link target-id>` → `\cref` → xref.lua) are already links; the residual literal-text refs the authors wrote
can't be safely auto-resolved as things stand. **To revive** this it would need: (a) the converter to emit a
stable `id` on every figure/table/example (so figure refs have a target), AND (b) a numbering reconciliation for
section refs (the ref scheme ≠ the sitemap scheme) — both non-trivial, for a small payoff. The prototype +
this analysis are preserved for that day.

## BLUF

Some in-book references render as **plain text** in the HTML — e.g. "as discussed in Section 1.5", "the street
map in Figure 10.6" — instead of hyperlinks. The properly-marked-up cross-references (CNXML `<link target-id>`)
are **already** hyperlinked (converter → `\cref` → xref.lua rewrites them to real HTML links). The gap is
references the source author wrote as literal text. This task auto-links those **safely**: build a per-book map
of displayed numbers → anchors from the HTML's own figure/example/table labels (+ the sitemap for sections), then
turn matching prose text into links — **only when the target number actually exists in the book** (so no broken
or cross-book links). "Done" = genuine literal-text internal refs become links across the books, with zero wrong
links introduced.

## Investigation (2026-09-03) — the numbers

Scanning all 16 books' built HTML for `(Figure|Table|Example|Section|Equation|Chapter) N`:
- **24,103** total occurrences of unlinked reference-text — BUT **~99% are LABELS**, not references: figure
  captions ("Figure 1.1."), example headings ("Example 1.1.") — the item itself, which must NOT become a
  self-link. (Confirmed by context: they sit in `envhead`/caption spans.)
- Excluding label spans, the real **prose references** are **~335** total. Breakdown: Section 182 (mostly
  organic-chemistry 86 changelog notes + writing-guide 76 real refs), Figure 84, Example 30, Table 26,
  Equation 13. Concentrated in contemporary-mathematics (54), organic-chemistry (138), writing-guide (89).
- Genuine, worth linking (samples): writing-guide "as discussed in Section 1.5", contemporary-math "the street
  map in Figure 10.6", "Using Figure 10.58". Low-value: organic-chemistry's preface changelog ("Section 17.5:
  Added coverage of…") — technically linkable but not navigational; harmless if linked, skip if easy.

## Design — a safe book-wide post-process (like build_nav.py)

A `build_xref_links.py`, run by `html.sh` after `build_nav.py`, per book-site:
1. **Pass 1 — build the number→target map** from the book's own rendered HTML + sitemap:
   - Figures/Examples/Tables/Equations: their label spans carry the displayed number ("Figure 10.6.") and the
     element has an `id` anchor → map `"Figure 10.6" -> page#anchor`. (These labels + anchors are emitted by
     xref.lua; scan every page.)
   - Sections: `"Section x.y" -> page` from `sitemap.json` (section number → page).
2. **Pass 2 — link matching prose.** In each page's body prose (NOT inside existing `<a>`, NOT inside a label
   span/caption/heading), replace `Figure 10.6` / `Section 1.5` / … with `<a href="page#anchor">…</a>` **only
   when the number is in the map**. Unmatched numbers are left as text (the safety net against broken/cross-book
   links). Never touch text already inside a link.

**Safety / discretion:**
- Only link when the exact displayed number resolves within the SAME book → no broken links, cross-book refs
  (e.g. the `(IA x.y.z)` case, [[openstax-ia-crossref-links]]) are naturally skipped.
- Exclude label spans / captions / headings (already anchored; linking = self-link).
- HTML-only; the PDF already links these via cleveref where the source marked them, and literal-text refs there
  are out of scope (see the note in [[openstax-ia-crossref-links]] for the general cross-ref-in-PDF thinking).

## Verify

Rebuild a couple of the ref-heavy books (writing-guide, contemporary-mathematics): the sampled prose refs become
links to the right figure/section; confirm NO label/caption/heading became a link, NO new broken (`#`) links,
and body text is otherwise byte-unchanged except the injected `<a>`s. Then fan out.
