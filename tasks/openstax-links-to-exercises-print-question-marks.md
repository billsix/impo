# Links kept their words, and exercises got labels (the "??" in the PDFs)

**Done 2026-11-27** (agent; found the same day while adding Introduction to Sociology 3e. William Emerison Six <billsix@gmail.com>, 2026-11-27: "for the three defect tasks, make a branch, turn gpg signing off, do the work, commit, archive, commit").

## What was wrong

Two things, one behind the other.

- **Exercises carried no label.** Where a module pointed at an exercise, the converter wrote `\cref{…}` and no matching `\label`, so the PDF printed "??": 1,193 exercises in 14 book folders, 874 of them in Life, Liberty, and the Pursuit of Happiness. The web editions showed the raw label in brackets.
- **A link with words of its own lost them.** Looking at what pointed at those 874 exercises showed the larger defect: `<link target-id="…">words</link>` and `<link document="…">words</link>` both became `\cref`, which prints the target's kind and number in place of the author's words. American Government 4e read "Drafted by Thomas Jefferson, the section 5.3.25 officially proclaimed the colonies' separation" for "the Declaration of Independence". 7,157 internal links in 30 book folders carry words. This was not known before; the task as proposed covered only the labels.

## What was done

- `inline_element` in `openstax/tooling/tools/cnxml2tex/convert.py`: a link with words becomes `\hyperref[label]{words}`; an empty one is still `\cref`. `render_exercise`: an exercise something points at gets its `\label`.
- `openstax/tooling/tools/pandoc/xref.lua`: the web editions number exercises as the PDF does (from 1 after every heading, the number printed in front), a reference to one reads "Exercise 3", and the filter rewrites a link's text only when pandoc marks the link as a `\cref`, so a worded link keeps its words.
- Tests in `tools/tests/test_helpers.py` (a referenced exercise, a worded link to an element, a worded link to a module).

## Decisions

- **The worded-link fix went in with this task** instead of getting its own: it is the same branch of the converter, and it is what most of the "??" in Life, Liberty, and the Pursuit of Happiness needed. Its reach is much wider than the task's title (the agent's call, with the maintainer away).
- **The web editions now show exercise numbers.** They showed none, so "Exercise 3" would have pointed at nothing a reader could see. The numbering follows the PDF's, which restarts after every heading.

## Result

All 37 book folders (57 books) were rebuilt in the three formats on 2026-11-27 with this change and the two made on the same branch. Checked in built output: the American Government sentence reads "the Declaration of Independence"; the Sociology question reads "noted in Exercise 1" in the PDF and in the web edition, where the exercises are numbered "1.", "2.".

## Left as it is

About 20 references in 9 books still print "??": they point at ids that get no label for other reasons. Nobody read the 7,157 reworded sentences; a sample of two was read.

## Recorded

`tasks/reference/tooling/converters.md` ("Links with words of their own, and references to exercises") and `tasks/reference/tooling/cross-references.md` (step 1 of the pipeline).
