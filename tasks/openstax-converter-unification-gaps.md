# OpenStax converter unification — gaps between the shared toolchain and the original per-book converters

**Status:** in progress — content + HTML gaps DONE 2026-09-03; #4 (font robustness), #5 (calculus theme), and the `\crefname{exercise}` warning remain
**Priority:** 2
**Difficulty:** 4

## Progress (2026-09-03)

- **Gap #3 (exercise scheme) — DONE.** Converter + fetcher handle both `#exercise/` and `#ost/api/ex/`;
  physics (846) and biology (2337) exercises fetched, caches committed with COPYRIGHT, PDFs rebuilt and
  verified (physics +149pp, biology AP +515pp). Audit confirmed only these two books were affected.
  Commits `1054cda`, `2a07faf`, `e37639b`.
- **`\unicode[<font>]{x<HEX>}` — DONE** (found remediating biology AP: a fatal `! Undefined control
  sequence` on `\unicode[Arial]{x3B2}`). Translated to the raw codepoint (unicode-math + STIX render it).
  Commit `438696f`.
- **Gap #6 (`oscode`→verbatim for HTML/EPUB) — DONE** (in the HTML-fix commit `0e245cf`, with the
  collapsible-answer + multicols-number fixes from [[openstax-html-exercise-rendering]]).
- **Gaps #1, #2 (code blocks, math-in-titles) — already DONE** as build-all fixes.

- **Gap #5 (calculus Times+blue theme) — DONE 2026-09-03.** Per-book style hook for BOTH editions:
  - **PDF:** `osbook.cls` `\InputIfFileExists{osbook-bookstyle.tex}`; apply.sh copies a book's
    `bookstyle.tex`. calculus ships Times + navy. 3 volumes rebuilt + verified. Commit `684c871`.
  - **Web (HTML/EPUB):** `html.sh`/`epub.sh` append a per-book `bookstyle-web.css` (its `:root` wins);
    apply.sh copies it into the checkout. calculus ships navy `#233A67` + Times body. Verified the
    calculus HTML css ends with the navy override winning. Commit `fe94ce3`. (The web edition was
    initially PDF-only — caught when the maintainer checked the calculus HTML.)
- **`\crefname{exercise}` — DONE 2026-09-03** (`789c67c`).

### Still remaining (one item, low priority)

- **Gap #4 — `osbook.cls` `\DeclareOldFontCommand`** (belt-and-braces for `{\rm}` in chem formulae).
  **Deliberately DEFERRED** (William Emerison Six <billsix@gmail.com>, 2026-09-03): the converter's
  `{\rm X}`→`{\mathrm X}` substitution already handles every observed case, so this is speculative
  robustness whose only cost is re-verifying all 16 books. Do it only if an un-stripped `{\rm}` case
  ever surfaces.

## BLUF

The 16 OpenStax `latex`-branch source repos did **not** share one converter — `tools/cnxml2tex/convert.py`
existed in **5 distinct versions**, with further divergence in `preprocess.py`, `fetch_exercises.py`, and
`osbook.cls`. impo hoisted a **single** shared toolchain (`openstax/tooling/`) that is a *superset* for two
of the divergences but **silently omits three others**. The serious one is a **content-loss bug**: impo's
converter only recognizes the `#exercise/<nickname>` os-embed scheme, so **physics (75 modules) and
biology (167 modules), which use the `#ost/api/ex/<id>` scheme, have ALL their practice exercises silently
dropped** from the built PDFs — the build reports 0 errors because unrecognized links just don't render.
"Done" = the shared converter handles every scheme/feature the per-book originals did (or provides a
per-book hook where the divergence is genuinely book-specific), physics + biology exercises are fetched
and appear, and the gap table below is all green.

## Context

