#!/bin/bash
# The study/ gate: ruff, the annotate-every-binding checker (shared with the
# OpenStax toolchain), ty, pytest (doctests + tests/), and the content checks
# (every bank and cliff-notes answer equals its sympy computation; the committed
# quiz JSON matches the bank). Runs every step and fails if any failed.
set -u
cd "$(dirname "$0")/.." || exit 1          # entrypoint/ -> study/
status=0
ruff check tools tests || status=1
ruff format --check tools tests || status=1
python3 ../openstax/tooling/tools/check_local_annotations.py --include-module tools || status=1
ty check tools tests || status=1
python3 -m pytest -q || status=1
python3 tools/bank.py check || status=1
python3 tools/cliffnotes.py check || status=1
python3 tools/bank.py export --check || status=1
exit "$status"
