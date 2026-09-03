# Build all 16 OpenStax books to PDF — results

**Status:** done (2026-09-03)
**Priority:** 2
**Difficulty:** 6

## BLUF

All **16** `openstax/osbooks-*` books were seeded from the local mirror at their
pinned SHA, overlaid with the shared toolchain (`openstax/tooling/`), converted
CNXML→LaTeX, and compiled with lualatex. **Every book produced a correct PDF** —
**28 collection masters total** (10 single-collection books + 6 multi-collection
bundles), all with **0 LaTeX errors** and page counts > 0. Three shared-toolchain
converter/style bugs were found and fixed along the way (commit `dc9f99c`); no
book-specific fixes were needed.

## Context

- Family contract: `openstax/CLAUDE.md`. Per book: `cd openstax/osbooks-<name>`,
  seed `checkout/` from `/foo/opt/openstax/<name>` at `PIN_SHA`, `./apply.sh`,
  then `NESTED_PODMAN=1 make pdf`. Outputs land in `checkout/output/*.pdf`
  (gitignored — build artifacts, never committed).
- The container image (`../tooling/Dockerfile`) is shared by all books and was
  pre-cached; it rebuilds (fast) whenever `tooling/tools/` changes, re-running its
  gate (`ty check tools/` + the 27 converter pytest tests) — which stayed green
  after every fix.
- Build driver used: `scratchpad/build_book.sh` (seed already done; runs
  `make pdf`, then records page count + `^! ` LaTeX-error count per master).

## Results

| Book | Master PDF(s) | Pages | LaTeX errors | Fix |
|------|---------------|-------|--------------|-----|
| anatomy-physiology | anatomy-and-physiology-2e | 1849 | 0 | — |
| astronomy | astronomy-2e | 1328 | 0 | — |
| chemistry-bundle | chemistry-2e | 1424 | 0 | — |
| chemistry-bundle | chemistry-atoms-first-2e | 1433 | 0 | — |
| microbiology | microbiology | 1576 | 0 | — |
| psychology | psychology-2e | 981 | 0 | — |
| university-physics-bundle | university-physics-volume-1 | 1219 | 0 | — |
| university-physics-bundle | university-physics-volume-2 | 1005 | 0 | — |
| university-physics-bundle | university-physics-volume-3 | 750 | 0 | — |
| college-algebra-bundle | algebra-and-trigonometry-2e | 2291 | 0 | — |
| college-algebra-bundle | college-algebra-2e | 1708 | 0 | — |
| college-algebra-bundle | college-algebra-corequisite-support-2e | 1708 | 0 | — |
| college-algebra-bundle | precalculus-2e | 2095 | 0 | — |
| prealgebra-bundle | elementary-algebra-2e | 1852 | 0 | — |
| prealgebra-bundle | intermediate-algebra-2e | 1929 | 0 | — |
| prealgebra-bundle | prealgebra-2e | 1708 | 0 | — |
| calculus-bundle | calculus-volume-1 | 986 | 0 | — |
| calculus-bundle | calculus-volume-2 | 924 | 0 | — |
| calculus-bundle | calculus-volume-3 | 1156 | 0 | — |
| writing-guide | writing-guide | 824 | 0 | — |
| introduction-python-programming | introduction-python-programming | 268 | 0 | **fix 1** (dc9f99c) |
| physics | physics | 1112 | 0 | — |
| algebra-1 | algebra-1 | 2290 | 0 | — |
| biology-bundle | biology-2e | 2147 | 0 | — |
| biology-bundle | biology-ap-courses | 1831 | 0 | — |
| biology-bundle | concepts-biology | 844 | 0 | — |
| contemporary-mathematics | contemporary-mathematics | 1780 | 0 | — |
| organic-chemistry | organic-chemistry | 1588 | 0 | **fix 2, 3** (dc9f99c) |

**28/28 masters built, 0 LaTeX errors.**

## Fixes made (all shared-toolchain, commit `dc9f99c`)

All three are book-agnostic converter/style bugs in `openstax/tooling/`, so one
fix each covers all 16 books.

1. **Multi-line `<code>` blocks** (found on introduction-python-programming).
   Program listings were emitted as inline `\texttt{...}`, which cannot span a
   paragraph break → fatal `Paragraph ended before \text@command was complete`.
   Now a multi-line `<code>` (via `<newline/>` sentinels *or* literal newlines)
   renders as a display listing in a new house `oscode` environment
   (`osbook-envs.sty`), registered in `convert.py`'s `_NOWRAP_ENVS`.

2. **Math in section/module titles** (found on organic-chemistry). Inline math in
   a heading broke hyperref's PDF bookmark → fatal `Improper alphabetic constant`.
   A title with math is now wrapped once as `\texorpdfstring{<title>}{<ascii>}`
   (visible heading keeps the math; bookmark uses a plain ASCII rendering).
   Applied at both `render_section` and the module-heading path.

3. **Obsolete `{\rm X}` font declaration in passthrough math** (found on
   organic-chemistry NMR formulas). memoir disables `\rm`/`\bf`/`\it`/… → fatal
   `Font command \rm is not supported`. The existing map only handled the argument
   form `\rm{X}`; the declaration form `{\rm CONTENT} → {\mathrm{CONTENT}}` is now
   handled too.

## Known cosmetic caveat (not a build failure)

Several books emit non-fatal `Missing character` warnings — a specific glyph
(e.g. `↓` U+2193, some arrows/symbols) absent from a specific font (Roboto Slab),
so it is silently dropped or substituted; latexmk still exits 0 and the PDF is
produced. Counts range from a handful (astronomy 4, contemporary-math 7) to many
in symbol-heavy books (organic-chemistry ~1330, university-physics ~1028,
biology ~737). These are pre-existing font-coverage gaps, independent of this
build pass — worth a later toolchain pass (widen the math/symbol font fallback)
but not blocking any PDF.

## Reproduce

```
cd openstax/osbooks-<name>
# seed checkout/ from the mirror at the pin (offline):
pin=$(grep -oE 'PIN_SHA=[0-9a-f]+' fetch.sh|cut -d= -f2)
mkdir -p checkout && git -C /foo/opt/openstax/osbooks-<name> archive "$pin" \
  collections modules media | tar -x -C checkout
(cd checkout && git init -q && git config commit.gpgsign false)
./apply.sh
NESTED_PODMAN=1 make pdf         # -> checkout/output/*.pdf
```
