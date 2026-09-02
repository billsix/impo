#!/bin/bash
# Download the os-embed practice exercises referenced by the CNXML into the
# committed exercises/ cache (questions-only; the public OpenStax Exercises API
# withholds answer keys and solutions).
#
# This is the ONLY networked step. Run it occasionally and commit exercises/;
# the build (convert/pdf/html/epub) reads the cache and never hits the network.
#
# Bundle-agnostic: fetch_exercises.py derives all its paths from its own file
# location (not cwd), so this wrapper is identical across every osbooks-* repo.
set -euo pipefail
python3 tools/cnxml2tex/fetch_exercises.py "$@"
