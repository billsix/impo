#!/usr/bin/env bash
# For each listed book: overlay the toolchain, convert (CNXML to LaTeX) and build every
# format, three books at a time. Writes one log per book and step under the log
# directory and prints a PASS/FAIL line per step; exits 1 if any step failed.
#
#   bash tasks/adhoc/openstax-sync-upstream-pins-2026-11/build_books.sh <log dir> <book> [<book> ...]
set -uo pipefail
cd "$(git -C "$(dirname "$0")" rev-parse --show-toplevel)" || exit 1
log_dir="$1"
shift
mkdir -p "$log_dir"

# Build one book; print PASS or FAIL for its convert and dist steps.
build_one() {
    local book="$1" folder="openstax/osbooks-$1" step
    (cd "$folder" && ./apply.sh) >"$log_dir/$book.apply.log" 2>&1 || { echo "$book apply FAIL"; return 1; }
    rm -f "$folder/checkout/latex/.converted"
    for step in convert dist; do
        if make -C "$folder" "$step" >"$log_dir/$book.$step.log" 2>&1; then
            echo "$book $step PASS $(date +%T)"
        else
            echo "$book $step FAIL $(date +%T)"
            return 1
        fi
    done
}
export -f build_one
export log_dir

# The image is the same for every book (context openstax/tooling), so build it once
# before fanning out; the per-book builds then hit the layer cache.
make -C "openstax/osbooks-$1" image >"$log_dir/image.log" 2>&1 || { echo "image FAIL"; exit 1; }
echo "image PASS $(date +%T)"
printf '%s\n' "$@" | xargs -P 3 -I{} bash -c 'build_one {}'
