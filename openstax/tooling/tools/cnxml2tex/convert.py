#!/usr/bin/env python3
"""
cnxml2tex -- convert OpenStax CNXML calculus modules to LaTeX.

One-time generator (see tasks/port-to-latex.md): emits latex/sections/m<id>.tex
(a subfiles document per module) and, given a collection, an assembled volume
master latex/calculus-volume-N.tex. After generation the .tex is committed and
hand-maintained; this tool is kept for re-runs and spot fixes.

Source vocabulary -> LaTeX mapping is documented inline. Math is W3C
Presentation MathML (no Content MathML); mml() walks it to LaTeX.

Usage:
    convert.py module <m-id> [<m-id> ...]      # convert specific modules
    convert.py collection <slug>               # convert a whole volume + master
    convert.py all                             # convert all three volumes
"""

from __future__ import (
    annotations,  # lazy annotations: use etree._Element / X | None freely
)

import glob
import json
import os
import re
import sys
import unicodedata
from collections.abc import Iterable
from html.parser import HTMLParser
from typing import Any, cast

from lxml import etree  # ty: ignore[unresolved-import]  # ty's lxml stub lacks etree

_Element = etree._Element  # MathML/CNXML node type, for annotations
_ElementTree = etree._ElementTree  # parsed-document type, for annotations

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MODULES = os.path.join(ROOT, "modules")
COLLECTIONS = os.path.join(ROOT, "collections")
OUT_SECTIONS = os.path.join(ROOT, "latex", "sections")

C = "{http://cnx.rice.edu/cnxml}"
M = "{http://www.w3.org/1998/Math/MathML}"
MD = "{http://cnx.rice.edu/mdml}"
COL = "{http://cnx.rice.edu/collxml}"

# --------------------------------------------------------------------------
# per-book configuration -- auto-derived so the SAME converter serves every
# bundle. Collections are discovered from collections/*.collection.xml, and
# the sectioning depth adapts to the collection's subcollection nesting.
# --------------------------------------------------------------------------
BOOK_CLASS = "osbook"
ENVS_PKG = "osbook-envs"
DEFER_PKG = "osbook-defer"


def _slugs() -> list[str]:
    fs: list[str] = sorted(glob.glob(os.path.join(COLLECTIONS, "*.collection.xml")))
    return [os.path.basename(f)[: -len(".collection.xml")] for f in fs]


COLLECTION_SLUGS = _slugs()
SUBFILES_MAIN = COLLECTION_SLUGS[0] if COLLECTION_SLUGS else "book"


def _max_subcol_depth() -> int:
    # self-contained (does not use local(), which is defined further down)
    md: int = 0
    for slug in COLLECTION_SLUGS:
        try:
            root: _Element = etree.parse(
                os.path.join(COLLECTIONS, slug + ".collection.xml")
            ).getroot()
        except Exception:
            continue

        def walk(e: _Element, d: int) -> None:
            nonlocal md
            for c in e:
                if isinstance(c.tag, str) and c.tag.split("}")[-1] == "subcollection":
                    md = max(md, d + 1)
                    walk(c, d + 1)
                else:
                    walk(c, d)

        walk(root, 0)
    return md


MAX_DEPTH = _max_subcol_depth()
# subcollection sectioning command by nesting level (0 = outermost); modules
# sit one level below the deepest subcollection.
if MAX_DEPTH >= 2:
    SUBCOL_CMDS = ["chapter", "section", "subsection"]
    MODULE_CMD = "subsection"
else:
    SUBCOL_CMDS = ["chapter"]
    MODULE_CMD = "section"


def subcol_cmd(level: int) -> str:
    return SUBCOL_CMDS[min(level, len(SUBCOL_CMDS) - 1)]


# collected diagnostics
UNKNOWN: dict[str, int] = {}


def warn_unknown(tag: str) -> None:
    UNKNOWN[tag] = UNKNOWN.get(tag, 0) + 1


def local(tag: Any) -> str | None:
    if tag is None or isinstance(tag, str) is False:
        return None
    return tag.split("}")[-1] if "}" in tag else tag


# --------------------------------------------------------------------------
# text escaping
# --------------------------------------------------------------------------
TEXT_REPL: list[tuple[str, str]] = [
    ("\\", r"\textbackslash{}"),
    ("&", r"\&"),
    ("%", r"\%"),
    ("$", r"\$"),
    ("#", r"\#"),
    ("_", r"\_"),
    ("{", r"\{"),
    ("}", r"\}"),
    ("~", r"\textasciitilde{}"),
    ("^", r"\textasciicircum{}"),
]
UNICODE_TEXT: dict[str, str] = {
    "–": "--",
    "—": "---",
    "‘": "`",
    "’": "'",
    "“": "``",
    "”": "''",
    "…": r"\dots{}",
    " ": "~",
    "×": r"$\times$",
    "°": r"\textdegree{}",
    "−": "$-$",
    "→": r"$\to$",
    "≤": r"$\leq$",
    "≥": r"$\geq$",
    "≠": r"$\neq$",
    "·": r"$\cdot$",
    "∞": r"$\infty$",
    "π": r"$\pi$",
    "½": r"$\tfrac12$",
    "÷": r"$\div$",
    "≈": r"$\approx$",
    "±": r"$\pm$",
    "∓": r"$\mp$",
    "≅": r"$\cong$",
    "∘": r"$\circ$",
    "√": r"$\surd$",
    "∑": r"$\sum$",
    "∫": r"$\int$",
    "∂": r"$\partial$",
    "∇": r"$\nabla$",
    "⇒": r"$\Rightarrow$",
    "≡": r"$\equiv$",
    "∈": r"$\in$",
    "α": r"$\alpha$",
    "β": r"$\beta$",
    "θ": r"$\theta$",
    "Δ": r"$\Delta$",
    "μ": r"$\mu$",
    "ε": r"$\varepsilon$",
    "⋅": r"$\cdot$",
    "′": r"$'$",
    "²": r"$^2$",
    "³": r"$^3$",
    "□": r"$\square$",
    "ϕ": r"$\phi$",
    "ℝ": r"$\mathbb{R}$",
    "≅": r"$\cong$",
    "∅": r"$\emptyset$",
    "ⁿ": r"$^n$",
    "δ": r"$\delta$",
    "Ω": r"$\Omega$",
    "ω": r"$\omega$",
    "σ": r"$\sigma$",
    "Σ": r"$\Sigma$",
    "ϵ": r"$\epsilon$",
    "γ": r"$\gamma$",
    "λ": r"$\lambda$",
    "ρ": r"$\rho$",
    "τ": r"$\tau$",
    "Φ": r"$\Phi$",
    "Ψ": r"$\Psi$",
    "Λ": r"$\Lambda$",
    "ℓ": r"$\ell$",
    "″": r"$''$",
    "⋯": r"$\cdots$",
    "∴": r"$\therefore$",
    "†": r"\dag{}",
    "‡": r"\ddag{}",
    "‴": r"$'''$",
    "ϕ": r"$\phi$",
    "ϱ": r"$\varrho$",
    "•": r"\textbullet{}",
    "™": r"\texttrademark{}",
    "​": "",
    "‰": r"\textperthousand{}",
    "˜": "\textasciitilde{}",
    "ﬀ": "ff",
    "ﬁ": "fi",
    "ﬂ": "fl",
    "ﬃ": "ffi",
    "ﬄ": "ffl",
    "ﬅ": "ft",
    "ﬆ": "st",
    "‹": r"\guilsinglleft{}",
    "›": r"\guilsinglright{}",
    "̂": "",
    "̃": "",
    "̄": "",
    "̇": "",
    "̈": "",
    "⃗": "",
    "́": "",
    "̀": "",
}

# OpenStax marks exercise sub-parts with circled letters/digits (ⓐ ⓑ ⓒ, ①..⑨).
# These are emitted as the RAW Unicode char in the .tex (NOT \textcircled{a}), so
# that the pandoc HTML build passes them straight through as proper circled glyphs.
# (\textcircled{a} was turned by pandoc into "a" + U+20DD combining-enclosing-circle,
# rendering as the broken "a⃝".) The lualatex PDF maps each raw char back to
# \textcircled via \newunicodechar in osbook.cls, so the PDF is unchanged.
# The chars are therefore intentionally NOT added to UNICODE_TEXT: esc_text leaves
# any char not in the table untouched, so the raw circled glyph flows into the .tex.
_CIRCLED_CHARS: str = (
    "".join(chr(0x24D0 + _i) for _i in range(26))  # ⓐ..ⓩ
    + "".join(chr(0x24B6 + _i) for _i in range(26))  # Ⓐ..Ⓩ
    + "".join(chr(0x2460 + _i) for _i in range(9))  # ①..⑨
)
# circled char -> the plain letter/digit it encloses (for caption downgrading)
_CIRCLED_TO_PLAIN: dict[str, str] = {}
for _i, _ch in enumerate("abcdefghijklmnopqrstuvwxyz"):
    _CIRCLED_TO_PLAIN[chr(0x24D0 + _i)] = _ch
for _i, _ch in enumerate("ABCDEFGHIJKLMNOPQRSTUVWXYZ"):
    _CIRCLED_TO_PLAIN[chr(0x24B6 + _i)] = _ch
for _i in range(1, 10):
    _CIRCLED_TO_PLAIN[chr(0x2460 + _i - 1)] = str(_i)
_CIRCLED_CLASS: str = "[%s]" % re.escape(_CIRCLED_CHARS)

# Greek capitals visually identical to Latin letters -- OpenStax uses them
# interchangeably; normalize to Latin (pdflatex/T1 cannot typeset the Greek
# code points, and they are not genuinely Greek in context).
_GREEK_CAP_LATIN: dict[int, str] = {
    0x391: "A",
    0x392: "B",
    0x395: "E",
    0x396: "Z",
    0x397: "H",
    0x399: "I",
    0x39A: "K",
    0x39C: "M",
    0x39D: "N",
    0x39F: "O",
    0x3A1: "P",
    0x3A4: "T",
    0x3A5: "Y",
    0x3A7: "X",
}

_RAW_LATEX_ENV = re.compile(r"\\begin\{([a-zA-Z*]+)\}.*?\\end\{\1\}", re.DOTALL)


def esc_text(s: str | None) -> str:
    if s is None:
        return ""
    # A few source paras paste raw LaTeX math as plain TEXT (it should be <m:math>
    # MathML). Escaping would print the LaTeX verbatim; instead, detect a complete
    # \begin{env}...\end{env} block and render it as display math -- reinterpreting
    # the malformed source (Bill's call), with a loud warning so it stays visible.
    if "\\begin{" in s and _RAW_LATEX_ENV.search(s):
        return _esc_text_raw_latex(s)
    return _esc_text_core(s)


def _esc_text_raw_latex(s: str) -> str:
    out: list[str] = []
    last: int = 0
    for m in _RAW_LATEX_ENV.finditer(s):
        out.append(_esc_text_core(s[last : m.start()]))  # escape the prose around it
        block: str = m.group(0)
        sys.stderr.write(
            "WARNING: RAW LATEX PASTED AS PLAIN TEXT IN MODULE %s -- "
            "REINTERPRETING AS DISPLAY MATH: %s\n"
            % (
                (globals().get("_CURMOD") or "?").upper(),
                re.sub(r"\s+", " ", block)[:90],
            )
        )
        out.append("\n\\[\n%s\n\\]\n" % block)  # emit the block as-is, in math
        last = m.end()
    out.append(_esc_text_core(s[last:]))
    return "".join(out)


def _esc_text_core(s: str) -> str:
    if s is None:
        return ""
    s = s.translate(_GREEK_CAP_LATIN)
    if any(0x1D400 <= ord(c) <= 0x1D7FF for c in s):
        s = "".join(
            unicodedata.normalize("NFKC", c) if 0x1D400 <= ord(c) <= 0x1D7FF else c
            for c in s
        )
    # 1. Escape LaTeX-special ASCII that is LITERALLY in the source text
    #    (currency $, &, %, _, backslash, braces, ...). Do this FIRST so we
    #    don't clobber the $ \ { } we are about to insert in step 2.
    out: list[str] = []
    for ch in s:
        for a, b in TEXT_REPL:
            if ch == a:
                out.append(b)
                break
        else:
            out.append(ch)
    s = "".join(out)
    # 2. Map unicode symbols to their LaTeX (these intentionally contain
    #    $, \, {, } and must NOT be re-escaped).
    for u, r in UNICODE_TEXT.items():
        if u in s:
            s = s.replace(u, r)
    # 3. Catch-all: any remaining known math symbol -> inline math.
    global _SYMBOLS
    if _SYMBOLS is None:
        _SYMBOLS = {}
        _SYMBOLS.update(GREEK)
        _SYMBOLS.update(MO_MAP)
        _SYMBOLS.update(MI_SYM)
    for u, r in _SYMBOLS.items():
        if u in s:
            s = s.replace(u, ("$" + r.strip() + "$") if r.strip() else "")
    return s


def collapse_ws(s: str) -> str:
    return re.sub(r"[ \t\n\r]+", " ", s)


