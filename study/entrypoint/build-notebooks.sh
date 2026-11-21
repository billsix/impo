#!/bin/bash
# Generate, execute and summarize one book's problem notebooks, in the notebook
# image (study/notebooks/Dockerfile):
#   build-notebooks.sh <book> [section ...]
# -> output/notebooks/<book>/<x.y>.py (jupytext source), <x.y>.ipynb (executed,
#    with outputs and ePiX graphs), <x.y>.status.json, and summary.json.
# Needs that book's converted sections (`make convert` in its openstax/ folder).
# Every notebook is executed (JOBS at a time, a failed one once more) and the
# script fails if any failed.
set -u
cd "$(dirname "$0")/.." || exit 1          # entrypoint/ -> study/
book=${1:?usage: build-notebooks.sh <book> [section ...]}
shift
export PYTHONPATH="$(pwd)/tools"
python3 tools/notebooks.py generate "$book" "$@" || exit 1
cd "output/notebooks/$book" || exit 1
rm -f ./*.status.json
if [ "$#" -gt 0 ]; then
    sources=(); for s in "$@"; do sources+=("$s.py"); done
else
    sources=(*.py)
fi
status=0
printf '%s\n' "${sources[@]}" | xargs -P "${JOBS:-8}" -I{} bash -c '
    nb="${1%.py}.ipynb"
    run() { jupyter nbconvert --log-level=ERROR --to notebook --execute --inplace \
                --ExecutePreprocessor.timeout=1200 "$nb" >"${1%.py}.log" 2>&1; }
    # Second try: with many kernels starting at once, one can die before its
    # first reply ("Kernel died before replying to kernel_info").
    if jupytext --quiet --to ipynb "$1" && { run "$1" || run "$1"; }; then
        echo "PASS  $nb"
    else
        echo "FAIL  $nb (log: ${1%.py}.log)"; exit 1
    fi' _ {} || status=1
cd ../../.. || exit 1
python3 tools/notebooks.py summary "$book" || status=1
exit $status
