#!/bin/bash
# Generate and typeset the study PDFs of one kind, in the study image:
#   build-pdfs.sh literacy      -> output/literacy/<subject>{,-key,-scoring}.pdf
#   build-pdfs.sh cliff-notes   -> output/cliff-notes/<subject>.pdf
# The generators check every answer first (sympy) and refuse to write a subject
# with a wrong one. The house class osbook.cls comes from openstax/tooling/latex
# through TEXINPUTS. Runs every document and fails if any failed.
set -u
cd "$(dirname "$0")/.." || exit 1          # entrypoint/ -> study/
kind=${1:?usage: build-pdfs.sh literacy|cliff-notes}
out="output/$kind"
mkdir -p "$out"
case "$kind" in
    literacy)    python3 tools/literacy.py "$out" || exit 1 ;;
    cliff-notes) python3 tools/cliffnotes.py "$out" || exit 1 ;;
    *)           echo "build-pdfs.sh: unknown kind $kind" >&2; exit 2 ;;
esac
export TEXINPUTS="$(cd ../openstax/tooling/latex && pwd)//:"
status=0
cd "$out" || exit 1
for tex in *.tex; do
    if latexmk -lualatex -interaction=nonstopmode -halt-on-error "$tex" >"${tex%.tex}.build.log" 2>&1; then
        echo "PASS  $out/${tex%.tex}.pdf"
    else
        echo "FAIL  $out/${tex%.tex}.pdf (log: $out/${tex%.tex}.build.log)"
        grep -m3 '^!' "${tex%.tex}.build.log" | sed 's/^/      /'
        status=1
    fi
done
exit $status
