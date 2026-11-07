#!/bin/bash
# Build every format (PDF, HTML web edition, EPUB) of one, several, or all impo
# book folders, and collect the results into the repo-root output/ tree — the
# one-call book build behind `make books` / `make <book>` (root Makefile).
#
#   bash tools/build-books.sh                       # every book folder
#   bash tools/build-books.sh anatomy-physiology    # one (folder name, osbooks- optional)
#   bash tools/build-books.sh calculus-bundle physics
#
# Per folder: fetch.sh when there is no checkout/ yet (network), apply.sh (re-overlay
# the current toolchain), `make dist` in the folder, then collect into output/:
#   output/<book>/        the HTML site (media/ copied in, so the dir is self-contained)
#   output/<book>.pdf     the PDF
#   output/<book>.epub    the EPUB
# where <book> is each book the folder produces (a bundle folder produces several).
#
# Non-fatal per folder (one broken book doesn't stop the run), but the exit status
# is 1 if ANY folder failed, so `make books` and CI see the failure. Verbose logs go
# to $LOGDIR/<folder>.log; a PASS/FAIL line per folder goes to stdout.
set -u
cd "$(dirname "$0")/.." || exit 1          # tools/ -> repo root
ROOT=$(pwd)
OUT="$ROOT/output"
LOGDIR="${LOGDIR:-$ROOT/output/logs}"
mkdir -p "$OUT" "$LOGDIR"

# Resolve a name to its folder: openstax/osbooks-<name>, openstax/<name>, trench/<name>.
resolve() {
    local n=$1
    for d in "openstax/osbooks-$n" "openstax/$n" "trench/$n"; do
        [ -f "$d/Makefile" ] && { echo "$d"; return 0; }
    done
    return 1
}

folders=()
if [ "$#" -ge 1 ]; then
    for n in "$@"; do
        d=$(resolve "$n") || { echo "unknown book folder: $n (see: make list-books)" >&2; exit 2; }
        folders+=("$d")
    done
else
    for d in openstax/osbooks-*/ trench/*/; do
        [ -f "$d/Makefile" ] && folders+=("${d%/}")
    done
fi

# Copy a folder's built products into output/. OpenStax: checkout/output/<book>/
# (html, its media/ is a symlink into the checkout, so copy with -L to make the site
# self-contained), <book>.pdf, <book>.epub. Trench: fixed file names, renamed to the
# folder name.
collect() {
    local dir=$1 co="$1/checkout/output"
    case "$dir" in
        openstax/*)
            for site in "$co"/*/; do
                [ -f "$site/index.html" ] || continue
                local book; book=$(basename "$site")
                rm -rf "${OUT:?}/$book"
                cp -rL "$site" "$OUT/$book"
                for ext in pdf epub; do
                    [ -f "$co/$book.$ext" ] && cp "$co/$book.$ext" "$OUT/$book.$ext"
                done
            done ;;
        trench/*)
            local book; book=$(basename "$dir")
            rm -rf "${OUT:?}/$book"
            cp -rL "$co/html" "$OUT/$book"
            # The web edition's entry page is bookW.html; give the site an index.html.
            [ -f "$OUT/$book/index.html" ] || ln -s bookW.html "$OUT/$book/index.html"
            cp "$co/TRENCH_DIFFEQ-osbook.pdf" "$OUT/$book.pdf"
            cp "$co/epub/bookW.epub" "$OUT/$book.epub" ;;
        *)
            echo "collect: no rule for $dir" >&2; return 1 ;;
    esac
}

status=0
for dir in "${folders[@]}"; do
    name=$(basename "$dir")
    log="$LOGDIR/$name.log"
    start=$(date +%s)
    if {
        { [ -d "$dir/checkout" ] || "./$dir/fetch.sh"; } &&
        "./$dir/apply.sh" &&
        make -C "$dir" dist &&
        collect "$dir"
    } >"$log" 2>&1; then
        echo "PASS  $name  ($(( $(date +%s) - start ))s)"
    else
        echo "FAIL  $name  ($(( $(date +%s) - start ))s; log: ${log#"$ROOT"/})"
        grep -m1 -iE 'error|fatal|No such file' "$log" | sed 's/^/      /'
        status=1
    fi
done
exit $status
