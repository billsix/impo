# Parameterize bare generic type annotations

**Status:** in progress. **Priority:** 5  **Difficulty:** 1

## BLUF

Two bare-`dict` annotations in `trench/elementary-differential-equations/tools/split_html.py`
build a nested, heterogeneous sitemap tree, so their honest parameters are
`dict[str, Any]` (shared Python standard, "Parameterize generic types" — an
explicit `Any` beats a bare generic, which silently means implicit `Any` anyway).
"Done" = both sites parameterized and the module still compiles.

## Context (cold-start)

Found by an AST scan for unsubscripted generic annotations across the repos. Only
this one tracked file is impo's own code; the other scanner hits
(`openstax/osbooks-*/checkout/tools/pandoc/build_nav.py`) live in **untracked
upstream OpenStax checkouts** — not impo's source — so they are out of scope.

## The sites and their fixes

- `build_sitemap(...) -> dict` → `-> dict[str, Any]` — returns the sitemap root, a
  recursive tree node whose values are strings, nested dicts, and child lists.
- `root: dict = {}` → `root: dict[str, Any] = {}` — that same heterogeneous node.

Adds `from typing import Any`.

## Verification

impo has no Python type/lint gate (this is a standalone tool), so verification is
`python -m py_compile` on the module. Annotation-only; no behaviour change.
