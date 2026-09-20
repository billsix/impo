# Add explicit Python type annotations to all impo tooling (globals + locals + params + returns)

**Status:** DONE — 2026-09-20 (William Emerison Six <billsix@gmail.com> gave the go-ahead; adhoc scripts
confirmed OUT of scope). All 6 impo toolchain files annotated to the exemplar density; `ty check tools/`
+ pytest (31) green both in-sandbox and in the container CI gate (`make image` on anatomy-physiology);
ruff clean; behavior proven unchanged. Requested 2026-09-19 ("add python types to everything, global
variables, local variables, etc"). Archived.
Sibling task still open in imps: `imps/tasks/annotate-tooling-python-types.md` (that repo's one tool).
**Priority:** 6
**Difficulty:** 5 (mostly mechanical; `convert.py` was large but its signatures were already typed)

## BLUF

Annotated **every** Python tool in impo's shared toolchain generously — not just function signatures but
**local variables and module globals too** — matching the standard already applied to the trench tools
(`split_html.py` etc., the **exemplar**). `ty` already passed over `tools/` (the Dockerfile gate), but
`ty` *infers*; this added the **explicit** annotations `ty` doesn't force. Done: every file below has
annotated globals, locals, params, and returns; `ty check tools/` + pytest stay green (the image gate);
ruff clean.

## Outcome (2026-09-20)

Fanned out three parallel subagents (each read the standard + `split_html.py` exemplar first), then ran
the authoritative combined-tree gate. Key finding: **function signatures were already fully typed across
all files** (an AST scan found zero missing params/returns) — the real gap was module globals and locals,
so this was a gap-fill, not the ~400-line sweep the plan assumed. `preprocess.py` was already fully
compliant (zero changes).

- **`convert.py`** — 24 module globals + 11 new locals. `_Element`/`_ElementTree` (used as annotation
  types hundreds of times, never at runtime — grep-confirmed) typed via `typing.TypeAlias`, not PEP 695
  `type X = Y` (the project pins no `requires-python`, so stay 3.11-safe). Conditional-branch globals
  (`SUBCOL_CMDS`/`MODULE_CMD`) and loop/unpack targets got the "bare annotation on the line above" idiom.
- **`fetch_exercises.py`** — 10 bare globals typed; 3 loop-target precision types (`etree._Element`,
  `dict[str, Any]` for the fetched-JSON question/answer shapes). Top-level `json.loads` result stays
  `Any` (genuinely dynamic until its shape narrows).
- **`build_nav.py`** — a `SitemapNode = dict[str, Any]` alias (parsed JSON, deliberately `Any` inside)
  used throughout; `render()`/`main()` locals + loop targets.
- **tests** (`conftest.py`, `test_helpers.py`, `test_mathml.py`) — module globals, `-> None` on every
  `test_*`, `etree._Element` locals; no pytest fixtures exist to type (conftest only mutates `sys.path`).
  Also **fixed a pre-existing ruff I001** (unsorted imports in `test_helpers.py`, confirmed in HEAD, not
  from this work) so the tree is ruff-clean — behaviour-neutral (conftest sets `sys.path` before any test
  module loads).

**`Any` was used only** where data is genuinely dynamic third-party-shaped JSON (the `SitemapNode` alias,
`fetch_one`'s top-level `json.loads`) — never as a shortcut.

### Verification (all green)
- **In-sandbox:** `ruff check tools/` clean; `ty check tools/` "All checks passed"; `pytest tools/tests -q`
  31 passed.
- **Container CI gate:** `make image` on `osbooks-anatomy-physiology` — its `RUN ty check tools/ &&
  pytest tools/tests` layer (Dockerfile:94-96) passed against the annotated tools (the image build context
  is `tooling/`, so it copies exactly these files); image built + tagged.
- **Behavior unchanged (proof, not spot-check):** an AST-normalizer stripped all annotations from both the
  git-HEAD and edited `convert.py` and compared `ast.dump()` — **identical**; the diffs on the other files
  are additive-annotation-only. With `from __future__ import annotations` in force, annotation expressions
  are never evaluated at runtime, so this covers every code path (stronger than a single-book `make
  convert` diff). No generated-LaTeX change is possible.

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
