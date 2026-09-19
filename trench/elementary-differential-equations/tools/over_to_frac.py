#!/usr/bin/env python3
r"""Convert TeX primitive fractions `{num \over den}` -> `\frac{num}{den}`.

Trench's source uses the TeX primitive `\over` ~4700 times. pandoc's MathML output
(the EPUB path) cannot parse `\over`; `\frac` it handles, and MathJax (the HTML
path) renders `\frac` too -- so converting once serves both editions. This is
brace-AWARE (not sed): it reads the whole file (so multi-line `\over` is fine) and
matches the enclosing group by scanning for the balancing `{`/`}` or the `$...$`
math delimiters -- handling the nested-brace and brace-less/implicit-group cases
that a line-by-line regex cannot. `\overline`/`\overbrace`/... are left alone.

VALIDATED (2026-09-19 spike): converts the whole book (4622, 0 unresolved) AND Chapter 1
(94) with pandoc rendering the converted chapter cleanly to HTML and MathML/EPUB. (An
earlier "it breaks pandoc" scare was a host/container file-crossing artifact, not this tool.)
Only the EPUB/MathML path needs it; HTML uses --mathjax and renders \over natively.

NON-DESTRUCTIVE: reads a source .tex, writes a new one (default: `<stem>-frac.tex`),
and prints a report (converted count + any `\over` it could NOT resolve, with line
numbers, so the maintainer can eyeball). The pinned source never changes.

Run:  python3 tools/over_to_frac.py <in.tex> [out.tex]
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

OVER: re.Pattern[str] = re.compile(r"\\over(?![a-zA-Z])")   # \over as a whole control word


def _group_start(s: str, i: int) -> tuple[int, str] | None:
    """Scan left from index i for the enclosing group open: a `{` at depth 0, or a
    `$` math boundary. Returns (index, kind) or None."""
    depth: int = 0
    j: int = i - 1
    while j >= 0:
        c: str = s[j]
        if c == "}":
            depth += 1
        elif c == "{":
            if depth == 0:
                return j, "{"
            depth -= 1
        elif c == "$" and depth == 0:
            return j, "$"
        j -= 1
    return None


def _group_end(s: str, i: int) -> int | None:
    """Scan right from index i for the enclosing group close: a `}` at depth 0 or a
    `$`. Returns index or None."""
    depth: int = 0
    k: int = i
    while k < len(s):
        c: str = s[k]
        if c == "{":
            depth += 1
        elif c == "}":
            if depth == 0:
                return k
            depth -= 1
        elif c == "$" and depth == 0:
            return k
        k += 1
    return None


def convert(s: str, limit: int | None = None) -> tuple[str, int, list[int]]:
    """Return (converted text, num_converted, unresolved_source_offsets). If `limit`
    is set, stop after that many conversions (debug: leaves the rest as \\over)."""
    converted: int = 0
    unresolved: list[int] = []
    # Iterate: always operate on the FIRST unresolved \over; nested cases resolve on
    # later passes (an inner \over ends up inside a \frac{...} group we then match).
    while True:
        if limit is not None and converted >= limit:
            break
        m: re.Match[str] | None = None
        for cand in OVER.finditer(s):
            if cand.start() not in unresolved:
                m = cand
                break
        if m is None:
            break
        i: int = m.start()
        start: tuple[int, str] | None = _group_start(s, i)
        end: int | None = _group_end(s, m.end())
        if start is None or end is None:
            unresolved.append(i)
            continue
        gstart: int
        kind: str
        gstart, kind = start
        num: str = s[gstart + 1 : i].strip()
        den: str = s[m.end() : end].strip()
        frac: str = "\\frac{" + num + "}{" + den + "}"
        if kind == "{":
            s = s[:gstart] + frac + s[end + 1 :]
        else:  # "$": keep the delimiters, rewrite the content
            s = s[: gstart + 1] + frac + s[end:]
        converted += 1
        # offsets shifted; drop stale unresolved marks (recompute next loop)
        unresolved = [o for o in unresolved if o < gstart]
    return s, converted, unresolved


def main() -> None:
    if len(sys.argv) < 2:
        raise SystemExit("usage: over_to_frac.py <in.tex> [out.tex]")
    src: Path = Path(sys.argv[1])
    out: Path = Path(sys.argv[2]) if len(sys.argv) > 2 else src.with_name(src.stem + "-frac.tex")
    text: str = src.read_text(encoding="utf-8")
    new: str
    n: int
    unresolved: list[int]
    new, n, unresolved = convert(text)
    out.write_text(new, encoding="utf-8")
    print(f"over_to_frac: converted {n} \\over -> \\frac; wrote {out}")
    if unresolved:
        for off in unresolved:  # off: int (from unresolved: list[int])
            line: int = text.count("\n", 0, off) + 1
            print(f"  UNRESOLVED \\over at line {line} (needs manual review)")
    else:
        print("over_to_frac: all \\over resolved.")


if __name__ == "__main__":
    main()
