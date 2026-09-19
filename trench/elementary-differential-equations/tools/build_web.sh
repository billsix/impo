#!/bin/bash
# Build the HTML or EPUB web edition of the Trench book (impo trench family),
# restyled to the OpenStax family's Furo-like chunked theme (route a of
# tasks/trench-differential-equations-html-epub.md). Runs INSIDE the build
# container (make4ht/tex4ebook/gs from TeX Live), cwd=/book.
#
# Pipeline:
#   1. rasterize the cropped figure PDFs to PNG (tex4ht embeds PNG in HTML);
#   2. preprocess the fetched master into a tex4ht-ready bookW.tex
#      (web_preprocess.py); math stays native MathML;
#   3. make4ht (HTML) / tex4ebook (EPUB) compile the real LaTeX;
#   4. RESTYLE to the OpenStax theme:
#        HTML  -> split_html.py splits the monolithic bookW.html into chunked
#                 pages + sitemap.json, then the SHARED assets are applied
#                 (osbook-web.css/.js + build_nav.py, reused unchanged);
#        EPUB  -> the osbook theme CSS is appended into the epub's stylesheet
#                 (the reader supplies nav; the .layout grid rules are inert).
# Output: output/<fmt>/ (HTML: index.html + NNN-*.html + EPS/; EPUB: bookW.epub).
#
# Usage (in-container): bash <this> html|epub [tools-dir] [osbook-assets-dir]
set -e
FMT="${1:-html}"
TOOLS="${2:-/toolsrc}"
ASSETS="${3:-/osbook-assets}"   # openstax/tooling/tools/pandoc, mounted RO by the Makefile
SRC=TRENCH_DIFFEQ.tex
WORK=bookW.tex
TITLE="Elementary Differential Equations"
SUBTITLE="Formatted by Bill Six"

[ -f "$SRC" ] || { echo "build_web: $SRC not found (run ./fetch.sh)" >&2; exit 1; }
[ -d EPS-pdf ] || { echo "build_web: EPS-pdf/ missing (run 'make figures' first)" >&2; exit 1; }
[ -f "$ASSETS/osbook-web.css" ] || {
    echo "build_web: shared theme assets not at $ASSETS (the Makefile mounts" \
         "openstax/tooling/tools/pandoc there); pass the dir as arg 3" >&2; exit 1; }

bash "$TOOLS/eps2png.sh" EPS-pdf EPS-png 120
python3 "$TOOLS/web_preprocess.py" "$SRC" -o "$WORK" --defs "$TOOLS/pandoc-defs.tex"

out="output/$FMT"
case "$FMT" in
    html)
        make4ht -u "$WORK" "mathml"
        # Restyle (route a): chunk + theme. Fresh outdir each build.
        rm -rf "$out"; mkdir -p "$out/EPS-png"
        cp bookW.css "$out/"                            # tex4ht content typography
        cp "$TOOLS/trench-web.css" "$out/"              # the trench adapter (clashes + polish)
        cp "$ASSETS/osbook-web.css" "$ASSETS/osbook-web.js" "$out/"   # shared theme, reused as-is
        # make4ht's graphicspath prefers EPS-png/, so the <img> srcs are EPS-png/*.png.
        cp EPS-png/*.png "$out/EPS-png/" 2>/dev/null || true
        python3 "$TOOLS/split_html.py" bookW.html "$out" --title "$TITLE" --subtitle "$SUBTITLE"
        python3 "$ASSETS/build_nav.py" "$out"           # inject the left book TOC (shared, as-is)
        echo "build_web: HTML (OpenStax theme) -> $out/index.html"
        ;;
    epub)
        tex4ebook -f epub3 "$WORK" "mathml"
        mkdir -p "$out"
        # Restyle: append the osbook theme CSS into the epub's stylesheet(s) so the
        # EPUB matches the HTML edition. The .layout grid rules are inert in a reader
        # (no .layout element); the palette/headings/figure/MathML rules apply.
        styled="$(pwd)/$out/bookW.epub"
        workdir="$(mktemp -d)"
        unzip -q bookW.epub -d "$workdir"
        for css in $(find "$workdir" -name '*.css'); do
            cat "$ASSETS/osbook-web.css" "$TOOLS/trench-web.css" >> "$css"
        done
        rm -f "$styled"
        # EPUB packaging rule: mimetype first and STORED, everything else deflated.
        ( cd "$workdir" && zip -q -X -0 "$styled" mimetype \
              && zip -q -X -9 -r "$styled" . -x mimetype )
        rm -rf "$workdir"
        echo "build_web: EPUB (themed) -> $out/bookW.epub"
        ;;
    *)
        echo "build_web: unknown format '$FMT' (html|epub)" >&2
        exit 2
        ;;
esac
