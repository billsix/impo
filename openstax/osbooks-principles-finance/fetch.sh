#!/bin/bash
# Fetch the pinned, pristine OpenStax content for Principles of Finance 2e into checkout/
# (gitignored). This is the OpenStax-owned layer (collections/ + modules/ +
# media/); the maintainer's toolchain is overlaid on top of it by apply.sh.
# Idempotent: an existing checkout/ is left untouched.
#
# Runnable from anywhere (cd to the script's own dir; only relative paths).
set -euo pipefail
cd "$(dirname "$0")"

# --- the pin -----------------------------------------------------------------
# The head of OpenStax's default branch when this book was added to impo
# (2026-11-28). The pin moves at every sync; this file is the source of truth.
PIN_SHA=e3e5135ae36e21282d7afb4cccd5ce09f421d830

# Canonical upstream; the pin is a commit on OpenStax's main history and is
# fetchable there by SHA. If the upstream does not answer or no longer has the
# pin, the fetch falls back to the maintainer's public mirror of the same
# repository (an unmodified copy, upstream's licence and history intact).
UPSTREAM_URL=https://github.com/openstax/osbooks-principles-finance
MIRROR_URL=https://github.com/billsix/osbooks-principles-finance

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
    git remote add mirror "$MIRROR_URL"
    # Fetch just the pinned commit (GitHub allows fetching a reachable SHA):
    # upstream first, then the mirror. GIT_TERMINAL_PROMPT=0 makes a repository
    # that is gone fail at once instead of asking for a user name.
    if ! GIT_TERMINAL_PROMPT=0 git fetch --depth 1 origin "$PIN_SHA"; then
        echo "fetch.sh: upstream did not provide $PIN_SHA — trying the mirror $MIRROR_URL ..." >&2
        if ! GIT_TERMINAL_PROMPT=0 git fetch --depth 1 mirror "$PIN_SHA"; then
            echo "fetch.sh: neither the upstream nor the mirror has $PIN_SHA." >&2
            exit 1
        fi
    fi
    git checkout -q FETCH_HEAD
) || {
    # Leave no half-made repository behind: the guard above treats a checkout
    # with a .git as already fetched.
    rm -rf "$CHECKOUT/.git"
    exit 1
}
echo "fetch.sh: done. Next: ./apply.sh, then make dist."
