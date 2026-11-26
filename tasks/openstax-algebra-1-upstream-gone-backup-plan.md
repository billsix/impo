# Algebra 1: the upstream is gone — publish the maintainer's mirrors and fetch from them

**Status:** blocked
**Blocked on:** the maintainer being on the network with the Pi machine (`192.168.0.186`), to push its full-history clone of `osbooks-algebra-1` to `github.com/billsix/osbooks-algebra-1`. Until then the book builds from the local files in its `checkout/` (see Context).
**Recheck:** `git ls-remote https://github.com/billsix/osbooks-algebra-1` lists refs, and `git fetch --depth 1 https://github.com/billsix/osbooks-algebra-1 332f78647098a60532a9833b8003dca5da7ff227` succeeds in a scratch repository.
**Priority:** 4
**Difficulty:** 3 (one push per book for the maintainer; a `fetch.sh` change per book for the agent)
**Created:** 2026-11-26 (William Emerison Six <billsix@gmail.com>: "make a task to investigate this on a later date and make a decision then, I need a backup plan, I planned for ideas like this (by cloning stuff on my raspberry pi box) but never thought it would happen").

## BLUF

OpenStax's `osbooks-algebra-1` repository no longer answers on GitHub, so impo cannot fetch that book's content. A copy of the content does survive as plain files in the book's `checkout/` folder (see Context), so nothing is lost, but it is not a git history and nothing can fetch it. The decided fix is a public mirror under the maintainer's GitHub account: the maintainer pushes his Pi clone to `github.com/billsix/osbooks-algebra-1`, and `fetch.sh` fetches from there, so the book builds off his home network. The same mirror is the backup for each of the other fifteen books. Done means algebra-1 builds again from the public mirror, every book has a public mirror that holds its pin, and each `fetch.sh` falls back to it.

## Context

**Read first:** `openstax/CLAUDE.md` (the per-book contract: `fetch.sh` → `apply.sh` → build), `CLAUDE.md` "Contracts" (the mirror rule this task puts in place) and `openstax/osbooks-algebra-1/fetch.sh`. Found during the pin recon of 2026-11-26, recorded in `tasks/archive/impo/2026/11/26/openstax-sync-upstream-pins-2026-11.md`; that sync leaves algebra-1 untouched.

**What was checked (2026-11-26, from the sandbox):**

| Check | Result |
|---|---|
| `https://github.com/openstax/osbooks-algebra-1` | HTTP 404; `git ls-remote` asks for a user name, as GitHub does for a private or deleted repository |
| The book's `checkout/` in the sandbox | the content **is there as files** (`collections/`, 976 folders under `modules/`, `media/`), but its `.git` has no commits, so git cannot say which upstream commit the files are. Corrected 2026-11-26: the first reading of this folder looked only at the empty git history and wrongly reported no content. |
| `github.com/billsix/osbooks-algebra-1` | does not exist publicly yet |
| Software Heritage, origin `https://github.com/openstax/osbooks-algebra-1` | not archived under that URL (API answered 404) |
| The maintainer's Pi mirror | not checked: unreachable from the sandbox |

**What impo itself still holds for this book:** the tracked files only (`fetch.sh`, `apply.sh`, `Makefile`, `CLAUDE.md`, `README.md`) and the committed `exercises/` cache (934 files). The CNXML modules, collections and media are not in impo; by the content model they are downloaded, never committed.

**Do not delete `openstax/osbooks-algebra-1/checkout/`.** Until a mirror is confirmed it is the only copy reachable from the sandbox, and `fetch.sh` cannot recreate it. The same is true of the `checkout/` folders of contemporary-mathematics, introduction-python-programming and writing-guide, which also hold content files under a `.git` with no commits; their upstreams still answer.

**For now the book lives on the local files** (William Emerison Six <billsix@gmail.com>, 2026-11-26: reflect this locally for now; the full history is wanted once he is on the network with the Raspberry Pi machine, `192.168.0.186`). Until then nothing changes in `fetch.sh`: it leaves an existing `checkout/` untouched, so `./apply.sh && make dist` keeps working on this machine from the files already there. A fresh clone of impo on another machine cannot build algebra-1 until the mirror exists.

