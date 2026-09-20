"""Unit tests for the converter's pure string/label helpers.

These pin the exact behavior we iterated on this week (continued-equality
alignment, list-vs-chain detection, delimiter mapping, LaTeX escaping, label
generation) and the HTML-only preprocessing. They are fast, offline, and need no
CNXML fixtures on disk -- so they are safe to run as an image-build gate.
"""

from __future__ import annotations

import convert as c
import preprocess as p
from lxml import etree  # ty: ignore[unresolved-import]


# -- depth-0 scanning: only top-level relations/separators count ------------
def test_depth0_positions_flat_chain() -> None:
    assert c._depth0_positions("a=b=c", "=") == [1, 3]


def test_depth0_positions_ignores_nested() -> None:
    # the '=' inside (a=b) is depth-1 and must not be reported
    assert c._depth0_positions("(a=b)=c", "=") == [5]


def test_has_depth0_separator_list_is_true() -> None:
    assert c._has_depth0_separator("x=1, y=2") is True


def test_has_depth0_separator_chain_is_false() -> None:
    assert c._has_depth0_separator("a=b=c") is False


# -- continued-equality promotion ------------------------------------------
def test_align_row_tabs_first_relation_only() -> None:
    assert c._align_row("a=b=c") == "a &= b=c"


def test_aligned_body_promotes_long_chain() -> None:
    assert c._aligned_body("a=b=c=d") == "a &= b \\\\\n&= c \\\\\n&= d"


def test_aligned_body_leaves_short_chain_inline() -> None:
    # fewer than three top-level '=' -> stay inline (None)
    assert c._aligned_body("a=b") is None


def test_aligned_body_rejects_list_of_equations() -> None:
    # comma-separated distinct equations are a LIST, not a chain -> not promoted
    assert c._aligned_body("x=1, y=2, z=3") is None


def test_aligned_body_skips_structured_environments() -> None:
    assert c._aligned_body(r"\begin{array}{l} a=b=c=d \end{array}") is None


# -- delimiter / measurement / script helpers ------------------------------
def test_left_delim_brace() -> None:
    assert c._left_delim("{") == r"\{"


def test_left_delim_empty_is_invisible() -> None:
    assert c._left_delim("") == "."


def test_delim_brace() -> None:
    assert c._delim("{") == r"\{"


def test_emval_parses_em() -> None:
    assert c._emval("1.5em") == 1.5


def test_emval_default_on_garbage() -> None:
    assert c._emval("junk") == 0.2


def test_empty_script_detects_blank_group() -> None:
    assert c._empty_script("{}") is True
    assert c._empty_script("x") is False


# -- image name / escaping / labels ----------------------------------------
def test_imgname_svg_becomes_pdf() -> None:
    assert c._imgname("a/b/pic.svg") == "pic.pdf"


def test_esc_text_escapes_specials() -> None:
    assert c.esc_text("a & b_c %") == r"a \& b\_c \%"


def test_subcol_cmd_top_level_is_chapter() -> None:
    assert c.subcol_cmd(0) == "chapter"


def test_mklabel_sanitizes_and_scopes() -> None:
    assert c.mklabel("foo:bar", "m123") == "xm123-foo-bar"


# -- HTML/EPUB-only preprocessing ------------------------------------------
def test_strip_cmd_arg_removes_rowcolor() -> None:
    assert p.strip_cmd_arg(r"\rowcolor{OScolor}A & B", "rowcolor") == "A & B"


def test_strip_resizebox_keeps_content() -> None:
    assert p.strip_resizebox(r"\resizebox{2cm}{!}{TABLE}") == "TABLE"


def test_fix_content_breaks_out_inline_math() -> None:
    assert p.fix_content(r"$-$") == r"}-\text{"


# -- os-embed exercise link: BOTH URL schemes resolve to a cache key --------
def _osembed_para(url: str) -> etree._Element:
    ns: str = c.C[1:-1]  # strip the {..} Clark braces back to a bare namespace URI
    return etree.fromstring(
        '<para xmlns="%s"><link class="os-embed" url="%s"/></para>' % (ns, url)
    )


def test_os_embed_nickname_scheme() -> None:
    # #exercise/<nickname> (most books) -> the nickname is the cache key
    node: etree._Element = _osembed_para("#exercise/anat-ch01-ex003")
    assert c._os_embed_nickname(node) == "anat-ch01-ex003"


def test_os_embed_tag_scheme() -> None:
    # #ost/api/ex/<id> (physics, biology) -> the id is the cache key
    node: etree._Element = _osembed_para("#ost/api/ex/k12phys-ch04-ex017")
    assert c._os_embed_nickname(node) == "k12phys-ch04-ex017"


def test_os_embed_other_link_is_none() -> None:
    # a non-exercise os-embed url is not an injected exercise
    assert c._os_embed_nickname(_osembed_para("#figure/foo")) is None
