# OpenStax resync — bump content pins to current upstream

**Status:** in progress 2026-10-19 — the 12 behind books' `PIN_SHA`s bumped to upstream HEAD and
committed; per-book build/visual verification is the maintainer's (one canary built in-sandbox).
**Priority:** 5
**Difficulty:** 4 (mechanical bump; the risk is content drift the converter must still handle)
**Created:** 2026-10-19 (William Emerison Six <billsix@gmail.com>, unattended batch: "impo, resync
from upstream sources like you did before, rebasing my patches on upstream")

## BLUF

impo's per-book delta is a **shared toolchain overlay**, not a `git am` patch series (see
`openstax/CLAUDE.md` › "How this family differs from N64"), so an OpenStax resync has **no patch
conflicts** — it is: bump each book's `fetch.sh` `PIN_SHA` to the newer pristine OpenStax content,
and the overlay (`apply.sh` copying `../tooling/`) re-applies unchanged. The only real risk is that
newer CNXML exercises a part of the converter the old pin didn't. "Done for the agent" = the behind
pins bumped + committed; "done overall" = the maintainer builds/eyeballs each book (the analog of
imps' "build + play-test is the maintainer's").

## Recon (2026-10-19, read-only `git ls-remote … HEAD` vs each `fetch.sh` PIN_SHA)

**3 up-to-date, 12 behind** (of 15 OpenStax books; the `trench/` book is separate and untouched):

| book | old pin | upstream HEAD (new pin) |
|---|---|---|
| algebra-1 | 332f7864 | 332f7864 — **UP-TO-DATE** |
| contemporary-mathematics | 2319ce22 | 2319ce22 — **UP-TO-DATE** |
| introduction-python-programming | d215dd3b | d215dd3b — **UP-TO-DATE** |
| anatomy-physiology | 716383a4 | `5ae32b3f4bc24ed003e91dc38bf47dba80751044` |
| astronomy | 2b24b8ee | `dff6acf8df597ceda73985308f838ed38417a606` |
| biology-bundle | 1e74a238 | `89c14e6d065606fdbe1e696ce2e8d9612a080147` |
| calculus-bundle | 9b6c28b2 | `8dbc2ce19e804924b2517b89ac72ee45be949d15` |
| chemistry-bundle | dba91045 | `db0a8e6027100ce082e67fc8879faab86f9a58a7` |
| college-algebra-bundle | 789b5409 | `463991614337632b0e02cbb6c76223cbb0d423d3` |
| microbiology | ecf34dad | `f91d7fcdc7ebbafa36ec33099f78ff0a494f1c2b` |
| organic-chemistry | 2a1f8284 | `8917713cdfb7f74018a8fd43cdcfe3173419bb82` |
| physics | cbf75cb4 | `56e71824e73e371c0d20eb68a77611aa438b5f89` |
| prealgebra-bundle | 98074b2c | `38cae454e644abf9f0a623e876994553881597c9` |
| psychology | 398f5085 | `de7e40c91813dabdc2875df9d0709fc4f46080bb` |
| university-physics-bundle | a33cac5d | `2300d5b8ca2571dacc6ec25ebef56ba8d49000a2` |

Target = upstream **default-branch HEAD** (OpenStax repos have no release tags; the pin is just
"the pristine content the port is built against," now refreshed to current).

## Decisions (agent, unattended batch, 2026-10-19)

1. **Bump to HEAD, commit the bumps.** Authorized by the maintainer for this batch ("commit
   unverified clean bumps"). For the overlay model every bump is "clean" by construction — there is
   no code hunk to conflict. Reversible (revert the commit). The bump is a mechanical codemod,
   `tasks/adhoc/openstax-resync/bump_pins.sh` (idempotent; proven by a second run = no change).
2. **One canary build in-sandbox** (prealgebra-bundle, which already has a local image): fetch the
   new content + overlay + `make convert` (CNXML→LaTeX — the step most likely to break on new
   content). Result recorded below. The other 11 books have **no local image** (building them means
   a full TeXLive image build each) — not attempted; left to the maintainer, matching imps' split.
3. **Historical `fetch.sh` prose left in place.** Some comments describe the old pin as the
   "merge-base where the maintainer's `latex` port branch diverged from main." After the bump the
   pin is upstream HEAD, not that merge-base; a dated resync marker line is inserted directly above
   each `PIN_SHA=` to state the current state, and the historical prose is kept as context for how
   the original pin was chosen. (If the maintainer wants the pin tied to a `latex`-branch merge-base
   rather than bare HEAD — see Open question 1 — these should be re-resolved.)

## Canary result — PASSED (2026-10-19)

prealgebra-bundle at the new pin `38cae454`: `./fetch.sh && ./apply.sh && make convert` ran in the
sandbox (it rebuilt the book image first — the nested `: image` trap — then ran `convert.sh`). The
CNXML→LaTeX converter ingested the current content cleanly and wrote all three masters —
`elementary-algebra-2e.tex` (82 modules), `intermediate-algebra-2e.tex` (83), `prealgebra-2e.tex`
(75) — with the `.converted` stamp. The "Unknown/fallback elements: inline:span/space/label" lines
are the converter's normal fallback handling, not errors; no convert errors. So the bump does not
break the converter for this book. The lualatex PDF and the other 11 books remain the maintainer's
to build (Open question 2).

## Open questions

1. **Is bare upstream HEAD the right target**, or should each pin track a specific stable
   commit / the maintainer's own `latex`-branch merge-base (as the old physics/`fetch.sh` prose
   implies)? Recommend confirming; bumping to HEAD is the literal "resync from upstream" reading and
   is what this task did, but OpenStax `main` is continuously edited, so HEAD can be mid-revision.
2. **Per-book build + visual verification** — the maintainer builds each bumped book (`./fetch.sh &&
   ./apply.sh && make dist`) and eyeballs the PDF/web edition for converter regressions on the new
   content. The 11 un-imaged books especially.

## See also

- `openstax/CLAUDE.md` — the overlay ("apply = overlay, not `git am`") + content model.
- `tasks/openstax-build-refresh-overlay.md` — the related overlay-staleness trap (a build must
  re-apply the overlay).
- `tasks/adhoc/openstax-resync/bump_pins.sh` — the idempotent pin-bump codemod used here.
