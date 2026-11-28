#!/bin/bash
# Apply = overlay the SHARED toolchain (../tooling/) onto the fetched pristine
# checkout/, so the toolchain's scripts find tools/, latex/ (the house .cls/.sty),
# and entrypoint/ sitting beside the OpenStax CNXML. This is the OpenStax family's
# form of "apply" (see ../CLAUDE.md): the delta is a shared file set, not a
# git-am patch series, so we copy rather than replay commits.
#
# Idempotent and guarded (run ./fetch.sh first). The Makefile runs it before every
# build, so it copies only what differs, and it touches $CHECKOUT/.applied only
# when it copied something: the converted LaTeX depends on that stamp, so an
# unchanged toolchain does not force a reconvert.
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

changed=0

# overlay SOURCE DESTINATION: copy a toolchain file or directory over its checkout
# copy when the checkout copy is missing or differs. Files that exist only in the
# checkout (build caches, images the build derived) do not count as a difference.
overlay() {
    local source="$1" destination="$2" differences
    differences="$(diff -rq -x __pycache__ -x .pytest_cache -x .ruff_cache \
        "$source" "$destination" 2>&1 | grep -v "^Only in $destination" || true)"
    if [ -n "$differences" ]; then
        if [ -d "$source" ]; then
            mkdir -p "$destination"
            cp -R "$source/." "$destination/"
        else
            mkdir -p "$(dirname "$destination")"
            cp "$source" "$destination"
        fi
        changed=1
        echo "apply.sh: refreshed $destination"
    fi
}

# The converter + web-edition tools.
overlay "$TOOLING/tools" "$CHECKOUT/tools"

# The container entrypoint scripts (the Makefile also bind-mounts these live, but
# overlaying them keeps the checkout self-describing).
overlay "$TOOLING/entrypoint" "$CHECKOUT/entrypoint"

# The house document class + style, beside the generated masters that \input them.
for style in osbook.cls osbook-envs.sty osbook-defer.sty; do
    overlay "$TOOLING/latex/$style" "$CHECKOUT/latex/$style"
done

# Optional per-book theme override: the book's own bookstyle.tex (if any) becomes
# osbook-bookstyle.tex, which osbook.cls loads via \InputIfFileExists to re-set
# the font/palette. No-op for books without one.
if [ -f bookstyle.tex ]; then
    overlay bookstyle.tex "$CHECKOUT/latex/osbook-bookstyle.tex"
fi
# Optional per-book WEB theme override: the book's bookstyle-web.css (if any)
# goes into the checkout root; html.sh/epub.sh append it to osbook-web.css.
if [ -f bookstyle-web.css ]; then
    overlay bookstyle-web.css "$CHECKOUT/bookstyle-web.css"
fi

# Converter lint/type/test config (format.sh + test target read it).
overlay "$TOOLING/pyproject.toml" "$CHECKOUT/pyproject.toml"

# The COPYRIGHT template used by fetch_exercises for books that have exercises.
overlay "$TOOLING/templates" "$CHECKOUT/templates"

# If this book carries a committed download cache (os-embed exercises), copy it
# in beside the CNXML so the build finds it offline. Books without exercises
# simply skip this (no exercises/ dir here).
if [ -d exercises ]; then
    overlay exercises "$CHECKOUT/exercises"
fi

# The stamp the converted LaTeX depends on (see the Makefile): newer than the
# conversion exactly when this run changed the overlay.
if [ "$changed" = 1 ] || [ ! -f "$CHECKOUT/.applied" ]; then
    touch "$CHECKOUT/.applied"
    echo "apply.sh: overlay updated. Next: make dist  (or make convert / make pdf)."
else
    echo "apply.sh: overlay already current."
fi
