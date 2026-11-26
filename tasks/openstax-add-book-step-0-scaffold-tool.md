# Step 0: a scaffold tool for new book folders (`tools/add-book.sh`)

**Status:** ready — approved 2026-11-26 as part of the umbrella; not started
**Part of:** `tasks/openstax-add-remaining-english-books.md`
**Next:** every `tasks/openstax-add-book-<name>.md`
**Priority:** 3
**Difficulty:** 3
**Created:** 2026-11-26 (William Emerison Six <billsix@gmail.com>, with the umbrella).

## BLUF

Adding 29 book folders by hand would produce 29 slightly different folders. This task writes `tools/add-book.sh <name>`, which creates `openstax/osbooks-<name>/` from the current pattern and pins it at the upstream head, and proves it by adding the first book. Done means the tool exists, is documented in `CLAUDE.md`, and one new book has been scaffolded with it and builds.

## Context

**Read first:** `openstax/CLAUDE.md` ("Per-book folder contract", "Adding a book") and an existing thin folder such as `openstax/osbooks-psychology/`.

- The September generator, `tasks/adhoc/openstax-populate-books/scaffold.sh`, was a one-shot and was removed when its task was archived; it is in git history (commit `a54a8bf`, "openstax: scaffold the remaining 15 book folders") and is the starting point.
- The sixteen `fetch.sh` files are identical below their header; the Makefiles differ only in `CONTAINER_NAME` and the header comment (nine are byte-identical after normalising the name). The tool should generate from one template, not copy whichever folder is nearest.
- What a folder needs today that the September scaffold did not write: `MIRROR_URL` and the two-step fetch with cleanup, `image-export`/`image-import`, the per-book `CLAUDE.md` section "The books this folder builds", and no mention of the Pi path.
- "Adding a book" in `openstax/CLAUDE.md` still describes the pin as the `latex` merge-base and predates the mirror; it is rewritten here to describe the tool.

## Plan

- [ ] Write `tools/add-book.sh <name>`: refuses an existing folder; reads the upstream head with `git ls-remote`; writes `fetch.sh`, `apply.sh`, `Makefile`, `README.md`, `CLAUDE.md`, `.gitignore`; keeps the executable bits; `bash -n` on what it wrote.
- [ ] Prove it does not drift from the existing folders: generate a folder for a book impo already has, into a scratch directory, and diff it against the real one; explain every difference.
- [ ] Use it for the first book (`tasks/openstax-add-book-statistics.md`) and build that book.
- [ ] Rewrite "Adding a book" in `openstax/CLAUDE.md`; list the tool in `CLAUDE.md`.

## Open questions

None.
