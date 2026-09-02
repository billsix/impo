#!/bin/bash
# LEGACY single-file HTML build (one big output/<slug>.html). The DEFAULT
# `make html` now builds the multipage chunked site (html.sh); this is kept as
# `make html-single` for the occasional one-file export.
# Build the web edition: pandoc converts each collection master (LaTeX) to a
# standalone HTML5 page with MathML, the house CSS, and the xref.lua filter
# (numbering + cross-references + media-path rewrite).
#
# The generated .tex are NOT modified: they are copied to a temp tree and run
# through an HTML-only preprocessor (fixes $...$ nested in \text{}, which pandoc
# rejects). pandoc resolves \subfile relative to the CWD, so it runs from there.
set -euo pipefail

ROOT=/book
cd "$ROOT"
mkdir -p output
ln -sfn ../media output/media                       # so <img src="media/..."> resolves
ln -sfn ../exercises output/exercises               # so <img src="exercises/..."> resolves
cp tools/pandoc/osbook-web.css output/osbook-web.css

# this book's figures are SVG; pandoc can't embed SVG/PDF, so rasterize
# media/*.svg -> media/*.png once (xref.lua remaps the .pdf names to .png).
# The generated .png are gitignored build artifacts.
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
BUILD=/tmp/htmlbuild
rm -rf "$BUILD" && mkdir -p "$BUILD/sections"
cp latex/*.tex "$BUILD/"
cp latex/sections/*.tex "$BUILD/sections/"
python3 tools/pandoc/preprocess.py "$BUILD"/*.tex "$BUILD"/sections/*.tex

# pandoc doesn't know \captionof (capt-of pkg); define it so figure captions
# survive (prepended as an input file, expanded before the master that uses it).
printf '%s\n' '\providecommand{\captionof}[2]{\par\textit{#2}}' > "$BUILD/defs.tex"

cd "$BUILD"
for slug in $(cd "$ROOT/collections" && ls *.collection.xml | sed 's/\.collection\.xml$//'); do
    title=$(grep -m1 -oP '(?<=<md:title>)[^<]+' "$ROOT/collections/${slug}.collection.xml" || echo "$slug")
    echo "=== building ${slug}.html ==="
    pandoc -f latex -t html5 \
        --standalone --toc --toc-depth=2 --mathml \
        --lua-filter="$ROOT/tools/pandoc/xref.lua" \
        --css=osbook-web.css \
        --metadata title="$title" \
        --metadata lang=en \
        defs.tex "${slug}.tex" \
        -o "$ROOT/output/${slug}.html"
done

echo "Web edition:"
ls -1 "$ROOT/output"/*.html 2>/dev/null || true
