#!/bin/bash
# Fetch the pinned, pristine Trench "Elementary Differential Equations" LaTeX
# source into checkout/ (gitignored). This is the content layer — the three .tex
# masters (main / boundary-value / student manual), wtrench.sty, and the EPS/
# figures. The OpenStax house style (osbook.cls) + the trench restyle shim are
# overlaid on top by apply.sh.
#
# Idempotent: an existing checkout/ is left untouched.
# Runnable from anywhere (cd to the script's own dir; only relative paths).
set -euo pipefail
cd "$(dirname "$0")"

# --- the pin -----------------------------------------------------------------
# HEAD of the maintainer's copy as of 2026-09-19 — the source this port is made
# against. Trench's book is native LaTeX; github.com/billsix carries the copy.
PIN_SHA=a7c17e34ee0326ff97824d166a1dc91547f8f2e7
UPSTREAM_URL=https://github.com/billsix/differentialEquationsTrench

CHECKOUT=checkout

if [ -e "$CHECKOUT/.git" ]; then
    echo "fetch.sh: $CHECKOUT/ already exists — leaving it untouched."
    echo "          (delete it and re-run to refetch at $PIN_SHA)"
    exit 0
fi

echo "fetch.sh: fetching $UPSTREAM_URL @ $PIN_SHA -> $CHECKOUT/ ..."
git init -q "$CHECKOUT"
(
    cd "$CHECKOUT"
    # Sandbox gitconfig enables commit signing, which fails here and would abort
    # any later git operation; disable it repo-locally (never globally).
    git config commit.gpgsign false
    git remote add origin "$UPSTREAM_URL"
    # Fetch just the pinned commit (GitHub allows fetching a reachable SHA).
    git fetch --depth 1 origin "$PIN_SHA"
    git checkout -q FETCH_HEAD
)
echo "fetch.sh: done. Next: ./apply.sh, then make pdf."
