#!/bin/bash
# Build the web edition as a MULTIPAGE (chunked) site via `pandoc -t chunkedhtml`:
# each collection is split into one page per section (output/<slug>/), with a TOC
# index page and top+bottom Up/Top/Prev/Next navigation (custom template). Entry
# point is  output/<slug>/index.html .
#
# The generated .tex are NOT modified: copied to a temp tree and run through the
# HTML-only preprocessor (same as before). Media/exercise images are SYMLINKED
# into each site dir (not copied) to keep the tree small. The old single-file
# build lives in html-single.sh (`make html-single`).
set -euo pipefail

ROOT=/book
cd "$ROOT"
mkdir -p output
cp tools/pandoc/osbook-web.css output/osbook-web.css

# this book's figures are SVG; pandoc can't embed SVG/PDF, so rasterize once.
if command -v rsvg-convert >/dev/null 2>&1; then
    shopt -s nullglob
    for f in media/*.svg; do p="${f%.svg}.png"; [ -e "$p" ] || rsvg-convert -f png -o "$p" "$f"; done
    if [ -d exercises/media ]; then          # injected-exercise images (anatomy-physiology only)
        mkdir -p exercises/media-derived
        for f in exercises/media/*.svg; do
            p="exercises/media-derived/$(basename "${f%.svg}").png"; [ -e "$p" ] || rsvg-convert -f png -o "$p" "$f"
        done
    fi
    shopt -u nullglob
fi

# temp build tree (generated LaTeX untouched), HTML-only preprocessing
BUILD=/tmp/htmlbuild
rm -rf "$BUILD" && mkdir -p "$BUILD/sections"
cp latex/*.tex "$BUILD/"
cp latex/sections/*.tex "$BUILD/sections/"
python3 tools/pandoc/preprocess.py "$BUILD"/*.tex "$BUILD"/sections/*.tex
printf '%s\n' '\providecommand{\captionof}[2]{\par\textit{#2}}' > "$BUILD/defs.tex"

SPLIT="${SPLIT_LEVEL:-2}"       # 1 = per chapter/unit, 2 = per section (default)
cd "$BUILD"
for slug in $(cd "$ROOT/collections" && ls *.collection.xml | sed 's/\.collection\.xml$//'); do
    title=$(grep -m1 -oP '(?<=<md:title>)[^<]+' "$ROOT/collections/${slug}.collection.xml" || echo "$slug")
    outdir="$ROOT/output/${slug}"
    rm -rf "$outdir"
    echo "=== building ${slug}/ (multipage, split-level=$SPLIT) ==="
    # --chunk-template "%n-%i.html": chunk NUMBER (zero-padded) + section id, so
    #   filenames are ordered and never start with a dash (the default "%s-%i"
    #   left unnumbered front matter as "-getting-started.html").
    # --resource-path: chunkedhtml collects referenced images, so it must find them.
    pandoc -f latex -t chunkedhtml \
        --split-level="$SPLIT" --toc --toc-depth=2 --mathml \
        --template="$ROOT/tools/pandoc/chunked-template.html" \
        --chunk-template="%n-%i.html" \
        --resource-path="$ROOT" \
        --lua-filter="$ROOT/tools/pandoc/xref.lua" \
        --css=osbook-web.css \
        --metadata title="$title" \
        --metadata lang=en \
        defs.tex "${slug}.tex" \
        -o "$outdir"
    cp "$ROOT/tools/pandoc/osbook-web.css" "$outdir/osbook-web.css"
    # Optional per-book web theme: a book may ship bookstyle-web.css (placed in the
    # checkout by apply.sh) to override the shared palette/fonts. Appended AFTER the
    # base css so its :root wins the cascade. No-op for books without one. This is
    # the web-edition twin of the PDF's bookstyle.tex / osbook-bookstyle.tex hook.
    [ -f "$ROOT/bookstyle-web.css" ] && cat "$ROOT/bookstyle-web.css" >> "$outdir/osbook-web.css"
    # the web-edition JS (right "On this page" TOC + scrollspy + mobile toggle)
    cp "$ROOT/tools/pandoc/osbook-web.js" "$outdir/osbook-web.js"
    # inject the whole-book TOC into each page's left sidebar (from sitemap.json,
    # at build time so it works offline/file://; see build_nav.py)
    python3 "$ROOT/tools/pandoc/build_nav.py" "$outdir"
    # pandoc COPIED media/ + exercises/ in to be self-contained; swap those for
    # symlinks to the repo dirs (identical files) to avoid ~100 MB of duplication.
    for res in media exercises; do
        [ -d "$ROOT/$res" ] || continue      # skip a resource dir this book lacks
        [ -e "$outdir/$res" ] && rm -rf "$outdir/$res"
        ln -sfn "../../$res" "$outdir/$res"
    done
    echo "  pages: $(ls "$outdir"/*.html 2>/dev/null | wc -l)  (entry: output/${slug}/index.html)"
done

echo "Web edition (multipage):"
for d in "$ROOT/output"/*/; do
    if [ -f "$d/index.html" ]; then
        echo "  ${d}index.html ($(ls "$d"*.html 2>/dev/null | wc -l) pages)"
    fi
done
