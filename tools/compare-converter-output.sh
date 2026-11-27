#!/bin/bash
# Convert every fetched OpenStax book twice, with the converter committed at HEAD and with
# the one in the working tree, and list the generated LaTeX files that differ.
#
#   bash tools/compare-converter-output.sh <scratch dir>
#
# <scratch dir> must not exist yet. Each conversion runs in a root of its own under
# <scratch dir>/<book>/{old,new}/, so the checkouts are only read; the differences are
# in <scratch dir>/<book>.diff.
set -euo pipefail
[ "$#" -eq 1 ] || {
    echo 'usage: compare-converter-output.sh <scratch dir that does not exist yet>' >&2
    exit 2
}
mkdir "$1"
scratch="$(cd "$1" && pwd)"
cd "$(git -C "$(dirname "$0")" rev-parse --show-toplevel)"
git show HEAD:openstax/tooling/tools/cnxml2tex/convert.py >"$scratch/convert-old.py"
cp openstax/tooling/tools/cnxml2tex/convert.py "$scratch/convert-new.py"

convert_one() {
    local book="$1" scratch="$2" which root entry
    for which in old new; do
        # The converter finds its book beside its own tools/ folder, so each run gets
        # a root of its own: the toolchain copied in, the book's source linked in.
        root="$scratch/$book/$which"
        mkdir -p "$root/latex"
        cp -R openstax/tooling/tools "$root/tools"
        cp "$scratch/convert-$which.py" "$root/tools/cnxml2tex/convert.py"
        for entry in modules collections media exercises; do
            [ -e "openstax/$book/checkout/$entry" ] && ln -s "$PWD/openstax/$book/checkout/$entry" "$root/$entry"
        done
        IMPO_COMMIT=compare IMPO_BUILD_DATE=compare python3 "$root/tools/cnxml2tex/convert.py" all \
            >"$scratch/$book.$which.log" 2>&1 || echo "$book: $which conversion FAILED"
    done
    diff -r "$scratch/$book/old/latex" "$scratch/$book/new/latex" >"$scratch/$book.diff" || true
    echo "$book: $(find "$scratch/$book/new/latex" -type f | wc -l) files, $(grep -c '^diff \|^Only in' "$scratch/$book.diff" || true) differ"
}
export -f convert_one

status=0
for folder in openstax/osbooks-*/checkout; do
    basename "$(dirname "$folder")"
done | xargs -P 6 -I{} bash -c "convert_one {} $scratch" || status=1
exit $status
