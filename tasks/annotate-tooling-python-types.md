# Add explicit Python type annotations to all impo tooling (globals + locals + params + returns)

**Status:** proposed — needs go-ahead. Requested 2026-09-19 (William Emerison Six <billsix@gmail.com>:
"add python types to everything, global variables, local variables, etc" for all impo + imps tools).
Sibling task in imps: `imps/tasks/annotate-tooling-python-types.md` (that repo's one Python tool).
**Priority:** 6
**Difficulty:** 5 (mostly mechanical, but `convert.py` is large; a few genuinely tricky types)

## BLUF

Annotate **every** Python tool in impo's shared toolchain generously — not just function signatures but
**local variables and module globals too** — matching the standard the maintainer already had applied to
the trench tools (`normalize_master.py`, `over_to_frac.py`, `web_preprocess.py`, `split_html.py`, which
are the **exemplar** — copy their density). `ty` already passes over `tools/` (the Dockerfile gate), but
`ty` *infers*; this task adds the **explicit** annotations `ty` doesn't force. "Done" = each file below
has annotated globals, locals, params, and returns; `ty check tools/` + the pytest suite stay green (the
image build gate); ruff clean.

## Context (cold-start)

- **The standard** is the maintainer's cross-project one: `~/.claude/reference/python-coding-standard.md`
  ("annotate generously — locals + globals too"). The trench book's `tools/*.py` were done to it this
  month and are the pattern to match (e.g. `re.Match[str] | None`, `list[int]`, `re.Pattern[str]`, every
  local `x: T = …`). Read one (`split_html.py`) before starting.
- **The gate** is baked into `openstax/tooling/Dockerfile`: `ty check tools/ && pytest tools/tests`. It
  runs on every `make image`, so a regression fails the build. `ty` passing is necessary but NOT
  sufficient here — it doesn't require explicit annotations, so this is a manual style pass verified by
  eye + `ty`/ruff staying green.
- **Enforcement option (worth considering):** github.com/billsix/modelviewprojection ships a
  *local-variable annotation checker* (its `make type-check` runs `ty` + "the annotation checker" over
  the source). Porting that checker into `openstax/tooling/tools/` and wiring it into the Docker gate
  would make "everything annotated" enforceable rather than a one-time sweep. Propose it; don't auto-wire
  without go-ahead.

## Scope — files to annotate (impo, excluding the already-done trench tools)

- `openstax/tooling/tools/cnxml2tex/convert.py` — the CNXML→LaTeX converter (**large**; the bulk of the
  work; many local vars, `lxml` element types, recursion helpers).
- `openstax/tooling/tools/cnxml2tex/fetch_exercises.py` — the os-embed exercise fetcher (network + JSON).
- `openstax/tooling/tools/pandoc/build_nav.py` — the chunked-HTML left-TOC injector (already partly typed
  — it has `-> tuple[str, bool]` etc.; finish the locals).
- `openstax/tooling/tools/pandoc/preprocess.py` — the pandoc LaTeX sanitizer.
- `openstax/tooling/tools/tests/{conftest.py,test_helpers.py,test_mathml.py}` — the test suite (annotate
  fixtures + test locals too, for consistency; lighter priority than the converters).

Out of scope: `tasks/adhoc/*.py` (throwaway scripts — the recent `add_provenance_env.py` is already
annotated; older ones can be left), the trench `tools/*.py` (done), and anything under `checkout/`.

## Plan

1. Go file by file, deepest/most-used first (`convert.py`). Annotate module globals, every function's
   params + return, and local variables (`x: T = …`), matching the trench tools' density.
2. Keep externally-dictated names as-is (per the cross-project rule) — e.g. pytest fixture names, any
   callback signatures; annotate their bodies.
3. After each file: `ruff check` clean, and `ty check tools/` clean (run via a quick container:
   `podman run --rm … <image> bash -c 'cd /book && ty check tools/'`, or just `make image` which gates it).
4. Final: `make image` for one book (e.g. anatomy-physiology) — the Docker gate runs `ty check tools/` +
   pytest; both must pass. `make convert` on one book to confirm no behavior change.
5. (Optional, if approved) port mvp's local-annotation checker + add it to the gate.

## Verification
- `ty check tools/` + `pytest tools/tests` green at image build (the existing gate).
- Spot-check `convert.py` runs unchanged: `make convert` on anatomy-physiology still emits the same master
  (diff the generated `.tex` before/after — should be identical; annotations don't change output).

## Related
- Exemplar: `trench/elementary-differential-equations/tools/*.py` (done to the target density).
- Standard: `~/.claude/reference/python-coding-standard.md`.
- Sibling: `imps/tasks/annotate-tooling-python-types.md` (imps `tools/squash_series.py`).
- Enforcement precedent: github.com/billsix/modelviewprojection `make type-check` (annotation checker).
