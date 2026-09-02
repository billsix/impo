#!/bin/bash
# Run the CNXML -> LaTeX converter, regenerating latex/sections/*.tex and the
# assembled collection masters. Per the project decision the generated .tex is
# committed and hand-maintained thereafter (one-time generator).
set -euo pipefail

cd /book

if [ -f tools/cnxml2tex/convert.py ]; then
    echo "Running CNXML -> LaTeX converter ..."
    python3 tools/cnxml2tex/convert.py "${@:-all}"
else
    echo "convert.sh: tools/cnxml2tex/convert.py missing." >&2
    exit 1
fi