# --------------------------------------------------------------------------
# MathML -> LaTeX
# --------------------------------------------------------------------------
MO_MAP = {
    "−": "-",
    "∗": "*",
    "×": r"\times ",
    "·": r"\cdot ",
    "→": r"\to ",
    "⇒": r"\Rightarrow ",
    "↔": r"\leftrightarrow ",
    "≠": r"\neq ",
    "≤": r"\leq ",
    "≥": r"\geq ",
    "≈": r"\approx ",
    "±": r"\pm ",
    "∓": r"\mp ",
    "∞": r"\infty ",
    "∫": r"\int ",
    "∑": r"\sum ",
    "∏": r"\prod ",
    "∂": r"\partial ",
    "∇": r"\nabla ",
    "∈": r"\in ",
    "∉": r"\notin ",
    "⊆": r"\subseteq ",
    "∩": r"\cap ",
    "∪": r"\cup ",
    "∅": r"\emptyset ",
    "⋅": r"\cdot ",
    "…": r"\dots ",
    "⋯": r"\cdots ",
    "′": "'",
    "″": "''",
    "°": r"^\circ ",
    "⁡": "",
    "⁢": "",
    "⁣": "",  # invisible operators
    "≅": r"\cong ",
    "≃": r"\simeq ",
    "∼": r"\sim ",
    "∥": r"\parallel ",
    "⊥": r"\perp ",
    "∠": r"\angle ",
    "√": r"\surd ",
    "∘": r"\circ ",
    "→": r"\to ",
    "…": r"\ldots ",
    "″": r"{''}",
    "‴": r"{'''}",
    "⋯": r"\cdots ",
    "⋮": r"\vdots ",
    "⌊": r"\lfloor ",
    "⌋": r"\rfloor ",
    "⌈": r"\lceil ",
    "⌉": r"\rceil ",
    "∴": r"\therefore ",
    "⇔": r"\Leftrightarrow ",
    "∀": r"\forall ",
    "∃": r"\exists ",
    "¬": r"\neg ",
    "⊂": r"\subset ",
    "⊃": r"\supset ",
    "∝": r"\propto ",
    "⊕": r"\oplus ",
    "⊗": r"\otimes ",
    "←": r"\gets ",
    "↦": r"\mapsto ",
    "∮": r"\oint ",
    "⟨": r"\langle ",
    "⟩": r"\rangle ",
    "​": "",
    "⁡": "",
    "⁢": "",
    "⁣": "",
    "︸": "",
    "︷": "",
    "⏟": "",
    "⏞": "",
    "∬": r"\iint ",
    "∭": r"\iiint ",
    "∯": r"\oiint ",
    "↛": r"\nrightarrow ",
    "∗": r"\ast ",
    "⟂": r"\perp ",
    "≢": r"\not\equiv ",
    "⊙": r"\odot ",
    "⊖": r"\ominus ",
    "≡": r"\equiv ",
    "≪": r"\ll ",
    "≫": r"\gg ",
    "⊤": r"\top ",
}
# Greek letters (lower/upper) appearing as <mi>
GREEK = {
    "α": r"\alpha ",
    "β": r"\beta ",
    "γ": r"\gamma ",
    "δ": r"\delta ",
    "ε": r"\varepsilon ",
    "ζ": r"\zeta ",
    "η": r"\eta ",
    "θ": r"\theta ",
    "λ": r"\lambda ",
    "μ": r"\mu ",
    "ν": r"\nu ",
    "ξ": r"\xi ",
    "π": r"\pi ",
    "ρ": r"\rho ",
    "σ": r"\sigma ",
    "τ": r"\tau ",
    "φ": r"\varphi ",
    "ϕ": r"\phi ",
    "χ": r"\chi ",
    "ψ": r"\psi ",
    "ω": r"\omega ",
    "Γ": r"\Gamma ",
    "Δ": r"\Delta ",
    "Θ": r"\Theta ",
    "Λ": r"\Lambda ",
    "Π": r"\Pi ",
    "Σ": r"\Sigma ",
    "Φ": r"\Phi ",
    "Ψ": r"\Psi ",
    "Ω": r"\Omega ",
    "κ": r"\kappa ",
    "ι": r"\iota ",
    "υ": r"\upsilon ",
    "ο": "o",
    "ς": r"\varsigma ",
    "ϰ": r"\varkappa ",
    "ϖ": r"\varpi ",
    "ϵ": r"\epsilon ",
    "ϑ": r"\vartheta ",
}
# symbols that appear as <m:mi> (identifiers) but are really math symbols
MI_SYM = {
    "∞": r"\infty ",
    "∅": r"\emptyset ",
    "□": r"\square ",
    "ℝ": r"\mathbb{R}",
    "ℕ": r"\mathbb{N}",
    "ℤ": r"\mathbb{Z}",
    "ℚ": r"\mathbb{Q}",
    "ℂ": r"\mathbb{C}",
    "∂": r"\partial ",
    "…": r"\ldots ",
    "⋯": r"\cdots ",
    "ⅈ": "i",
    "ℯ": "e",
    "ϕ": r"\phi ",
    "∇": r"\nabla ",
    "ℓ": r"\ell ",
    "″": r"{''}",
    "‴": r"{'''}",
    "⋯": r"\cdots ",
    "⋮": r"\vdots ",
    "⋱": r"\ddots ",
    "⌊": r"\lfloor ",
    "⌋": r"\rfloor ",
    "⌈": r"\lceil ",
    "⌉": r"\rceil ",
    "∴": r"\therefore ",
    "ȷ": r"\jmath ",
    "ƒ": "f",
    "​": "",
    "ϵ": r"\epsilon ",
    "ϱ": r"\varrho ",
    "ϑ": r"\vartheta ",
    "∬": r"\iint ",
    "∭": r"\iiint ",
    "∯": r"\oiint ",
    "↛": r"\nrightarrow ",
    "∗": r"\ast ",
    "∠": r"\angle ",
    "∇": r"\nabla ",
    "⊙": r"\odot ",
    "≢": r"\not\equiv ",
    "Ⅎ": r"\Im ",
    "ℜ": r"\Re ",
    "℘": r"\wp ",
}
# function-name words that should become math operators
FUNC_WORDS = {
    "sin",
    "cos",
    "tan",
    "cot",
    "sec",
    "csc",
    "sinh",
    "cosh",
    "tanh",
    "coth",
    "log",
    "ln",
    "exp",
    "lim",
    "max",
    "min",
    "sup",
    "inf",
    "det",
    "gcd",
    "arg",
    "deg",
    "dim",
    "ker",
    "arcsin",
    "arccos",
    "arctan",
}

# --- additional glyphs found in the algebra/precalculus corpus -------------
MO_MAP.update(
    {
        "\u00f7": r"\div ",
        "\u2219": r"\cdot ",
        "\u2223": r"\mid ",
        "\u2206": r"\Delta ",
        "\u2221": r"\measuredangle ",
        "\u27f6": r"\longrightarrow ",
        "\u2329": r"\langle ",
        "\u232a": r"\rangle ",
        "\u3008": r"\langle ",
        "\u3009": r"\rangle ",
        "\u2009": r"\, ",
        "\u2713": r"\checkmark ",
        "\u02ba": r"'' ",
        "\u2013": "-",
        "\u2014": "-",
        "\u00b2": r"^2 ",
        "\u00b3": r"^3 ",
        "\u2500": r"\text{---}",
        "\u00a2": r"\text{\textcent}",
        "\u00ba": r"\text{\textordmasculine}",
        "\u2003": r"\quad ",
        "\u2198": r"\searrow ",
        "\u2199": r"\swarrow ",
        "\u25b3": r"\triangle ",
        "\u2012": "-",
        "\u299c": r"\angle ",
        "\u266d": r"\flat ",
        "\u2119": r"\mathbb{P}",
        "\u2135": r"\aleph ",
        "\u00b5": r"\mu ",
        "\u25a2": r"\square ",
        "\u2715": r"\times ",
        "\u2714": r"\checkmark ",
        "\u274c": r"\times ",
        "\u2010": "-",
        "\u29f8": "/",
    }
)
MI_SYM.update(
    {
        "\u00f7": r"\div ",
        "\u2219": r"\cdot ",
        "\u2223": r"\mid ",
        "\u2206": r"\Delta ",
        "\u2221": r"\measuredangle ",
        "\u27f6": r"\longrightarrow ",
        "\u2329": r"\langle ",
        "\u232a": r"\rangle ",
        "\u3008": r"\langle ",
        "\u3009": r"\rangle ",
        "\u2713": r"\checkmark ",
        "\u02ba": r"'' ",
        "\u00b2": r"^2 ",
        "\u00b3": r"^3 ",
        "\u2198": r"\searrow ",
        "\u2199": r"\swarrow ",
        "\u25b3": r"\triangle ",
        "\u299c": r"\angle ",
        "\u266d": r"\flat ",
        "\u2119": r"\mathbb{P}",
        "\u2135": r"\aleph ",
        "\u00b5": r"\mu ",
        "\u25a2": r"\square ",
        "\u2715": r"\times ",
        "\u2714": r"\checkmark ",
        "\u274c": r"\times ",
        "\u2010": "-",
        "\u29f8": "/",
    }
)
UNICODE_TEXT.update(
    {
        "\u04ab": "\u00e7",  # Cyrillic es-w-descender typo -> c-cedilla
        "\u2009": r"\,",
        "\u00a2": r"\textcent{}",
        "\u00ba": r"\textordmasculine{}",
        "\u2713": r"$\checkmark$",
        "\u2500": "---",
        "\u00b4": "'",
        "\u00af": r"\textasciimacron{}",
        "\u2003": r"\quad{}",
        "\u2012": "--",
        "\u00a3": r"\pounds{}",
        "\u20ac": r"\texteuro{}",
        "\u00ae": r"\textregistered{}",
        "\u00b5": r"$\mu$",
        "\U0001f4ac": "",
        "\u274c": r"$\times$",
        "\u2714": r"$\checkmark$",
        "\u25a2": r"$\square$",
        "\u2715": r"$\times$",
        "\u2010": "-",
        "\u29f8": "/",
        "\u00a6": "|",
        "\u1d57": r"\textsuperscript{t}",
        "\u02b0": r"\textsuperscript{h}",
        "\u02e2": r"\textsuperscript{s}",
        "\u02b3": r"\textsuperscript{r}",
        "\u1d48": r"\textsuperscript{d}",
    }
)


def mtext_to_latex(s: str) -> str:
    """Render an <m:mtext>: operator words -> \\op, else \\text{}.
    Inside \\text{} we are in text mode, so use the text-mode escaper
    (math symbols come back wrapped in $...$)."""
    raw: str = s if s is not None else ""
    stripped: str = raw.strip()
    if stripped in FUNC_WORDS:
        return "\\%s " % stripped
    if not raw.strip():
        return r"\ " if raw else ""
    return "\\text{%s}" % esc_text(raw)


_SYMBOLS = None  # combined math-symbol map, built lazily
_CELL_MODE = False  # True while rendering a tabular cell (LR mode)
# Sentinel for <mspace linebreak="newline"/> (an author-declared line break in a
# multi-line derivation). Emitted by mml(), then consumed by the aligned-display
# promotion (render_math / render_equation); any stray one is scrubbed to a thin
# space in cleanup_latex. A private-use codepoint so it never collides with content.
_MNL = "\ue000"


def _math_literal(s: str) -> str:
    """Render literal <mi>/<mn>/<mo> text: map any known math-symbol unicode
    (e.g. a stray ∞, ϵ, −∞) to its LaTeX command, then escape characters that
    are special in math mode (fill-in-the-blank '____', currency '$5')."""
    global _SYMBOLS
    s = s.translate(_GREEK_CAP_LATIN)
    if _SYMBOLS is None:
        _SYMBOLS = {}
        _SYMBOLS.update(GREEK)
        _SYMBOLS.update(MO_MAP)
        _SYMBOLS.update(MI_SYM)
    # escape literal braces in the raw token BEFORE inserting symbol macros
    # (which legitimately contain { }), so a stray } can't unbalance math mode.
    s = s.replace("{", r"\{").replace("}", r"\}")
    for u, r in _SYMBOLS.items():
        if u in s:
            s = s.replace(u, r)
    # drop combining diacritical marks (can't attach them to a base reliably)
    s = re.sub(r"[̀-ͯ⃐-⃿]", "", s)
    # normalize math-alphanumeric letters (𝑥 𝑓 …) to ASCII
    s = "".join(
        unicodedata.normalize("NFKC", c) if 0x1D400 <= ord(c) <= 0x1D7FF else c
        for c in s
    )
    # safety net: any remaining non-ASCII letter (accented Latin in an <mi>) ->
    # \text{}; silently drop other unknown non-ASCII so it can't crash math mode.
    s = re.sub(
        r"[^\x00-\x7F]",
        lambda m: (r"\text{%s}" % m.group(0)) if m.group(0).isalpha() else "",
        s,
    )
    for a, b in (("_", r"\_"), ("$", r"\$"), ("#", r"\#"), ("%", r"\%"), ("&", r"\&")):
        s = s.replace(a, b)
    return s


# backward-compatible alias
_esc_math_lit = _math_literal


