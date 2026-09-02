#!/bin/bash
# Fetch the pinned, pristine OpenStax content for Contemporary Mathematics into checkout/
# (gitignored). This is the OpenStax-owned layer (collections/ + modules/ +
# media/); the maintainer's toolchain is overlaid on top of it by apply.sh.
# Idempotent: an existing checkout/ is left untouched.
#
# Runnable from anywhere (cd to the script's own dir; only relative paths).
set -euo pipefail
cd "$(dirname "$0")"

# --- the pin -----------------------------------------------------------------
# The merge-base where the maintainer's `latex` port branch diverged from
# OpenStax's `main`, i.e. the pristine content the port was made against.
# Resolved from the short pin in tasks/openstax-populate-books.md (2026-09-02).
PIN_SHA=2319ce22654c12c946a7faed3b135f4a2c6f613e

# Canonical upstream; the pin is a commit on OpenStax's main history and is
# fetchable there by SHA. The maintainer's Pi mirror
# (pi@192.168.0.186:/mnt/usbdrive2/gitRepos/openstax/**/osbooks-contemporary-mathematics.git)
# is the fallback if GitHub is ever unreachable.
UPSTREAM_URL=https://github.com/openstax/osbooks-contemporary-mathematics

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
echo "fetch.sh: done. Next: ./apply.sh, then make dist."
