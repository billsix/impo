#!/usr/bin/env python3
"""Fetch os-embed practice exercises referenced by the CNXML into a committed,
offline cache under exercises/.

Questions-only: the public OpenStax Exercises API withholds answer keys and
solutions (responses are solutions_are_public=false, answers carry no
correctness, collaborator_solutions is empty), so we store exactly what it
returns -- question stems + multiple-choice options. No auth token is used.

This is the ONLY networked step. Run it occasionally and commit exercises/;
the build (convert/pdf/html/epub) reads the cache and never touches the network.

Bundle-agnostic: all paths derive from this file's location, so the same script
works unchanged in any osbooks-* repo (see tasks/fetch-inject-exercises.md).

Usage:
  python3 tools/cnxml2tex/fetch_exercises.py            # fetch all (idempotent)
  python3 tools/cnxml2tex/fetch_exercises.py --limit=5  # first N (smoke test)
  python3 tools/cnxml2tex/fetch_exercises.py --list     # just list nicknames
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from typing import Any, cast

from lxml import etree  # ty: ignore[unresolved-import]

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MODULES = os.path.join(ROOT, "modules")
CACHE = os.path.join(ROOT, "exercises")
MEDIA = os.path.join(CACHE, "media")
API = "https://exercises.openstax.org/api/exercises"
CNXML = "{http://cnx.rice.edu/cnxml}"
UA = "osbooks-latex-port exercise fetcher (contact: billsix@gmail.com)"

_IMG_TAG = re.compile(r"<img\b[^>]*>", re.I)
_SRC = re.compile(r'src="([^"]+)"')
_EXT = {
    "image/png": ".png",
    "image/jpeg": ".jpg",
    "image/jpg": ".jpg",
    "image/gif": ".gif",
    "image/svg+xml": ".svg",
    "image/webp": ".webp",
}


def discover_targets() -> dict[str, str]:
    """Map every os-embed exercise link to the API query that fetches it.

    Two URL schemes appear across the OpenStax books:
      * `#exercise/<nickname>`   -> query `nickname:<nickname>`
      * `#ost/api/ex/<id>`       -> query `tag:<id>`  (physics/biology; e.g.
                                     `k12phys-ch04-ex017`, `apbio-ch01-ex001`)
    The trailing token is the cache key (exercises/<key>.json) either way."""
    targets: dict[str, str] = {}
    for mid in sorted(os.listdir(MODULES)):
        path: str = os.path.join(MODULES, mid, "index.cnxml")
        if not os.path.exists(path):
            continue
        try:
            tree: etree._ElementTree = etree.parse(
                path, etree.XMLParser(recover=True, huge_tree=True)
            )
        except Exception as e:  # noqa: BLE001
            print("  WARN parse %s: %s" % (mid, e))
            continue
        for ln in tree.iter(CNXML + "link"):
            if ln.get("class") != "os-embed":
                continue
            url: str = ln.get("url") or ""
            if url.startswith("#exercise/"):
                key: str = url[len("#exercise/") :]
                targets.setdefault(key, "nickname:" + key)
            elif url.startswith("#ost/api/ex/"):
                key = url[len("#ost/api/ex/") :]
                targets.setdefault(key, "tag:" + key)
    return targets


def http_get(
    url: str, want_bytes: bool = False, tries: int = 5
) -> tuple[bytes | str, str]:
    """GET with exponential backoff; give up immediately on 4xx."""
    delay: float = 1.0
    last: Exception | None = None
    for attempt in range(1, tries + 1):
        try:
            req: urllib.request.Request = urllib.request.Request(
                url, headers={"User-Agent": UA}
            )
            with urllib.request.urlopen(req, timeout=30) as r:
                data: bytes = r.read()
                ctype: str = r.headers.get("Content-Type", "")
                return (data, ctype) if want_bytes else (data.decode("utf-8"), ctype)
        except urllib.error.HTTPError as e:
            if 400 <= e.code < 500:
                raise
            last = e
        except Exception as e:  # noqa: BLE001
            last = e
        if attempt < tries:
            time.sleep(delay)
            delay = min(delay * 2, 30)
    if last is not None:
        raise last
    raise RuntimeError("http_get: no attempts made")  # unreachable (tries >= 1)


def cache_image(url: str, stats: dict[str, int]) -> str:
    """Download a remote exercise image; return its repo-root-relative path."""
    h: str = hashlib.sha1(url.encode()).hexdigest()[:16]
    if os.path.isdir(MEDIA):
        for f in os.listdir(MEDIA):
            if f.startswith(h + "."):
                return "exercises/media/" + f  # already cached
    raw, ctype = http_get(url, want_bytes=True)  # want_bytes -> raw is bytes
    data: bytes = cast(bytes, raw)
    ext: str | None = _EXT.get(ctype.split(";")[0].strip().lower())
    if not ext:
        ext = os.path.splitext(urllib.parse.urlparse(url).path)[1] or ".img"
    os.makedirs(MEDIA, exist_ok=True)
    fn: str = h + ext
    with open(os.path.join(MEDIA, fn), "wb") as f:
        f.write(data)
    stats["img"] += 1
    return "exercises/media/" + fn


def localize_images(html: str, stats: dict[str, int]) -> str:
    """Rewrite absolute <img src> URLs to locally-cached copies."""
    if not html or "<img" not in html:
        return html

    def on_tag(m: re.Match[str]) -> str:
        def on_src(sm: re.Match[str]) -> str:
            src: str = sm.group(1)
            if src.startswith(("http://", "https://")):
                try:
                    return 'src="%s"' % cache_image(src, stats)
                except Exception as e:  # noqa: BLE001
                    print("    WARN image %s: %s" % (src, e))
            return sm.group(0)

        return _SRC.sub(on_src, m.group(0))

    return _IMG_TAG.sub(on_tag, html)


def localize_item(item: dict[str, Any], stats: dict[str, int]) -> dict[str, Any]:
    item["stimulus_html"] = localize_images(item.get("stimulus_html", ""), stats)
    for q in item.get("questions", []) or []:
        q["stimulus_html"] = localize_images(q.get("stimulus_html", ""), stats)
        q["stem_html"] = localize_images(q.get("stem_html", ""), stats)
        for a in q.get("answers", []) or []:
            a["content_html"] = localize_images(a.get("content_html", ""), stats)
    return item


def fetch_one(key: str, query: str, stats: dict[str, int]) -> None:
    out: str = os.path.join(CACHE, key + ".json")
    if os.path.exists(out):
        stats["cached"] += 1
        return
    url: str = API + "?" + urllib.parse.urlencode({"q": query})
    data: Any = json.loads(http_get(url)[0])
    os.makedirs(CACHE, exist_ok=True)
    if not data.get("total_count"):
        with open(out, "w") as f:
            json.dump({"_missing": True, "key": key, "query": query}, f, indent=1)
        stats["missing"] += 1
        print("  MISSING %s" % key)
        return
    item: dict[str, Any] = localize_item(data["items"][0], stats)
    with open(out, "w") as f:
        json.dump(item, f, indent=1, ensure_ascii=False)
    stats["fetched"] += 1


def main(argv: list[str]) -> None:
    limit: int | None = None
    list_only: bool = False
    for a in argv:
        if a.startswith("--limit="):
            limit = int(a.split("=", 1)[1])
        elif a == "--list":
            list_only = True
    targets: dict[str, str] = discover_targets()
    print("discovered %d unique os-embed exercises" % len(targets))
    if list_only:
        for k in sorted(targets):
            print(k)
        return
    keys: list[str] = sorted(targets)
    if limit:
        keys = keys[:limit]
    stats: dict[str, int] = {"fetched": 0, "cached": 0, "missing": 0, "img": 0}
    for i, key in enumerate(keys, 1):
        fetch_one(key, targets[key], stats)
        if i % 25 == 0 or i == len(keys):
            print(
                "[%d/%d] fetched=%d cached=%d missing=%d images=%d"
                % (
                    i,
                    len(keys),
                    stats["fetched"],
                    stats["cached"],
                    stats["missing"],
                    stats["img"],
                )
            )
        time.sleep(0.12)
    print("DONE: %s -> %s" % (stats, CACHE))


if __name__ == "__main__":
    main(sys.argv[1:])
