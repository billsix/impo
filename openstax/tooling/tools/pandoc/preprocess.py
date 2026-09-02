#!/usr/bin/env python3
"""HTML-only LaTeX preprocessing for the pandoc build.

pandoc's math reader rejects $...$ nested inside \\text{} (and a few text-mode
commands like \\textdegree / \\textbullet used in math). Our generated math
always puts \\text{} INSIDE math, so for every \\text{...} span we break the
inner inline-math out of the text:  \\text{$-$}  ->  \\text{}-\\text{} .

This runs on a TEMP COPY of the .tex (see entrypoint/html.sh); the committed
LaTeX is never modified, and the PDF build is unaffected.
"""

from __future__ import annotations

import re
import sys

# an UNescaped $...$ span (DOTALL: the committed .tex are line-wrapped, so a
# span can straddle a newline)
_MATH: re.Pattern[str] = re.compile(r"(?<!\\)\$(.*?)(?<!\\)\$", re.DOTALL)


def fix_content(c: str) -> str:
    # break out inline-math spans: $X$ -> }X\text{
    c = _MATH.sub(r"}\1\\text{", c)
    # math-spacing commands (\, \; \: \!) are invalid inside pandoc's \text{} ->
    # collapse to a plain space (text mode allows ordinary spaces).
    c = re.sub(r"\\[,;:!]", " ", c)
    # textcomp currency commands pandoc's math reader doesn't know -> Unicode
    # (the PDF build keeps the real commands; this is the temp HTML/EPUB copy).
    for cmd, ch in (
        (r"textcent", "¢"),
        (r"texteuro", "€"),
        (r"pounds", "£"),
        (r"textsterling", "£"),
    ):
        c = re.sub(r"\\" + cmd + r"(\{\})?", ch, c)
    # text-mode commands invalid inside a math \text{} -> break out as math.
    # re.sub (not str.replace) so a replacement's own text isn't re-scanned
    # (the inserted command name would otherwise be matched again).
    for cmd, math in (
        (r"textdegree", r"^\circ"),
        (r"textbullet", r"\bullet"),
        (r"textordmasculine", r"^\circ"),  # used for angle degrees (45o)
        (r"dots", r"\dots"),
        (r"ldots", r"\ldots"),
    ):
        c = re.sub(r"\\" + cmd + r"(\{\})?", lambda m, mm=math: "}" + mm + r"\text{", c)
    # an em-dash ligature in text mode trips pandoc's math reader -> Unicode
    c = c.replace("---", "—").replace("--", "–")
    return c


def strip_resizebox(s: str) -> str:
    r"""Remove \resizebox{..}{..}{ CONTENT } wrappers, keeping CONTENT.

    pdflatex wraps wide tables in \resizebox to fit them to the text width;
    pandoc drops \resizebox *and its content*, which would delete the table. So
    for the HTML/EPUB build we unwrap it to expose the bare tabular (the web CSS
    handles width). Brace-matched so nested braces in the table survive.
    """
    key: str = "\\resizebox"
    out: list[str] = []
    i: int = 0
    n: int = len(s)
    while True:
        j: int = s.find(key, i)
        if j < 0:
            out.append(s[i:])
            break
        out.append(s[i:j])
        k: int = j + len(key)
        ok: bool = True
        for _ in range(2):  # skip {width}{height}
            while k < n and s[k] in " \t\r\n":
                k += 1
            if k >= n or s[k] != "{":
                ok = False
                break
            depth: int = 1
            k = k + 1
            while k < n and depth:
                depth += (s[k] == "{") - (s[k] == "}")
                k += 1
        if not ok:
            out.append(s[j:k])  # malformed: leave untouched
            i = k
            continue
        while k < n and s[k] in " \t\r\n":
            k += 1
        if k < n and s[k] == "{":  # unwrap the {content} group
            depth, k = 1, k + 1
            start: int = k
            while k < n and depth:
                if s[k] == "{":
                    depth += 1
                elif s[k] == "}":
                    depth -= 1
                    if depth == 0:
                        break
                k += 1
            out.append(s[start:k])
            k += 1
        i = k
    return "".join(out)


def strip_cmd_arg(s: str, cmd: str) -> str:
    r"""Remove every \cmd{...} (the command plus one brace-matched argument).

    Drops \rowcolor{OScolor} / \arrayrulecolor{OScolor} from the temp HTML/EPUB
    copy. In LaTeX these color a table row / its rules; the PDF keeps them. But
    pandoc treats \rowcolor{OScolor} as swallowing the FOLLOWING header cell
    group ({\color..$x$}), so the first header label vanishes in HTML/EPUB. The
    remaining {\color{white}\bfseries $x$} pandoc renders fine (as the other
    cells prove), so removing only the color wrappers restores the label."""
    key: str = "\\" + cmd
    out: list[str] = []
    i: int = 0
    n: int = len(s)
    while True:
        j: int = s.find(key, i)
        if j < 0:
            out.append(s[i:])
            break
        e: int = j + len(key)
        if e < n and s[e].isalpha():  # a longer command name -> not this one
            out.append(s[i:e])
            i = e
            continue
        out.append(s[i:j])
        k: int = e
        while k < n and s[k] in " \t\r\n":
            k += 1
        if k < n and s[k] == "{":  # skip the brace-matched {arg}
            depth: int = 1
            k = k + 1
            while k < n and depth:
                depth += (s[k] == "{") - (s[k] == "}")
                k += 1
        else:
            k = e  # bare command, no arg -> just drop it
        i = k
    return "".join(out)


def fix_text_spans(s: str) -> str:
    out: list[str] = []
    i: int = 0
    n: int = len(s)
    while i < n:
        if s.startswith(r"\text{", i):
            j: int = i + 6
            depth: int = 1
            while j < n and depth:
                ch: str = s[j]
                if ch == "{":
                    depth += 1
                elif ch == "}":
                    depth -= 1
                    if depth == 0:
                        break
                j += 1
            out.append("\\text{" + fix_content(s[i + 6 : j]) + "}")
            i = j + 1
        else:
            out.append(s[i])
            i += 1
    return "".join(out)


def main(argv: list[str]) -> None:
    for path in argv:
        with open(path, encoding="utf-8") as f:
            txt: str = f.read()
        out: str = fix_text_spans(txt)
        # the empty \text{} left at $...$ break-out seams trips pandoc's math
        # reader (\text{$-$}\infty -> \text{}-\text{}\infty). Replace with a
        # SPACE, not nothing: the \text{} can separate a command from a following
        # letter (\Delta\text{}y), and deleting it would weld them into \Deltay.
        out = out.replace(r"\text{}", " ")
        out = strip_resizebox(out)  # unwrap PDF-only table fit wrapper
        out = strip_cmd_arg(out, "rowcolor")  # else pandoc eats 1st header cell
        out = strip_cmd_arg(out, "arrayrulecolor")  # table rule color -> irrelevant
        with open(path, "w", encoding="utf-8") as f:
            f.write(out)


if __name__ == "__main__":
    main(sys.argv[1:])
