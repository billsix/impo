# Algebra 1: the upstream is gone — publish the maintainer's mirrors and fetch from them

**Status:** blocked
**Blocked on:** the maintainer pushing the Pi mirror of `osbooks-algebra-1` to `github.com/billsix/osbooks-algebra-1` (needs the home network, where the Pi lives; the sandbox cannot reach it).
**Recheck:** `git ls-remote https://github.com/billsix/osbooks-algebra-1` lists refs, and `git fetch --depth 1 https://github.com/billsix/osbooks-algebra-1 332f78647098a60532a9833b8003dca5da7ff227` succeeds in a scratch repository.
**Priority:** 4
**Difficulty:** 3 (one push per book for the maintainer; a `fetch.sh` change per book for the agent)
**Created:** 2026-11-26 (William Emerison Six <billsix@gmail.com>: "make a task to investigate this on a later date and make a decision then, I need a backup plan, I planned for ideas like this (by cloning stuff on my raspberry pi box) but never thought it would happen").

## BLUF

OpenStax's `osbooks-algebra-1` repository no longer answers on GitHub, so impo cannot fetch that book's content, and no copy of it is in the sandbox. The decided fix is a public mirror under the maintainer's GitHub account: the maintainer pushes his Pi clone to `github.com/billsix/osbooks-algebra-1`, and `fetch.sh` fetches from there, so the book builds off his home network. The same mirror is the backup for each of the other fifteen books. Done means algebra-1 builds again from the public mirror, every book has a public mirror that holds its pin, and each `fetch.sh` falls back to it.

## Context

**Read first:** `openstax/CLAUDE.md` (the per-book contract: `fetch.sh` → `apply.sh` → build), `CLAUDE.md` "Contracts" (the mirror rule this task puts in place) and `openstax/osbooks-algebra-1/fetch.sh`. Found during the pin recon of 2026-11-26, recorded in `tasks/openstax-sync-upstream-pins-2026-11.md`; that sync leaves algebra-1 untouched.

**What was checked (2026-11-26, from the sandbox):**

| Check | Result |
|---|---|
| `https://github.com/openstax/osbooks-algebra-1` | HTTP 404; `git ls-remote` asks for a user name, as GitHub does for a private or deleted repository |
| The book's `checkout/` in the sandbox | an initialised repository with no commits, so no content |
| `github.com/billsix/osbooks-algebra-1` | does not exist publicly yet |
| Software Heritage, origin `https://github.com/openstax/osbooks-algebra-1` | not archived under that URL (API answered 404) |
| The maintainer's Pi mirror | not checked: unreachable from the sandbox |

**What impo itself still holds for this book:** the tracked files only (`fetch.sh`, `apply.sh`, `Makefile`, `CLAUDE.md`, `README.md`) and the committed `exercises/` cache (934 files). The CNXML modules, collections and media are not in impo; by the content model they are downloaded, never committed.

**The pin:** `PIN_SHA=332f78647098a60532a9833b8003dca5da7ff227`. The comment in `fetch.sh` calls it the merge-base where the maintainer's `latex` port branch left OpenStax's `main`, so any clone that holds that branch also holds the pin.

**Every book names the Pi mirror, none uses it.** All sixteen `openstax/*/fetch.sh` scripts mention the Pi mirror as the fallback in a comment; none falls back to anything automatically. Whether each Pi mirror exists, and how fresh it is, has never been verified from here.

## Decisions (William Emerison Six <billsix@gmail.com>, 2026-11-26)

- **The backup is a public mirror on the maintainer's GitHub account**, one repository per book (`github.com/billsix/<book>`, the same name as the upstream), pushed from the Pi clones, "so that it can be built without being on my network". This is the plan for algebra-1 and for the whole family. The content is CC BY 4.0, so redistribution with attribution is allowed.
- **A pin sync must leave every pin fetchable from the mirror.** After a pin moves, the book's mirror must hold the new commit. When that cannot be done in the same sitting (as today: the mirrors are not published yet), the sync is not silently finished: a task is filed for what did not resolve. The rule is written into `CLAUDE.md` ("Contracts").
- Rejected: committing the content into impo (against the *downloaded → ignore* content model, and too large); the Pi mirror as the only fallback (works only on the home network, so the sandbox and the release workflow still fail).

## Plan

Maintainer (home network):

- [ ] Confirm the Pi mirror holds the pin: `git -C <pi mirror of osbooks-algebra-1> cat-file -e 332f78647098a60532a9833b8003dca5da7ff227^{commit}`. If it does not, look for another clone: the old port working copy with the `latex` branch, a host machine's `checkout/`, or a backup.
- [ ] Create `github.com/billsix/osbooks-algebra-1` (public, empty) and push the mirror to it: `git -C <pi mirror> push --mirror https://github.com/billsix/osbooks-algebra-1`.
- [ ] Do the same for the other fifteen books, each under its upstream's name. The upstream names are the `UPSTREAM_URL` lines of `openstax/*/fetch.sh`. Fetch the upstream into the Pi mirror first, so the mirror holds the book's current pin.

Agent (after the Recheck passes):

- [ ] algebra-1: set `UPSTREAM_URL` in `openstax/osbooks-algebra-1/fetch.sh` to the public mirror; `./fetch.sh && ./apply.sh && make convert`, then `make dist`.
- [ ] Find out what happened upstream (renamed, merged into another repository, made private, withdrawn) and record it in `openstax/osbooks-algebra-1/CLAUDE.md`. A rename would give the book an upstream to sync with again.
- [ ] The other fifteen: give each `fetch.sh` an automatic fallback (upstream first, then the public mirror) and replace the Pi-mirror comment. For each book, verify the mirror holds `PIN_SHA` (`git fetch --depth 1 <mirror> <PIN_SHA>` in a scratch repository); record the table here.
- [ ] Add the mirror check to the sync method: after a pin bump, the new commit must be fetchable from the mirror, or a task is filed.
- [ ] Update `openstax/CLAUDE.md` (the per-book contract: where content comes from, the fallback) and `tasks/reference/openstax/book-inventory.md` if it records sources.

## Open questions

None.
