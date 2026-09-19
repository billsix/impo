# Add the Trench boundary-value variant + student solutions manual (osbook style)

**Status:** proposed — gated
**Depends on:** `add-trench-differential-equations-book.md` (the main book must build in osbook style
first — this reuses its shim, build wiring, and family folder). Internal sequence, so this is a
`Depends on`, not a `blocked` external gate.
**Priority:** 7 (do after the main book; not an easy win)
**Difficulty:** 6
Created 2026-09-19 (William Emerison Six <billsix@gmail.com>).

## BLUF

Once the main Trench *Elementary Differential Equations* book builds in OpenStax house style (task
`add-trench-differential-equations-book.md`), bring in the other two `.tex` from the same pinned
source in the same style: **`TRENCH_DIFFEQ_BV.tex`** (the boundary-value-problems variant) and
**`TRENCH_DIFFEQ_STUDENT_MANUAL.tex`** (the student solutions manual). They share Trench's
`wtrench.sty` + `book` class, so the **shim and build machinery from task 1 should largely carry
over** — this task is mostly re-applying that work to two more masters and handling their deltas.
"Done" = both build to osbook-styled PDFs with content unchanged and cross-references intact.

## Context (cold-start)

Source: https://github.com/billsix/differentialEquationsTrench @
`a7c17e34ee0326ff97824d166a1dc91547f8f2e7`, in the `trench/` family created by task 1. Three
standalone `.tex` there; task 1 handles `TRENCH_DIFFEQ.tex`. This task handles:
- `TRENCH_DIFFEQ_BV.tex` (1.9MB) — the boundary-value edition; largely the main book's content plus
  boundary-value chapters, same custom class/macros.
- `TRENCH_DIFFEQ_STUDENT_MANUAL.tex` (784KB) — worked solutions; likely reuses `wtrench.sty` and may
  cross-reference the main book's exercise numbering.

**Read task 1 first** — its Decisions block, macro-mapping table (`wtrench.sty` → osbook), EPS→PDF
step, license-page handling, and verification approach are the foundation here. Do not re-derive
them; reuse `trench-osbook.sty` and the preprocessing transform, extending only where these two
files use macros the main book didn't.

## Plan

1. Confirm the shim from task 1 covers the macros these two files use (grep each for `\begin{` and
   custom commands; diff against the main book's macro set). Extend the shim for any new ones
   (solutions-specific environments, boundary-value-specific constructs).
2. Add each as an **additional build master inside the one `trench/elementary-differential-equations/`
   folder** (decision, 2026-09-19): the single fetched checkout already holds all three `.tex` + the
   shared `EPS/`, so add `make pdf-bv` / `pdf-manual` targets rather than re-fetching the repo into
   separate folders.
3. EPS→PDF, license page (CC BY-NC-SA 3.0), subtitle "Formatted by Bill Six", build under lualatex.
4. Verify: content unchanged, structure/figures/cross-refs sound. The student manual's refs to the
   main book (if any) resolve or are handled.

## Open questions

1. ~~**Folder vs master.**~~ **RESOLVED 2026-09-19 (William Emerison Six <billsix@gmail.com>): (b)** —
   both are additional build masters/targets (`pdf-bv`, `pdf-manual`) inside the one
   `trench/elementary-differential-equations/` folder, sharing its single checkout + `EPS/`.
2. **Student-manual coupling.** Does the manual stand alone, or must it reference the main book's
   exercise/answer numbering (which the osbook restyle may relabel)? Determine when the shim is
   applied; if coupled, keep numbering consistent across the two.