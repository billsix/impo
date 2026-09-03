# HTML/EPUB exercise rendering — collapse the answer behind "show answer", fix the floating number

**Status:** proposed — needs go-ahead
**Priority:** 3
**Difficulty:** 3

## BLUF

In the multipage HTML web edition, end-of-section Review Questions and Critical Thinking Questions render with
**two problems**: (1) each question's **answer is shown immediately and visibly** right under it (bad — a reader
should attempt the question first); (2) a **bare number floats loose** before each question block (the maintainer:
"I have no idea what the 2's are"). Fix both: put every answer behind a collapsible **"Show answer"** control
that expands on click (native `<details>`/`<summary>`, no JS), and either attach the stray number to its
question as a proper label or drop it. "Done" = anatomy's HTML Review/Critical-Thinking answers are hidden until
clicked, the floating numbers are gone or made meaningful, and the change is in the **shared toolchain**
(applies to all 16 books); PDF output is unchanged.

## Context

**Read first:** `openstax/tooling/entrypoint/html.sh` (chunkedhtml build), `openstax/tooling/tools/pandoc/`
(`xref.lua`, `chunked-template.html`, `osbook-web.css`, `preprocess.py`), and `openstax/tooling/entrypoint/epub.sh`
(same pandoc path — fix should carry to EPUB too). The HTML is produced by **pandoc from the generated LaTeX**,
so the fix belongs in the pandoc leg (a lua filter and/or CSS), NOT in `convert.py`'s LaTeX (which drives the PDF
and must stay untouched).

**Concrete findings (anatomy, built 2026-09-03,
`checkout/output/anatomy-and-physiology-2e/003-an-introduction-to-the-human-body.html`):**

- **The visible answer** — each question is `<div class="exercise">` (problem `<p>` + choices `<ol>`), followed by:
  ```html
  <div class="answer"><p>C</p></div>
  ```
  rendered inline and visible. The `answer` Div is the hook to transform.
- **The floating number** — immediately after the `<h3 …>Review Questions</h3>` heading and before the first
  exercise:
  ```html
  <div class="multicols"><p><span>2</span></p><div class="exercise">…
  ```
  i.e. a bare `<span>2</span>` in its own paragraph, detached from any question. Likely the exercise **number**
  (from the CNXML/`\begin{exercise}` counter) that pandoc emits as a standalone span instead of a run-in label.
  Investigate whether it's per-question (only the first shows here — check a multi-question block) and what the
  value tracks (source problem number? a counter that resets oddly?). In the PDF it presumably renders as a
  proper run-in number; only the HTML mapping is wrong.

## Approach (proposed — confirm the mechanism in Q1 before building)

1. **Collapsible answers — a pandoc lua filter** (`tools/pandoc/xref.lua` already runs; add to it or a new
   `reveal-answers.lua`): match `Div` with class `answer`, wrap its content as
   `<details class="answer"><summary>Show answer</summary>…</details>`. Native, no JS, works in browsers.
   - **EPUB caveat, attach it here:** `<details>` is valid EPUB3 but **reader support is uneven** (some e-readers
     show the content always-expanded, a few hide it with no toggle). Acceptable degradation (worst case = today's
     behavior), but verify in an EPUB reader and note it; if a reader hides with no toggle, fall back to a CSS
     `.answer{}` that stays visible in EPUB while `<details>` governs HTML.
   - Style `summary` as an obvious button in `osbook-web.css` (cursor, border, "Show answer"/"Hide" affordance).
2. **The floating number** — first identify it (grep the LaTeX the HTML came from: `/tmp/htmlbuild/*.tex` during a
   build, or the committed `checkout/latex/`). If it's the exercise number, either (a) make the lua filter pull the
   bare leading `<span>` number into the following `exercise` Div as a real `<span class="exercise-number">` label,
   or (b) if it's redundant/noise in HTML, drop it. Decide by what it tracks (Q2).
3. **Rebuild anatomy HTML + EPUB**, confirm: answers hidden-until-clicked, numbers fixed, no regression elsewhere.
   Then confirm one other book (e.g. a bundle) since the toolchain is shared.

## Notes / relationship to other work

- This is HTML/EPUB-only; the PDF is unaffected and correct.
- Independent of [[openstax-converter-unification-gaps]] (that's about *which* exercises exist and PDF content);
  this is about *how* end-of-section questions are presented in the web/EPUB editions. They can be done in either
  order, but both touch the shared toolchain, so re-verify all-16 build after each.

## Open questions

1. **Mechanism for the collapsible answer:** a pandoc **lua filter emitting `<details>`** (my recommendation —
   native, no JS, one place), or CSS-hide + a small injected JS toggle, or post-processing the built HTML? *Recommend
   the lua filter + `<details>`.*
2. **The floating number's fate:** once identified — attach it to its question as a visible label, or remove it from
   the HTML entirely? *Recommend attaching it as a proper per-question number if it's meaningful; removing only if
   it's a rendering artifact with no counterpart in the PDF.* (Needs the identification step first.)
3. **Answer-visibility default:** collapsed-by-default with "Show answer" (my recommendation), or a per-page
   "reveal all" toggle too? *Recommend collapsed-by-default, no global toggle for now.*
