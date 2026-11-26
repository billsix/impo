# Algebra 1: the upstream is gone — mirror it from the maintainer's clone and fetch from the mirror

**Status:** blocked
**Blocked on:** the maintainer being on the network with the Pi machine (`192.168.0.186`), where his full-history clone of `osbooks-algebra-1` is believed to be. Until then the book builds from the files already in its `checkout/`.
**Recheck:** `bash tools/mirror-upstreams.sh check algebra-1` reports "mirror holds the pin".
**Priority:** 4
**Difficulty:** 3
**Created:** 2026-11-26 (William Emerison Six <billsix@gmail.com>: "make a task to investigate this on a later date and make a decision then, I need a backup plan, I planned for ideas like this (by cloning stuff on my raspberry pi box) but never thought it would happen").

## BLUF

OpenStax's `osbooks-algebra-1` repository no longer answers on GitHub, so impo cannot fetch that book's source; the only copy reachable from here is the plain files in `openstax/osbooks-algebra-1/checkout/`. The maintainer intends a public mirror at `github.com/billsix/osbooks-algebra-1`, pushed from his own full-history clone. Done means the mirror holds the pinned commit, `fetch.sh` fetches the book from it, and the book builds from that fetch.

## Context

**Read first:** `tasks/reference/openstax/algebra-1-upstream-removal.md`. It records what happened, what impo still holds, what is and is not known about why, the maintainer's intent, and the points to settle before the mirror is public. This task holds only the steps.

- **The pin:** `332f78647098a60532a9833b8003dca5da7ff227`, the commit where the maintainer's `latex` port branch left OpenStax's `main`. Any clone that holds that branch holds the pin.
- **Do not delete `openstax/osbooks-algebra-1/checkout/`.** It is in no commit, and `fetch.sh` cannot recreate it until the mirror exists.
- **Already in place (2026-11-26):** `fetch.sh` tries the upstream and then `https://github.com/billsix/osbooks-algebra-1`; `tools/mirror-upstreams.sh` pushes and checks mirrors; the survey table (`tasks/reference/openstax/upstream-book-repositories.md`) shows this book as a "gone" row from `tools/upstream-books-gone.txt`.
- **Looked for and not found, 2026-11-26:** a public fork under the maintainer's GitHub account; a Software Heritage archive of the upstream URL.

## Decisions (William Emerison Six <billsix@gmail.com>, 2026-11-26, in order)

1. **Investigate later, with a backup plan**: the task was filed instead of acting at once, because the Pi could not be reached.
2. **The book lives on the local files for now**; the full history is wanted once he is on the network with the Pi.
3. **The backup is a public mirror under his GitHub account**, for this book and for every book impo builds, with `fetch.sh` defaulting to OpenStax and falling back to the mirror. Rejected: committing the source into impo (about 4.6 GB across the books), and the Pi as the only fallback (it works only on his home network).
4. **He intends the Algebra 1 mirror to be public**, and wants the source material kept for his own children (recorded in the reference doc).

## Plan

Maintainer, on the network with the Pi:

- [ ] Confirm the Pi clone holds the pin: `git -C <clone> cat-file -e 332f78647098a60532a9833b8003dca5da7ff227^{commit} && echo present`. If it does not, look for another clone with history: the old port working copy with the `latex` branch, or a backup. Record the result in `tools/upstream-books-gone.txt` (the `private-clone` field, with the date).
- [ ] Settle the points listed in the reference doc under "Things to settle before the mirror is public" (the licence read for this book, that OpenStax took the source out of public view, the third-party material inside it).
- [ ] Push the mirror: copy the clone to `~/openstax-mirrors/osbooks-algebra-1.git` (or point `MIRROR_DIR` at its folder), then `CREATE=1 bash tools/mirror-upstreams.sh push algebra-1`. The tool refuses a clone that lacks the pin.
- [ ] Only if no clone with history exists: seed the mirror from the files in `checkout/` as a single commit, and say in `fetch.sh` and in the mirror that the upstream commit id was lost.

Agent, after the Recheck passes:

- [ ] Refetch the book from the mirror into a fresh folder and compare it with the files in `checkout/` (`git diff --no-index`), so the old copy is known to match or the differences are recorded.
- [ ] `./fetch.sh && ./apply.sh`, then `make convert` and `make dist`.
- [ ] Update `tools/upstream-books-gone.txt`, refresh the survey table, and record the outcome in the reference doc.

## Open questions

None.
