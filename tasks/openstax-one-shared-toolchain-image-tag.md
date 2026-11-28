# The OpenStax toolchain image has one name, shared by every book folder

**Done 2026-11-28** (agent. Created the same day by William Emerison Six <billsix@gmail.com>: "yes, write it
up as a proposed task"; the name, "sure that name is fine"; the go-ahead, "can you now do that task to make
it all one image?").

## What was wrong

Every book folder's `Makefile` built its own image tag (`osbooks-<name>`) from the same Dockerfile and the
same build context, `openstax/tooling/`. The 45 tags named one image, so after a Dockerfile change each
folder whose `make image` had not run since kept its tag on the old image, and the old 6.6 GB image stayed
on disk while any tag pointed at it. Seen on 2026-11-28: three folders' tags on one image ID, and one of
them a second time on an older ID.

## What changed

- **`CONTAINER_NAME = impo-openstax-toolchain`** in `tools/book-template/Makefile`, in all 45
  `openstax/osbooks-*/Makefile` files and in `trench/elementary-differential-equations/Makefile`. The name
  is used by `image` (`build -t`), by every `run`, and by `image-export`, whose tar is now
  `impo-openstax-toolchain-<date>.tar` from any folder. The trench `image` target still runs that book's own
  tools gate after the build.
- **`tools/fill-book-folders.py`** (new) rewrites every book folder's `apply.sh` and `Makefile` from the
  template, keeping each Makefile's title line. It is the one-off script of
  `tasks/archive/impo/2026/11/28/openstax-build-refresh-overlay.md`, kept this time because the fan-out was
  needed twice in a day. Run before the template changed it rewrote 0 files; after, 45; again, 0.

## Not changed

`make image` still runs a cache-hit `podman build` before every build target. A GitHub Actions release job
builds the image in its own runner as before. `tools/add-book.sh` needed no change: the template's `@NAME@`
now occurs only where a folder's own name is meant.

## Verification (2026-11-28, nested)

- `make image` in `openstax/osbooks-business-ethics` and then in `openstax/osbooks-statistics`: one tag,
  `localhost/impo-openstax-toolchain`, one image ID.
- `make dist` in `openstax/osbooks-business-ethics`: PDF, EPUB and HTML built with that image.
- `make pdf` in `trench/elementary-differential-equations`: built with that image.
- `ruff check` and `ruff format --check` pass on the new tool.
- `make image-export` was not run (it writes a 6.6 GB tar); its recipe differs only in the name.

## The maintainer's one-time cleanup

- Remove the old per-book tags on each machine that has them:
  `podman images --format '{{.Repository}}' | grep -E '^localhost/(osbooks-|trench-elementary)' | sort -u | xargs podman rmi`.
  In the sandbox they are still there (two image IDs under `osbooks-business-ethics` alone), some of them in
  the read-only host store, which only the host can remove.
- A tar saved before this change loads under its old per-book name: `podman tag <old name>
  impo-openstax-toolchain` after `make image-import`.

## Recorded

Root `CLAUDE.md` ("Contracts", the image export; `tools/`), `openstax/CLAUDE.md` ("Per-book folder
contract"), `tasks/openstax-books-buildable-forever-source-backup-and-licences.md`.
