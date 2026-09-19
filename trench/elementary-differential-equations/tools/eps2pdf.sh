#!/bin/bash
# Phase 3 (impo trench family): convert Trench's EPS figures to PDF so lualatex
# (osbook) can \includegraphics them -- lualatex cannot read EPS directly. Reads
# <SRC>/*.eps and writes <OUT>/*.pdf (which is on the normalized master's
# \graphicspath). Idempotent: skips a .pdf at least as new as its .eps.
#
# Two steps per figure: (1) epstopdf converts EPS->PDF; (2) pdfcrop trims the PDF
# to its true ink bounds. Step 2 matters -- these figures' EPS BoundingBoxes
# carry ASYMMETRIC dead whitespace (e.g. ~100pt left vs ~57pt right), so an
# uncropped PDF renders offset sideways inside its centered figure box. pdfcrop
# removes it so \centering actually centers the drawing.
#
# Needs epstopdf + pdfcrop + ghostscript (TeX Live), so it runs inside the build
# container. Paths are arguments (relative to cwd) -- never container-absolute.
#   In-container:  cd /book && bash <this> EPS EPS-pdf
set -e
SRC="${1:-EPS}"
OUT="${2:-EPS-pdf}"

[ -d "$SRC" ] || { echo "eps2pdf: source dir '$SRC' not found (run fetch.sh?)" >&2; exit 1; }
mkdir -p "$OUT"

# Per the multi-step-failure rule: convert EVERY figure (report all failures) but
# still exit nonzero if any failed -- do NOT let one bad EPS abort the batch.
status=0
converted=0
skipped=0
shopt -s nullglob
for eps in "$SRC"/*.eps; do
    base=$(basename "$eps" .eps)
    pdf="$OUT/$base.pdf"
    if [ -f "$pdf" ] && [ "$pdf" -nt "$eps" ]; then
        skipped=$((skipped + 1))
        continue
    fi
    tmp="$OUT/$base.tmp.pdf"
    if epstopdf --outfile="$tmp" "$eps" 2>/dev/null \
       && pdfcrop --margins 2 "$tmp" "$pdf" >/dev/null 2>&1; then
        rm -f "$tmp"
        converted=$((converted + 1))
    else
        rm -f "$tmp"
        echo "eps2pdf: FAILED $eps" >&2
        status=1
    fi
done

total=$(find "$SRC" -maxdepth 1 -name '*.eps' | wc -l)
[ "$total" -gt 0 ] || { echo "eps2pdf: no .eps files in '$SRC'" >&2; exit 1; }
echo "eps2pdf: $converted converted, $skipped up-to-date, of $total EPS -> $OUT (status $status)"
exit $status
