#!/bin/bash
# Read-only gate for the in-repo converter tooling (tools/*.py). ONE place for
# the gate logic, wrapped by both the Dockerfile build gate and the GitHub CI
# workflow (.github/workflows/checks.yml) -- so the two can't drift.
#
# Portable: runs in the toolchain image AND on a host from the repo root
# (openstax/tooling/), needing only ruff, ty, pytest and python3-lxml on PATH.
# No venv (system python3 from dnf), so the tools are invoked directly.
#
# Runs EVERY step and fails if ANY failed (reports all the red, not just the
# first) -- the multi-step-gate rule; `set -e` would be the wrong fix here:
#   1. ruff check          -- lint (non-mutating; `make format` does the --fix)
#   2. annotation checker  -- every local AND global carries an explicit type
#                             (ty/ruff don't enforce this; see the script)
#   3. ty check            -- static types
#   4. pytest tools/tests  -- converter unit tests
# Bundle-agnostic: relative paths from the repo root (the image WORKDIR, over
# which the Makefile bind-mounts the bundle), so this file is IDENTICAL across
# every osbooks-* bundle -- no hardcoded bundle path.
set -u

test -d tools || {
    echo "check-tools.sh: run from the repo root (tools/ not found in $(pwd))" >&2
    exit 1
}

status=0
ruff check tools/ || status=1
python3 tools/check_local_annotations.py --include-module tools || status=1
ty check tools/ || status=1
python3 -m pytest tools/tests -q || status=1
exit "$status"
