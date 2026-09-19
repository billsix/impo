#!/bin/bash
# Apply = overlay the shared OpenStax house style + the trench restyle shim onto
# the fetched Trench source in checkout/, so the book typesets in the same style
# as the OpenStax books.
#
# Unlike the OpenStax books (whose "apply" overlays a CNXML->LaTeX converter), the
# Trench source is ALREADY LaTeX, so here "apply" = drop osbook.cls + envs/defer
# and the trench->osbook shim beside the .tex masters. No python converter runs.
#
# Idempotent (plain overwrite) and guarded: run ./fetch.sh first.
# Runnable from anywhere (cd to the script's own dir; only relative paths).
set -euo pipefail
cd "$(dirname "$0")"

# The shared toolchain lives in the openstax family; the trench family reuses its
# LaTeX house-style layer and its Fedora/TeXLive/pandoc image (see the impo family
# contract, ../../openstax/CLAUDE.md, and tasks/add-trench-differential-equations-book.md).
TOOLING=../../openstax/tooling
CHECKOUT=checkout

[ -d "$CHECKOUT" ] || {
    echo "apply.sh: $CHECKOUT/ not found — run ./fetch.sh first." >&2
    exit 1
}
[ -d "$TOOLING" ] || {
    echo "apply.sh: $TOOLING/ not found — expected the shared OpenStax toolchain." >&2
    exit 1
}

echo "apply.sh: overlaying the OpenStax house style onto $CHECKOUT/ ..."

# The house LaTeX class + styles, beside the Trench masters (which the phase-2
# normalization switches to \documentclass{osbook}).
cp "$TOOLING/latex/osbook.cls" "$TOOLING/latex/osbook-envs.sty" \
   "$TOOLING/latex/osbook-defer.sty" "$CHECKOUT/"

# PHASE 2 (tasks/add-trench-differential-equations-book.md): the trench->osbook
# compatibility shim (latex/trench-osbook.sty) maps wtrench.sty's macros/sectioning
# onto osbook; a deterministic transform then normalizes the .tex master preamble.
# Both are added in phase 2. Until the shim exists this overlay only supplies the
# class, so a build won't yet produce the osbook look.
if [ -f latex/trench-osbook.sty ]; then
    cp latex/trench-osbook.sty "$CHECKOUT/"
    echo "apply.sh: copied trench-osbook.sty shim."
else
    echo "apply.sh: NOTE latex/trench-osbook.sty not present yet (phase 2) — style not applied."
fi

echo "apply.sh: done. Next: make pdf  (needs the phase-2 shim + phase-3 EPS step to succeed)."
