#!/bin/bash
# Convert the cropped figure PDFs (EPS-pdf/, from `make figures`) to PNG for the
# HTML/EPUB web edition -- tex4ht and pandoc embed PNG in HTML, not PDF/EPS.
# Uses ghostscript (poppler's pdftoppm/pdftocairo are not in the build image);
# preserves the pdfcrop crop and rasterizes at <DPI> with antialiasing. Idempotent.
#
# Args are paths/number (relative to cwd), never container-absolute. In-container:
#   cd /book && bash <this> EPS-pdf EPS-png 120
set -e
SRC="${1:-EPS-pdf}"
OUT="${2:-EPS-png}"
DPI="${3:-120}"

[ -d "$SRC" ] || { echo "eps2png: source dir '$SRC' not found (run 'make figures' first)" >&2; exit 1; }
mkdir -p "$OUT"

# Convert every figure (report all failures) but still exit nonzero if any failed.
status=0
converted=0
skipped=0
shopt -s nullglob
for pdf in "$SRC"/*.pdf; do
    base=$(basename "$pdf" .pdf)
    png="$OUT/$base.png"
    if [ -f "$png" ] && [ "$png" -nt "$pdf" ]; then
        skipped=$((skipped + 1))
        continue
    fi
    if gs -sDEVICE=png16m -r"$DPI" -dQUIET -dNOPAUSE -dBATCH \
          -dGraphicsAlphaBits=4 -dTextAlphaBits=4 -o "$png" "$pdf" 2>/dev/null; then
        converted=$((converted + 1))
    else
        echo "eps2png: FAILED $pdf" >&2
        status=1
    fi
done

total=$(find "$SRC" -maxdepth 1 -name '*.pdf' | wc -l)
[ "$total" -gt 0 ] || { echo "eps2png: no .pdf files in '$SRC'" >&2; exit 1; }
echo "eps2png: $converted converted, $skipped up-to-date, of $total -> $OUT (status $status)"
exit $status
