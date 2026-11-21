# Problem notebooks: restate, solve and check every exercise, plot with ePiX

**Partly done 2026-11-21** (branch `study-and-publishing`): the pipeline is built and **Prealgebra 2e
is complete end to end**; the other math-ladder books are not generated, and in Prealgebra most
exercises are restated only ("manual"). Remainder: `tasks/openstax-problem-notebooks-remaining-books.md`.
Contracts: `study/CLAUDE.md`; state: `tasks/reference/study/status.md`.

## Decisions (William Emerison Six <billsix@gmail.com>, 2026-11-21: "go with your recommendations")

- The math ladder first (prealgebra bundle, Algebra 1, College Algebra, Calculus 1–3); every problem,
  the ones without a book answer marked unchecked until reviewed; one notebook per section; in `study/`.

## Choices made while building (the maintainer was away)

- **Scale settled by counting** (discovery script `tasks/adhoc/openstax-problem-notebooks/count.py`,
  one-shot): the ladder books hold about 67 000 CNXML exercises (counts per book in the follow-on).
  Hand-writing a solution per problem was out of reach, so the "solve" step is **automatic where the
  exercise is mechanical**, and everything else is restated for a person:
  - `study/tools/problems.py` reads the converter's generated section LaTeX
    (`checkout/latex/sections/<module>.tex`) in the order of the cross-book page index, with each
    exercise's subsection and governing instruction ("In the following exercises, simplify.").
  - `study/tools/solver.py` decides whether an exercise is a bare expression/equation (or lettered parts
    of them) under a known task (simplify, evaluate, solve, factor, add/subtract/multiply/divide),
    parses it with sympy's LaTeX parser, computes, and compares with the book's answer (rounding to the
    book's decimals; variables taken positive when simplifying, as the books do). Statuses: checked,
    mismatch (flagged for review), computed (no book answer), manual.
  - `study/tools/notebooks.py` writes one jupytext percent notebook per section: attribution header
    (CC BY 4.0, link to the section), per exercise a Markdown restatement (pandoc) with the book's answer
    and a code cell running the solver, an ePiX graph cell (`study/tools/nbplot.py`) for exercises that
    graph an x-y equation, and a status file; `summary` totals them.
- **Notebook image** `study/notebooks/Dockerfile`: the study image + a uv `/venv` pinned by
  `notebooks/constraints.txt` (Jupyter, jupytext, sympy, antlr runtime 4.11) + ePiX from
  github.com/billsix/epix-mirror at `5f7a8c2…` (geometricalgebra's pin, with its install scripts
  copied). `make -C study problem-notebooks BOOK=<book>`; generated notebooks are gitignored
  (`study/output/notebooks/`), since they are regenerated from CC BY content.
- Prealgebra 2e was chosen as the complete book: its exercises are the most mechanical, so the
  automatic check covers the most of them.

## Verification (Prealgebra 2e)

- `make -C study problem-notebooks BOOK=prealgebra-2e` (container, JOBS=12, about a minute): exit 0;
  60 notebooks (the 74 indexed sections less 11 chapter openers and 3 appendix pages, which have no
  exercises), all executed with 0 cell errors, 147 ePiX graphs rendered.
- 7368 exercises: **1188 checked** against the answer key, **15 mismatch** (several are OpenStax
  errata, e.g. §7.3 "9(u−4)" answered "9y − 36"; others are the parser misreading, e.g. long-division
  layouts), **1235 computed** with no book answer (unchecked until reviewed), **4930 manual** (word
  problems, graphs, number lines, explanations). (The 737 worked examples, which carry their own
  solutions, are not exercises.)
- `make -C study test`: exit 0 (the solver's and extractor's doctests included).