def _norm_math(s: str) -> str:
    """Sanitize a `data-math` string (real LaTeX from the Exercises API) for
    pdflatex math mode: fold math-alphanumeric unicode (𝑥 𝑦 …) to ASCII, map
    known unicode symbols to LaTeX, drop remaining non-ASCII. Unlike
    _math_literal this PRESERVES LaTeX syntax (backslashes, braces) since the
    input is already LaTeX, not literal token text."""
    global _SYMBOLS
    if _SYMBOLS is None:
        _SYMBOLS = {}
        _SYMBOLS.update(GREEK)
        _SYMBOLS.update(MO_MAP)
        _SYMBOLS.update(MI_SYM)
    s = "".join(
        unicodedata.normalize("NFKC", c) if 0x1D400 <= ord(c) <= 0x1D7FF else c
        for c in s
    )
    # MathJax-isms the Exercises API emits that base LaTeX lacks -> ASCII math
    # (both pdflatex and pandoc understand < >). Word-boundary so \ltimes etc.
    # are untouched.
    s = re.sub(r"\\lt(?![a-zA-Z])", "<", s)
    s = re.sub(r"\\gt(?![a-zA-Z])", ">", s)
    # Obsolete LaTeX2.09 font switches: MathType/MathJax export emits the argument
    # form \rm{...} (also \bf \it ...). The memoir base class DISABLES the two-letter
    # commands ("! Class memoir Error: Font command \rm is not supported"), aborting
    # the PDF build, so map them to the LaTeX2e math-font commands. \rm{X} -> \mathrm{X}
    # is exact for the argument form these carry (\sc/\sl have no math analogue -> mathrm/mathit).
    for _old, _new in (
        ("rm", "mathrm"), ("bf", "mathbf"), ("it", "mathit"), ("sf", "mathsf"),
        ("tt", "mathtt"), ("cal", "mathcal"), ("sc", "mathrm"), ("sl", "mathit"),
    ):
        s = s.replace("\\" + _old + "{", "\\" + _new + "{")
    # Systems of equations from the Exercises API come as \begin{gathered} rows with
    # & alignment tabs (`x-2y &=& -5 \\ ...`). `gathered` (like `gather`) does NOT
    # allow & -> lualatex aborts with "Extra alignment tab has been changed to \cr".
    # MathJax tolerates it; map to `aligned`, which supports & (and aligns the = to
    # boot). Both are the nestable env used inside the system's \left\{ ... \right. .
    s = s.replace(r"\begin{gathered}", r"\begin{aligned}")
    s = s.replace(r"\end{gathered}", r"\end{aligned}")
    # data-math is the CONTENT between delimiters, so a literal $ is a currency
    # sign, not a math toggle -> escape it (else $...$10...$ desyncs math mode).
    # Likewise a bare % would comment out the rest of the line.
    s = re.sub(r"(?<!\\)\$", r"\\$", s)
    s = re.sub(r"(?<!\\)%", r"\\%", s)
    for u, r in _SYMBOLS.items():
        if u in s:
            s = s.replace(u, r)
    s = re.sub(r"[̀-ͯ⃐-⃿]", "", s)  # combining marks
    # remaining non-ASCII: keep letters as \text{}, drop other unknown glyphs
    s = re.sub(
        r"[^\x00-\x7F]",
        lambda m: (r"\text{%s}" % m.group(0)) if m.group(0).isalpha() else "",
        s,
    )
    # collapse whitespace: a blank line inside inline $...$ is an illegal \par.
    return re.sub(r"\s+", " ", s).strip()


def _left_delim(ch: str) -> str | None:
    r"""LaTeX delimiter for a fence <mo>, for use after \left / \right. Empty (a
    one-sided fence, e.g. a system's absent right brace) -> '.' (invisible)."""
    return {
        "{": r"\{",
        "}": r"\}",
        "[": "[",
        "]": "]",
        "(": "(",
        ")": ")",
        "|": "|",
        "‖": r"\|",
        "⟨": r"\langle ",
        "⟩": r"\rangle ",
        "": ".",
    }.get(ch)


def _fenced_row(node: _Element) -> str | None:
    r"""Wrap content bracketed by a stretchy fence <mo> as \left<d> ... \right<d>
    so the delimiter STRETCHES to the content (a system / piecewise / cases is a
    brace around an <mtable>). Without this, mml() emits a fixed-size literal \{
    that stays single-line-height in front of a tall array.

    The fence may sit MID-ROW: `C(n) = { <mtable>` renders the `C(n)=` prefix
    normally, then \left\{ around the table. Tolerates inconsistent source markup
    (fence="true" marked only on the opener, only on the empty closer, or neither
    -- then a following <mtable> is the tell). The closer must be a fence <mo>, so
    an unrelated `)` is never mistaken for it; a missing closer -> invisible
    \right. so \left is always balanced. Returns None if there's no stretchy fence
    (a plain literal `{` is then left as-is)."""
    kids: list[_Element] = [c for c in node if local(c.tag) is not None]
    if len(kids) < 2:
        return None
    # locate an OPENING fence <mo>: a delimiter marked fence/stretchy, or one that
    # is followed (possibly through a wrapper mrow) by a tall <mtable>.
    oi: int | None = None
    for i, c in enumerate(kids):
        if local(c.tag) != "mo" or (c.text or "").strip() not in (
            "{",
            "[",
            "(",
            "|",
            "‖",
            "⟨",
        ):
            continue
        if (
            c.get("fence") == "true"
            or c.get("stretchy") == "true"
            or any(_has_mtable(k) for k in kids[i + 1 :])
        ):
            oi = i
            break
    if oi is None:
        return None
    od: str | None = _left_delim((kids[oi].text or "").strip())
    if od is None:
        return None
    ci: int | None = None  # matching closer: the last fence <mo> after it
    for j in range(len(kids) - 1, oi, -1):
        if local(kids[j].tag) == "mo" and kids[j].get("fence") == "true":
            ci = j
            break
    prefix: str = "".join(mml(c) for c in kids[:oi])
    if ci is not None:
        cd: str = _left_delim((kids[ci].text or "").strip()) or "."
        mid: list[_Element] = kids[oi + 1 : ci]
    else:
        cd, mid = ".", kids[oi + 1 :]  # no closing fence -> invisible \right.
    return prefix + r"\left%s %s \right%s" % (od, "".join(mml(c) for c in mid), cd)


def _has_mtable(node: _Element) -> bool:
    return any(local(d.tag) == "mtable" for d in node.iter())


def mml_children(node: _Element) -> str:
    return "".join(mml(c) for c in node)


def mml(node: _Element) -> str:
    tag: str | None = local(node.tag)
    if tag is None:  # comment / PI
        return ""
    txt: str = node.text or ""

    if tag == "mrow":
        fenced = _fenced_row(node)  # {system} -> stretchy \left\{ ... \right.
        return fenced if fenced is not None else mml_children(node)
    if tag == "math" or tag == "mstyle" or tag == "semantics":
        return mml_children(node)
    if tag == "mi":
        t: str = (txt or "").strip()
        if t in GREEK:
            return GREEK[t]
        if t in MI_SYM:
            return MI_SYM[t]
        if t in MO_MAP:
            return MO_MAP[t]
        for u, r in GREEK.items():
            t = t.replace(u, r)
        if len(t) > 1 and t.isalpha():
            return r"\mathrm{%s}" % t
        if not t:
            return mml_children(node)
        return _esc_math_lit(t)
    if tag == "mn":
        t = txt or ""
        t = t.replace("−", "-").replace("–", "-")
        return _esc_math_lit(t)
    if tag == "mo":
        t = (txt or "").strip()
        if t in MO_MAP:
            return MO_MAP[t]
        if t in (
            "(",
            ")",
            "[",
            "]",
            "|",
            "+",
            "-",
            "=",
            "<",
            ">",
            ",",
            ".",
            "/",
            "!",
            ";",
            ":",
        ):
            return t
        if t == "{":
            return r"\{"
        if t == "}":
            return r"\}"
        if t == "%":
            return r"\%"
        if t == '"':
            return r'\text{"}'  # straight double quote (punctuation in math)
        if t == "\u201c":
            return r"\text{``}"  # left double quote
        if t == "\u201d":
            return r"\text{''}"  # right double quote
        if t == "`":
            return r"\text{`}"  # backtick = opening single quote (punctuation in math)
        for u, r in MO_MAP.items():
            t = t.replace(u, r)
        return _esc_math_lit(t)
    if tag == "mtext":
        return mtext_to_latex(txt)
    if tag == "mspace":
        if "newline" in (node.get("linebreak") or ""):
            return _MNL  # author line break -> aligned-display split point
        w: str = node.get("width", "")
        if "negative" in w or w.startswith("-"):
            return r"\!"
        return r"\;" if w and _emval(w) >= 0.3 else r"\,"
    if tag == "msup":
        ch: list[_Element] = list(node)
        if len(ch) >= 2:
            sup: str = mml(ch[1])
            return _grp(ch[0]) if _empty_script(sup) else "%s^{%s}" % (_grp(ch[0]), sup)
        return mml_children(node)
    if tag == "msub":
        ch = list(node)
        if len(ch) >= 2:
            sub: str = mml(ch[1])
            return _grp(ch[0]) if _empty_script(sub) else "%s_{%s}" % (_grp(ch[0]), sub)
        return mml_children(node)
    if tag == "msubsup":
        ch = list(node)
        if len(ch) >= 3:
            base: str = _grp(ch[0])
            sub = mml(ch[1])
            sup = mml(ch[2])
            out: str = base
            if not _empty_script(sub):
                out += "_{%s}" % sub
            if not _empty_script(sup):
                out += "^{%s}" % sup
            return out
        return mml_children(node)
    if tag == "mfrac":
        ch = list(node)
        if len(ch) >= 2:
            return r"\frac{%s}{%s}" % (mml(ch[0]), mml(ch[1]))
        return mml_children(node)
    if tag == "msqrt":
        return r"\sqrt{%s}" % mml_children(node)
    if tag == "mroot":
        ch = list(node)
        if len(ch) >= 2:
            return r"\sqrt[%s]{%s}" % (mml(ch[1]), mml(ch[0]))
        return mml_children(node)
    if tag == "munder":
        ch = list(node)
        if len(ch) >= 2:
            base = mml(ch[0])
            # A lowline/underbar under-glyph is a vinculum (e.g. long-division
            # subtraction bars): render a true \underline, not a tiny \underset.
            under_raw = "".join(ch[1].itertext()).strip()
            if under_raw in ("_", "‾", "̲", "―", "_"):
                return r"\underline{%s}" % base
            sub = mml(ch[1])
            if base.strip() in (r"\lim", r"\max", r"\min", r"\sup", r"\inf"):
                return "%s_{%s}" % (base.strip(), sub)
            if not sub:
                return base
            return r"\underset{%s}{%s}" % (sub, base)
        return mml_children(node)
    if tag == "mover":
        ch = list(node)
        if len(ch) >= 2:
            base = mml(ch[0])
            # Inspect the RAW over-glyph: an overbar (macron U+00AF / overline
            # U+203E / combining U+0305) is dropped by mo's unknown-glyph net,
            # so mml() would return "" and the vinculum would be lost. Detecting
            # it here yields a true \overline (fixes long-division bars, etc.).
            over_raw = "".join(ch[1].itertext()).strip()
            if over_raw in ("¯", "‾", "̅", "_", "―"):
                return r"\overline{%s}" % base
            over = mml(ch[1]).strip()
            acc = {
                "¯": r"\overline",
                "→": r"\vec",
                "^": r"\hat",
                "~": r"\tilde",
                ".": r"\dot",
            }.get(over)
            if acc:
                return r"%s{%s}" % (acc, base)
            if not over:
                return base
            return r"\overset{%s}{%s}" % (over, base)
        return mml_children(node)
    if tag == "munderover":
        ch = list(node)
        if len(ch) >= 3:
            base = mml(ch[0]).strip()
            return "%s_{%s}^{%s}" % (base, mml(ch[1]), mml(ch[2]))
        return mml_children(node)
    if tag == "mfenced":
        opn: str = node.get("open", "(")
        cls: str = node.get("close", ")")
        sep: str = node.get("separators", ",")
        parts: list[str] = [mml(c) for c in node]
        inner: str = (sep or ",").join(parts)
        return r"\left%s %s \right%s" % (_delim(opn), inner, _delim(cls))
    if tag in ("annotation", "annotation-xml"):
        return ""
    if tag == "mtable":
        return _mtable(node)
    if tag == "mmultiscripts":
        ch = list(node)
        if not ch:
            return ""
        base = mml(ch[0])

        def _r(x: _Element | None) -> str:
            return "" if (x is None or local(x.tag) == "none") else mml(x)

        pre: list[tuple[str, str]] = []
        post: list[tuple[str, str]] = []
        inpre: bool = False
        i: int = 1
        while i < len(ch):
            if local(ch[i].tag) == "mprescripts":
                inpre = True
                i += 1
                continue
            sub = _r(ch[i]) if i < len(ch) else ""
            sup = _r(ch[i + 1]) if i + 1 < len(ch) else ""
            (pre if inpre else post).append((sub, sup))
            i += 2
        out = ""
        for sub, sup in pre:
            out += ("_{%s}" % sub if sub else "") + ("^{%s}" % sup if sup else "")
        if out:
            out = "{}" + out
        out += base
        for sub, sup in post:
            out += ("_{%s}" % sub if sub else "") + ("^{%s}" % sup if sup else "")
        return out
    if tag in ("mprescripts", "none"):
        return ""
    if tag in ("mtr", "mtd", "mlabeledtr"):
        return mml_children(node)  # handled by _mtable normally
    if tag == "mphantom":
        return r"\phantom{%s}" % mml_children(node)
    if tag == "mpadded":
        inner = mml_children(node)
        # MathJax uses width="0" to make a box zero-width (for measurement or an
        # intentional overlap); honoring it stops the content from shoving the
        # following math right -- e.g. the long-division "house" dividend, which
        # otherwise renders far to the right. \mathrlap = zero-width, overlaps right.
        if (node.get("width") or "").strip() in ("0", "0em", "0px", "0pt"):
            return r"\mathrlap{%s}" % inner
        return inner
    if tag == "menclose":
        return mml_children(node)
    # fallback
    warn_unknown("m:" + (tag or "?"))
    return mml_children(node)


def _empty_script(x: str) -> bool:
    return x.strip() in ("", "{}", "\\text{}")


def _emval(w: str) -> float:
    m: re.Match[str] | None = re.match(r"(-?[\d.]+)\s*em", w)
    return float(m.group(1)) if m else 0.2


def _delim(d: str) -> str:
    return {
        "(": "(",
        ")": ")",
        "[": "[",
        "]": "]",
        "{": r"\{",
        "}": r"\}",
        "|": "|",
        "": ".",
    }.get(d, d)


def _grp(node: _Element) -> str:
    """Render a base for sup/sub; wrap in braces if it is not a single token."""
    s: str = mml(node)
    bare: str = s.strip()
    if len(bare) == 1 or (local(node.tag) in ("mi", "mn") and len(bare) <= 1):
        return s
    if local(node.tag) in ("mrow", "msup", "msub", "mfrac", "msqrt", "mfenced"):
        return "{%s}" % s
    return "{%s}" % s if len(bare) > 1 else s


