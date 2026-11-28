# Give the OpenStax toolchain image one name, shared by every book folder

**Status:** proposed — needs go-ahead
**Priority:** 6
**Difficulty:** 2
**Created:** 2026-11-28 (William Emerison Six <billsix@gmail.com>: "yes, write it up as a proposed task, but
not part of the current branch, it will be off of master").

## BLUF

Every book folder's `Makefile` builds its own image tag (`osbooks-<name>`) from the same Dockerfile and the
same build context, `openstax/tooling/`. The 45 tags name one image, so a Dockerfile change leaves every
folder whose `make image` has not run since holding its tag on the old image, and the old 6.6 GB image stays
on disk while any tag points at it. Done means all 45 book Makefiles and the trench Makefile build and run one
shared tag, the tools and docs that name a per-book image use it, and one book is built with it.

## Context

- Read first: "Per-book folder contract" and "The shared toolchain" in `openstax/CLAUDE.md`.
- Seen 2026-11-28: `podman images` listed `osbooks-principles-finance`, `osbooks-business-ethics` and
  `osbooks-principles-marketing` with the same image ID, 6.62 GB, and `osbooks-principles-marketing` a second
  time with an older ID.
- Where the name is set: `CONTAINER_NAME = @NAME@` in `tools/book-template/Makefile`, filled per folder by
  `tools/add-book.sh`; `CONTAINER_NAME = trench-elementary-differential-equations` in
  `trench/elementary-differential-equations/Makefile`. The name is used by `image` (`build -t`), by every
  `run`, and by `image-export` (the tar's file name starts with it).
- What already limits the harm: `pdf`, `html`, `epub` and the other build targets depend on `image`, so a
  normal build re-tags first (a cache hit). The entrypoint scripts are bind-mounted at run time and the
  converter and styles reach the build through the checkout overlay, so only a Dockerfile-level change (a
  package, a font, TeX Live) needs a new image.
- Not changed by this task: `make image` still runs a cache-hit `podman build` before every build target. A
  GitHub Actions release job builds the image in its own runner under either naming.
- The 45 `apply.sh` and `Makefile` copies are filled from `tools/book-template/` (since 2026-11-28;
  `tasks/archive/impo/2026/11/28/openstax-build-refresh-overlay.md`). Fill them the same way here: change
  the template, then rewrite each folder's `Makefile` from it, keeping the folder's first line (its title).
  The script that did it last time is
  `git show 1279ecb9:tasks/adhoc/openstax-build-refresh-overlay/regenerate_from_template.py`.

## Plan

1. Set the name `impo-openstax-toolchain` in `tools/book-template/Makefile`; keep
   `@NAME@` only where the folder's own name is still wanted (the comment line).
2. Refill the 45 `openstax/osbooks-*/Makefile` files from the template and set the same name in the trench
   Makefile (its `image` target also runs that book's tools gate, which stays).
3. Update what names a per-book image: root `CLAUDE.md` (`make image-export` "in one book folder"),
   `openstax/CLAUDE.md`, `tasks/openstax-books-buildable-forever-source-backup-and-licences.md` and
   `tasks/openstax-emoji-font-in-the-toolchain-image.md`; `grep -rn 'CONTAINER_NAME\|osbooks-.* image'` over
   `tools/`, `.github/` and the docs finds the rest.
4. Verify: `make image` in two folders gives one tag and one image ID; `make dist` in one OpenStax folder and
   `make pdf` in the trench folder; `make image-export` writes `impo-openstax-toolchain-<date>.tar`.
5. Tell the maintainer the one-time cleanup, which is his: remove the old tags
   (`podman images --format '{{.Repository}}' | grep '^localhost/osbooks-' | xargs podman rmi`) on each
   machine, and after loading a tar saved before this change, `podman tag <old name> impo-openstax-toolchain`.

## Decisions

- **The name is `impo-openstax-toolchain`** (William Emerison Six <billsix@gmail.com>, 2026-11-28: "sure that name is fine").

## Open questions

None. The go-ahead to do the work is still needed.
