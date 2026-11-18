# Collect the converter doctests in `make test`

**Status:** open (asked for 2026-11-18 by William Emerison Six <billsix@gmail.com>)
**Priority:** 4
**Difficulty:** 2
**Started:** 2026-11-18 (William Emerison Six <billsix@gmail.com>)

## BLUF

Every book's `make test` runs `python3 -m pytest tools/tests -q`, which collects no doctests.
The house rule is that the test gate runs them (the `doctests-by-default.md` reference doc in
github.com/billsix/runClaudeInContainer, "## Python"). Done = pytest collects `--doctest-modules`
over `openstax/tooling/tools/` from every book's `make test` and from `check-tools.sh` (the image
build gate), and the gate is green.

## Plan

1. `openstax/tooling/pyproject.toml` `[tool.pytest.ini_options]`: `testpaths = ["tools"]`,
   `addopts = "--doctest-modules --import-mode=importlib"`. All five converter modules are
   `__main__`-guarded (checked 2026-11-18), so importing them at collection is safe.
2. The 16 `openstax/osbooks-*/Makefile` `test` recipes and `entrypoint/check-tools.sh`: call bare
   `python3 -m pytest -q`, since a path argument overrides `testpaths`.
3. If a converter module needs the `cnxml2tex`/`pandoc` dirs on `sys.path` to import, move the
   `tools/tests/conftest.py` path setup up to `tools/conftest.py` so it covers the whole collection.
4. Verify: `make image` (runs `check-tools.sh`) and one book's `apply.sh` + `make test`.
