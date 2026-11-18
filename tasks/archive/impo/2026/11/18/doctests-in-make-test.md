# Collect the converter doctests in `make test` (done)

**Done:** 2026-11-18 (William Emerison Six <billsix@gmail.com>)

Every book's `make test` ran `python3 -m pytest tools/tests -q`, which collected no doctests. The
house rule is that the test gate runs them (the `doctests-by-default.md` reference doc in
github.com/billsix/runClaudeInContainer, "## Python").

What changed:
- `openstax/tooling/pyproject.toml` `[tool.pytest.ini_options]` sets `testpaths = ["tools"]` and
  `addopts = "--doctest-modules --import-mode=importlib"`. Each `apply.sh` copies that file into the
  checkout, so every book picks it up.
- The 16 `openstax/osbooks-*/Makefile` `test` recipes and `openstax/tooling/entrypoint/check-tools.sh`
  (the image-build gate) call bare `python3 -m pytest -q`, since a path argument would override
  `testpaths`.

All five converter modules were already `__main__`-guarded, so collecting them imports cleanly. No
`conftest.py` move was needed: the modules' own imports resolve without the `tools/tests`
`sys.path` setup.

Verified nested on 2026-11-18 with `osbooks-introduction-python-programming`: `make image` (its
`check-tools.sh` step: 33 passed), then `./apply.sh` and `make test` (33 passed). The 31 unit tests
are joined by the two doctests in the vendored `tools/check_local_annotations.py` (`display_path`,
`iter_py`). The converter modules carry no doctests yet; any added to them now run in `make test`.
