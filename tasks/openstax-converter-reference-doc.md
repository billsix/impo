# Author a reference doc: the OpenStax converters — similarities and differences, in detail

**Status:** proposed — needs go-ahead
**Priority:** 3
**Difficulty:** 3

## BLUF

Write a durable reference doc, `tasks/reference/tooling/converters.md`, that characterizes the OpenStax
CNXML→LaTeX converter landscape **in enough detail that a future session understands the shared toolchain
and every per-book divergence without re-reading all 2900+ lines of `convert.py` or re-diffing the 16 source
repos.** The 16 `latex`-branch source repos did **not** share one converter — `convert.py` had 5 versions,
with further divergence in `preprocess.py`, `fetch_exercises.py`, and `osbook.cls`. impo merged them into one
shared toolchain (`openstax/tooling/`). This doc records what is common, what diverged and why, and how the
shared version relates to each original. "Done" = the reference doc exists, every claim is `file:line`- or
`repo:branch:path`-anchored, and it cross-links the companion fix task [[openstax-converter-unification-gaps]].

## Context

**Read first:** [[openstax-converter-unification-gaps]] (`tasks/openstax-converter-unification-gaps.md`) — the
sibling *fix* task, which already contains the raw comparison data this reference doc should be written up
from (the 5-version hash table, the per-book feature diffs, the gap table). This reference task is the
*documentation* half; that one is the *do* half. Also `openstax/CLAUDE.md` (has an **incorrect** "byte-identical"
claim to correct here too).

**Why a reference doc, not just the fix task:** per the maintainer's conventions, a fix task gets archived when
done and buried in a date bucket; the *knowledge* of how the converters relate is worth re-reading whenever
the toolchain is touched. It belongs in `tasks/reference/`, living, never archived. (This task exists because
the maintainer asked for a standalone reference doc, 2026-09-03.)

**Source of truth:** the per-book converters live on each source repo's `latex` branch at
`/foo/opt/openstax/osbooks-<subject>` — an **upstream-only, read-only** checkout (the `latex` branch is the
maintainer's own work; do not edit these repos). Read with `git -C <repo> cat-file -p latex:<path>`.

**Much of the analysis is already done** (this session, 2026-09-03) and lives in the fix task — the reference
doc is mostly a write-up + verification pass, not a fresh investigation.

## What the reference doc must cover

1. **The shared skeleton (the ~2856 lines all 16 share):** a high-level map of `convert.py` — CNXML parse →
   structure discovery (subcollection nesting auto-detect) → block/inline element handlers → MathML→LaTeX →
   os-embed exercise injection → assembly. Name the key functions and what each does, `file:line`-anchored to
   impo's `openstax/tooling/tools/cnxml2tex/convert.py`, so the doc is a jump-table into the code.

2. **The 5 convert.py versions and their deltas** (from the fix task's data):
   - majority (12 books) — the base.
   - physics — the `#ost/api/ex/<id>` second os-embed scheme.
   - organic-chemistry — `_pdfsafe` (math-in-titles `\texorpdfstring`).
   - python-programming — `render_code_block` (multi-line `<code>` → verbatim).
   - biology-bundle — `_pdfsafe` + the second os-embed scheme (union of two others).
   For each: what it added, WHY that book needed it, and where the merged impo converter stands (has it / how).

3. **The other divergent files:** `preprocess.py` (python's `codeblock`→`verbatim` pandoc rename),
   `fetch_exercises.py` (physics/biology's `discover_targets` two-query fetch), `osbook.cls` (organic/biology's
   `\DeclareOldFontCommand` block; calculus's Times-font + blue palette), `osbook-envs.sty` (python's env).
   `osbook-defer.sty` is identical everywhere — say so (a "confirmed same" is as valuable as a diff).

4. **The unification model** — the general lesson: *logic* divergences (schemes, math-in-titles, code) unify by
   folding all variants into one feature-detecting converter; *presentation* divergences (calculus theme) need a
   per-book style hook, not converter logic. This is the reusable insight the maintainer will want on hand.

5. **A per-book quick-reference table:** book → collections/nesting → figure format (raster/SVG) → os-embed
   scheme (nickname / tag / none) → any special converter feature → exercise count. So a future session sees a
   book's shape at a glance.

## Method (cheap, since the data exists)

- Lift the comparison tables from [[openstax-converter-unification-gaps]]; re-verify each hash/anchor against
  the current tree before committing it (a reference doc is trusted later without re-checking — verify now).
- Anchor every code claim to impo's `openstax/tooling/` copy (the maintained one), not a source repo, since
  that's what a future session edits.
- Add a pointer block in `openstax/CLAUDE.md` indexing the new reference doc, and **fix the "byte-identical"
  falsehood** there in the same change.

## Open questions

1. **Project key for the reference dir:** `tasks/reference/tooling/converters.md` (my recommendation — the
   converter is the shared toolchain, not one book), or `tasks/reference/impo/`? *Recommend `tooling/`.*
2. **Sequence vs. the fix task:** author this reference doc BEFORE fixing the gaps (documents the current
   divergent reality), or AFTER (documents the unified end state)? *Recommend a first pass now capturing the
   as-found state, then a short update after [[openstax-converter-unification-gaps]] lands to reflect the
   merged converter — the doc is living, so both.*
