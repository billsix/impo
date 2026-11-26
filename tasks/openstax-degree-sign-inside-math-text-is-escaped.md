# A degree sign written as "º" inside math text comes out with literal braces

**Status:** proposed — needs go-ahead
**Priority:** 5
**Difficulty:** 2
**Created:** 2026-11-26 (agent, found in the first build of College Physics).

## BLUF

In twelve lines of College Physics the source writes a degree sign as the character "º" (U+00BA) inside MathML text, as in "cal/g·ºC". The converter emits `\text\{\textordmasculine\}`: the braces of its own replacement are escaped, so the PDF shows them literally and pandoc cannot convert the formula for the HTML and EPUB editions (72 "Could not convert TeX math" warnings in that build, and the formula is shown there as raw TeX). Done means those formulas read "ºC" in all three editions and the warnings are gone.

## Context

**Read first:** the two maps in `openstax/tooling/tools/cnxml2tex/convert.py` that contain `º` (one maps it to `\text{\textordmasculine}`, the other to `\textordmasculine{}`), and the code that escapes the contents of an `<m:mtext>`.

- Only `osbooks-college-physics-bundle` has such lines today (12, checked across every checkout's generated LaTeX on 2026-11-26). They are in the heat and thermodynamics chapters: specific heat and conductivity units.
- The likely cause: the character is replaced first and the result is then escaped as literal text. The replacement and the escaping need to happen in the other order, or the replacement inside text should be `\textordmasculine{}` without a second `\text`.
- The Introductory Statistics bundle's build printed three of the same pandoc warnings for a different formula; look at those in the same pass.

## Plan

1. Reproduce with a unit test in `openstax/tooling/tools/tests/test_mathml.py` (an `<mtext>` containing "º").
2. Fix the order of replacement and escaping; run the toolchain gate.
3. Compare every book's generated LaTeX before and after, as was done for Content MathML on 2026-11-26; only the twelve lines should change.
4. Rebuild College Physics and confirm the warnings are gone.

## Open questions

None.