**Read first:** `openstax/CLAUDE.md` (the family contract — note its **incorrect** claim, to be fixed, that
"the core files … are byte-identical; the only per-book variation was the hardcoded book slug"),
`openstax/tooling/tools/cnxml2tex/convert.py`, `.../fetch_exercises.py`, `openstax/tooling/latex/osbook.cls`,
`tasks/build-all-books.md` (the build-all run that produced the 3 converter fixes referenced below).

**How this was found (2026-09-03):** the maintainer recalled the per-book converters differing. Verified by
hashing the core toolchain files across all 16 source repos' `latex` branches (at `/foo/opt/openstax/osbooks-*`,
an upstream-only read-only checkout — the `latex` branch is the maintainer's own work):

| File | distinct versions | who diverges |
|------|------|------|
| `tools/cnxml2tex/convert.py` | **5** | physics, organic-chemistry, python-programming, biology-bundle each unique; other 12 share one |
| `tools/pandoc/preprocess.py` | 2 | introduction-python-programming |
| `tools/cnxml2tex/fetch_exercises.py` | 2 | biology-bundle, physics |
| `latex/osbook.cls` | 3 | biology+organic share one; calculus-bundle another; other 13 the majority |
| `latex/osbook-envs.sty` | 2 | introduction-python-programming |
| `latex/osbook-defer.sty` | 1 | (identical everywhere) |

impo's `convert.py` is `3afeb88…`, **2930 lines — larger than every original** (majority 2856, physics 2863,
organic 2873, python 2906, biology 2889): a merged superset, but incomplete.

## The gap table — what each divergence was, and impo's coverage

| # | Divergence (what the per-book original added) | Books | impo status | Impact |
|---|---|---|---|---|
| 1 | `_pdfsafe(title)` — wrap math-bearing headings in `\texorpdfstring` (else hyperref aborts on `$…$` in a bookmark) | organic, biology | ✅ **HAS** — re-derived as build-all **fix #2** | none |
| 2 | `render_code_block` — multi-line `<code>` → a verbatim block env (inline `\texttt` can't hold a paragraph) | python | ✅ **HAS** — re-derived as build-all **fix #1** (`oscode` env) | none in PDF (but see #6 for HTML/EPUB) |
| 3 | **2nd os-embed scheme** — `convert.py` + `fetch_exercises.py` recognize BOTH `#exercise/<nickname>` (query `nickname:`) AND `#ost/api/ex/<id>` (query `tag:`) | physics, biology | ❌ **MISSING** | **SILENT CONTENT LOSS: physics (75 modules) + biology (167 modules) drop every practice exercise** |
| 4 | `osbook.cls` `\DeclareOldFontCommand{\rm}{…}{\mathrm}` (+ `\bf \it \sf \tt \cal`) — the robust fix for obsolete `{\rm}` font switches in Exercises-API/MathML chem formulae, working for multi-letter groups like `{\rm CH}` in both text and math | organic, biology | ⚠️ **DIFFERENT approach** — build-all **fix #3** does a `{\rm X}`→`{\mathrm X}` substitution in `convert.py` instead | organic built clean, so covered in practice; the `.cls` form is strictly more general (a naive swap breaks some multi-letter/text-mode cases) — robustness risk if such a case appears |
| 5 | `osbook.cls` calculus theme — `\setmainfont{TeX Gyre Termes}` (a Times face) + a **blue** palette sampled from the official Calculus PDF | calculus | ❌ **MISSING** — impo uses the majority `.cls` (Roboto Slab + algebra-1 **teal** palette) | cosmetic: the 3 calculus volumes build, but with the generic theme, not the maintainer's calculus-specific Times+blue styling |
| 6 | `preprocess.py` `codeblock`→`verbatim` rename so pandoc (HTML/EPUB) reads the code env | python | ❌ **MISSING** — and impo renamed the env to `oscode`, so even the original rename wouldn't match | python-programming HTML/EPUB likely drop code blocks (pandoc doesn't know `oscode`). Affects the HTML/EPUB build-out, not PDF |

