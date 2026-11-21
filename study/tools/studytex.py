"""Shared LaTeX pieces for the study/ documents (literacy tests, cliff notes).

Every document uses the house class `osbook.cls` from openstax/tooling/latex/
(found through TEXINPUTS, set by the study Makefile), so the study material has
the same fonts and palette as the books. Book-section pointers ("PA 4.2") are
resolved through the OpenStax cross-book index (crossbook.py), giving the
section's title and its page on the published site.
"""

from __future__ import annotations

import os
import re
import sys

STUDY: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CROSSBOOK_DIR: str = os.path.join(STUDY, "..", "openstax", "tooling", "tools", "cnxml2tex")
if CROSSBOOK_DIR not in sys.path:
    sys.path.insert(0, CROSSBOOK_DIR)

import crossbook  # noqa: E402 -- found through CROSSBOOK_DIR

SECTION_POINTER: re.Pattern[str] = re.compile(r"^([A-Z][A-Z0-9]) (\d+\.\d+)$")


def preamble(title: str, subtitle: str) -> str:
    """The document start: osbook class, letter paper, a plain title block."""
    return (
        "\\documentclass[letter]{osbook}\n\\usepackage{osbook-envs}\n"
        "\\setOSbooktitle{%s}\n"
        "\\pagestyle{plain}\n"
        "\\setlength{\\parindent}{0pt}\n"
        "\\setlength{\\parskip}{0.5em}\n"
        "\\begin{document}\n"
        "{\\sffamily\\bfseries\\LARGE\\color{OScolor}%s\\par}\n"
        "\\smallskip{\\large\\itshape %s\\par}\n"
        "\\medskip\n" % (title, title, subtitle)
    )


def review_pointer(pointer: str) -> str:
    """LaTeX for one review pointer: a linked book section, or the text as is.

    >>> review_pointer("CCSS G-CO.2-5")
    'CCSS G-CO.2-5'
    >>> review_pointer("PA 4.2")  # doctest: +ELLIPSIS
    '\\\\href{https://billsix.github.io/impo/prealgebra-2e/...}{Prealgebra 2e \\\\S4.2} Multiply and Divide Fractions'
    """
    found: re.Match[str] | None = SECTION_POINTER.match(pointer)
    if found is None or found.group(1) not in crossbook.BOOKS:
        return crossbook.latex_text(pointer)
    code: str = found.group(1)
    number: str = found.group(2)
    return "\\href{%s}{%s \\S%s} %s" % (
        crossbook.section_url((code, number)),
        crossbook.BOOKS[code][1],
        number,
        crossbook.latex_text(crossbook.book_index(code)[number]["title"]),
    )


def footer(note: str) -> str:
    """A small closing note (licence/attribution) and the document end."""
    return "\n\\vfill\n{\\footnotesize %s\\par}\n\\end{document}\n" % note
