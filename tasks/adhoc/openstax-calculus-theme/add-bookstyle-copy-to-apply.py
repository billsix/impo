#!/usr/bin/env python3
"""Wire the per-book theme override into every book's apply.sh.

After the shared osbook.cls/osbook-envs.sty/osbook-defer.sty are overlaid onto a
book's checkout, also copy the book's own optional `bookstyle.tex` (if present in
the book folder) to `checkout/latex/osbook-bookstyle.tex` -- which osbook.cls loads
via `\\InputIfFileExists{osbook-bookstyle.tex}` to re-set the font/palette. No-op
for the (many) books without a bookstyle.tex; only calculus ships one today.

Idempotent: skips an apply.sh that already has the copy line. Run from the repo
root:  python3 tasks/adhoc/openstax-calculus-theme/add-bookstyle-copy-to-apply.py
"""
from __future__ import annotations

import glob
import os

# the exact line every apply.sh has, right after which we insert the override copy
ANCHOR = '   "$TOOLING/latex/osbook-defer.sty" "$CHECKOUT/latex/"\n'
INSERT = (
    '# Optional per-book theme override: copy the book\'s own bookstyle.tex (if any)\n'
    '# to osbook-bookstyle.tex, which osbook.cls loads via \\InputIfFileExists to\n'
    '# re-set the font/palette. No-op for books without one.\n'
    '[ -f bookstyle.tex ] && cp bookstyle.tex "$CHECKOUT/latex/osbook-bookstyle.tex"\n'
)

root = os.path.dirname(os.path.abspath(__file__))
os.chdir(os.path.join(root, "..", "..", "..", "openstax"))

for path in sorted(glob.glob("osbooks-*/apply.sh")):
    text = open(path, encoding="utf-8").read()
    if "osbook-bookstyle.tex" in text:
        print(f"skip (already wired): {path}")
        continue
    if ANCHOR not in text:
        print(f"WARN anchor not found, skipping: {path}")
        continue
    text = text.replace(ANCHOR, ANCHOR + "\n" + INSERT, 1)
    open(path, "w", encoding="utf-8").write(text)
    print(f"wired: {path}")
