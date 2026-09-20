# OpenStax tooling type-check gate — enforce annotations, run it via make/Dockerfile, wrap it in CI

**Status:** DONE — 2026-09-20 (William Emerison Six <billsix@gmail.com>). The follow-on to the archived
annotation sweep (`tasks/archive/impo/2026/09/20/annotate-tooling-python-types.md`): make "everything
annotated" enforceable, and make the gate runnable via `make` + used by CI, modeled on
github.com/billsix/modelviewprojection.
**Priority:** 5
**Difficulty:** 4

## BLUF

The shared OpenStax toolchain (`openstax/tooling/tools/*.py`) now has an enforced gate: **ruff check +
the local/global annotation checker (`check_local_annotations.py`, ported from mvp) + `ty check` +
pytest**. The whole gate is ONE script, `entrypoint/check-tools.sh`, wrapped by three callers that
therefore can't drift: the **Dockerfile build gate** (every `make image` runs it), **`make type-check`**
(a new `openstax/tooling/Makefile`), and **`.github/workflows/checks.yml`** (a thin wrapper over `make
type-check`). Done = the gate is green, runnable by `make`, and CI runs the same containerized checks.

## Two questions the maintainer raised (2026-09-20), and the answers

1. **"Why no `make shell` / `make shell-exec` to run the type-check?"** — There was no good reason; the
   book Makefiles had `shell` but no `shell-exec`, and there was no target that ran the gate. The gate is a
   *toolchain-wide* concern (it checks `tooling/tools/`, not any one book's checkout), so it did not belong
   in the per-book Makefiles (which mount a book checkout at `/book`). Fixed by adding a **tooling-level
   `openstax/tooling/Makefile`** with `image`, `type-check` (alias `check`), `shell`, and `shell-exec` (the
   batch twin, sharing one `SHELL_RUN_FLAGS` block with `shell` per mvp's anti-drift convention). It mounts
   the live `tools/` + `pyproject.toml` over the image's baked copies, so a tooling edit is checked without
   an image rebuild.
2. **"Why doesn't the GitHub Action use the Makefile/Dockerfile?"** — The first cut had CI `pip install`
   the tools and run `check-tools.sh` directly, to dodge a slow ~GB TeX Live image build. That was a weak
   reason: it violated the maintainer's "CI is a thin wrapper over make/Dockerfile" rule and created a
   second environment that could drift from the container gate. Fixed the mvp way: a **`WITH_TEXLIVE`
   build-arg** (default 1; the book builds need LaTeX) lets CI build a **lean image** (`WITH_TEXLIVE=0` —
   converter + gate deps only, no TeX Live, installs in seconds), exactly like mvp's `BUILD_DOCS=0` CI
   image. CI is now `checkout` → `make type-check` (which defaults to the lean image).

## What was done (2026-09-20)

- **`openstax/tooling/tools/check_local_annotations.py`** — ported verbatim (logic-identical) from mvp;
  only the docstring is impo-specific. Flags any local OR module-level `name = …` never annotated in its
  scope, with the same exemptions (unpack/`for`/`with`/`except`/comprehension/walrus/augmented/attr/
  subscript targets, `global`/`nonlocal`, `TypeVar`/`ParamSpec`/`TypeVarTuple`). Running it surfaced 3
  real gaps, now fixed: a missed `convert.py` local (`t`), `build_nav.py`'s `SitemapNode` alias (now
  `TypeAlias`), and the checker's own locals (impo checks all of `tools/`, so it is self-clean).
- **`entrypoint/check-tools.sh`** — the single gate script (ruff check + the annotation checker + ty +
  pytest), status-accumulating (`|| status=1`; runs every step, fails if any failed), portable
  (in-container and on a host from the repo root).
- **`Dockerfile`** — the build gate `RUN` now calls `check-tools.sh` (was inline `ty && pytest`); added
  the `WITH_TEXLIVE` build-arg splitting the dnf install into an always-installed base (make, python3,
  python3-lxml, python3-pytest, ruff, ty, pandoc) and a conditional TeX Live + book-output layer (latexmk,
  the 18 texlive collections, librsvg2-tools, roboto, zip, tidy). With `WITH_TEXLIVE=1` (book default) the
  package set is identical to before.
- **`entrypoint/format.sh`** — runs the annotation checker after its ruff `--fix` + `ty`, so `make format`
  catches a missing annotation locally before the build gate does.
- **`openstax/tooling/Makefile`** (new) + **`.github/workflows/checks.yml`** (rewritten) — see the answers
  above.
- **`openstax/CLAUDE.md`** — documents the checker + the gate.

## Verification (all green)
- `make -C openstax/tooling type-check` — builds the LEAN image (no TeX Live) and runs the gate in the
  container; ruff/ty/annotation-checker clean, pytest 31 passed. (The build-time gate `RUN` also passes.)
- Book image (`osbooks-anatomy-physiology`, `WITH_TEXLIVE=1` default) rebuilt with TeX Live present
  (`latexmk` + `ty` confirmed in the image, build-time gate green) — the dnf split didn't break book
  builds; `make image` exits 0 on a cached run. (One caveat: the first *uncached* `podman build` in this
  nested sandbox printed a spurious `make Error 1` AFTER a successful tag+commit — a nested-podman
  cache-mount teardown quirk, not reproducible on the cached rerun and not present on a non-nested host;
  the image was complete and correct either way.)
- In-sandbox `ruff` / `ty` / the checker / `pytest` over `tools/` are all clean.

## Related
- `tasks/archive/impo/2026/09/20/annotate-tooling-python-types.md` — the one-time sweep this enforces.
- Model: github.com/billsix/modelviewprojection `tools/check_local_annotations.py`, `make type-check`,
  `.github/workflows/checks.yml` (and its `BUILD_DOCS=0` lean-CI image).
