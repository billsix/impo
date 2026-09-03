"""Golden MathML -> LaTeX conversions.

Small in-memory Presentation-MathML fixtures fed through math_to_latex(), pinning
the recursive mml() walker for the common node types. Hermetic: fixtures are
inline strings, so no modules/ tree is needed (safe as a build gate).
"""

from __future__ import annotations

import convert as c
from lxml import etree  # ty: ignore[unresolved-import]

_MML = "http://www.w3.org/1998/Math/MathML"


def _latex(fragment: str) -> str:
    """Wrap a MathML fragment in <math> and convert to inline LaTeX."""
    node = etree.fromstring('<math xmlns="%s">%s</math>' % (_MML, fragment))
    return c.math_to_latex(node)


def test_fraction():
    assert _latex("<mfrac><mn>1</mn><mn>2</mn></mfrac>") == r"\frac{1}{2}"


def test_superscript():
    assert _latex("<msup><mi>x</mi><mn>2</mn></msup>") == "x^{2}"


def test_square_root():
    assert _latex("<msqrt><mi>x</mi></msqrt>") == r"\sqrt{x}"


def test_subscript():
    assert _latex("<msub><mi>a</mi><mn>1</mn></msub>") == "a_{1}"


def test_row_concatenation():
    # <mrow> of a=b concatenates its children
    out = _latex("<mrow><mi>a</mi><mo>=</mo><mi>b</mi></mrow>")
    assert "a" in out and "b" in out and "=" in out


def test_nonstretchy_paren_before_piecewise_stays_plain():
    # f(x) with stretchy="false" parens, sitting before a piecewise {...} in the
    # same row: the ( must stay literal, NOT become a giant \left( stretched over
    # the whole cases table (the calculus f(x)={...} bug).
    out = _latex(
        '<mrow><mi>f</mi><mo stretchy="false">(</mo><mi>x</mi>'
        '<mo stretchy="false">)</mo><mo>=</mo>'
        "<mrow><mo>{</mo><mtable><mtr><mtd><mn>1</mn></mtd></mtr>"
        "<mtr><mtd><mn>2</mn></mtd></mtr></mtable></mrow></mrow>"
    )
    assert r"\left(" not in out               # no stretched f-paren
    assert "f(x)" in out.replace(" ", "")
    assert r"\left\{" in out                   # piecewise brace still stretchy
