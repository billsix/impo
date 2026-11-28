"""Compare two tests for a chapter's unnumbered opening module, over every fetched book.

OpenStax marks the module with class="introduction" on its <document>. The
cross-book page index tests instead for a chapter's first module whose title
starts with "Introduction" and that has no sections of its own. This prints,
per collection, how many modules each test selects and every module on which
they disagree.

Usage: python3 tasks/adhoc/openstax-web-section-numbering/survey_openers.py
"""

import pathlib
import re

root: pathlib.Path = pathlib.Path(__file__).resolve().parents[3]
module_ref: re.Pattern[str] = re.compile(r'<col:(module) document="([^"]+)"|<(/?)col:subcollection')
document_tag: re.Pattern[str] = re.compile(r"<document\b[^>]*>")
title_tag: re.Pattern[str] = re.compile(r"<title>(.*?)</title>", re.DOTALL)


def facts(checkout: pathlib.Path, module: str) -> tuple[bool, str, bool]:
    """Return (has the introduction class, title, has sections) for a module."""
    path: pathlib.Path = checkout / "modules" / module / "index.cnxml"
    if not path.exists():
        return (False, "(missing)", False)
    text: str = path.read_text()
    tag: re.Match[str] | None = document_tag.search(text)
    title: re.Match[str] | None = title_tag.search(text)
    marked: bool = tag is not None and 'class="introduction"' in tag.group(0)
    return (marked, title.group(1).strip() if title else "", "<section" in text)


for collection in sorted(root.glob("openstax/osbooks-*/checkout/collections/*.collection.xml")):
    checkout: pathlib.Path = collection.parents[1]
    by_class: int = 0
    by_title: int = 0
    disagreements: list[str] = []
    first_in_group: bool = False
    depth: int = 0
    for found in module_ref.finditer(collection.read_text()):
        if found.group(1) is None:
            depth += -1 if found.group(3) else 1
            first_in_group = not found.group(3)
            continue
        marked, title, has_sections = facts(checkout, found.group(2))
        position_first: bool = first_in_group and depth > 0
        first_in_group = False
        titled: bool = position_first and title.startswith("Introduction") and not has_sections
        by_class += marked
        by_title += titled
        if marked != titled:
            disagreements.append(
                f"    {found.group(2)} class={marked} first={position_first} "
                f"sections={has_sections} title={title[:60]!r}"
            )
    name: str = f"{checkout.parent.name}/{collection.name.removesuffix('.collection.xml')}"
    print(f"{name}: class {by_class}, title test {by_title}, differ {len(disagreements)}")
    print("\n".join(disagreements), end="\n" if disagreements else "")
