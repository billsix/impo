#!/bin/bash
# Discovery for tasks/openstax-cross-book-references.md: grep every fetched
# OpenStax checkout's CNXML for text that names ANOTHER book (explicit
# cross-book references), and write the matches + per-book counts to data/.
# Needs the books' checkouts (each folder's ./fetch.sh). Run from anywhere.
set -u
cd "$(dirname "$0")" || exit 1
ROOT=../../..
DATA=data
mkdir -p "$DATA"

# label|extended regex over the CNXML text
patterns=(
    'ia-tag|\(IA [0-9]+(\.[0-9]+)+\)'
    'calculus-volume|Calculus Volume [123]'
    'university-physics-volume|University Physics Volume [123]'
    'named-math-book|(Prealgebra|Elementary Algebra|Intermediate Algebra|College Algebra|Algebra and Trigonometry|Precalculus)( 2e)?( book| text|,? (Section|Chapter) [0-9])'
    'see-another-book|[Ss]ee (OpenStax|the OpenStax) [A-Z][a-z]+'
)

: > "$DATA/matches.tsv"
for co in "$ROOT"/openstax/osbooks-*/checkout; do
    folder=$(basename "$(dirname "$co")")
    for p in "${patterns[@]}"; do
        label=${p%%|*}; re=${p#*|}
        grep -rEoH --include=index.cnxml "$re" "$co/modules" 2>/dev/null |
            sed -E "s#^$co/modules/([^/]+)/index.cnxml:#\1\t#" |
            awk -v f="$folder" -v l="$label" -F'\t' '{print f "\t" l "\t" $1 "\t" $2}' >> "$DATA/matches.tsv"
    done
done
cut -f1,2 "$DATA/matches.tsv" | sort | uniq -c | sort -k2,2 -k1,1nr > "$DATA/counts.txt"
cat "$DATA/counts.txt"
