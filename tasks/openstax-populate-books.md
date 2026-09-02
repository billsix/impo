# Populate the OpenStax family — the 16 osbooks-* books, on the shared-toolchain pattern

**Status:** scaffolding done; representative subset build-verified; large caches deferred (2026-09-02,
autonomous — maintainer away, "use your discretion, log decisions, talk later"). All 16 folders now
exist. Done vs deferred:
- **Phase A (done):** all 15 remaining book folders scaffolded on the pilot pattern (`fetch.sh` with
  full 40-char pins, generic `apply.sh` that also injects a committed `exercises/` cache, thin
  `Makefile`, `README.md`, `.gitignore`, per-book `CLAUDE.md`). `bash -n` clean; Makefiles differ from
  anatomy's only in `CONTAINER_NAME` + header. Generator saved at
  `tasks/adhoc/openstax-populate-books/scaffold.sh`. Committed.
- **Phase B (done):** build-verified the subset **astronomy** (toolchain-only), **algebra-1** (SVG book),
  **introduction-python-programming** (downloads). For each: `fetch.sh` (pin fetchable from GitHub by
  SHA — assumption confirmed), `apply.sh`, `make convert` → LaTeX master generated
  (`astronomy-2e.tex`/199 modules, `algebra-1.tex`/976, `introduction-python-programming.tex`/115).
  **No fixups were needed** — the generic pattern worked across all three book types, so no fixup commit.
- **Phase C (partial by design):** **python-programming** exercises fetched (`make fetch-exercises`,
  613 questions, 0 images, 5.5M), committed with a `COPYRIGHT` NOTICE; injection verified end-to-end
  (the 607 `exercise-uncached` fallbacks resolve after apply+reconvert). **All other download books
  deferred** (see Open items) — no unattended bulk-commit of thousands of binaries.
**Priority:** 3
**Difficulty:** 6
**Created:** 2026-09-02 (William Emerison Six <billsix@gmail.com>).

## BLUF

