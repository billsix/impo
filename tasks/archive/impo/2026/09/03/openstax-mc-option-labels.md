# Multiple-choice options should be labeled a,b,c,d to match the letter answer

**Status:** DONE 2026-09-03 — options a,b,c,d (PDF via labelenumi, HTML via CSS) + lowercased answer; verified anatomy (commit `44252bc`)
**Priority:** 3
**Difficulty:** 2

## BLUF

In a book's own end-of-section Review Questions, the multiple-choice **options render as a numbered list
(1,2,3,4)** while the **answer is given as a letter ("A"/"D")** — so a reader can't tell which numbered
option the letter means. Make the options use **a,b,c,d** (matching the answer), consistently in **PDF, HTML,
and EPUB**, and lowercase the answer letter so both read `a,b,c,d`. "Done" = anatomy's Review-Question options
show `a. b. c. d.` and the answer shows the matching lowercase letter, in all three formats; injected os-embed
exercises (which already label options a,b,c,d) are unchanged.

## Context

**Two exercise-rendering paths, only one is wrong:**
- `render_injected_exercise` (os-embed practice, e.g. physics/organic) — already builds option labels a,b,c,d
  into the text via `_EX_LETTERS` (`convert.py:1780,2051`). Correct; leave alone.
- `render_exercise` (a book's OWN review questions, e.g. anatomy — `convert.py:2378`) — emits the options as a
  plain `\begin{enumerate}`, which defaults to **1,2,3,4** in both LaTeX and pandoc-HTML, while the answer is a
  bare letter `A` from the CNXML `<solution>` (`convert.py:2402`). This mismatch is the bug.

**Source shape** (anatomy `m45985.tex`):
```latex
\begin{exercise}
The smallest independently functioning biological unit ... is a(n) ____.
\begin{enumerate}\item cell \item molecule \item organ \item tissue\end{enumerate}
\begin{answer} A \end{answer}
\end{exercise}
```
The `exercise` env (`osbook-defer.sty:34`) sets no enumerate label, so options number 1,2,3,4.

## Fix (3 coordinated changes, one per format concern)

1. **PDF options → (a)(b)(c)(d):** in `osbook-defer.sty`, the `exercise` environment redefines the level-1
   enumerate label — `\renewcommand{\labelenumi}{(\alph{enumi})}` in its begin code (scoped to the env). Plain
   LaTeX, no enumitem needed. Injected exercises build options as text (not an enumerate), so unaffected.
2. **HTML/EPUB options → a,b,c,d:** in `osbook-web.css`, `.exercise > ol { list-style-type: lower-alpha; }`.
   Targets the option `<ol>` (direct child of the exercise div); injected exercises render options as text, so
   unaffected.
3. **Answer letter → lowercase (all formats):** in `render_exercise`, when a `<solution>` renders to a bare
   single letter A–Z, lowercase it (`A`→`a`) so it matches the a,b,c,d options. Only bare single-letter answers
   are touched — prose/worked-solution answers (critical-thinking questions) are left as-is.

## Verify

Rebuild anatomy PDF + HTML (+ spot-check EPUB): options show `a. b. c. d.`, answers show the matching lowercase
letter, in all formats. Confirm an os-embed book (physics) is unchanged (still a,b,c,d, no regression). Re-run
the converter unit tests.
