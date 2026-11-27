# A link to an exercise prints "??" in the PDF: exercises carry no label

**Status:** proposed — needs go-ahead
**Priority:** 5
**Difficulty:** 4 (a one-line change in the converter; the work is rebuilding 14 book folders and checking the web editions' numbering)
**Created:** 2026-11-27 (agent, found while adding Introduction to Sociology 3e; `tasks/openstax-add-remaining-english-books.md`)

## BLUF

Where a module links to an exercise (`<link target-id="…"/>` whose target is an `<exercise>`), the converter writes `\cref{…}` but never writes the matching `\label` on the exercise, so LaTeX prints "??" and warns "Reference … undefined". 1,193 exercises in 14 book folders are pointed at this way. Done means each such exercise carries its label, the PDFs' final logs have no undefined reference from this cause, and the HTML and EPUB show the exercise's number.

## Context

**Read first:** `tasks/reference/tooling/cross-references.md` (how references become links in the PDF and, through `tools/pandoc/xref.lua`, in the web editions) and `render_exercise` in `openstax/tooling/tools/cnxml2tex/convert.py`.

### What was measured (2026-11-27)

The change was tried and taken out again, because it rewrites many books that were not part of the work in hand. In `render_exercise`:

```python
out: list[str] = [
    "\\begin{exercise}" + (opt_label(node) if node.get("id") in labels else "")
]
```

`labels` is the set of ids something points at, so only referenced exercises change. `tools/compare-converter-output.sh` then showed these exercises gaining a label: Life, Liberty, and the Pursuit of Happiness 874, Introductory Statistics bundle 119, Statistics 62, College Physics bundle 35, Chemistry bundle 32, Astronomy 24, University Physics bundle 16, Prealgebra bundle 15, College Algebra bundle 5, Biology bundle 4, Calculus bundle 3, Microbiology 2, Physics 1, Introduction to Sociology 3e 1. `osbook-envs.sty` already has `\crefname{exercise}{Exercise}{Exercises}`, and the `exercise` environment steps its counter with `\refstepcounter`, so the label resolves in the PDF.

The one case in Introduction to Sociology 3e: module `m90145`, "What did the Clarks use in their experiment noted in ??".

### Not checked yet

- What the web editions do with the new labels: `xref.lua` numbers theorems, figures and equations; whether it gives an exercise its number, and the right one (exercises are numbered per section), has to be looked at in a built page.
- Life, Liberty, and the Pursuit of Happiness has 874 of the 1,193. What points at its exercises (an answer key, most likely) and whether a number is what the reader should see there.

## Plan

- [ ] Put the change above back, with a test (`tools/tests/test_helpers.py`) and the comparison.
- [ ] Build Introduction to Sociology 3e and Statistics; read the references in the PDF and in the web edition; extend `xref.lua` if an exercise gets no number there.
- [ ] Look at what Life, Liberty, and the Pursuit of Happiness does with its 874 and decide whether it needs something else.
- [ ] Rebuild the 14 folders; record the result in `tasks/reference/tooling/cross-references.md`.

## Open questions

None.
