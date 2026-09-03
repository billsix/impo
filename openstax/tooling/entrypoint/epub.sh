#!/bin/bash
# Build the EPUB edition: pandoc converts each collection master (LaTeX) to an
# EPUB3 file with MathML, the house CSS, and embedded images, using the same
# xref.lua filter as the HTML build (numbering + cross-references + media-path
# rewrite).
#
# Like html.sh, the generated .tex are NOT modified: copied to a temp tree and
# run through the HTML-only preprocessor. Images embed via --resource-path
# pointing at the repo (where media/ lives).
set -euo pipefail

ROOT=/book
cd "$ROOT"
mkdir -p output

# this book's figures are SVG; pandoc can't embed SVG/PDF, so rasterize
# media/*.svg -> media/*.png once (xref.lua remaps the .pdf names to .png).
if command -v rsvg-convert >/dev/null 2>&1; then
    shopt -s nullglob
    for f in media/*.svg; do
        p="${f%.svg}.png"
        [ -e "$p" ] || rsvg-convert -f png -o "$p" "$f"
    done
    mkdir -p exercises/media-derived                # exercise SVGs -> PNG
    for f in exercises/media/*.svg; do
        p="exercises/media-derived/$(basename "${f%.svg}").png"
        [ -e "$p" ] || rsvg-convert -f png -o "$p" "$f"
    done
    shopt -u nullglob
fi

# temp build tree (committed/generated LaTeX untouched)
BUILD=/tmp/epubbuild
rm -rf "$BUILD" && mkdir -p "$BUILD/sections"
cp latex/*.tex "$BUILD/"
cp latex/sections/*.tex "$BUILD/sections/"
python3 tools/pandoc/preprocess.py "$BUILD"/*.tex "$BUILD"/sections/*.tex

printf '%s\n' '\providecommand{\captionof}[2]{\par\textit{#2}}' > "$BUILD/defs.tex"

# per-book web theme (same hook as html.sh): base css + optional book override
# (bookstyle-web.css, placed in the checkout by apply.sh), appended so its :root
# wins. Built once, embedded into every volume's EPUB. No-op without an override.
WEBCSS="$BUILD/osbook-web.css"
cp "$ROOT/tools/pandoc/osbook-web.css" "$WEBCSS"
[ -f "$ROOT/bookstyle-web.css" ] && cat "$ROOT/bookstyle-web.css" >> "$WEBCSS"

cd "$BUILD"
for slug in $(cd "$ROOT/collections" && ls *.collection.xml | sed 's/\.collection\.xml$//'); do
    title=$(grep -m1 -oP '(?<=<md:title>)[^<]+' "$ROOT/collections/${slug}.collection.xml" || echo "$slug")
    echo "=== building ${slug}.epub ==="
    pandoc -f latex -t epub3 \
        --toc --toc-depth=2 --mathml \
        --lua-filter="$ROOT/tools/pandoc/xref.lua" \
        --css="$WEBCSS" \
        --resource-path="$BUILD:$ROOT" \
        --metadata title="$title" \
        --metadata author="OpenStax" \
        --metadata lang=en \
        defs.tex "${slug}.tex" \
        -o "$ROOT/output/${slug}.epub"
done

echo "EPUB edition:"
ls -1 "$ROOT/output"/*.epub 2>/dev/null || true
