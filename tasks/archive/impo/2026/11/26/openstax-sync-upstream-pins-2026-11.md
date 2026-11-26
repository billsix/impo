# Synced the nine out-of-date OpenStax content pins with upstream

**Done 2026-11-26** (agent; William Emerison Six <billsix@gmail.com>, 2026-11-26: "do the recon for both … a sync means to just update the pins and make sure everything still works in my project", then "all nine" for the full builds and "go ahead and work"). The maintainer committed the work the same day; at archive the three scripts were promoted from `tasks/adhoc/` to `tools/`.

## What was done

Nine of the sixteen OpenStax books were pinned behind their upstream default-branch head. Each `fetch.sh` `PIN_SHA` was moved to that head, the book's checkout was brought to the new commit, the toolchain overlay was re-applied, and every book was converted and built in all three formats. impo carries no patch series, so nothing was rebased.

| Book folder | Old pin | New pin | Books built (modules) | Convert | PDF, EPUB, HTML |
|---|---|---|---|---|---|
| anatomy-physiology | `5ae32b3f` | `f2737623` | anatomy-and-physiology-2e (198) | pass | pass |
| biology-bundle | `89c14e6d` | `bc1be223` | biology-2e (259), biology-ap-courses-2e (209), concepts-biology (107) | pass | pass |
| calculus-bundle | `8dbc2ce1` | `018da4da` | calculus-volume-1 (55), -2 (54), -3 (54) | pass | pass |
| chemistry-bundle | `db0a8e60` | `78b742a7` | chemistry-2e (149), chemistry-atoms-first-2e (149) | pass | pass |
| college-algebra-bundle | `46399161` | `709c7417` | algebra-and-trigonometry-2e (94), college-algebra-2e (69), college-algebra-corequisite-support-2e (69), precalculus-2e (87) | pass | pass |
| microbiology | `f91d7fcd` | `ccd8e233` | microbiology (159) | pass | pass |
| organic-chemistry | `8917713c` | `72cb625c` | organic-chemistry (342) | pass | pass |
| prealgebra-bundle | `38cae454` | `efab2179` | prealgebra-2e (75), elementary-algebra-2e (82), intermediate-algebra-2e (83), healthcare-foundations (30) | pass | pass |
| psychology | `de7e40c9` | `43035bcc` | psychology-2e (105) | pass | pass |

Already current, untouched: astronomy, contemporary-mathematics, introduction-python-programming, physics, university-physics-bundle, writing-guide, and the Trench book. `osbooks-algebra-1` was left alone: its upstream is gone, which is `tasks/openstax-algebra-1-upstream-gone-backup-plan.md`.

## Decisions, in the order they were made (William Emerison Six <billsix@gmail.com>, 2026-11-26)

1. **What "sync" means here.** The maintainer asked for a recon and defined the request: where there is nothing to rebase, a sync is moving the pins and making sure everything still works. That went into `CLAUDE.md` ("Contracts"). The pin target stayed the upstream default-branch head, as confirmed on 2026-10-20.
2. **The recon** (read-only `git ls-remote`, counts from blobless bare clones) found nine books behind, six current, the Trench book current, and `osbooks-algebra-1`'s upstream gone (HTTP 404). It first reported that no copy of the algebra-1 content was on the machine; that was wrong, the files are in the book's `checkout/` and only its git history is empty. The correction is in `tasks/openstax-algebra-1-upstream-gone-backup-plan.md`.
3. **Full build for all nine**, not only the two that changed most (the agent had recommended biology-bundle and prealgebra-bundle; the maintainer said "all nine").
4. **algebra-1 was taken out of the sync** and given its own task; the maintainer wanted a backup plan decided later, on his home network.
5. **Every pin must stay fetchable without the upstream, and what a sync cannot resolve gets a task.** Decided after the algebra-1 finding; written into `CLAUDE.md` ("Contracts"). The backup is a public mirror per book on the maintainer's GitHub account, for all sixteen books.
6. **The checkouts were updated in place** (the agent's choice during the work), not deleted and refetched as the plan first said: four checkouts turned out to hold content with no git history, and an in-place update kept the earlier outputs until new ones replaced them. Its cost was the stale AP Biology outputs noted below.
7. **After the builds:** Healthcare Foundations is kept and published with its bundle, the old AP Biology address is left to disappear at the next publish, and the stale old-named AP Biology outputs were deleted. These are recorded in `tasks/archive/impo/2026/11/26/openstax-biology-ap-rename-and-healthcare-foundations.md`.

## How

- `tools/bump-pins.sh <book> …` reads each upstream head with `git ls-remote`, sets `PIN_SHA` with one dated line above it, and moves the existing checkout to the new commit in place (`git fetch --depth 1`, `git checkout --detach`). The checkout was not deleted and refetched, so earlier outputs survived until the new ones replaced them.
- `tools/build-after-sync.sh <log dir> <book> …` builds the toolchain image once, then per book runs `./apply.sh`, `make convert` and `make dist`, three books at a time. All nine passed both steps. Every PDF, EPUB and HTML zip in the nine `checkout/output/` folders carries a 2026-11-26 timestamp. The image build and the nine builds took about 50 minutes nested.
- The converter's only notices were its normal "Unknown/fallback elements" lines (`inline:span`, `inline:label`); the LaTeX runs used `-halt-on-error` and none halted.
- `tools/sync-pin-docs.py` made each book's `CLAUDE.md` name the pin its `fetch.sh` carries. Twelve of the sixteen still named the original September pin, two syncs old (the October sync had not updated them); the original pin is kept in the sentence as the port's first base.

## What upstream changed that matters

- **prealgebra-bundle gained a fourth book, Healthcare Foundations** (`healthcare-foundations.collection.xml`, 30 modules). It converts and builds in all three formats without any change to impo. This explains the 146 changed media files the recon counted.
- **Biology for AP Courses was renamed** from `biology-ap-courses` to `biology-ap-courses-2e`. The book builds under the new name. The October outputs under the old name had stayed in `openstax/osbooks-biology-bundle/checkout/` (`latex/biology-ap-courses.tex`, `output/biology-ap-courses/`, `output/biology-ap-courses.epub`), because the checkout was updated in place; they were deleted the same day with the maintainer's approval.
- Both were followed up in `tasks/archive/impo/2026/11/26/openstax-biology-ap-rename-and-healthcare-foundations.md`.

## study/

`study/` is generated from prealgebra-2e. At the new pin `make -C study test` passed (the four question banks, 0 problems), and `make -C study problem-notebooks BOOK=prealgebra-2e` regenerated the notebooks with **15 answer-key mismatches, the same number as before the sync** (`tasks/study-prealgebra-answer-key-mismatches.md`). The 15 were not compared one by one with the earlier list.

## Not done

- **Mirror check.** The contract added that day (`CLAUDE.md`, "Every pin must stay fetchable without the upstream") asks that each moved pin be fetchable from the maintainer's public mirror. The mirrors did not exist yet, so the nine new pins were not checked; `tasks/openstax-algebra-1-upstream-gone-backup-plan.md` verifies every book's pin once they are pushed, and `tasks/openstax-refresh-pi-mirrors-after-2026-11-sync.md` has the maintainer refresh the private mirrors first.
- **Visual check** of the rebuilt books: left to the maintainer.
- `tasks/reference/openstax/book-inventory.md` records no pins, so it needed no change; listing Healthcare Foundations there was left to the follow-up task.