def _mtable(node: _Element) -> str:
    """Aligned derivation. OpenStax pattern: cols = [lhs, =rhs, (blanks), reason].
    Render as an array; reason cells (text) pushed right with \\quad."""
    rows: list[_Element] = [r for r in node if local(r.tag) in ("mtr", "mlabeledtr")]
    body_rows: list[list[str]] = []
    maxcols: int = 0
    for r in rows:
        cells: list[_Element] = [c for c in r if local(c.tag) == "mtd"]
        maxcols = max(maxcols, len(cells))
    for r in rows:
        cells = [c for c in r if local(c.tag) == "mtd"]
        rendered: list[str] = []
        for c in cells:
            rendered.append(mml_children(c))
        while len(rendered) < maxcols:
            rendered.append("")
        body_rows.append(rendered)
    if maxcols == 0:
        return ""
    # column alignment from first row's cells, default r then l...
    aligns: list[str] = []
    first: _Element | None = rows[0] if rows else None
    fcells: list[_Element] = (
        [c for c in first if local(c.tag) == "mtd"] if first is not None else []
    )
    for i in range(maxcols):
        a: str | None = fcells[i].get("columnalign") if i < len(fcells) else None
        aligns.append({"right": "r", "left": "l", "center": "c"}.get(a or "l", "l"))
    colspec: str = "".join(aligns)
    lines: list[str] = []
    for rr in body_rows:
        lines.append(" & ".join(rr))
    return r"\begin{array}{%s}%s\end{array}" % (colspec, " \\\\ ".join(lines))


def math_to_latex(mnode: _Element, display: bool = False) -> str:
    inner: str = mml(mnode).strip()
    inner = re.sub(r"\s+", " ", inner)
    # drop trailing math-spacing commands (\, \; \: \! \ ) -- a whitespace
    # <mtext> renders to a control space, and a later strip() would leave a bare
    # trailing backslash that escapes the closing $.
    inner = re.sub(r"(?:\\[ ,;:!])+\s*$", "", inner).rstrip()
    if inner.endswith("\\") and not inner.endswith("\\\\"):
        inner = inner[:-1]
    return inner.strip()


# --------------------------------------------------------------------------
# continued-equality promotion
# --------------------------------------------------------------------------
# A chain of equalities (a = b = c = d), or an explicitly line-broken derivation
# (rows separated by <mspace linebreak="newline"/> -> _MNL), is emitted inline as
# one $...$ by default. When it is too wide, pdflatex breaks it at the '=' relations
# and hangs each continuation '=' at the left margin, detached from the opening
# expression. OpenStax sets these as an aligned display with the '=' in a column.
# We reproduce that: promote such math to \[\begin{aligned}...\end{aligned}\], with
# an alignment tab before each relation. Genuinely inline short math is left alone.
def _depth0_positions(s: str, ch: str) -> list[int]:
    r"""Positions of `ch` at nesting-depth 0 in a LaTeX string. Tracks braces AND
    parentheses/brackets, so a '=' inside \frac{}, inside (4x+y=1), or inside
    \left[...\right] is nested and correctly ignored -- only a top-level relation
    counts. \-escapes are skipped so \{ \} \left( etc. don't unbalance the count."""
    out: list[int] = []
    depth: int = 0
    i: int = 0
    n: int = len(s)
    while i < n:
        c: str = s[i]
        if c == "\\":
            i += 2  # skip a control sequence / escaped char
            continue
        if c in "([{":
            depth += 1
        elif c in ")]}":
            depth -= 1
        elif c == ch and depth == 0:
            out.append(i)
        i += 1
    return out


def _align_row(s: str) -> str:
    """One equation -> put an alignment tab before its first depth-0 '='."""
    pos: list[int] = _depth0_positions(s, "=")
    if not pos:
        return s.strip()
    p: int = pos[0]
    return "%s &= %s" % (s[:p].strip(), s[p + 1 :].strip())


def _has_depth0_separator(s: str) -> bool:
    r"""True if `s` has a top-level list separator -- a comma/semicolon, or a spacing
    macro (\, \; \: \  \quad \qquad) -- i.e. it is a LIST of distinct equations
    (`m=0 \, m=-6`, `x=1;y=2`), NOT one continued equality `a=b=c`. Needed because
    _depth0_positions skips \-escapes, so it never sees the comma in a \, separator."""
    depth: int = 0
    i: int = 0
    n: int = len(s)
    while i < n:
        c: str = s[i]
        if c == "\\":
            if depth == 0 and (
                s[i + 1 : i + 2] in ",;: "
                or s[i + 1 : i + 5] == "quad"
                or s[i + 1 : i + 6] == "qquad"
            ):
                return True
            i += 2
            continue
        if c in "([{":
            depth += 1
        elif c in ")]}":
            depth -= 1
        elif depth == 0 and c in ",;":
            return True
        i += 1
    return False


def _aligned_body(inner: str) -> str | None:
    r"""Body for an `aligned` environment if `inner` is a display-worthy continued
    equality, else None (caller keeps it inline). Two shapes:
      - explicit line breaks (_MNL): one equation per row, each aligned at its '=';
      - a plain chain a=b=c=d (>=3 top-level '='): shared LHS, one '=' per row."""
    # Never touch math that is already a structured environment: an mtable renders
    # as \begin{array}{rcl}...\end{array} (already aligned at its own '=' column),
    # and a system is \left\{\begin{array}{l}...\right. -- both contain '=' signs
    # that must NOT be treated as chain relations. Only flat math is promotable.
    if "\\begin{" in inner:
        return None
    if _MNL in inner:
        # Split only at TOP-LEVEL line breaks. A linebreak nested inside a group
        # (e.g. a multi-row \underline{} in a vertical multiplication/long-division
        # layout) must NOT split, or its braces would be torn across '\\'.
        nl: list[int] = _depth0_positions(inner, _MNL)
        rows: list[str] = []
        prev: int = 0
        for p in nl:
            rows.append(inner[prev:p])
            prev = p + 1
        rows.append(inner[prev:])
        rows = [r for r in rows if r.strip()]
        if len(rows) < 2:
            return None
        if not any(_depth0_positions(r, "=") for r in rows):
            return None  # no relations -> a layout (multiplication/division), not
            # a continued equality -> leave it inline, unpromoted
        lines: list[str] = [_align_row(r) for r in rows]
    else:
        eqs: list[int] = _depth0_positions(inner, "=")
        if len(eqs) < 3:  # short inline chain: don't promote
            return None
        if _has_depth0_separator(inner):
            return None  # a top-level separator (comma / semicolon /
            # \, \quad ...) means a LIST of distinct
            # equations (x=3, y=4, m=2), not a chain
        seg: list[str] = []
        prev = 0
        for p in eqs:
            seg.append(inner[prev:p])
            prev = p + 1
        seg.append(inner[prev:])
        lines = ["%s &= %s" % (seg[0].strip(), seg[1].strip())]
        lines += ["&= %s" % s.strip() for s in seg[2:]]
    return " \\\\\n".join(lines)


def _toplevel_kids(node: _Element) -> list[_Element]:
    """Element children of `node`, descending through a lone mrow/mstyle wrapper."""
    kids: list[_Element] = [c for c in node if local(c.tag) is not None]
    while len(kids) == 1 and local(kids[0].tag) in (
        "math",
        "mrow",
        "mstyle",
        "semantics",
    ):
        kids = [c for c in kids[0] if local(c.tag) is not None]
    return kids


def _degenerate_eq_mtable(mnode: _Element) -> str | None:
    r"""A continued-equality mtable whose rows are [empty]...[= rhs] -- the opening
    LHS lives in separate prose, so _mtable renders it as an array with empty
    leading columns and the '=' hanging at the left (the '= on the left' bug).
    Return an `aligned` body (each row `&= rhs`) if `mnode` has exactly this shape,
    else None. Normal [lhs][=][rhs] mtables have a non-empty first cell -> excluded."""
    kids: list[_Element] = _toplevel_kids(mnode)
    if len(kids) != 1 or local(kids[0].tag) != "mtable":
        return None
    rows: list[_Element] = [r for r in kids[0] if local(r.tag) in ("mtr", "mlabeledtr")]
    if len(rows) < 2:
        return None
    lines: list[str] = []
    for r in rows:
        cells: list[_Element] = [c for c in r if local(c.tag) == "mtd"]
        nonempty: list[_Element] = [c for c in cells if "".join(c.itertext()).strip()]
        if not nonempty:
            return None
        first: list[_Element] = list(nonempty[0])
        if not (
            first
            and local(first[0].tag) == "mo"
            and (first[0].text or "").strip() == "="
        ):
            return None  # a row not led by '=' -> not this shape
        rowtex: str = "".join(mml(c) for c in cells).strip()
        lines.append(_align_row(rowtex))
    return " \\\\\n".join(lines)


def render_math(node: _Element) -> str:
    r"""Inline math `$...$`, unless it is a wide continued equality / explicitly
    line-broken derivation -> promote to an aligned display so the '=' signs line
    up (OpenStax house style) instead of wrapping with '=' flushed left. Display
    math is illegal in a tabular cell, so cell mode always stays inline."""
    if not _CELL_MODE:
        body: str | None = _degenerate_eq_mtable(
            node
        )  # continued-equality mtable ('=' on the left)
        if body is not None:
            return "\n\\[\n\\begin{aligned}\n%s\n\\end{aligned}\n\\]\n" % body
    inner: str = math_to_latex(node)
    if not inner:
        return ""
    if not _CELL_MODE:
        body = _aligned_body(inner)
        if body is not None:
            return "\n\\[\n\\begin{aligned}\n%s\n\\end{aligned}\n\\]\n" % body
    return "$%s$" % inner.replace(_MNL, r"\,")  # inline: sentinel -> thin space


# --------------------------------------------------------------------------
# inline content (text + inline elements) within a block
# --------------------------------------------------------------------------
def inline(node: _Element, labels: set[str]) -> str:
    """Render mixed inline content of `node` to LaTeX (text + tail handled by caller)."""
    out: list[str] = []
    if node.text:
        out.append(esc_text(node.text))
    for child in node:
        out.append(inline_element(child, labels))
        if child.tail:
            out.append(esc_text(child.tail))
    return "".join(out)


def inline_element(node: _Element, labels: set[str]) -> str:
    tag: str | None = local(node.tag)
    if tag is None:
        return ""
    ns: str = node.tag.split("}")[0][1:] if "}" in node.tag else ""
    if ns.endswith("MathML"):
        return render_math(node)
    if tag == "emphasis":
        # CNXML defaults emphasis/@effect to "bold" (verified against the official
        # PDF: bare <emphasis> renders bold; italics only when effect="italics").
        eff: str = node.get("effect", "bold")
        body: str = inline(node, labels)
        _bs: str = body.strip()
        # OpenStax styles worked-example labels specially regardless of the source
        # <emphasis>: "Step N" in bold, "Example N" as a teal badge.
        if re.match(r"^Step\s+\d", _bs):
            return r"\textbf{%s}" % body
        if re.match(r"^Example\s+\d", _bs):
            return r"\OSexamplebadge{%s}" % _bs
        if eff == "bold":
            return r"\textbf{%s}" % body
        if eff == "underline":
            return r"\underline{%s}" % body
        if eff == "smallcaps":
            return r"\textsc{%s}" % body
        return r"\emph{%s}" % body
    if tag == "term":
        if node.get("class") == "no-emphasis":
            return inline(node, labels)
        # OpenStax renders key-vocabulary terms in bold, not italic.
        return r"\textbf{%s}" % inline(node, labels)
    if tag == "link":
        tgt: str | None = node.get("target-id")
        doc: str | None = node.get("document")
        url: str | None = node.get("url")
        if node.get("class") == "os-embed" and url and url.startswith("#exercise/"):
            # os-embed exercises are injected block-level (see block_element);
            # if one appears inline, emit a short marker, never a dead \url.
            return r"\emph{(practice exercise --- online edition)}"
        if url:
            body = inline(node, labels).strip()
            if body:
                return r"\href{%s}{%s}" % (url.replace("%", r"\%"), body)
            return r"\url{%s}" % url.replace("%", r"\%")
        if tgt:
            return r"\cref{%s}" % link_label(tgt, doc)
        if doc:  # whole-module reference
            return r"\cref{mod:%s}" % doc
        return inline(node, labels)
    if tag == "sub":
        return r"\textsubscript{%s}" % inline(node, labels)
    if tag == "sup":
        return r"\textsuperscript{%s}" % inline(node, labels)
    if tag == "newline":
        return " " if _CELL_MODE else r" \NLBREAK "
    if tag == "footnote":
        return r"\footnote{%s}" % inline(node, labels)
    if tag == "code":
        return r"\texttt{%s}" % inline(node, labels)
    if tag == "quote":
        return "``%s''" % inline(node, labels)
    if tag == "math":
        return render_math(node)
    if tag == "media":
        return render_media(node, labels)
    if tag == "image":
        src: str = _imgname(node.get("src", ""))
        return "\\includegraphics[height=1em]{%s}" % src if src else ""
    if tag == "emphasis":
        return r"\emph{%s}" % inline(node, labels)
    # block-ish element appearing inline -> just recurse
    warn_unknown("inline:" + (tag or "?"))
    return inline(node, labels)


# --------------------------------------------------------------------------
# labels
# --------------------------------------------------------------------------
# module-scoped label state (CNXML reuses fs-id values across modules, so a
# bare id is NOT globally unique -> prefix every label with its owning module)
_CURMOD = ""  # module currently being converted
_LOCAL_IDS: set[str] = set()  # ids defined in the current module
_ID2MOD: dict[
    str, str
] = {}  # id -> module, across the volume (built in convert_collection)
_ALL_TARGETS: set[str] = set()  # every referenced target-id across the whole collection


