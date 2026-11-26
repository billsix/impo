"""Golden MathML -> LaTeX conversions.

Small in-memory Presentation-MathML fixtures fed through math_to_latex(), pinning
the recursive mml() walker for the common node types. Hermetic: fixtures are
inline strings, so no modules/ tree is needed (safe as a build gate).
"""

from __future__ import annotations

import convert as c
from lxml import etree  # ty: ignore[import-not-found]

_MML: str = "http://www.w3.org/1998/Math/MathML"


def _latex(fragment: str) -> str:
    """Wrap a MathML fragment in <math> and convert to inline LaTeX."""
    node: etree._Element = etree.fromstring(
        '<math xmlns="%s">%s</math>' % (_MML, fragment)
    )
    return c.math_to_latex(node)


def test_fraction() -> None:
    assert _latex("<mfrac><mn>1</mn><mn>2</mn></mfrac>") == r"\frac{1}{2}"


def test_superscript() -> None:
    assert _latex("<msup><mi>x</mi><mn>2</mn></msup>") == "x^{2}"


def test_square_root() -> None:
    assert _latex("<msqrt><mi>x</mi></msqrt>") == r"\sqrt{x}"


def test_subscript() -> None:
    assert _latex("<msub><mi>a</mi><mn>1</mn></msub>") == "a_{1}"


def test_row_concatenation() -> None:
    # <mrow> of a=b concatenates its children
    out: str = _latex("<mrow><mi>a</mi><mo>=</mo><mi>b</mi></mrow>")
    assert "a" in out and "b" in out and "=" in out


def test_nonstretchy_paren_before_piecewise_stays_plain() -> None:
    # f(x) with stretchy="false" parens, sitting before a piecewise {...} in the
    # same row: the ( must stay literal, NOT become a giant \left( stretched over
    # the whole cases table (the calculus f(x)={...} bug).
    out: str = _latex(
        '<mrow><mi>f</mi><mo stretchy="false">(</mo><mi>x</mi>'
        '<mo stretchy="false">)</mo><mo>=</mo>'
        "<mrow><mo>{</mo><mtable><mtr><mtd><mn>1</mn></mtd></mtr>"
        "<mtr><mtd><mn>2</mn></mtd></mtr></mtable></mrow></mrow>"
    )
    assert r"\left(" not in out               # no stretched f-paren
    assert "f(x)" in out.replace(" ", "")
    assert r"\left\{" in out                   # piecewise brace still stretchy


def test_content_mathml_fraction_of_a_sum() -> None:
    fragment: str = (
        "<apply><eq/><apply><divide/><apply><plus/><cn>6.8</cn><cn>7.2</cn></apply><cn>2</cn></apply>"
        "<cn>7</cn></apply>"
    )
    assert _latex(fragment) == r"\frac{6.8 + 7.2}{2} = 7"


def test_content_mathml_conjugate_is_an_overline() -> None:
    assert _latex("<apply><conjugate/><ci>x</ci></apply>") == r"\overline{x}"


def test_content_mathml_sum_of_a_power_of_a_named_quantity() -> None:
    fragment: str = "<apply><sum/><apply><power/><ci>residual</ci><cn>2</cn></apply></apply>"
    assert _latex(fragment) == r"\sum {\mathrm{residual}}^{2}"


def test_content_mathml_groups_a_sum_inside_a_product() -> None:
    fragment: str = "<apply><times/><cn>2</cn><apply><minus/><ci>a</ci><ci>b</ci></apply></apply>"
    assert _latex(fragment) == r"2 \cdot \left(a - b\right)"


def test_content_mathml_relation_in_the_older_reln_form() -> None:
    assert _latex("<reln><lt/><ci>p</ci><cn>0.05</cn></reln>") == "p < 0.05"


def test_content_mathml_bare_identifier_is_kept() -> None:
    # Psychology 2e sets a scrambled word this way; it used to vanish from the book.
    assert _latex("<ci>AETPL</ci>") == r"\mathrm{AETPL}"


def test_content_mathml_infinity() -> None:
    assert _latex("<reln><lt/><ci>x</ci><infinity/></reln>") == r"x < \infty"
