#!/usr/bin/env python3
r"""Preprocess Trench LaTeX into a pandoc-ready .tex for the web/EPUB edition.

The PDF path (osbook.cls + trench-osbook.sty) is untouched; this is a SEPARATE,
non-destructive transform for pandoc, which is a LaTeX *parser*, not a TeX engine.
The 2026-09-19 spike proved a Chapter renders to HTML (--mathjax) and MathML/EPUB
once three things are done -- and this script does them:

  1. Sectioning -> real \chapter/\section as TEXT (pandoc silently empties the whole
     document if two *macros* both expand to sectioning commands):
       \chaptertitle{X}       -> \chapter{X}
       \newsection{a}{b}{c}    -> \section{c}
       \sectiontitle{X}        -> (removed)
  2. Strip ALL comments from the prepended defs (inline `code % ...` too, not just
     full-line) -- a `%` comment containing LaTeX commands empties pandoc's output.
  3. (--frac) \over -> \frac for the MathML/EPUB path (HTML/--mathjax renders \over
     natively, so --frac is only needed for EPUB).

The custom macros come from `--defs` (default tools/pandoc-defs.tex), redefined to
pandoc-friendly forms and with `\pageref` -> a hyperlink (no page numbers on the web).

Paths are arguments; run from the book folder (host or container). Output is a new
file -- the source is never modified.
  python3 tools/web_preprocess.py <body.tex> -o <out.tex> [--defs tools/pandoc-defs.tex] [--frac]

KNOWN LIMITATIONS (spike): the `\newsection` rewrite assumes non-nested braces in its
args (true for Trench's titles); ~14 math constructs per chapter (mostly `\eqno`,
`\left/...\right.`) still fall back to raw TeX under --mathml -- a small tail to
rewrite (`\eqno{X}`->`\tag{X}`) when polishing EPUB.
"""
from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from over_to_frac import convert as over_convert  # noqa: E402


def about_this_edition() -> str:
    r"""The "About This Edition" colophon prepended to the web/EPUB master (bookW.tex):
    formatted by Bill Six, the impo toolchain + build commit SHA + date, and the
    CC BY-NC-SA 3.0 / MIT split. `\chapter*` (unnumbered, no counter step) so it doesn't
    shift chapter 1. This runs IN the build container (no impo .git mounted), so the SHA
    comes only from IMPO_COMMIT / IMPO_BUILD_DATE (passed by the Makefile via -e); absent
    them it degrades to a development-build note. Flows to the make4ht HTML (front matter)
    AND the tex4ebook EPUB, since both build from this master."""
    sha: str = os.environ.get("IMPO_COMMIT", "").strip()
    date: str = os.environ.get("IMPO_BUILD_DATE", "").strip()
    if sha:
        built: str = ", built from commit \\texttt{%s}" % sha
        if date:
            built += " on %s" % date
    else:
        built = " (a local development build)"
    return (
        "\\chapter*{About This Edition}\n"
        "This edition of \\emph{Elementary Differential Equations} by William F. Trench "
        "was formatted by William Emerison Six (``Bill~Six'') using the \\emph{impo} "
        "toolchain (\\href{https://github.com/billsix/impo}{github.com/billsix/impo})%s. "
        "The text and figures are \\textcopyright{} William F. Trench, licensed under a "
        "Creative Commons Attribution-NonCommercial-ShareAlike 3.0 Unported License "
        "(CC~BY-NC-SA~3.0); the impo toolchain and this formatting are \\textcopyright{} "
        "William Emerison Six, released under the MIT License.\n\n" % built
    )


def extract_body(s: str) -> str:
    """If given a full master, keep from the Preface to the final \\end{document}
    (drops the hand title/license/TOC front matter and the \\end{document}); pandoc
    --toc / tex4ht build the web TOC. A pre-extracted chapter/body passes through."""
    m: re.Match[str] | None = re.search(r"\\pdfbookmark\[0\]\{Preface\}", s)
    if m is None:
        return s
    end: int = s.rfind(r"\end{document}")
    return s[m.start() : end if end != -1 else len(s)]


def rewrite_sectioning(s: str) -> str:
    s = s.replace(r"\chaptertitle{", r"\chapter{")
    s = re.sub(r"\\newsection\s*\{[^}]*\}\s*\{[^}]*\}\s*\{([^}]*)\}", r"\\section{\1}", s)
    s = re.sub(r"\\sectiontitle\s*\{[^}]*\}", "", s)
    # Drop the manual chapter- AND section-counter setters, exactly as
    # normalize_master.py does for the PDF. `\setcounter{chapter}{N}` before each
    # `\chaptertitle` would offset every chapter by one ("Introduction" -> "Chapter 2");
    # `\setcounter{section}{1}` before a chapter's first section bumps it to ".2"
    # (Chapter 2 started at 2.2). \chapter/\section auto-number from \newsection's real
    # first arg once the setters are gone, so sections run 2.1, 2.2, ... consecutively.
    s = re.sub(r"^[ \t]*\\setcounter\{(?:chapter|section)\}\{\d+\}[ \t]*\n", "", s, flags=re.M)
    # Drop the back-of-book index (tindex): it is page-number based and useless on
    # the web (no pages; use browser search), and pandoc has no binding for it.
    s = re.sub(r"\\begin\{tindex\}.*?\\end\{tindex\}", "", s, flags=re.DOTALL)
    return s


def strip_comments(s: str) -> str:
    # Remove an unescaped % to end of line (keeps \%). Applies to full-line and
    # inline comments alike.
    return re.sub(r"(?<!\\)%.*", "", s)


def main() -> None:
    ap: argparse.ArgumentParser = argparse.ArgumentParser()
    ap.add_argument("body", help="source LaTeX body (chapter extract or full-book body)")
    ap.add_argument("-o", "--out", required=True)
    ap.add_argument("-d", "--defs", default=str(Path(__file__).resolve().parent / "pandoc-defs.tex"))
    ap.add_argument("--frac", action="store_true", help="convert \\over -> \\frac (EPUB/MathML path)")
    a: argparse.Namespace = ap.parse_args()

    body: str = rewrite_sectioning(extract_body(Path(a.body).read_text(encoding="utf-8")))
    if a.frac:
        n: int
        unresolved: list[int]
        body, n, unresolved = over_convert(body)
        print(f"web_preprocess: converted {n} \\over; {len(unresolved)} unresolved", file=sys.stderr)
    defs: str = strip_comments(Path(a.defs).read_text(encoding="utf-8"))

    # Packages Trench's body needs. pandoc ignores \usepackage, but make4ht (real
    # LaTeX) requires them (e.g. \color needs xcolor). graphicspath so
    # \includegraphics resolves the phase-3 figures.
    pkgs: str = (
        "\\usepackage{amsmath,amssymb,amsfonts,amsbsy,graphicx,float}\n"
        "\\usepackage[usenames,dvipsnames,svgnames,table]{xcolor}\n"
        "\\usepackage{hyperref}\n"
        "\\graphicspath{{EPS-png/}{EPS-pdf/}{EPS/}}\n"  # PNG first: tex4ht/pandoc embed PNG in HTML
    )
    # "About This Edition" colophon first in the body (front matter, before the Preface).
    out: str = (
        "\\documentclass{book}\n" + pkgs + defs + "\n\\begin{document}\n"
        + about_this_edition() + body + "\n\\end{document}\n"
    )
    Path(a.out).write_text(out, encoding="utf-8")
    print(f"web_preprocess: wrote {a.out}")


if __name__ == "__main__":
    main()
