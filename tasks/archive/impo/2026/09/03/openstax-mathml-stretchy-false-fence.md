# Huge open-paren in HTML math: `f(x)` stretched over a piecewise — honor stretchy="false"

**Status:** DONE 2026-09-03 — converter now honors `stretchy="false"` on fence `<mo>`; unit test added
**Priority:** 3
**Difficulty:** 3

## BLUF

In the calculus HTML (and PDF), a piecewise definition rendered with a **giant open parenthesis** right after
`f`: `f⎛x)={…}` — the `(` of `f(x)` was stretched to the full height of the cases table. Cause: the converter's
`_fenced_row` promoted the `(` to a stretchy `\left(` because an `mtable` appeared *later in the same row*,
**ignoring the `<mo stretchy="false">` on that paren**; its `\right` then landed past the whole piecewise, so the
`(` stretched over everything. Fixed by honoring `stretchy="false"`. Happens in any book where a plain `f(x)`
(or similar literal-paren group) sits before a piecewise/matrix in one `<mrow>`. "Done" = `f(x)` renders with a
normal-size paren and only the piecewise brace stretches, in HTML and PDF.

## Context

**Source MathML** (calculus module `m53477`): the `f(x)` parens are explicitly non-stretchy —
```xml
<mrow><mi>f</mi><mo stretchy="false">(</mo><mi>x</mi><mo stretchy="false">)</mo><mo>=</mo>
  <mrow><mo>{</mo><mtable>…piecewise…</mtable></mrow><mo>.</mo></mrow>
```
The piecewise `{` (no stretchy attr → defaults stretchy) is the one that *should* stretch.

**Bug** (`convert.py` `_fenced_row`): the opening-fence search accepted the `(` because
`any(_has_mtable(k) for k in kids[i+1:])` was true (the piecewise mtable is later in the row) — with no check
for `stretchy="false"`. So it emitted `\left( x)=\left\{ … \right.. \right` — the outer `\left(` matched a far
`\right`, stretching the paren over the whole system.

## Fix

`convert.py` `_fenced_row`: skip an opening-fence candidate `<mo>` that carries `stretchy="false"` (a literal
delimiter, not a fence to `\left…\right`). One `if c.get("stretchy") == "false": continue` guard in the fence
loop. With it, the outer row finds no stretchy fence → renders `f(x)=…` with plain parens, and the *inner*
piecewise mrow still fences its `{` correctly as `\left\{ … \right.`.

## Verify

- Unit test `test_mathml.py::test_nonstretchy_paren_before_piecewise_stays_plain` — pins: no `\left(`, literal
  `f(x)`, piecewise `\left\{` intact. (31 tests pass.)
- Direct check on the real MathML → `f(x)=\left\{ \begin{array}{l}3x+1\;x\geq 2 \\ x^{2}\;x<2\end{array} \right..`
- Full check: rebuild calculus-volume-1 PDF + HTML, confirm the piecewise renders with a normal `f(x)` paren.