**No book checkout holds history.** Each `fetch.sh` runs `git fetch --depth 1 origin <PIN_SHA>`, so a normal checkout is one shallow commit (checked 2026-11-26 on microbiology, physics and astronomy: one commit each, `--is-shallow-repository` true). Four checkouts have no commit at all (algebra-1, contemporary-mathematics, introduction-python-programming, writing-guide): their `.git` folders were initialised on 2026-09-03 and never fetched into, and the content files date from April, so they were copied in from the original port working copy. Nothing under impo can therefore stand in for an upstream repository; full history exists only in the Pi clones or an old working copy.

**The pin:** `PIN_SHA=332f78647098a60532a9833b8003dca5da7ff227`. The comment in `fetch.sh` calls it the merge-base where the maintainer's `latex` port branch left OpenStax's `main`, so any clone that holds that branch also holds the pin.

**Every book names the Pi mirror, none uses it.** All sixteen `openstax/*/fetch.sh` scripts mention the Pi mirror as the fallback in a comment; none falls back to anything automatically. Whether each Pi mirror exists, and how fresh it is, has never been verified from here.

## Decisions (William Emerison Six <billsix@gmail.com>, 2026-11-26)

- **The backup is a public mirror on the maintainer's GitHub account**, one repository per book (`github.com/billsix/<book>`, the same name as the upstream), pushed from the Pi clones, "so that it can be built without being on my network". This is the plan for algebra-1 and for the whole family. The content is CC BY-NC-SA 4.0 for fifteen of the sixteen book folders and CC BY 4.0 for `osbooks-physics`, so an unmodified public mirror is allowed when it is non-commercial, attributed and under the same licence (corrected 2026-11-26; this sentence first said CC BY 4.0 for all).
- **A pin sync must leave every pin fetchable from the mirror.** After a pin moves, the book's mirror must hold the new commit. When that cannot be done in the same sitting (as today: the mirrors are not published yet), the sync is not silently finished: a task is filed for what did not resolve. The rule is written into `CLAUDE.md` ("Contracts").
- Rejected: committing the content into impo (against the *downloaded → ignore* content model, and too large); the Pi mirror as the only fallback (works only on the home network, so the sandbox and the release workflow still fail).

## Plan

Maintainer (home network):

- [ ] The goal is the **full history** from the Pi clone. Only if no clone with history can be found do the files in `checkout/` seed the mirror as a single commit (the pin's commit id is then lost; record that in `fetch.sh`). Compare them with a real clone first if one turns up (`git diff --no-index`).
- [ ] Confirm the Pi mirror holds the pin: `git -C <pi mirror of osbooks-algebra-1> cat-file -e 332f78647098a60532a9833b8003dca5da7ff227^{commit}`. If it does not, look for another clone: the old port working copy with the `latex` branch, a host machine's `checkout/`, or a backup.
- [ ] Mirror algebra-1 with the tool: copy the Pi clone to `~/openstax-mirrors/osbooks-algebra-1.git` (or point `MIRROR_DIR` at the folder that holds it), then `CREATE=1 bash tools/mirror-upstreams.sh push algebra-1`. The tool reuses a clone it finds there, refuses to push one that lacks the pin, and creates the GitHub repository with `gh`.
- [ ] **The other fifteen do not need the Pi or the home network** (rethought 2026-11-26): their upstreams still answer, so `CREATE=1 bash tools/mirror-upstreams.sh push` from any machine with the maintainer's GitHub credentials clones each upstream in full and pushes it to `github.com/billsix/<name>`. It can be run today. Add `BUNDLE_DIR=<folder>` to write an offline bundle of each as well.

Agent (after the Recheck passes):

- [ ] algebra-1: set `UPSTREAM_URL` in `openstax/osbooks-algebra-1/fetch.sh` to the public mirror; `./fetch.sh && ./apply.sh && make convert`, then `make dist`.
- [ ] Find out what happened upstream (renamed, merged into another repository, made private, withdrawn) and record it in `openstax/osbooks-algebra-1/CLAUDE.md`. A rename would give the book an upstream to sync with again.
- [x] Done 2026-11-26 for all sixteen: each `fetch.sh` has an automatic fallback (upstream first, then the public mirror), tested with a dead upstream and with both sources dead.
- [ ] The other fifteen: For each book, verify the mirror holds `PIN_SHA` (`git fetch --depth 1 <mirror> <PIN_SHA>` in a scratch repository); record the table here.
- [ ] Add the mirror check to the sync method: after a pin bump, the new commit must be fetchable from the mirror, or a task is filed.
- [ ] Update `openstax/CLAUDE.md` (the per-book contract: where content comes from, the fallback) and `tasks/reference/openstax/book-inventory.md` if it records sources.

## Open questions

None.