**Anchors for the content bug (#3):** impo `convert.py:1784` still reads `if not url.startswith("#exercise/"):`
(nickname-only); `convert.py:1794` returns `url[len("#exercise/"):]`. impo `fetch_exercises.py` has
`discover_nicknames()` (nickname-only), not the originals' `discover_targets()` returning `nickname:`/`tag:`
queries. Raw-CNXML proof: `grep -rl '#ost/api/ex/' checkout/modules` → physics 75, biology 167;
`grep -rl 'url="#exercise/'` → 0 for both.

## Was there a way to unify the differences? (the maintainer's question)

Yes — and impo mostly did. The divergences split into two kinds, unified differently:

- **Logic divergences (schemes, math-in-titles, code blocks: #1–#4).** These are *feature detection*, and the
  right unification is a converter that handles **all** variants — exactly what the physics/biology originals
  already modeled with `discover_targets()` returning both `nickname:` and `tag:` queries. impo captured #1,
  #2, #4 (mostly) but not #3. Fixing #3 = port the ~15-line both-schemes branch into impo's `convert.py`
  (`_os_embed_nickname` → return the key for either prefix) and `fetch_exercises.py` (`discover_nicknames`
  → `discover_targets`, `fetch_one(key, query)`). This is pure superset merge; no per-book config needed.
- **Presentation divergence (calculus font+palette: #5).** This is genuinely book-specific and does NOT
  belong in a universal converter. The clean unification is a **per-book style hook**: the shared `osbook.cls`
  `\InputIfFileExists{book-style.tex}` (or reads a `\definecolor`/`\setmainfont` fragment the book folder
  provides), defaulting to the current Roboto-Slab-teal theme. Then calculus ships a 4-line `book-style.tex`
  and every other book ships nothing. This keeps the toolchain shared while letting a book override its theme.

## Proposed fix (do NOT start until the open questions are answered)

1. **Content bug #3 (highest value):** port both-scheme handling into impo `convert.py` + `fetch_exercises.py`
   from the physics original; add converter unit tests for both prefixes; `make fetch-exercises` for physics +
   biology, commit the caches **with their `COPYRIGHT` NOTICE**; rebuild both PDFs; confirm exercises now
   render and page counts grow.
2. **HTML/EPUB #6:** make impo `preprocess.py` rename `oscode`→`verbatim` (mirroring the original
   `codeblock`→`verbatim`); rebuild python-programming HTML/EPUB; confirm code blocks survive.
3. **Robustness #4:** add the `\DeclareOldFontCommand` block to the shared `osbook.cls` (belt-and-braces
   alongside the existing convert.py substitution); it's harmless for books without such formulae.
4. **Calculus theme #5:** add the `\InputIfFileExists{book-style.tex}` hook to `osbook.cls`; ship calculus's
   Times+blue `book-style.tex`; rebuild the 3 calculus volumes and eyeball the theme.
5. **Fix the `openstax/CLAUDE.md` "byte-identical" claim** — replace it with "the originals had 5 converter
   versions; the shared toolchain merges them (see this task / its archived record)."
6. Re-verify **all 16** still build after the shared-file edits (a converter change touches every book).

## Open questions

1. **Scope now vs. later:** fix all four gaps (#3, #4, #5, #6) as one unit, or just the content bug (#3,
   physics+biology exercises) now and task the rest? *Recommend #3 now (it's silent content loss and the
   maintainer's stated rule is "a book should have all of its content"), with #4–#6 in the same task but
   done second.*
2. **Calculus theme mechanism (#5):** is the `\InputIfFileExists{book-style.tex}` per-book hook the design
   you want, or would you rather each book carry its own full `osbook.cls`? *Recommend the hook — keeps one
   shared class, lets a book override only font+palette.*
3. **Are there MORE divergent books than the four?** I compared the 5 convert.py versions but only fully
   diffed the 4 non-majority ones; the "majority" 12 are byte-identical to each other, so no — but if you
   recall a book with special handling beyond these, name it and I'll check.
