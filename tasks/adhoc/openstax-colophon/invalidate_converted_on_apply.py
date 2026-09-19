#!/usr/bin/env python3
r"""Make every OpenStax book's apply.sh drop the .converted stamp (idempotent).

Part of tasks/openstax-about-this-edition-colophon.md. A re-apply overlays a new
shared toolchain (e.g. the colophon-emitting convert.py) into checkout/, but the
`checkout/latex/.converted` stamp was left intact -- so `make pdf`/`convert` could
skip regenerating and keep serving masters made by the OLD converter (exactly the
"I don't see the colophon" symptom). This inserts a `rm -f
"$CHECKOUT/latex/.converted"` at the end of each apply.sh so re-applying always
invalidates the generated LaTeX and the next build reconverts.

Idempotent: an apply.sh that already removes the stamp is skipped; a second run
changes nothing. Paths are relative to the git repo root, never container-absolute.
Run:  python3 tasks/adhoc/openstax-colophon/invalidate_converted_on_apply.py
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

FINAL_ECHO: str = 'echo "apply.sh: done. Next: make dist  (or make convert / make pdf)."'
INSERT: str = (
    "# A re-apply means the shared toolchain changed, so the previously generated\n"
    "# LaTeX masters are stale -- drop the convert stamp so the next build reconverts\n"
    "# with the just-overlaid converter (otherwise a stale checkout copy could linger).\n"
    'rm -f "$CHECKOUT/latex/.converted"\n'
    "\n" + FINAL_ECHO
)


def repo_root() -> Path:
    out: str = subprocess.check_output(
        ["git", "rev-parse", "--show-toplevel"], text=True
    ).strip()
    return Path(out)


def main() -> int:
    root: Path = repo_root()
    scripts: list[Path] = sorted(root.glob("openstax/osbooks-*/apply.sh"))
    if not scripts:
        print("no openstax/osbooks-*/apply.sh found", file=sys.stderr)
        return 1
    changed: int = 0
    for sh in scripts:
        text: str = sh.read_text(encoding="utf-8")
        rel: str = sh.relative_to(root).as_posix()
        if 'rm -f "$CHECKOUT/latex/.converted"' in text:
            print(f"  skip (already done): {rel}")
            continue
        if FINAL_ECHO not in text:
            print(f"  WARN: final echo not found, skipping: {rel}", file=sys.stderr)
            continue
        sh.write_text(text.replace(FINAL_ECHO, INSERT, 1), encoding="utf-8")
        print(f"  updated: {rel}")
        changed += 1
    print(f"invalidate_converted_on_apply: {changed} changed of {len(scripts)} apply.sh")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
