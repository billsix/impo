# Sync the OpenStax content pins with upstream (nine books behind, one upstream gone)

**Status:** ready — decisions recorded 2026-11-26; starts on the maintainer's word (recon done, no pin moved)
**Priority:** 5
**Difficulty:** 4 (a mechanical pin bump; the risk is new markup the converter has not met, and one book whose upstream has disappeared)
**Created:** 2026-11-26 (William Emerison Six <billsix@gmail.com>: "do the recon for both … if there's nothing to rebase, then a sync means to just update the pins and make sure everything still works in my project").

## BLUF

Nine of the sixteen OpenStax books are pinned behind their upstream head, six are current, and one (`osbooks-algebra-1`) has an upstream that no longer answers. This task moves the nine pins to upstream head and proves each book still converts and builds. Done means each bumped book's `fetch.sh` carries the new `PIN_SHA`, each has passed `make convert` at the new pin, and all nine have built with `make dist`. The algebra-1 problem is out of scope here: it has its own task, `tasks/openstax-algebra-1-upstream-gone-backup-plan.md`.

## Context

**Read first:** `CLAUDE.md` ("Contracts": what "sync" means here) and `openstax/CLAUDE.md` (the per-book contract: `fetch.sh` → `apply.sh` → build). impo carries no patch series, so nothing is rebased: the delta is the shared toolchain in `openstax/tooling/`, which `apply.sh` copies over a pristine checkout. The previous sync and its method: `tasks/archive/impo/2026/10/20/openstax-resync-upstream-pins.md`. The pin target is the upstream default-branch head (confirmed by the maintainer on 2026-10-20).

**Recon (2026-11-26, read-only).** `git ls-remote <upstream> HEAD` against each `fetch.sh` `PIN_SHA`; the counts come from a blobless bare clone (`git rev-list --count <pin>..HEAD`, `git diff --name-only <pin> HEAD`).

| Book | Pin | Upstream head | Commits behind | Files changed | Of those, `modules/` or `collections/` | Of those, `media/` |
|---|---|---|---|---|---|---|
| anatomy-physiology | `5ae32b3f` | `f2737623` | 5 | 6 | 4 | 1 |
| biology-bundle | `89c14e6d` | `bc1be223` | 72 | 238 | 233 | 3 |
| calculus-bundle | `8dbc2ce1` | `018da4da` | 24 | 21 | 20 | 1 |
| chemistry-bundle | `db0a8e60` | `78b742a7` | 4 | 7 | 7 | 0 |
| college-algebra-bundle | `46399161` | `709c7417` | 13 | 17 | 16 | 0 |
| microbiology | `f91d7fcd` | `ccd8e233` | 2 | 2 | 2 | 0 |
| organic-chemistry | `8917713c` | `72cb625c` | 5 | 6 | 1 | 5 |
| prealgebra-bundle | `38cae454` | `efab2179` | 19 | 193 | 45 | 146 |
| psychology | `de7e40c9` | `43035bcc` | 3 | 3 | 3 | 0 |

**Current (pin equals head):** astronomy, contemporary-mathematics, introduction-python-programming, physics, university-physics-bundle, writing-guide. The Trench book (`trench/elementary-differential-equations`, upstream github.com/billsix/differentialEquationsTrench) is current too.

**`osbooks-algebra-1`: the upstream is gone.** `https://github.com/openstax/osbooks-algebra-1` returns HTTP 404, and `git ls-remote` on it asks for a user name, which is what GitHub does for a repository that is private or deleted. The pin `332f7864` therefore cannot be fetched from GitHub. The book's `checkout/` in the sandbox is an initialised repository with no commits, so the content is not on this machine either. `fetch.sh` names the maintainer's Pi mirror as the fallback; the sandbox did not try it. This sync leaves the book alone (its pin and `fetch.sh` do not change); the investigation and the decision are in `tasks/openstax-algebra-1-upstream-gone-backup-plan.md`.

**Where the risk is.** biology-bundle (233 content files) and prealgebra-bundle (45 content files, 146 media files) changed most. The media change in prealgebra matters to `study/`, whose problem notebooks and answer keys are generated from that book (`study/CLAUDE.md`; the open task `tasks/study-prealgebra-answer-key-mismatches.md` lists known mismatches at the current pin).

**How to check a book** (each step runs in the book's folder; the image build is nested and slow, since each book image carries TeX Live):

1. Set `PIN_SHA` in `fetch.sh`; add a dated marker line above it, as the 2026-10-19 sync did.
2. Remove `checkout/` and run `./fetch.sh && ./apply.sh`.
3. `make convert` (CNXML to LaTeX). New "Unknown/fallback elements" lines are the converter's normal fallback; an error is not.
4. `make dist` for every bumped book (PDF, EPUB, HTML). From the root, `make <book>` does fetch, apply and `make dist` in one call.

The earlier sync wrote its bump as a script, `tasks/adhoc/openstax-resync/bump_pins.sh`; it was removed when that task was archived and is in git history.

## Plan

- [ ] Bump the nine pins.
- [ ] `make convert` for all nine at the new pins; record the result per book.
- [ ] Full build (`make dist`) for all nine; record the result per book.
- [ ] If prealgebra moves: rebuild `study/` and compare its answer checks with the current run.
- [ ] Refresh `tasks/reference/openstax/book-inventory.md` if it records pins.
- [ ] Mirror check (`CLAUDE.md`, "Contracts"): the public mirrors do not exist yet, so the nine new pins cannot be checked against them in this sync. That gap is tracked in `tasks/openstax-algebra-1-upstream-gone-backup-plan.md`, whose plan verifies every book's pin once the mirrors are pushed. Any other item that does not resolve here gets its own task.

## Decisions (William Emerison Six <billsix@gmail.com>, 2026-11-26)

- **Full build for all nine bumped books**, not only the two that changed most. Each book image carries TeX Live and each build is slow, so the nine builds run one after another and each result is recorded here as it finishes.
- **algebra-1 is not part of this sync.** Its upstream disappearing is investigated later, in `tasks/openstax-algebra-1-upstream-gone-backup-plan.md`; the decided fix is a public mirror on the maintainer's GitHub account, which he pushes from his home network.
- **Nothing that fails is left as a remark.** A book that does not convert or build at its new pin, or an upstream that does not answer, gets a task.

## Open questions

None.
