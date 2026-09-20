#!/bin/bash
# Format + lint + type-check the in-repo converter sources (tools/*.py), in the
# container, via `make format`. Modeled on the geometricalgebra project, but this
# repo has NO venv (system python3 from dnf), so the tools are invoked directly.
#
# Order: ruff auto-fixes (import sort, unused imports, pyupgrade) -> ruff format
# (the canonical layout) -> ty type check. Rule selection + line length live in
# pyproject.toml [tool.ruff]. Source is bind-mounted, so fixes land on the host.
#
# Bundle-agnostic: runs from the repo root (the image WORKDIR, over which the
# Makefile bind-mounts the bundle), so this file is IDENTICAL across every
# osbooks-* bundle -- no hardcoded bundle path.
set -eu

test -d tools || {
    echo "format.sh: run from the repo root (tools/ not found in $(pwd))" >&2
    exit 1
}

ruff check tools/ --fix
ruff format tools/

# Directory form: checks every .py the repo ships (some bundles lack
# fetch_exercises.py); tools/tests/* resolve via [tool.ty.environment] in
# pyproject.toml. Bundle-agnostic, so this file is identical across all bundles.
ty check tools/

# Enforce the house rule that every local AND module-level variable carries an
# explicit annotation (ty/ruff don't). The same check runs in the build/CI gate
# (entrypoint/check-tools.sh); running it here means `make format` catches a
# missing annotation before the image build does.
python3 tools/check_local_annotations.py --include-module tools
