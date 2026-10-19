#!/usr/bin/env bash
# Resync codemod (2026-10-19, agent unattended batch): bump each listed OpenStax
# book's PIN_SHA in its fetch.sh to the upstream default-branch HEAD captured at
# recon time, inserting a dated resync comment once. Idempotent: a file already at
# the new SHA is left untouched.
#
# Run from anywhere; resolves the repo root itself. The new SHAs are the HEADs read
# by `git ls-remote https://github.com/openstax/osbooks-<book> HEAD` on 2026-10-19.
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"

MARK="# Resync 2026-10-19 (agent): bumped to upstream HEAD; prior pin in git history."

declare -A NEW=(
  [anatomy-physiology]=5ae32b3f4bc24ed003e91dc38bf47dba80751044
  [astronomy]=dff6acf8df597ceda73985308f838ed38417a606
  [biology-bundle]=89c14e6d065606fdbe1e696ce2e8d9612a080147
  [calculus-bundle]=8dbc2ce19e804924b2517b89ac72ee45be949d15
  [chemistry-bundle]=db0a8e6027100ce082e67fc8879faab86f9a58a7
  [college-algebra-bundle]=463991614337632b0e02cbb6c76223cbb0d423d3
  [microbiology]=f91d7fcdc7ebbafa36ec33099f78ff0a494f1c2b
  [organic-chemistry]=8917713cdfb7f74018a8fd43cdcfe3173419bb82
  [physics]=56e71824e73e371c0d20eb68a77611aa438b5f89
  [prealgebra-bundle]=38cae454e644abf9f0a623e876994553881597c9
  [psychology]=de7e40c91813dabdc2875df9d0709fc4f46080bb
  [university-physics-bundle]=2300d5b8ca2571dacc6ec25ebef56ba8d49000a2
)

for book in "${!NEW[@]}"; do
  f="openstax/osbooks-$book/fetch.sh"
  sha="${NEW[$book]}"
  [ -f "$f" ] || { echo "MISSING: $f" >&2; exit 1; }
  if grep -q "PIN_SHA=$sha" "$f"; then
    echo "up-to-date: $book"
    continue
  fi
  # Insert the resync marker once, on the line above PIN_SHA=.
  if ! grep -qF "$MARK" "$f"; then
    python3 - "$f" "$MARK" <<'PY'
import sys
path, mark = sys.argv[1], sys.argv[2]
lines = open(path).read().splitlines(keepends=True)
out = []
for line in lines:
    if line.startswith("PIN_SHA="):
        out.append(mark + "\n")
    out.append(line)
open(path, "w").write("".join(out))
PY
  fi
  # Replace the PIN_SHA value (any 40-hex) with the new one.
  python3 - "$f" "$sha" <<'PY'
import re, sys
path, sha = sys.argv[1], sys.argv[2]
text = open(path).read()
text = re.sub(r'^PIN_SHA=[0-9a-f]{40}', f'PIN_SHA={sha}', text, count=1, flags=re.M)
open(path, "w").write(text)
PY
  echo "bumped: $book -> $sha"
done
