# Links between books: "(IA x.y.z)" references and math-ladder "Prerequisites" boxes

**Done 2026-11-21** for the explicit references and the math ladder (prealgebra → algebra →
college algebra → calculus 1–3). The map awaits the maintainer's review, and physics and the
sciences were explicitly later: follow-on `tasks/openstax-cross-book-prerequisites-review.md`.
Absorbed and closed `tasks/archive/impo/2026/11/21/openstax-ia-crossref-links.md`. Mechanism, data
and findings: `tasks/reference/tooling/cross-book-links.md`.

## Decisions (William Emerison Six <billsix@gmail.com>, 2026-11-21: "go with your recommendations")

- Implicit prerequisites too, as "Review: <book> §x.y" links in a **Prerequisites box** at the top of
  each section (OpenStax prose unchanged), math ladder first, reviewed before physics and sciences.
- PDF/EPUB: absolute `\href` URLs to the published site (`billsix.github.io/impo/`, fixed by
  `tasks/archive/impo/2026/11/21/openstax-publish-books.md`).

## Choices made while building (recorded here; the maintainer was away)

- **Emit the links in the converter's LaTeX**, not only in an HTML post-pass, so one mechanism serves
  all three editions; `html.sh` rewrites the site prefix to `../` for the web edition.
- **A committed page index per book instead of a build-order dependency.** Each book folder's container
  mounts only its own checkout, so a target book's `sitemap.json` cannot be read at convert time; the
  index (`crossbook/index/<book>.json`, from `crossbook_index.py`) is generated from built sites and
  committed. The plan's "target books first" ordering in `build-books.sh` was therefore not added.
- **Official OpenStax section numbers** in the index and the map (the web edition's numbering is one
  higher in chapters that open with an Introduction module; see the reference doc).
- **The map is keyed by book section, applied per module** (modules are shared between editions and
  volumes), as plain text `prerequisites.txt` for easy review.

## What was built

- `openstax/tooling/tools/cnxml2tex/crossbook.py` (+ `crossbook/prerequisites.txt`, 303 entries;
  `crossbook/index/*.json` for prealgebra-2e, elementary-algebra-2e, intermediate-algebra-2e,
  college-algebra-2e, college-algebra-corequisite-support-2e, algebra-and-trigonometry-2e,
  precalculus-2e, calculus-volume-1..3), `crossbook_index.py`; hooked into `convert.py`
  (`convert_module`); `prerequisites` environment in `osbook-envs.sty`, titled in `xref.lua`, styled in
  `osbook-web.css`; `html.sh` relativizes; `tools/tests/test_crossbook.py`.
- Discovery: `tasks/adhoc/openstax-cross-book-references/discover.sh` (the scan of all 16 folders;
  one-shot, removed at archive).

## Verification

- Rebuilt (nested podman, the fresh Fedora-45 image) `osbooks-prealgebra-bundle`,
  `osbooks-college-algebra-bundle` and `osbooks-calculus-bundle`: `apply.sh` → `make convert` →
  `make html`, all exit 0 (10 web editions). The boxes render (e.g. Calculus Volume 1 §1.1 lists
  College Algebra 2e §3.1, §3.2, §3.4) with relative links.
- Link check over those 10 sites side by side (`check_links.py`): 0 broken links, among them 1185
  cross-book links (833 to intermediate-algebra-2e — the IA tags and the College Algebra boxes — 97 to
  prealgebra-2e, 87 to elementary-algebra-2e, 65 to college-algebra-2e, 62 to calculus-volume-1, 28
  to precalculus-2e, 13 to calculus-volume-2).
- PDF: `pdf.sh calculus-volume-1` exit 0 (958 pages); its text has the Prerequisites boxes and
  `pdfinfo -url` lists 65 absolute `https://billsix.github.io/impo/...` link annotations.
- `make -C openstax/tooling type-check` exit 0 (with `test_crossbook.py`: every entry resolves, no box
  points at its own module, the official-numbering case).
- **Not verified:** EPUBs of these books (same LaTeX through pandoc as the HTML; not rebuilt), the PDFs
  of the other nine books, and whether the published-site links resolve on GitHub (nothing is
  published yet).
