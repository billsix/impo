"""The cross-book link data resolves, and the links render as LaTeX."""

from __future__ import annotations

import pathlib

import crossbook
import site_files


def test_every_prerequisite_resolves() -> None:
    lines: list[str] = (
        crossbook.review_lines()
    )  # raises KeyError on a bad code or section
    assert len(lines) == len(crossbook.entries()) > 0


def test_boxes_never_point_at_their_own_module() -> None:
    module: str
    targets: list[crossbook.SectionRef]
    for module, targets in crossbook.module_prerequisites().items():
        assert targets
        assert all(
            crossbook.book_index(t[0])[t[1]]["module"] != module for t in targets
        )


def test_box_is_a_prerequisites_environment() -> None:
    module: str = crossbook.book_index("C1")["1.1"]["module"]
    box: str = crossbook.prerequisites_box(module)
    assert box.startswith("\\begin{prerequisites}")
    assert "\\href{https://billsix.github.io/impo/college-algebra-2e/" in box


def test_ia_reference_official_numbering() -> None:
    linked: str = crossbook.link_ia_references("(IA 8.2.1)")
    assert crossbook.book_index("IA")["8.2"]["title"] == "Simplify Radical Expressions"
    assert crossbook.book_index("IA")["8.2"]["page"] in linked


def test_site_files_keeps_only_used_media(tmp_path: pathlib.Path) -> None:
    (tmp_path / "media").mkdir()
    (tmp_path / "media" / "used.png").write_text("x")
    (tmp_path / "media" / "unused.png").write_text("x")
    (tmp_path / "index.html").write_text(
        '<img src="media/used.png"><a href="https://x.org">x</a>'
    )
    assert site_files.site_files(str(tmp_path)) == ["index.html", "media/used.png"]