def mklabel(raw_id: str | None, mid: str | None = None) -> str:
    """Map a CNXML id to a safe, module-scoped LaTeX label."""
    m: str = mid if mid is not None else _CURMOD
    safe: str = re.sub(r"[^A-Za-z0-9]", "-", raw_id or "")
    return "x%s-%s" % (m, safe) if m else "x" + safe


def link_label(tgt: str, doc: str | None) -> str:
    """Resolve a <link target-id=.. document=..> to the right module-scoped label."""
    if doc:
        m: str = doc
    elif tgt in _LOCAL_IDS:
        m = _CURMOD
    elif tgt in _ID2MOD:
        m = _ID2MOD[tgt]
    else:
        m = _CURMOD
    return mklabel(tgt, m)


_BLOCK_BEGIN = (
    r"\\begin\{(?:figure|equation|center|itemize|enumerate|example|"
    r"theorem|corollary|lemma|definition|exercise|checkpoint|calcnote|"
    r"strategy|mathrule|objectives|keyconcepts|keyequations|medianote|"
    r"tabular|quote|description|answer|solution|array)"
)


def cleanup_latex(s: str) -> str:
    r"""Resolve \NLBREAK sentinels (from <newline/>) into \\ line breaks,
    dropping the ones that fall at block boundaries (which would cause
    'There's no line here to end'). Structural \\ inside math arrays use a
    literal \\ and are never touched here."""
    # A sentinel adjacent to a line boundary (newline) can't be a \\ line break
    # ("There's no line here to end") -> make it a paragraph break instead.
    s = re.sub(r"[^\S\n]*\\NLBREAK[^\S\n]*\n[^\S\n]*", "\n\n", s)  # end of a line
    s = re.sub(r"(?<=\n)[^\S\n]*\\NLBREAK[^\S\n]*", "\n\n", s)  # start of a line
    # a sentinel just before a block/\end/\item/par/display math -> paragraph break
    s = re.sub(
        r"\\NLBREAK[^\S\n]*(?=(%s|\\\[|\\end\{|\\item\b|\\par\b))" % _BLOCK_BEGIN,
        "\n\n",
        s,
    )
    # a sentinel right after a block begin / \item -> drop
    s = re.sub(r"((?:%s|\\item\b)[^\n]*?)[^\S\n]*\\NLBREAK" % _BLOCK_BEGIN, r"\1", s)
    # any surviving (mid-line) sentinel becomes a real line break
    s = s.replace(r"\NLBREAK", r"\\")
    # a line break with nothing before it on the line ("There's no line here to
    # end") -- drop a \\ that is alone on a line or starts a line.
    s = re.sub(r"(?m)^[ \t]*\\\\+[ \t]*$", "", s)
    s = re.sub(r"(?m)^[ \t]*\\\\+[ \t]*(?=\S)", "", s)
    # a \\ immediately followed by [ is misread as \\[<dimen>]; we never emit
    # an optional line-break length, so protect the bracket with {}.
    s = re.sub(r"(\\\\)(\s*)\[", r"\1\2{}[", s)
    s = re.sub(r"\n{3,}", "\n\n", s)
    s = s.replace(
        _MNL, r"\,"
    )  # backstop: any unpromoted newline sentinel -> thin space
    return s


# --------------------------------------------------------------------------
# source-line wrapping (readability of the committed .tex)
# --------------------------------------------------------------------------
# Wrap PROSE lines to a comfortable width, but use discretion:
#  - never touch display math / tables: lines inside \[..\] or a math/tabular
#    environment stay exactly as-is (an equation is easier to read on one line,
#    even if it runs past the width);
#  - inline math $...$ is an unbreakable unit (kept whole on whatever line it
#    lands on); everything else (\cref{}, \emph{}, \includegraphics{}, ...) has
#    no internal spaces, so plain whitespace splitting already keeps it intact.
WRAP_WIDTH = 95
_NOWRAP_ENVS = {
    "equation",
    "equation*",
    "align",
    "align*",
    "alignat",
    "alignat*",
    "gather",
    "gather*",
    "multline",
    "multline*",
    "array",
    "array*",
    "tabular",
    "tabular*",
    "matrix",
    "bmatrix",
    "pmatrix",
    "cases",
    "verbatim",
}
# lines that are structural delimiters / restricted args -> leave untouched
_SKIP_WRAP = re.compile(
    r"\\(begin|end)\{|"
    r"\\(chapter|section|subsection|subsubsection|paragraph|part)\*?\{|"
    r"\\(includegraphics|input|subfile|printanswerkey|tableofcontents|"
    r"frontmatter|mainmatter|backmatter|OSfrontmatter)\b"
)
_INLINE_MATH = re.compile(
    r"((?<!\\)\$.*?(?<!\\)\$)"
)  # capturing -> re.split keeps spans


def _wrap_prose(line: str, width: int) -> str:
    # split into atoms: inline-math spans stay whole, the rest splits on spaces
    atoms: list[str] = []
    for i, part in enumerate(_INLINE_MATH.split(line)):
        if i % 2:
            atoms.append(part)  # an inline-math span
        else:
            atoms.extend(part.split())  # ordinary words
    if not atoms:
        return line
    out: list[str] = []
    cur: str = ""
    for a in atoms:
        if not cur:
            cur = a
        elif len(cur) + 1 + len(a) <= width:
            cur += " " + a
        else:
            out.append(cur)
            cur = a  # an over-long atom (e.g. a big $...$) sits alone
    if cur:
        out.append(cur)
    return "\n".join(out)


def wrap_latex(s: str, width: int = WRAP_WIDTH) -> str:
    out: list[str] = []
    nowrap: bool = False
    for line in s.split("\n"):
        st: str = line.strip()
        if nowrap:
            out.append(line)
            _endm: re.Match[str] | None = re.match(r"\\end\{([a-zA-Z*]+)\}", st)
            if st == r"\]" or (_endm and _endm.group(1) in _NOWRAP_ENVS):
                nowrap = False
            continue
        if st == r"\[":
            out.append(line)
            nowrap = True
            continue
        m: re.Match[str] | None = re.match(r"\\begin\{([a-zA-Z*]+)\}", st)
        if m and m.group(1) in _NOWRAP_ENVS:
            out.append(line)
            nowrap = True
            continue
        if not st or _SKIP_WRAP.search(st) or len(line) <= width:
            out.append(line)
            continue
        out.append(_wrap_prose(line, width))
    return "\n".join(out)


# --------------------------------------------------------------------------
# block content
# --------------------------------------------------------------------------
BLOCK_TAGS = {
    "para",
    "section",
    "list",
    "equation",
    "figure",
    "media",
    "example",
    "exercise",
    "note",
    "table",
    "rule",
    "commentary",
}


def is_block(child: _Element) -> bool:
    if not isinstance(child.tag, str):
        return False
    ns: str = child.tag.split("}")[0][1:] if "}" in child.tag else ""
    if ns.endswith("MathML"):
        return False
    return local(child.tag) in BLOCK_TAGS


def flow(node: _Element, labels: set[str], depth: int = 0) -> str:
    """Render mixed (block + inline + text) content in document order.
    Block children are emitted on their own lines; inline children and text
    runs are emitted inline. This is the single content renderer used for
    every container (content, section, para, problem, solution, item, ...)."""
    parts: list[str] = []
    if node.text:
        t: str = collapse_ws(node.text)
        if t.strip() or (parts == [] and t == " "):
            parts.append(esc_text(t))
    children: list[_Element] = list(node)
    i: int = 0
    n: int = len(children)
    while i < n:
        child: _Element = children[i]
        ctag: str | None = local(child.tag)
        if ctag is None:
            i += 1
            continue  # comment / processing instruction
        if ctag == "title":
            i += 1
            continue  # consumed by the parent renderer
        # OpenStax lays consecutive practice questions out in TWO columns: group
        # a run of adjacent <exercise> siblings into a multicols block (>=2).
        if ctag == "exercise" and not _CELL_MODE:
            j: int = i
            run: list[str] = []
            while j < n and local(children[j].tag) == "exercise":
                r: str = block_element(children[j], labels, depth).strip()
                if r:
                    run.append(r)
                j += 1
            if len(run) >= 2:
                parts.append(
                    "\n\\begin{multicols}{2}\n"
                    + "\n\n".join(run)
                    + "\n\\end{multicols}\n"
                )
            elif run:
                parts.append("\n" + run[0] + "\n")
            tl: str | None = children[
                j - 1
            ].tail  # tail of the last exercise in the run
            if tl:
                t = collapse_ws(tl)
                if t.strip() or t == " ":
                    parts.append(esc_text(t))
            i = j
            continue
        if is_block(child):
            b: str = block_element(child, labels, depth)
            if b and b.strip():
                parts.append("\n" + b.strip() + "\n")
        else:
            parts.append(inline_element(child, labels))
        if child.tail:
            t = collapse_ws(child.tail)
            if t.strip() or t == " ":
                parts.append(esc_text(t))
        i += 1
    return "".join(parts)


# `blocks` kept as an alias: same unified renderer.
def blocks(node: _Element, labels: set[str], depth: int = 0) -> str:
    return flow(node, labels, depth)


def opt_label(node: _Element) -> str:
    i: str | None = node.get("id")
    return ("\\label{%s}" % mklabel(i)) if i else ""


def get_title(node: _Element) -> _Element | None:
    t: _Element | None = node.find(C + "title")
    return t


# --------------------------------------------------------------------------
# injected os-embed practice exercises. The CNXML references practice items as
# <link class="os-embed" url="#exercise/<nickname>"/>; the content lives in the
# OpenStax Exercises service, fetched into exercises/<nickname>.json by
# tools/cnxml2tex/fetch_exercises.py. Questions-only: we render the stem and the
# multiple-choice options (the public API gives no answer key or solution).
# --------------------------------------------------------------------------
EXERCISES = os.path.join(ROOT, "exercises")
_EX_LETTERS = "abcdefghijklmnop"  # OpenStax uses lowercase option labels
_IN_CALLOUT = False  # True while rendering a callout box body
_IN_EXERCISE = False  # True while rendering an <exercise> body
_EX_ONLINE = (
    "\\begin{practice}\n\\emph{Practice exercise available in the "
    "online edition.}\n\\end{practice}\n"
)


def _os_embed_nickname(node: _Element) -> str | None:
    """If this <para> is nothing but an os-embed #exercise link, return its
    nickname (else None). These links are always the sole content of a para."""
    links: list[_Element] = node.findall(C + "link")
    if len(links) != 1:
        return None
    ln: _Element = links[0]
    if ln.get("class") != "os-embed":
        return None
    url: str = ln.get("url") or ""
    if not url.startswith("#exercise/"):
        return None
    if (node.text or "").strip():
        return None
    for c in node:
        if c is ln:
            if (c.tail or "").strip():
                return None
        elif local(c.tag) is not None:
            return None
    return url[len("#exercise/") :]


def _ex_img(src: str | None) -> str | None:
    """Resolve a cached exercise image for \\includegraphics. Downloaded SVGs are
    rasterized to PNG at build time into exercises/media-derived/ (PNG works in
    both pdflatex and pandoc); jpg/png are used from the committed cache."""
    if not src or src.startswith(("http://", "https://")):
        return None  # not cached -> drop
    if src.lower().endswith(".svg"):
        base: str = os.path.splitext(os.path.basename(src))[0]
        return "exercises/media-derived/%s.png" % base
    return src


def _clean_ex_cell(c: str) -> str:
    r"""Neutralize constructs illegal in an LR-mode tabular cell: a display \[..\]
    becomes inline $..$, \par/skip macros and blank-line breaks become a space."""
    c = re.sub(
        r"\\\[\s*(.*?)\s*\\\]",
        lambda m: "$" + m.group(1).strip() + "$",
        c,
        flags=re.DOTALL,
    )
    c = re.sub(r"\\(par|smallskip|medskip|bigskip)\b", " ", c)
    c = re.sub(r"\s*\n+\s*", " ", c)
    return c.strip()


