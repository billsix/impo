# Fixed: a degree sign in a multi-character MathML operator came out with literal braces

**Done 2026-11-27** (agent; go-ahead from William Emerison Six <billsix@gmail.com>, 2026-11-27. Found 2026-11-26 in the first build of College Physics).

## The defect

Twelve lines of College Physics showed `\text\{\textordmasculine\}` in formulas such as "cal/g·ºC": literal braces in the PDF, and 72 "Could not convert TeX math" warnings from pandoc, with the formula left as raw TeX in the HTML and EPUB.

## The cause, which was not the one the task guessed

The task expected the fault in `<m:mtext>`. It was in `<m:mo>`: the source writes the unit's operator as one element holding two characters, `<m:mo>⋅º</m:mo>`. For an operator of more than one character, `mml()` in `openstax/tooling/tools/cnxml2tex/convert.py` substituted the symbol macros first and escaped the result second, so the braces of its own `\text{\textordmasculine}` were escaped. A single-character operator, `<m:mn>` and `<m:mtext>` were never affected.

## The fix

That branch now calls `_math_literal` alone, which escapes the literal braces first and substitutes the macros second. One new test in `openstax/tooling/tools/tests/test_mathml.py` (`test_multi_character_operator_keeps_macro_braces`).

## Proof

- `tools/compare-converter-output.sh` (written for this task, kept in `tools/`) converted all 20 fetched books with the old and the new converter: 19 identical; College Physics differed in 5 section files, 15 lines, every one a formula that had held the escaped braces. No `\text\{` remains.
- College Physics was rebuilt in all three formats on 2026-11-27: PDFs of 2,552 and 2,595 pages as before, and no "Could not convert TeX math" warning (72 before). In the HTML the formula is MathML with the source `\text{0.50~cal/g}\cdot ^\circ \text{C}`.
- The toolchain gate (`make -C openstax/tooling type-check`) passed.

## Not done

The task asked for a look at three similar pandoc warnings in the Introductory Statistics bundle's build. That bundle's generated LaTeX is unchanged by this fix, so those warnings have another cause and were not looked at.
