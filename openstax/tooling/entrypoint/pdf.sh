#!/bin/bash
# Build the book master PDFs with latexmk into output/.
# Usage: pdf.sh [master-stem ...]   (default: every collection master in latex/)
set -euo pipefail

PROJ=/book
cd "$PROJ"
mkdir -p output

# pdflatex can't embed SVG figures: convert any media/*.svg to media/*.pdf once
# (skipped if the .pdf already exists). The .pdf are gitignored build artifacts.
if command -v rsvg-convert >/dev/null 2>&1; then
    shopt -s nullglob
    n=0
    for f in media/*.svg; do
        pdf="${f%.svg}.pdf"
        if [ ! -e "$pdf" ]; then rsvg-convert -f pdf -o "$pdf" "$f" && n=$((n+1)); fi
    done
    [ "$n" -gt 0 ] && echo "converted $n SVG figure(s) to PDF"
    shopt -u nullglob
fi

# rasterize exercise SVGs -> PNG (committed source stays in exercises/media/;
# derived PNGs in exercises/media-derived/ are gitignored). PNG works in pdflatex.
if command -v rsvg-convert >/dev/null 2>&1; then
    shopt -s nullglob
    mkdir -p exercises/media-derived
    for f in exercises/media/*.svg; do
        p="exercises/media-derived/$(basename "${f%.svg}").png"
        [ -e "$p" ] || rsvg-convert -f png -o "$p" "$f"
    done
    shopt -u nullglob
fi

cd latex

if [ "$#" -gt 0 ]; then
    targets=("$@")
else
    targets=()
    # build only the collection masters (by slug), NOT cheat-sheet/fragment .tex
    for c in ../collections/*.collection.xml; do
        [ -e "$c" ] || continue
        targets+=("$(basename "$c" .collection.xml)")
    done
fi

for stem in "${targets[@]}"; do
    stem="${stem%.tex}"
    echo "=== Building ${stem}.pdf ==="
    latexmk -pdflua -interaction=nonstopmode -halt-on-error \
        -output-directory=../output "${stem}.tex"
    # LuaTeX prints nothing for a character no font has and says so only in the
    # log. Report the distinct ones, so a hole in the PDF is seen at build time.
    missing="$(grep -a -o 'Missing character: There is no .* (U+[0-9A-F]*)' "../output/${stem}.log" |
        grep -o 'U+[0-9A-F]*' | sort -u | tr '\n' ' ' || true)"
    if [ -n "$missing" ]; then
        echo "WARNING: ${stem}.pdf leaves out characters no font has: $missing"
    else
        echo "${stem}.pdf: no character is missing from the fonts."
    fi
done

echo "PDFs are in $PROJ/output:"
ls -1 "$PROJ"/output/*.pdf 2>/dev/null || true
