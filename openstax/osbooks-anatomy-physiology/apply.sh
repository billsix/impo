#!/bin/bash
# Apply = overlay the SHARED toolchain (../tooling/) onto the fetched pristine
# checkout/, so the toolchain's scripts find tools/, latex/ (the house .cls/.sty),
# and entrypoint/ sitting beside the OpenStax CNXML. This is the OpenStax family's
# form of "apply" (see ../CLAUDE.md): the delta is a shared file set, not a
# git-am patch series, so we copy rather than replay commits.
#
# Idempotent (plain overwrite) and guarded: run ./fetch.sh first.
# Anatomy & Physiology has NO os-embed exercises, so there is nothing else to
# overlay.
#
# Runnable from anywhere (cd to the script's own dir; only relative paths).
set -euo pipefail
cd "$(dirname "$0")"

TOOLING=../tooling
CHECKOUT=checkout

[ -d "$CHECKOUT" ] || {
    echo "apply.sh: $CHECKOUT/ not found — run ./fetch.sh first." >&2
    exit 1
}
[ -d "$TOOLING" ] || {
    echo "apply.sh: $TOOLING/ not found — expected the shared toolchain beside this book." >&2
    exit 1
}

echo "apply.sh: overlaying $TOOLING/ onto $CHECKOUT/ ..."

# The converter + web-edition tools.
cp -R "$TOOLING/tools" "$CHECKOUT/"

# The container entrypoint scripts (the Makefile also bind-mounts these live, but
# overlaying them keeps the checkout self-describing).
cp -R "$TOOLING/entrypoint" "$CHECKOUT/"

# The house document class + style, beside the generated masters that \input them.
mkdir -p "$CHECKOUT/latex"
cp "$TOOLING/latex/osbook.cls" "$TOOLING/latex/osbook-envs.sty" \
   "$TOOLING/latex/osbook-defer.sty" "$CHECKOUT/latex/"

# Optional per-book theme override: copy the book's own bookstyle.tex (if any)
# to osbook-bookstyle.tex, which osbook.cls loads via \InputIfFileExists to
# re-set the font/palette. No-op for books without one.
[ -f bookstyle.tex ] && cp bookstyle.tex "$CHECKOUT/latex/osbook-bookstyle.tex"
# Optional per-book WEB theme override: copy the book's bookstyle-web.css (if
# any) into the checkout root; html.sh/epub.sh append it to osbook-web.css.
[ -f bookstyle-web.css ] && cp bookstyle-web.css "$CHECKOUT/bookstyle-web.css"

# Converter lint/type/test config (format.sh + test target read it).
cp "$TOOLING/pyproject.toml" "$CHECKOUT/"

# The COPYRIGHT template used by fetch_exercises for books that have exercises.
cp -R "$TOOLING/templates" "$CHECKOUT/"

echo "apply.sh: done. Next: make dist  (or make convert / make pdf)."
