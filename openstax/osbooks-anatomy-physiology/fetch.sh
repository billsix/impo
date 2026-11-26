#!/bin/bash
# Fetch the pinned, pristine OpenStax content for Anatomy & Physiology 2e into
# checkout/ (gitignored). This is the OpenStax-owned layer (collections/ +
# modules/ + media/); the maintainer's toolchain is overlaid on top of it by
# apply.sh. Idempotent: an existing checkout/ is left untouched.
#
# Runnable from anywhere (cd to the script's own dir; only relative paths).
set -euo pipefail
cd "$(dirname "$0")"

# --- the pin -----------------------------------------------------------------
# 716383a4c6 is the merge-base where the maintainer's `latex` port branch
# diverged from OpenStax's `main`, i.e. the pristine content the port was made
# against. It is main/HEAD of the canonical repo, verified fetchable there via
# `git ls-remote` (2026-09-02). OpenStax Anatomy & Physiology 2e content pin.
# Synced with the upstream default-branch head on 2026-11-26.
PIN_SHA=f273762340768a5f50e833c876e40b5a9c565da1

# Canonical upstream; the pin is a commit on OpenStax's main history and is
# fetchable there by SHA. If the upstream does not answer or no longer has the
# pin, the fetch falls back to the maintainer's public mirror of the same
# repository (an unmodified copy, upstream's licence and history intact).
UPSTREAM_URL=https://github.com/openstax/osbooks-anatomy-physiology
MIRROR_URL=https://github.com/billsix/osbooks-anatomy-physiology

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