Bring all 16 OpenStax LaTeX-port books into `imps/openstax/` on the shared-toolchain contract
(`openstax/CLAUDE.md`): each book = a thin folder (`fetch.sh` pinning pristine OpenStax content →
`checkout/`, `apply.sh` overlaying the shared `../tooling/`, a thin `Makefile`, `CLAUDE.md`,
`README.md`, `.gitignore`), plus — for books that embed `os-embed` exercises — a committed
`exercises/` download cache **with a `COPYRIGHT` NOTICE** (© OpenStax, CC BY 4.0, not the maintainer's).
The anatomy-physiology pilot is the verified template. "Done" = all 16 folders exist, wiring verified
(bash -n, fetch+apply), a representative subset build-verified (image+convert, ideally a PDF), and the
downloaded content committed with copyright marking.

## Design (decided; full contract in `openstax/CLAUDE.md`)

Maintainer-approved decisions (2026-09-02):
1. **Carrier:** shared toolchain in `openstax/tooling/` (not 16 patch copies); a book's "apply" is an
   **overlay of `../tooling/`** onto the pinned checkout, not `git am`. Downloaded content is a
   **committed subtree** in the book folder (not binary patches).
2. **Downloaded content IS tracked** ("a book should have all its content") **+ a redownload script**
   (`tools/cnxml2tex/fetch_exercises.py`, already in the toolchain) — with a **COPYRIGHT NOTICE** so
   no one mistakes OpenStax's images/problem sets for the maintainer's work.
3. **Full container build** contract (`make image/convert/pdf/html/epub/dist`).
4. **All-personal family** — a LaTeX conversion is never upstreamed, so no upstream-submission tier.

## The 16 books (survey 2026-09-02: pin = merge-base of `latex` vs `main`; delta = latex-branch files)

| Book | pin (merge-base) | latex commits | delta files | has downloads? |
|---|---|---|---|---|
| osbooks-anatomy-physiology | 716383a4c6 | 5 | 27 | no (PILOT — done) |
| osbooks-astronomy | 2b24b8eeb4 | 5 | 27 | no |
| osbooks-chemistry-bundle | dba91045bc | 7 | 27 | no |
| osbooks-microbiology | ecf34dad12 | 6 | 27 | no |
| osbooks-psychology | 398f50856c | 6 | 27 | no |
| osbooks-university-physics-bundle | a33cac5de6 | 6 | 27 | no |
| osbooks-college-algebra-bundle | 789b540991 | 9 | 46 | small |
| osbooks-prealgebra-bundle | 98074b2c4c | 9 | 48 | small |
| osbooks-calculus-bundle | 9b6c28b21c | 9 | 53 | small |
| osbooks-writing-guide | 7312ec11c4 | 6 | 209 | some |
| osbooks-introduction-python-programming | d215dd3b99 | 7 | 641 | yes |
| osbooks-physics | cbf75cb4a1 | 7 | 904 | yes |
| osbooks-algebra-1 | 332f786470 | 9 | 1268 | yes (+ SVG figures) |
| osbooks-biology-bundle | 1e74a23833 | 8 | 2723 | yes (large) |
| osbooks-contemporary-mathematics | 2319ce2265 | 8 | 3692 | yes (large) |
| osbooks-organic-chemistry | 2a1f82843a | 7 | 4062 | yes (2076 jpg + 1959 json) |

(The 6 "no-download" 27-file books are toolchain-only — the easiest. The big ones are big *only*
because of downloaded exercise content; the toolchain itself is identical across all.)

## Per-book procedure (from the anatomy template)

1. `openstax/osbooks-<name>/` with `fetch.sh` (upstream `https://github.com/openstax/<name>`, verify
   the pin is fetchable there — Pi mirror `pi@192.168.0.186:.../openstax/**/<name>.git` is the
   fallback), `apply.sh` (overlay `../tooling/`, + copy any committed `exercises/` into the checkout),
   `Makefile` (`CONTAINER_NAME=<name>`, otherwise identical to anatomy's), `CLAUDE.md`, `README.md`,
   `.gitignore` (`checkout/`, `output/`, `*.tar`).
2. **Books with `os-embed` exercises:** `make fetch-exercises` once (network), then commit
   `exercises/` (JSON + `exercises/media/`) **with a top-level `COPYRIGHT`** copied from
   `openstax/tooling/templates/exercises-COPYRIGHT`. (Verify per book whether the delta's images are
   downloaded exercise images vs upstream `media/` figures — only the *downloaded* ones belong in the
   committed cache.)
3. **SVG-figure books (algebra-1):** the toolchain's `pdf.sh` already rasterizes `media/*.svg`→PDF and
   `exercises/media/*.svg`→PNG — no extra work, but the first PDF build is heavier.

## Decisions I am making autonomously (for later review)

- **Upstream = canonical `github.com/openstax/<name>`** at the surveyed pin; Pi mirror is the
  documented fallback. Rationale: imps references canonical URLs; the pins are OpenStax `main` history,
  fetchable from GitHub.
- **Build verification is a REPRESENTATIVE SUBSET, not all 16.** Each book's image is the same shared
  TeX Live layer set (podman layer-cache makes builds 2..16 fast), but a full ~1000–1849pp lualatex
  compile per book is too much to run for all 16 unattended. Plan: build-verify anatomy (pilot) + one
  download+exercises book + the SVG book (algebra-1); the rest are **structure+wiring verified**
  (bash -n, fetch+apply, `make convert`) with the full PDF left for the maintainer / a later pass.
  Each book's `CLAUDE.md` will state exactly what was verified.
- **Committing large download caches:** per decision 2 the downloaded exercises/images are committed.
  For the large books (organic-chem ~2k images, biology/contemporary-math) this adds real binary bulk
  to imps — **flagged here** as the one consequential-but-authorized action; done because the
  maintainer explicitly asked for the content tracked. If on review this is unwanted, the alternative
  is caching them out-of-band and keeping only the fetch script — easy to switch, since the fetch
  script is the source of truth either way.
- **Image tag is per-book** (`osbooks-<name>`) matching the pilot; layers are shared via podman's
  cache so this costs ~one image on disk. (A single shared `openstax-tooling` tag would be marginally
  cleaner; not worth diverging the pilot for.)

## Open items / to discuss later

- **Deferred download caches — await a deliberate `make fetch-exercises` + commit, flagged for
  maintainer review because of the binary bulk added to imps.** Not run unattended. The books with
  `os-embed` exercises that were left structure-only: `college-algebra-bundle`, `prealgebra-bundle`,
  `calculus-bundle` (small), `writing-guide`, `physics`, `algebra-1` (+ SVG figures), and **especially
  the three large ones** — `biology-bundle`, `contemporary-mathematics`, and `organic-chemistry`
  (~2076 jpg + 1959 json). For each: `./fetch.sh && ./apply.sh && make fetch-exercises`, then copy
  `checkout/exercises/` (JSON + any `media/`) up to the book folder's `exercises/` with a `COPYRIGHT`
  copied from `openstax/tooling/templates/exercises-COPYRIGHT`, and commit — exactly as done for
  python-programming. (Per-book, verify the delta's images are *downloaded* exercise images, not
  upstream `media/` figures — only the downloaded ones belong in the committed cache.)
- Whether to build-verify all 16 PDFs (heavy) or accept the representative-subset + structure
  verification above.
- The large-download commit-bulk decision (see above): if unwanted on review, the alternative is
  caching them out-of-band and keeping only the fetch script — the fetch script is the source of truth
  either way.
- The N64 stale-doc pass (separate, authorized "as I see fit"): update the pre-torch ocarina
  asset-pipeline/build-system docs and the mario64 hooks→events docs against the current pins; fix the
  5 pre-existing broken `../../CLAUDE.md`/`wiki/`/`docs/` links in the mario64 reference docs.

## Relationships

- `openstax/CLAUDE.md` — the family contract (canonical design).
- `tasks/imps-family-folder-restructure.md` — the restructure + OpenStax survey that led here.
- `openstax/osbooks-anatomy-physiology/` — the verified pilot / template.
