#!/usr/bin/env python3
"""Add the per-book WEB theme override copy to every book's apply.sh.

Companion to the PDF bookstyle wiring (add-bookstyle-copy-to-apply.py): after a
book's bookstyle.tex is copied for the PDF, also copy its optional bookstyle-web.css
into the checkout root, where html.sh/epub.sh append it to osbook-web.css to override
the shared web palette/fonts. No-op for books without one; only calculus ships one.

Inserts the copy line right after the existing bookstyle.tex line. Idempotent: skips
an apply.sh that already has the web copy. Run from the repo root:
  python3 tasks/adhoc/openstax-web-theme/add-web-bookstyle-copy-to-apply.py
"""
from __future__ import annotations

import glob
import os

# the PDF-bookstyle line every apply.sh already has (added by the earlier codemod)
ANCHOR = '[ -f bookstyle.tex ] && cp bookstyle.tex "$CHECKOUT/latex/osbook-bookstyle.tex"\n'
INSERT = (
    '# Optional per-book WEB theme override: copy the book\'s bookstyle-web.css (if\n'
    '# any) into the checkout root; html.sh/epub.sh append it to osbook-web.css.\n'
    '[ -f bookstyle-web.css ] && cp bookstyle-web.css "$CHECKOUT/bookstyle-web.css"\n'
)

os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "openstax"))

for path in sorted(glob.glob("osbooks-*/apply.sh")):
    text = open(path, encoding="utf-8").read()
    if "bookstyle-web.css" in text:
        print(f"skip (already wired): {path}")
        continue
    if ANCHOR not in text:
        print(f"WARN anchor not found, skipping: {path}")
        continue
    open(path, "w", encoding="utf-8").write(text.replace(ANCHOR, ANCHOR + INSERT, 1))
    print(f"wired: {path}")
