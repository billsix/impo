#!/usr/bin/env python3
r"""Auto-link literal-text internal references in the chunked HTML web edition.

Properly marked-up cross-references (CNXML <link target-id>) are already links
(converter -> \cref -> xref.lua). This handles the ones the source left as PLAIN
TEXT -- "as discussed in Section 1.5", "the street map in Figure 10.6" -- turning
them into links, but ONLY when the referenced number actually resolves within the
same book. Unresolved numbers stay text (the safety net: never a broken or
cross-book link; cross-book refs like "(IA 8.2.1)" are naturally skipped).

Two passes over a book's site dir:
  1. Build a map  "<Kind> <number>" -> "page#anchor":
       - Section x.y      -> page            (from sitemap.json)
       - Figure/Table/Example/Equation n.m -> page#id  (from the rendered label
         spans + the nearest ancestor id; best-effort -- a miss just means no link)
  2. Rewrite matching text in each page, using an HTML parser so replacement only
     touches real text nodes, never attributes, never text already inside an <a>,
     and never the label/caption/heading spans themselves.

Usage:  python3 build_xref_links.py <output-site-dir>
"""
from __future__ import annotations

import glob
import json
import os
import re
import sys

from lxml import etree, html  # type: ignore[import-not-found]

KINDS = ("Figure", "Table", "Example", "Equation", "Section")
# a reference like "Figure 10.6" / "Section 1.5" / "Equation 3" (word + number)
REF = re.compile(r"\b(%s)\s+(\d+(?:\.\d+)*)" % "|".join(KINDS))
# containers whose text is a LABEL (the item itself) or already a link -> never rewrite
SKIP_ANCESTORS = {"a", "script", "style"}
SKIP_CLASSES = {"envhead", "book-toc", "page-toc", "breadcrumb", "prevnext"}


def section_map(site: str) -> dict[str, str]:
    """`Section x.y` -> page, from sitemap.json (section number -> its page)."""
    out: dict[str, str] = {}
    p = os.path.join(site, "sitemap.json")
    if not os.path.exists(p):
        return out

    def walk(node: dict) -> None:
        s = node.get("section") or {}
        num, path = s.get("number"), (s.get("path") or "")
        if num and path:
            out.setdefault("Section %s" % num, path.split("#", 1)[0])
        for k in node.get("subsections") or []:
            walk(k)

    walk(json.load(open(p, encoding="utf-8")))
    return out


def label_map(pages: list[str]) -> dict[str, str]:
    """`Figure/Table/Example/Equation n.m` -> page#id, from each page's rendered
    label span and the nearest ancestor carrying an id."""
    out: dict[str, str] = {}
    for pg in pages:
        page = os.path.basename(pg)
        try:
            doc = html.parse(pg).getroot()
        except Exception:  # noqa: BLE001
            continue
        for span in doc.iter("span"):
            if "envhead" not in (span.get("class") or ""):
                continue
            text = "".join(span.itertext())
            m = re.match(r"\s*(Figure|Table|Example|Equation)\s+(\d+(?:\.\d+)*)\.", text)
            if not m:
                continue
            key = "%s %s" % (m.group(1), m.group(2))
            anc = span
            while anc is not None and not anc.get("id"):
                anc = anc.getparent()
            if anc is not None and anc.get("id"):
                out.setdefault(key, "%s#%s" % (page, anc.get("id")))
    return out


def _skip(el) -> bool:
    """True if this element (or an ancestor) is a link/label/nav we must not touch."""
    while el is not None:
        tag = el.tag if isinstance(el.tag, str) else ""
        if tag in SKIP_ANCESTORS:
            return True
        if set((el.get("class") or "").split()) & SKIP_CLASSES:
            return True
        el = el.getparent()
    return False


def link_text(text: str, ref_map: dict[str, str], cur_page: str):
    """Split a text string on resolvable references, returning a list of
    (str | <a> element) fragments, or None if nothing matched."""
    frags: list = []
    last = 0
    changed = False
    for m in REF.finditer(text):
        key = "%s %s" % (m.group(1), m.group(2))
        target = ref_map.get(key)
        if not target:
            continue
        # a same-page anchor ref -> keep it relative (#id); else page[#id]
        href = target
        if target.split("#", 1)[0] == cur_page and "#" in target:
            href = "#" + target.split("#", 1)[1]
        frags.append(text[last:m.start()])
        a = etree.Element("a")
        a.set("href", href)
        a.text = m.group(0)
        frags.append(a)
        last = m.end()
        changed = True
    if not changed:
        return None
    frags.append(text[last:])
    return frags


def rewrite_page(pg: str, ref_map: dict[str, str]) -> int:
    cur_page = os.path.basename(pg)
    try:
        root = html.parse(pg).getroot()
    except Exception:  # noqa: BLE001
        return 0
    n = 0
    # collect text nodes first (mutating the tree while iterating is unsafe)
    targets = []
    for el in root.iter():
        if not isinstance(el.tag, str):
            continue
        if el.text and REF.search(el.text) and not _skip(el):
            targets.append((el, "text"))
        if el.tail and REF.search(el.tail) and not _skip(el.getparent()):
            targets.append((el, "tail"))
    for el, which in targets:
        text = el.text if which == "text" else el.tail
        frags = link_text(text, ref_map, cur_page)
        if not frags:
            continue
        # rebuild: leading string + a-elements (each carrying following string as tail)
        if which == "text":
            el.text = frags[0] if isinstance(frags[0], str) else ""
            insert_at = 0
            anchor_parent = el
        else:
            el.tail = frags[0] if isinstance(frags[0], str) else ""
            parent = el.getparent()
            insert_at = list(parent).index(el) + 1
            anchor_parent = parent
        i = insert_at
        pending_a = None
        for frag in frags[1:]:
            if isinstance(frag, str):
                if pending_a is not None:
                    pending_a.tail = frag
            else:
                anchor_parent.insert(i, frag)
                i += 1
                pending_a = frag
                n += 1
    if n:
        with open(pg, "wb") as f:
            f.write(html.tostring(root, encoding="utf-8", doctype="<!DOCTYPE html>"))
    return n


def main(argv: list[str]) -> int:
    if len(argv) != 1:
        print("usage: build_xref_links.py <output-site-dir>", file=sys.stderr)
        return 2
    site = argv[0]
    pages = sorted(glob.glob(os.path.join(site, "*.html")))
    if not pages:
        return 0
    ref_map = section_map(site)
    ref_map.update(label_map(pages))
    total = sum(rewrite_page(pg, ref_map) for pg in pages)
    print("build_xref_links: linked %d internal refs across %d pages in %s"
          % (total, len(pages), site))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
