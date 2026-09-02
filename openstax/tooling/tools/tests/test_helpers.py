"""Unit tests for the converter's pure string/label helpers.

These pin the exact behavior we iterated on this week (continued-equality
alignment, list-vs-chain detection, delimiter mapping, LaTeX escaping, label
generation) and the HTML-only preprocessing. They are fast, offline, and need no
CNXML fixtures on disk -- so they are safe to run as an image-build gate.
"""

from __future__ import annotations

import convert as c
import preprocess as p


# -- depth-0 scanning: only top-level relations/separators count ------------
def test_depth0_positions_flat_chain():
    assert c._depth0_positions("a=b=c", "=") == [1, 3]


def test_depth0_positions_ignores_nested():
    # the '=' inside (a=b) is depth-1 and must not be reported
    assert c._depth0_positions("(a=b)=c", "=") == [5]


def test_has_depth0_separator_list_is_true():
    assert c._has_depth0_separator("x=1, y=2") is True


def test_has_depth0_separator_chain_is_false():
    assert c._has_depth0_separator("a=b=c") is False


# -- continued-equality promotion ------------------------------------------
def test_align_row_tabs_first_relation_only():
    assert c._align_row("a=b=c") == "a &= b=c"


def test_aligned_body_promotes_long_chain():
    assert c._aligned_body("a=b=c=d") == "a &= b \\\\\n&= c \\\\\n&= d"


def test_aligned_body_leaves_short_chain_inline():
    # fewer than three top-level '=' -> stay inline (None)
    assert c._aligned_body("a=b") is None


def test_aligned_body_rejects_list_of_equations():
    # comma-separated distinct equations are a LIST, not a chain -> not promoted
    assert c._aligned_body("x=1, y=2, z=3") is None


def test_aligned_body_skips_structured_environments():
    assert c._aligned_body(r"\begin{array}{l} a=b=c=d \end{array}") is None


# -- delimiter / measurement / script helpers ------------------------------
def test_left_delim_brace():
    assert c._left_delim("{") == r"\{"


def test_left_delim_empty_is_invisible():
    assert c._left_delim("") == "."


def test_delim_brace():
    assert c._delim("{") == r"\{"


def test_emval_parses_em():
    assert c._emval("1.5em") == 1.5


def test_emval_default_on_garbage():
    assert c._emval("junk") == 0.2


def test_empty_script_detects_blank_group():
    assert c._empty_script("{}") is True
    assert c._empty_script("x") is False


# -- image name / escaping / labels ----------------------------------------
def test_imgname_svg_becomes_pdf():
    assert c._imgname("a/b/pic.svg") == "pic.pdf"


def test_esc_text_escapes_specials():
    assert c.esc_text("a & b_c %") == r"a \& b\_c \%"


def test_subcol_cmd_top_level_is_chapter():
    assert c.subcol_cmd(0) == "chapter"


def test_mklabel_sanitizes_and_scopes():
    assert c.mklabel("foo:bar", "m123") == "xm123-foo-bar"


# -- HTML/EPUB-only preprocessing ------------------------------------------
def test_strip_cmd_arg_removes_rowcolor():
    assert p.strip_cmd_arg(r"\rowcolor{OScolor}A & B", "rowcolor") == "A & B"


def test_strip_resizebox_keeps_content():
    assert p.strip_resizebox(r"\resizebox{2cm}{!}{TABLE}") == "TABLE"


def test_fix_content_breaks_out_inline_math():
    assert p.fix_content(r"$-$") == r"}-\text{"