class _ExHTML(HTMLParser):
    """Minimal exercise-HTML -> LaTeX for the shapes the Exercises API emits:
    <span data-math>, <p>, <br>, <ol>/<ul>/<li>, <img>, <strong>/<em>/<sup>/
    <sub>, and <table> (thead/tbody/tr/th/td -> a house-style tabular; without
    this a data table linearizes to a vertical list). Other tags are transparent
    (children still render)."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.out: list[str] = []
        self._skip: int = 0  # >0 while inside a data-math span
        self._stack: list[str] = []  # open list environments
        self._tables: list[
            dict[str, Any]
        ] = []  # tables being collected (rows/row/rowhdr)
        self._cellsave: list[list[str]] = []  # saved self.out while capturing a cell
        self._th: list[bool] = []  # per-open-cell: is this cell a header cell?
        self._incell: int = 0  # >0 while capturing a table cell
        self._inthead: int = 0  # >0 while inside <thead>

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if self._skip:
            self._skip += 1
            return
        a: dict[str, str | None] = dict(attrs)
        if tag == "span" and "data-math" in a:
            m: str = _norm_math((a.get("data-math") or "").strip())
            if m:  # guard: empty -> no $$ toggle
                self.out.append("$%s$" % m)
            self._skip = 1
        elif tag == "table":
            self._tables.append({"rows": [], "row": None, "rowhdr": False})
        elif tag == "thead":
            self._inthead += 1
        elif tag == "tr" and self._tables:
            self._tables[-1]["row"] = []
            self._tables[-1]["rowhdr"] = False
        elif tag in ("td", "th") and self._tables:
            self._cellsave.append(self.out)  # capture the cell in its own buffer
            self.out = []
            self._th.append(tag == "th" or self._inthead > 0)
            self._incell += 1
        elif tag in ("p", "div"):
            self.out.append(" " if self._incell else "\n\n")  # no \par inside a cell
        elif tag == "br":
            self.out.append(" " if self._incell else "\n\n")  # \par outside cells
        elif tag in ("strong", "b"):
            self.out.append(r"{\bfseries ")  # group decl (not \textbf{}) so an
        elif tag in ("em", "i"):  # image/\par nested inside can't
            self.out.append(r"{\itshape ")  # break a fragile text-command
        elif tag == "sup":
            self.out.append(r"\textsuperscript{")
        elif tag == "sub":
            self.out.append(r"\textsubscript{")
        elif tag == "ol":
            self._stack.append("enumerate")
            self.out.append("\n\\begin{enumerate}\n")
        elif tag == "ul":
            self._stack.append("itemize")
            self.out.append("\n\\begin{itemize}\n")
        elif tag == "li":
            self.out.append(r"\item ")
        elif tag == "img":
            r: str | None = _ex_img(a.get("src", ""))
            if r:
                self.out.append(
                    r"\par\noindent\includegraphics[width=\linewidth]{%s}\par " % r
                )

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.handle_starttag(tag, attrs)  # <br/>, <img .../>

    def handle_endtag(self, tag: str) -> None:
        if self._skip:
            self._skip -= 1
            return
        if tag in ("td", "th") and self._incell:
            cell: str = _clean_ex_cell("".join(self.out))
            self.out = self._cellsave.pop()  # restore parent buffer
            self._incell -= 1
            is_h: bool = self._th.pop()
            t: dict[str, Any] | None = self._tables[-1] if self._tables else None
            if t is not None and t["row"] is not None:
                t["row"].append(cell)
                if is_h:
                    t["rowhdr"] = True
        elif tag == "tr" and self._tables and self._tables[-1]["row"] is not None:
            t = self._tables[-1]
            t["rows"].append((t["row"], t["rowhdr"]))
            t["row"] = None
        elif tag == "thead" and self._inthead:
            self._inthead -= 1
        elif tag == "table" and self._tables:
            t = self._tables.pop()
            self.out.append(self._render_ex_table(t["rows"]))
        elif tag in ("strong", "b", "em", "i", "sup", "sub"):
            self.out.append("}")
        elif tag in ("ol", "ul") and self._stack:
            self.out.append("\n\\end{%s}\n" % self._stack.pop())

    def _render_ex_table(self, rows: list[tuple[list[str], bool]]) -> str:
        r"""Collected exercise-HTML rows -> a LaTeX tabular in the book's table
        house style (teal rules + teal header row, fit-to-width). A nested table
        (captured inside a cell) is kept plain -- no \resizebox/center."""
        rows = [(cells, hdr) for cells, hdr in rows if cells]
        if not rows:
            return ""
        ncols: int = max(len(cells) for cells, _ in rows)
        if ncols == 0:
            return ""
        nested: bool = self._incell > 0
        lines: list[str] = []
        if not nested:
            lines.append("\\arrayrulecolor{OScolor}")
        lines.append("\\begin{tabular}{|%s}" % ("l|" * ncols))
        lines.append("\\hline")
        for cells, is_header in rows:
            cells = (list(cells) + [""] * ncols)[:ncols]
            if is_header and not nested:
                cells = ["{\\color{white}\\bfseries %s}" % c for c in cells]
                lines.append("\\rowcolor{OScolor}" + " & ".join(cells) + r" \\")
            else:
                lines.append(" & ".join(cells) + r" \\")
            lines.append("\\hline")
        lines.append("\\end{tabular}")
        tab: str = "\n".join(lines)
        if nested:
            return tab
        tab = re.sub(r"\n[ \t]*\n", "\n", tab)  # no blank line inside a scanned arg
        if "\\href" in tab or "\\url" in tab:  # links can't be re-tokenized by
            tab = "{\\small\\setlength{\\tabcolsep}{3pt}%\n" + tab + "}"  # \resizebox
        else:
            tab = (
                "\\resizebox{\\ifdim\\width>\\linewidth\\linewidth\\else\\width\\fi}"
                "{!}{%\n" + tab + "%\n}"
            )
        return "\n\\begin{center}\n" + tab + "\n\\end{center}\n"

    def handle_data(self, data: str) -> None:
        if self._skip:
            return
        # &nbsp; (-> U+00A0 with convert_charrefs) becomes ~; escape the rest.
        self.out.append("~".join(esc_text(p) for p in data.split("\xa0")))


def _unwrap_single_item(tex: str) -> str:
    """A stem stored as a single-item <ol>/<ul> (OpenStax's os-raise-noindent
    wrapper) becomes an ugly indented one-item list; render it as plain text."""
    m: re.Match[str] | None = re.fullmatch(
        r"\\begin\{(enumerate|itemize)\}\s*\\item\s+(.*?)\s*"
        r"\\end\{\1\}",
        tex,
        re.S,
    )
    # unwrap only a genuine single item: no further \item (a nested list would
    # have one). Math environments like array/aligned in the item are fine.
    if m and "\\item" not in m.group(2):
        return m.group(2).strip()
    return tex


def _ex_html_to_latex(s: str) -> str:
    if not s:
        return ""
    p: _ExHTML = _ExHTML()
    p.feed(s)
    for env in reversed(p._stack):  # close any unbalanced lists
        p.out.append("\n\\end{%s}\n" % env)
    out: str = "".join(p.out)
    # drop empty lists (an <ol>/<ul> with no <li> -> "missing \item"); loop for
    # nested cases.
    for _ in range(4):
        new: str = re.sub(r"\\begin\{(itemize|enumerate)\}\s*\\end\{\1\}", "", out)
        if new == out:
            break
        out = new
    return re.sub(r"\n{3,}", "\n\n", out).strip()


def render_injected_exercise(nickname: str) -> str:
    path: str = os.path.join(EXERCISES, nickname + ".json")
    if not os.path.exists(path):
        warn_unknown("exercise-uncached")
        return _EX_ONLINE
    try:
        with open(path, encoding="utf-8") as f:
            ex: Any = json.load(f)
    except Exception:  # noqa: BLE001
        return _EX_ONLINE
    if ex.get("_missing"):
        return _EX_ONLINE
    parts: list[str] = []
    stim: str = _unwrap_single_item(_ex_html_to_latex(ex.get("stimulus_html", "")))
    if stim:
        parts.append(stim)
    for q in ex.get("questions", []) or []:
        qstim: str = _unwrap_single_item(_ex_html_to_latex(q.get("stimulus_html", "")))
        if qstim:
            parts.append(qstim)
        stem: str = _unwrap_single_item(_ex_html_to_latex(q.get("stem_html", "")))
        if stem:
            parts.append(stem)
        answers: list[Any] = q.get("answers") or []
        if answers:  # questions-only: options, unmarked,
            lines: list[str] = []  # lowercase a./b./c. like OpenStax
            for i, a in enumerate(answers):
                letter: str = _EX_LETTERS[i] if i < len(_EX_LETTERS) else str(i + 1)
                txt: str = _ex_html_to_latex(a.get("content_html", "")) or "~"
                lines.append(
                    "\\par\\noindent\\hspace*{1.5em}%s.\\quad %s" % (letter, txt)
                )
            parts.append("\n".join(lines))
    body: str = "\n\n".join(p for p in parts if p.strip())
    bare: bool = _IN_CALLOUT or _IN_EXERCISE  # a container already frames/numbers it
    if not body.strip():
        return "" if bare else _EX_ONLINE
    if bare:
        return body + "\n"
    return "\\begin{practice}\n%s\n\\end{practice}\n" % body


def block_element(node: _Element, labels: set[str], depth: int) -> str:
    tag: str | None = local(node.tag)
    if tag is None:
        return ""
    if tag == "para":
        nick: str | None = _os_embed_nickname(node)
        if nick:
            return render_injected_exercise(nick)
        body: str = flow(node, labels, depth)
        lab: str = opt_label(node) if node.get("id") in labels else ""
        return body + lab + "\n"
    if tag == "section":
        return render_section(node, labels, depth)
    if tag == "list":
        return render_list(node, labels, depth)
    if tag == "equation":
        return render_equation(node, labels)
    if tag == "figure":
        return render_figure(node, labels)
    if tag == "media":
        return render_media(node, labels)
    if tag == "example":
        return render_example(node, labels, depth)
    if tag == "exercise":
        return render_exercise(node, labels, depth)
    if tag == "note":
        return render_note(node, labels, depth)
    if tag == "table":
        return render_table(node, labels)
    if tag == "title":
        return ""  # handled by parent
    if tag == "rule":
        return render_rule(node, labels, depth)
    if tag in ("commentary",):
        return blocks(node, labels, depth)
    if tag == "quote":
        return r"\begin{quote}%s\end{quote}" % inline(node, labels)
    # unknown block: recurse
    warn_unknown("block:" + (tag or "?"))
    return blocks(node, labels, depth)


SECT = {1: "section", 2: "subsection", 3: "subsubsection", 4: "paragraph"}


def render_section(node: _Element, labels: set[str], depth: int) -> str:
    cls: str = node.get("class", "")
    title_el: _Element | None = get_title(node)
    title: str = inline(title_el, labels).strip() if title_el is not None else ""
    body: str = blocks(node, labels, depth + 1)
    lab: str = opt_label(node) if node.get("id") in labels else ""
    if cls == "key-concepts":
        return "\\begin{keyconcepts}\n%s\n\\end{keyconcepts}\n" % body
    if cls == "key-equations":
        return "\\begin{keyequations}\n%s\n\\end{keyequations}\n" % body
    # OpenStax restarts question numbering at each activity -> reset at each heading
    if cls in ("section-exercises", "review-exercises", "problem-solving"):
        head: str = title or ("Exercises" if "exerc" in cls else "Problems")
        lvl: str = SECT.get(min(depth + 1, 3), "subsection")
        return "\\setcounter{exercise}{0}\\%s*{%s}%s\n%s\n" % (lvl, head, lab, body)
    lvl = SECT.get(min(depth + 1, 4), "subsubsection")
    if title:
        return "\\setcounter{exercise}{0}\\%s{%s}%s\n%s\n" % (lvl, title, lab, body)
    return body


# A list item leads with a circled sub-part marker: now a RAW circled char (ⓐ ①),
# not \textcircled{...} (see the _CIRCLED_CHARS note above).
_CIRCLED_ITEM = re.compile(r"^" + _CIRCLED_CLASS)


def render_list(node: _Element, labels: set[str], depth: int) -> str:
    lt: str = node.get("list-type", "bulleted")
    item_els: list[_Element] = node.findall(C + "item")
    bodies: list[str] = [inline_block(it, labels, depth) for it in item_els]
    # OpenStax marks multi-part items with circled letters/digits (ⓐ ⓑ ⓒ ...),
    # which are ALREADY the visible marker. If every item leads with one, adding
    # the list's own number/bullet doubles it ("1. ⓐ", "\textbullet ⓐ"); render
    # the list markerless so the circled letter stands alone (matches the PDF).
    circled: bool = bool(bodies) and all(
        _CIRCLED_ITEM.match(b.lstrip()) for b in bodies if b.strip()
    )
    if _CELL_MODE:
        # lists are illegal in a tabular cell (LR mode): render inline
        out: list[str] = []
        for n, b in enumerate(bodies, 1):
            if circled:
                mark: str = ""
            elif lt == "enumerated":
                mark = "%d. " % n
            else:
                mark = r"\textbullet{} "
            out.append(mark + b.strip())
        return " ".join(out)
    lab: str = opt_label(node) if node.get("id") in labels else ""
    if circled:
        # empty optional label ([]) suppresses the bullet/number, keeping only
        # the circled marker already inside the item body.
        items: list[str] = ["  \\item[] %s" % b for b in bodies]
        return "\\begin{itemize}%s\n%s\n\\end{itemize}" % (lab, "\n".join(items))
    env: str = "enumerate" if lt == "enumerated" else "itemize"
    items = ["  \\item %s" % b for b in bodies]
    return "\\begin{%s}%s\n%s\n\\end{%s}" % (env, lab, "\n".join(items), env)


def inline_block(node: _Element, labels: set[str], depth: int) -> str:
    """An item/cell that may contain inline text and/or block children."""
    has_block: bool = any(
        local(c.tag)
        in ("para", "list", "equation", "figure", "note", "example", "table", "section")
        for c in node
    )
    if not has_block:
        return inline(node, labels)
    return blocks(node, labels, depth)


def render_equation(node: _Element, labels: set[str]) -> str:
    mnode: _Element | None = node.find(M + "math")
    if mnode is None:
        return ""
    body: str = math_to_latex(mnode, display=True).strip()
    if not body:
        return ""
    if _CELL_MODE:
        return "$%s$" % body.replace(_MNL, r"\,")
    if _MNL in body:  # explicit line breaks -> aligned display
        rows: list[str] = [_align_row(r) for r in body.split(_MNL) if r.strip()]
        body = "\\begin{aligned}\n%s\n\\end{aligned}" % " \\\\\n".join(rows)
    unnful: bool = node.get("class", "") == "unnumbered"
    eid: str | None = node.get("id")
    referenced: bool = eid in labels
    if unnful or not referenced:
        return "\\[\n%s\n\\]" % body
    return "\\begin{equation}\\label{%s}\n%s\n\\end{equation}" % (mklabel(eid), body)


def _imgname(raw: str | None) -> str:
    n: str = os.path.basename(raw or "")
    if n.lower().endswith(".svg"):
        n = n[:-4] + ".pdf"  # pdflatex can't embed SVG; the build converts it
    return n


def _defootnote(s: str) -> str:
    """Captions are fragile moving arguments; a \\footnote inside one breaks
    hyperref. Demote footnotes to parenthetical text (brace-matched)."""
    needle: str = "\\footnote{"
    out: list[str] = []
    i: int = 0
    while True:
        j: int = s.find(needle, i)
        if j < 0:
            out.append(s[i:])
            break
        out.append(s[i:j])
        k: int = j + len(needle)
        depth: int = 1
        buf: list[str] = []
        while k < len(s) and depth > 0:
            ch: str = s[k]
            if ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    break
            buf.append(ch)
            k += 1
        inner: str = "".join(buf).strip()
        out.append(" (%s)" % inner if inner else "")
        i = k + 1
    return "".join(out)


def render_figure(node: _Element, labels: set[str]) -> str:
    cap: _Element | None = node.find(C + "caption")
    media: _Element | None = node.find(C + "media")
    img: _Element | None = None
    if media is not None:
        img = media.find(C + "image")
    if img is None:
        img = node.find(".//" + C + "image")
    eid: str | None = node.get("id")
    src: str | None = img.get("src") if img is not None else None
    if src:
        src = _imgname(src)
    if _CELL_MODE:
        return "\\includegraphics[width=.4\\linewidth]{%s}" % src if src else ""
    # captions are a restricted (moving) argument: no line breaks / paragraphs
    capt: str = inline(cap, labels).strip() if cap is not None else ""
    capt = re.sub(r"\s+", " ", capt.replace(r"\NLBREAK", " ")).strip()
    capt = _defootnote(capt)
    capt = re.sub(
        _CIRCLED_CLASS, lambda m: "(%s)" % _CIRCLED_TO_PLAIN[m.group()], capt
    )
    lab: str = "\\label{%s}" % mklabel(eid) if eid else ""
    inc: str = "\\includegraphics[width=\\maxfigwidth]{%s}" % src if src else ""
    # non-floating (works inside theorem/example boxes, and is faithful to the
    # web book where images sit inline). \captionof keeps Figure numbering+refs.
    # An empty caption -> number only ("Figure N"), no dangling ": " delimiter.
    capline: str = (
        "\\captionof{figure}{%s}%s" % (capt, lab)
        if capt
        else "\\OSnumonlycaption{figure}%s" % lab
    )
    return "\\begin{calcfig}\n%s\\par\\smallskip\n%s\n\\end{calcfig}" % (inc, capline)


def render_media(node: _Element, labels: set[str]) -> str:
    img: _Element | None = node.find(C + "image")
    if img is None:
        return ""
    src: str = _imgname(img.get("src", ""))
    if not src:
        return ""
    if _CELL_MODE:
        return "\\includegraphics[width=.4\\linewidth]{%s}" % src
    return (
        "\\begin{center}\\includegraphics[width=.6\\textwidth]{%s}\\end{center}" % src
    )


def _problem_solution(
    node: _Element, labels: set[str], depth: int
) -> tuple[_Element | None, list[_Element], str]:
    prob: _Element | None = node.find(C + "problem")
    sols: list[_Element] = node.findall(C + "solution")
    parts: list[str] = []
    if prob is not None:
        ptitle: _Element | None = get_title(prob)
        if ptitle is not None:
            parts.append(r"\textbf{%s} " % inline(ptitle, labels).strip())
        parts.append(blocks(prob, labels, depth))
    return prob, sols, "\n".join(parts)


def render_example(node: _Element, labels: set[str], depth: int) -> str:
    title_el: _Element | None = get_title(node)
    title: str = inline(title_el, labels).strip() if title_el is not None else ""
    eid: str | None = node.get("id")
    lab: str = "\\label{%s}" % mklabel(eid) if eid else ""
    opt: str = "[{{%s}}]" % title if title else ""
    inner_ex: _Element | None = node.find(C + "exercise")
    out: list[str] = ["\\begin{example}%s%s" % (opt, lab)]
    if inner_ex is not None:
        prob, sols, ptext = _problem_solution(inner_ex, labels, depth)
        out.append(ptext)
        for s in sols:
            out.append(
                "\\begin{solution}\n%s\n\\end{solution}" % blocks(s, labels, depth)
            )
    else:
        # direct content (may include its own problem/solution or paragraphs)
        prob = node.find(C + "problem")
        if prob is not None:
            _, sols, ptext = _problem_solution(node, labels, depth)
            out.append(ptext)
            for s in sols:
                out.append(
                    "\\begin{solution}\n%s\n\\end{solution}" % blocks(s, labels, depth)
                )
        else:
            out.append(blocks(node, labels, depth))
    out.append("\\end{example}")
    return "\n".join(out)


def render_exercise(node: _Element, labels: set[str], depth: int) -> str:
    # checkpoint exercises are handled by render_note; this is a drill exercise.
    # An os-embed practice inside is rendered UNBOXED (the exercise number is the
    # structure) so 2-column runs aren't full of cramped boxes.
    global _IN_EXERCISE
    prob: _Element | None = node.find(C + "problem")
    sols: list[_Element] = node.findall(C + "solution")
    out: list[str] = ["\\begin{exercise}"]
    prev: bool = _IN_EXERCISE
    _IN_EXERCISE = True
    if prob is not None:
        ptitle: _Element | None = get_title(prob)
        if ptitle is not None:
            out.append(r"\textbf{%s} " % inline(ptitle, labels).strip())
        # strip: a leading blank line here becomes a \par, dropping the question
        # onto its own line below the number (OpenStax runs it in after "N.").
        body: str = blocks(prob, labels, depth).strip()
        # Many OpenStax problems bake the list number into the text ("2. What is…").
        # \begin{exercise} already auto-numbers, so a leading "N."/"N)" would double
        # it ("2. 2. …"); drop that redundant marker. (Math-first problems render as
        # "$…$", not a bare "N.", so they are untouched.)
        body = re.sub(r"^\s*\d+[.)]\s+", "", body)
        out.append(body)
    for s in sols:
        out.append("\\begin{answer}\n%s\n\\end{answer}" % blocks(s, labels, depth))
    _IN_EXERCISE = prev
    out.append("\\end{exercise}")
    return "\n".join(out)


NOTE_ENV = {
    "theorem": "theorem",
    "definition": "definition",
    "rule": "mathrule",
}


def render_note(node: _Element, labels: set[str], depth: int) -> str:
    global _IN_CALLOUT
    cls: str = node.get("class", "")
    label_el: _Element | None = node.find(C + "label")
    title_el: _Element | None = get_title(node)
    title: str = inline(title_el, labels).strip() if title_el is not None else ""
    if not title and label_el is not None and label_el.text:
        title = esc_text(label_el.text.strip())
    eid: str | None = node.get("id")
    lab: str = "\\label{%s}" % mklabel(eid) if eid else ""

    if cls == "project":
        opt: str = "[{{%s}}]" % title if title and title.lower() != "project" else ""
        return "\\begin{project}%s%s\n%s\n\\end{project}" % (
            opt,
            lab,
            blocks(node, labels, depth),
        )
    # classless notes are typed by their title: "Definition" / "Rule: ..."
    if not cls:
        if title == "Definition":
            return "\\begin{definition}%s\n%s\n\\end{definition}" % (
                lab,
                blocks(node, labels, depth),
            )
        if title.startswith("Rule"):
            return "\\begin{mathrule}[{{%s}}]%s\n%s\n\\end{mathrule}" % (
                title,
                lab,
                blocks(node, labels, depth),
            )
        if title and not title.lower().startswith("problem-solving"):
            # a classless titled note is a procedural "How To"/aside callout:
            # gray box with a teal title bar (matches the OpenStax PDF).
            prev: bool = _IN_CALLOUT
            _IN_CALLOUT = True  # inner practice needs no box
            body: str = blocks(node, labels, depth)
            _IN_CALLOUT = prev
            return "\\begin{oscallout}{%s}%s\n%s\n\\end{oscallout}" % (title, lab, body)

    # OpenStax lesson callouts -> light-gray boxes with a teal heading
    _CALLOUT: dict[str, str] = {
        "try": "tryit",
        "self-check": "selfcheck",
        "mini-lesson-question": "minilesson",
        "link-to-learning": "linklearning",
    }
    if cls.strip() in _CALLOUT:
        env: str = _CALLOUT[cls.strip()]
        prev = _IN_CALLOUT
        _IN_CALLOUT = True  # inner practice needs no box
        body = blocks(node, labels, depth)
        _IN_CALLOUT = prev
        if title:  # lead with the specific title
            body = "\\textbf{%s}\\par\n%s" % (title, body)
        return "\\begin{%s}%s\n%s\n\\end{%s}" % (env, lab, body, env)

    if cls == "checkpoint":
        ex: _Element | None = node.find(C + "exercise")
        out: list[str] = ["\\begin{checkpoint}%s" % lab]
        if ex is not None:
            prob: _Element | None = ex.find(C + "problem")
            if prob is not None:
                out.append(blocks(prob, labels, depth))
            for s in ex.findall(C + "solution"):
                out.append(
                    "\\begin{solution}\n%s\n\\end{solution}" % blocks(s, labels, depth)
                )
        else:
            out.append(blocks(node, labels, depth))
        out.append("\\end{checkpoint}")
        return "\n".join(out)

    if cls == "theorem":
        opt = "[{{%s}}]" % title if title else ""
        body = blocks(node, labels, depth)
        return "\\begin{theorem}%s%s\n%s\n\\end{theorem}" % (opt, lab, body)
    if cls == "definition":
        opt = "[{{%s}}]" % title if title else ""
        body = blocks(node, labels, depth)
        return "\\begin{definition}%s%s\n%s\n\\end{definition}" % (opt, lab, body)
    if cls and cls.startswith("media"):
        return "\\begin{medianote}\n%s\n\\end{medianote}" % blocks(node, labels, depth)
    if cls == "rule":
        opt = "[{{%s}}]" % title if title else ""
        return "\\begin{mathrule}%s\n%s\n\\end{mathrule}" % (
            opt,
            blocks(node, labels, depth),
        )
    if "problem-solving" in cls or title.lower().startswith("problem-solving"):
        return "\\begin{strategy}\n%s\n\\end{strategy}" % blocks(node, labels, depth)
    # generic note
    body = blocks(node, labels, depth)
    if title:
        return "\\begin{calcnote}[{{%s}}]%s\n%s\n\\end{calcnote}" % (title, lab, body)
    return "\\begin{calcnote}%s\n%s\n\\end{calcnote}" % (lab, body)


def render_rule(node: _Element, labels: set[str], depth: int) -> str:
    title_el: _Element | None = node.find(C + "title")
    title: str = inline(title_el, labels).strip() if title_el is not None else "Rule"
    stmt: _Element | None = node.find(C + "statement")
    body: str = (
        blocks(stmt, labels, depth) if stmt is not None else blocks(node, labels, depth)
    )
    return "\\begin{mathrule}[{{%s}}]\n%s\n\\end{mathrule}" % (title, body)


def render_table(node: _Element, labels: set[str]) -> str:
    tgroup: _Element | None = node.find(C + "tgroup")
    if tgroup is None:
        return ""
    declared: int = int(tgroup.get("cols", "1"))
    # actual max cells per row (CALS `cols` attr is often wrong / spans exist)
    observed: int = 0
    for row in tgroup.iter(C + "row"):
        observed = max(observed, len(row.findall(C + "entry")))
    ncols: int = max(declared, observed, 1)
    colspecs: list[_Element] = tgroup.findall(C + "colspec")
    aligns: list[str] = []
    for cs in colspecs:
        aligns.append(
            {"left": "l", "right": "r", "center": "c"}.get(cs.get("align"), "l")
        )
    while len(aligns) < ncols:
        aligns.append("l")
    colfmt: str = "".join(aligns[:ncols])

    def _inline_cell(c: str) -> str:
        # belt-and-suspenders: inline any stray display math, neutralize spacing
        # macros and blank-line paragraph breaks (all illegal in a tabular cell).
        c = re.sub(
            r"\\\[\s*(.*?)\s*\\\]",
            lambda m: "$" + m.group(1).strip() + "$",
            c,
            flags=re.DOTALL,
        )
        c = re.sub(r"\\(par|smallskip|medskip|bigskip)\b", " ", c)
        c = re.sub(r"\s*\n\s*\n\s*", " ", c)
        return c.strip()

    def render_rows(parent: _Element, header: bool = False) -> str:
        global _CELL_MODE
        lines: list[str] = []
        for row in parent.findall(C + "row"):
            prev: bool = _CELL_MODE
            _CELL_MODE = True
            cells: list[str] = [
                _inline_cell(inline_block(ent, labels, 0).strip())
                for ent in row.findall(C + "entry")
            ]
            _CELL_MODE = prev
            while len(cells) < ncols:  # pad short rows to ncols
                cells.append("")
            cells = cells[:ncols]  # never exceed colspec
            if header:  # teal row, white bold text (leave any
                cells = ["{\\color{white}\\bfseries %s}" % c for c in cells]
                lines.append("\\rowcolor{OScolor}" + " & ".join(cells) + r" \\")
            else:
                lines.append(" & ".join(cells) + r" \\")
        return "\n".join(lines)

    thead: _Element | None = tgroup.find(C + "thead")
    tbody: _Element | None = tgroup.find(C + "tbody")
    in_cell: bool = (
        _CELL_MODE  # a \begin{center} wrapper is illegal inside a table cell
    )
    if not in_cell:
        # OpenStax grid: teal rules, teal header row (white bold), bold row labels.
        aa: list[str] = aligns[:ncols]
        grid: str = "|>{\\bfseries}" + aa[0] + "|" + "".join(a + "|" for a in aa[1:])
        tab: list[str] = [
            "\\arrayrulecolor{OScolor}",
            "\\begin{tabular}{%s}" % grid,
            "\\hline",
        ]
        head_flag: bool = True
    else:  # nested table in a cell: keep it plain
        tab = ["\\begin{tabular}{%s}" % colfmt, "\\hline"]
        head_flag = False
    if thead is not None:
        tab.append(render_rows(thead, header=head_flag))
        tab.append("\\hline")
    if tbody is not None:
        tab.append(render_rows(tbody))
    tab.append("\\hline")
    tab.append("\\end{tabular}")
    tabular: str = "\n".join(tab)
    # Fit wide tables to the text width so columns are never clipped off the page
    # (tables inside a cell are left alone). Two methods:
    #  * \resizebox scales to \linewidth (only when wider, else natural size). But
    #    it reads its body as a macro ARGUMENT, and \href/\url can't be
    #    re-tokenized there (hyperref needs verbatim catcodes) -> fatal. So use it
    #    only for link-free tables. HTML/EPUB: preprocess.py strips this wrapper.
    #  * tables containing \href/\url instead get a smaller font + tighter columns
    #    (href-safe and pandoc-safe); such link-list tables are rare and were
    #    already overflowing, so this is no regression.
    if not in_cell:
        tabular = re.sub(r"\n[ \t]*\n", "\n", tabular)  # no blank line in a scanned arg
        if "\\href" in tabular or "\\url" in tabular:
            tabular = "{\\small\\setlength{\\tabcolsep}{3pt}%\n" + tabular + "}"
        else:
            tabular = (
                "\\resizebox{\\ifdim\\width>\\linewidth\\linewidth"
                "\\else\\width\\fi}{!}{%\n" + tabular + "%\n}"
            )
    out: list[str] = ([] if in_cell else ["\\begin{center}"]) + [tabular]
    # number + label referenced tables so \cref resolves to "Table N.M"
    # (the caption sits OUTSIDE the \resizebox so it is not scaled).
    eid: str | None = node.get("id")
    if not in_cell and eid in labels:
        title_el: _Element | None = node.find(C + "title")
        cap: str = ""
        if title_el is not None:
            cap = re.sub(
                r"\s+", " ", inline(title_el, labels).replace("\\NLBREAK", " ")
            ).strip()
            cap = _defootnote(cap)
        capcmd: str = (
            "\\captionof{table}{%s}" % cap if cap else "\\OSnumonlycaption{table}"
        )
        out.append("%s\\label{%s}" % (capcmd, mklabel(eid)))
    if not in_cell:
        out.append("\\end{center}")
    return "\n".join(out)


# --------------------------------------------------------------------------
# label discovery: which ids are referenced (so we only \label those)
# --------------------------------------------------------------------------
def collect_targets(tree: _ElementTree) -> set[str]:
    targets: set[str] = set()
    for ln in tree.iter(C + "link"):
        t: str | None = ln.get("target-id")
        if t:
            targets.add(t)
    return targets


# --------------------------------------------------------------------------
# module conversion
# --------------------------------------------------------------------------
def parse(path: str) -> _ElementTree:
    p: etree.XMLParser = etree.XMLParser(
        huge_tree=True, recover=True, resolve_entities=False
    )
    return etree.parse(path, p)


def convert_module(mid: str, standalone: bool = True) -> str:
    global _CURMOD, _LOCAL_IDS
    path: str = os.path.join(MODULES, mid, "index.cnxml")
    tree: _ElementTree = parse(path)
    root: _Element = tree.getroot()
    _CURMOD = mid
    _LOCAL_IDS = {el.get("id") for el in root.iter() if el.get("id")}
    labels: set[str] = collect_targets(tree)
    labels |= _ALL_TARGETS  # also label cross-module reference targets
    # figures/equations/sections always get ids referenced by figure-number naming;
    # but we only \label referenced ones -> labels set. Add all ids that match
    # CNX_Calc_Figure (they are referenced cross-module sometimes).
    for el in root.iter():
        i: str | None = el.get("id") if hasattr(el, "get") else None
        if i and i.startswith("CNX_Calc_"):
            labels.add(i)

    title_el: _Element | None = root.find(C + "title")
    title: str = inline(title_el, labels).strip() if title_el is not None else mid

    # learning objectives from abstract
    obj_tex: str = ""
    meta: _Element | None = root.find(C + "metadata")
    if meta is not None:
        ab: _Element | None = meta.find(MD + "abstract")
        if ab is not None:
            lst: _Element | None = ab.find(C + "list")
            if lst is not None:
                items: str = "\n".join(
                    "  \\item %s" % inline_block(it, labels, 0)
                    for it in lst.findall(C + "item")
                )
                obj_tex = (
                    "\\begin{objectives}\n\\begin{itemize}\n%s\n"
                    "\\end{itemize}\n\\end{objectives}\n" % items
                )
            elif (ab.text or "").strip():
                obj_tex = "\\begin{objectives}\n%s\n\\end{objectives}\n" % esc_text(
                    ab.text.strip()
                )

    content: _Element | None = root.find(C + "content")
    body: str = blocks(content, labels, depth=1) if content is not None else ""

    # glossary
    gloss: _Element | None = root.find(C + "glossary")
    gloss_tex: str = ""
    if gloss is not None:
        defs: list[_Element] = gloss.findall(C + "definition")
        if defs:
            entries: list[str] = []
            for d in defs:
                term: _Element | None = d.find(C + "term")
                meaning: _Element | None = d.find(C + "meaning")
                tname: str = inline(term, labels).strip() if term is not None else ""
                mtext: str = blocks(meaning, labels, 2) if meaning is not None else ""
                entries.append("\\item[%s] %s" % (tname, mtext))
            gloss_tex = (
                "\\subsection*{Key Terms}\n\\begin{description}\n%s\n"
                "\\end{description}\n" % "\n".join(entries)
            )

    sec_cmd: str = MODULE_CMD
    body_all: str = "\n\n".join(x for x in [obj_tex, body, gloss_tex] if x.strip())
    body_all = cleanup_latex(body_all)
    body_all = wrap_latex(body_all)
    section_block: str = "\\setcounter{exercise}{0}\\%s{%s}\\label{mod:%s}\n\n%s\n" % (
        sec_cmd,
        title,
        mid,
        body_all,
    )

    if standalone:
        doc: str = (
            "%% Auto-generated from modules/%s/index.cnxml by tools/cnxml2tex.\n"
            "%% One-time generator: safe to hand-edit after generation.\n"
            "\\documentclass[%s]{subfiles}\n"
            "\\begin{document}\n%s\\end{document}\n"
            % (mid, SUBFILES_MAIN, section_block)
        )
        return doc
    return section_block


def write_module(mid: str) -> str:
    os.makedirs(OUT_SECTIONS, exist_ok=True)
    tex: str = convert_module(mid, standalone=True)
    outp: str = os.path.join(OUT_SECTIONS, "%s.tex" % mid)
    with open(outp, "w") as f:
        f.write(tex)
    return outp


# --------------------------------------------------------------------------
# collection / volume assembly (Phase 2)
# --------------------------------------------------------------------------
def convert_collection(slug: str) -> tuple[str, list[str]]:
    cpath: str = os.path.join(COLLECTIONS, "%s.collection.xml" % slug)
    tree: _ElementTree = parse(cpath)
    root: _Element = tree.getroot()
    title: str | None = None
    for t in root.iter(MD + "title"):
        title = t.text
        break
    content: _Element | None = root.find(COL + "content")
    if content is None:
        content = root.find("{*}content")

    os.makedirs(OUT_SECTIONS, exist_ok=True)
    module_ids: list[str] = []

    # collect all module ids referenced by this collection, then build a global
    # id -> module map so cross-module <link>s resolve to the right label.
    def collect_module_ids(elem: _Element, acc: list[str]) -> None:
        for ch in elem:
            lt: str | None = local(ch.tag)
            if lt == "subcollection":
                cc: _Element | None = ch.find(COL + "content")
                if cc is not None:
                    collect_module_ids(cc, acc)
            elif lt == "module" and ch.get("document"):
                acc.append(cast(str, ch.get("document")))

    all_ids: list[str] = []
    collect_module_ids(content, all_ids)
    global _ID2MOD, _ALL_TARGETS
    _ID2MOD = {}
    _ALL_TARGETS = set()
    for mid in all_ids:
        mp: str = os.path.join(MODULES, mid, "index.cnxml")
        if not os.path.exists(mp):
            continue
        root = parse(mp).getroot()
        for ln in root.iter(C + "link"):
            t = ln.get("target-id")
            if t:
                _ALL_TARGETS.add(t)
        for el in root.iter():
            i: str | None = el.get("id") if hasattr(el, "get") else None
            if i and i not in _ID2MOD:  # first definer wins
                _ID2MOD[i] = mid

    # OpenStax numbers only the subject units (1..N). "Getting Started" and
    # "Supporting All Learners" are unnumbered front matter; "Research in
    # Practice" and "Appendix" are unnumbered back matter. Route the three
    # groups separately so the math units number 1..9 (matching the official).
    front_lines: list[str] = []
    main_lines: list[str] = []
    back_lines: list[str] = []
    FRONT_UNITS: set[str] = {"getting started", "supporting all learners"}
    BACK_UNITS: set[str] = {"research in practice", "appendix"}

    def handle(
        elem: Iterable[_Element], out: list[str], mode: str, level: int = 0
    ) -> None:
        for ch in elem:
            lt: str | None = local(ch.tag)
            if lt == "subcollection":
                md: _Element | None = ch.find(MD + "title")
                ctitle: str = esc_text((md.text if md is not None else None) or "")
                cmd: str = subcol_cmd(level)
                if level == 0 and mode == "front":
                    # \chapter* does not advance the chapter counter, so the
                    # first main unit becomes chapter 1 (descendants unnumbered
                    # via secnumdepth set around the front group in build_master).
                    out.append("\\chapter*{%s}" % ctitle)
                    out.append("\\addcontentsline{toc}{chapter}{%s}" % ctitle)
                elif (
                    level == 1
                    and mode == "main"
                    and ctitle.strip().lower().endswith("overview and readiness")
                ):
                    # unnumbered unit intro: \section* keeps the section counter
                    # so the lessons that follow number from N.1 (matches official).
                    out.append("\\section*{%s}" % ctitle)
                    out.append("\\addcontentsline{toc}{section}{%s}" % ctitle)
                else:
                    out.append("\\%s{%s}" % (cmd, ctitle))
                cc: _Element | None = ch.find(COL + "content")
                if cc is not None:
                    handle(cc, out, mode, level + 1)
            elif lt == "module":
                doc: str | None = ch.get("document")
                if doc:
                    module_ids.append(doc)
                    out.append("\\subfile{sections/%s}" % doc)

    for ch in content:
        lt: str | None = local(ch.tag)
        if lt == "subcollection":
            md: _Element | None = ch.find(MD + "title")
            key: str = ((md.text if md is not None else "") or "").strip().lower()
            mode: str = (
                "front"
                if key in FRONT_UNITS
                else "back"
                if key in BACK_UNITS
                else "main"
            )
            out: list[str] = {"front": front_lines, "back": back_lines}.get(
                mode, main_lines
            )
            handle([ch], out, mode, level=0)
        elif lt == "module":
            doc: str | None = ch.get("document")
            if doc:
                module_ids.append(doc)
                main_lines.append("\\subfile{sections/%s}" % doc)

    # write each module as a non-standalone include (wrapped so it works under
    # both the master and standalone compile via subfiles)
    for mid in module_ids:
        write_module(mid)

    master: str = build_master(slug, title or slug, front_lines, main_lines, back_lines)
    mpath: str = os.path.join(ROOT, "latex", "%s.tex" % slug)
    with open(mpath, "w") as f:
        f.write(master)
    return mpath, module_ids


def build_master(
    slug: str,
    title: str,
    front_lines: list[str],
    main_lines: list[str],
    back_lines: list[str],
) -> str:
    front: str = "\n".join(front_lines)
    main: str = "\n".join(main_lines)
    back: str = "\n".join(back_lines)
    return (
        "%% Auto-generated volume master for %s.\n"
        "\\documentclass[letter]{osbook}\n"
        "\\usepackage{osbook-envs}\n"
        "\\usepackage{osbook-defer}\n"
        "\\usepackage{subfiles}\n"
        "\\graphicspath{{../media/}{media/}{../exercises/media/}"
        "{../exercises/media-derived/}{../}}\n"
        "\\setOSbooktitle{%s}\n"
        "\\setOSbooksubtitle{LaTeX edition}\n"
        "\\begin{document}\n"
        "\\OSfrontmatter\n"
        "%% front-matter units: unnumbered headings, kept in the TOC\n"
        "\\setcounter{secnumdepth}{-10}\n"
        "%s\n"
        "\\setcounter{secnumdepth}{2}\n"
        "%% numbered subject units (1..N)\n"
        "%s\n"
        "\\backmatter\n"
        "%% back-matter units: unnumbered (\\backmatter)\n"
        "%s\n"
        "\\printanswerkey\n"
        "\\end{document}\n" % (slug, esc_text(title), front, main, back)
    )


# --------------------------------------------------------------------------
def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__)
        return 1
    cmd: str = sys.argv[1]
    if cmd == "module":
        for mid in sys.argv[2:]:
            p: str = write_module(mid)
            print("wrote", p)
    elif cmd == "collection":
        for slug in sys.argv[2:]:
            p, mids = convert_collection(slug)
            print("wrote", p, "with", len(mids), "modules")
    elif cmd == "all":
        for slug in COLLECTION_SLUGS:
            p, mids = convert_collection(slug)
            print("wrote", p, "with", len(mids), "modules")
    else:
        print("unknown command", cmd)
        return 1
    if UNKNOWN:
        sys.stderr.write("Unknown/fallback elements encountered:\n")
        for k, v in sorted(UNKNOWN.items(), key=lambda kv: -kv[1]):
            sys.stderr.write("  %6d  %s\n" % (v, k))
    return 0


if __name__ == "__main__":
    sys.exit(main())
