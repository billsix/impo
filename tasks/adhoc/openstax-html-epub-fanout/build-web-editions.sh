#!/bin/bash
# Build the HTML (chunked web) + EPUB editions for every OpenStax book, to
# validate those two formats across all 16 books (the PDF pass was done earlier;
# see tasks/build-all-books.md). Refreshes each book's tooling overlay first
# (./apply.sh) so the latest converter + pandoc filters are used, then runs
# `make html` and `make epub`. Non-fatal: logs each book's result and continues,
# so one broken book doesn't stop the sweep (the report-everything discipline).
#
# Run from the impo repo root:  bash tasks/adhoc/openstax-html-epub-fanout/build-web-editions.sh
# Concise per-book status goes to stdout (and $SUMMARY); verbose per-book build
# logs go to $LOGDIR/<book>.<fmt>.log for diagnosing a failure.
#
# Idempotent: re-running rebuilds; make skips up-to-date targets. Pass a single
# book slug as $1 to build just that one (used to re-run a book after a fix).
set -u
cd "$(dirname "$0")/../../.." || exit 1   # tasks/adhoc/<slug>/ -> repo root

LOGDIR="${LOGDIR:-/tmp/claude-0/-foo-opt/88fea41b-84fa-46ae-b72d-0fa3a0da0348/scratchpad/fanout}"
SUMMARY="$LOGDIR/summary.log"
mkdir -p "$LOGDIR"

books=()
if [ "$#" -ge 1 ]; then
    books=("openstax/osbooks-$1/" )        # single book: pass its slug w/o osbooks-
    [ -d "${books[0]}" ] || books=("openstax/$1/")
else
    for d in openstax/osbooks-*/; do books+=("$d"); done
fi

for book in "${books[@]}"; do
    b=$(basename "$book")
    # refresh the tooling overlay so the current converter/filters/css are used
    ( cd "$book" && ./apply.sh ) >"$LOGDIR/$b.apply.log" 2>&1
    for fmt in html epub; do
        vlog="$LOGDIR/$b.$fmt.log"
        if ( cd "$book" && make "$fmt" ) >"$vlog" 2>&1; then
            # count what was produced as a sanity signal
            if [ "$fmt" = html ]; then
                n=$(find "$book/checkout/output" -name index.html 2>/dev/null | wc -l)
                unit="site(s)"
            else
                n=$(ls "$book"/checkout/output/*.epub 2>/dev/null | wc -l)
                unit="epub(s)"
            fi
            line="PASS  $b  $fmt  ($n $unit)"
        else
            # surface the first hard error signature for triage
            err=$(grep -m1 -E '! Undefined|! LaTeX Error|Fatal|pandoc:|Error producing|Traceback' "$vlog" | head -c 120)
            line="FAIL  $b  $fmt  -- ${err:-see $vlog}"
        fi
        echo "$line" | tee -a "$SUMMARY"
    done
done
echo "FANOUT COMPLETE ($(date +%H:%M:%S))" | tee -a "$SUMMARY"
