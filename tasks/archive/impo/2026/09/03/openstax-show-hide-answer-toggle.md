# "Show answer" button should toggle to "Hide answer" when expanded

**Status:** DONE 2026-09-03 — empty summary + CSS ::after content swap (Show/Hide), no JS; verified anatomy HTML (commit `44252bc`)
**Priority:** 4
**Difficulty:** 1

## BLUF

The collapsible answer's summary button always reads "Show answer", even when the answer is expanded. Make it
read **"Hide answer"** while open. Pure CSS (no JS, so it works in the EPUB editions too): the label moves from a
literal `<summary>` text node to a `::after` pseudo-element whose `content` swaps on `details[open]`. "Done" =
clicking the button expands the answer and flips the label to "Hide answer"; clicking again collapses and flips
back — in HTML and EPUB, no JavaScript.

## Context

Built on the collapsible-answer work (`tasks/archive/impo/2026/09/03/openstax-html-exercise-rendering.md`,
commit `0e245cf`): `xref.lua` wraps the `.answer` Div as `<details class="answer"><summary>Show answer</summary>
…</details>`, styled in `osbook-web.css`. A native `<details>` summary's text is static, so a plain text node
can't toggle without JS — but JS won't run in EPUB readers. CSS pseudo-element `content` on `details[open]` is
the JS-free way, supported by browsers and modern EPUB3 readers.

## Fix (2 small changes)

1. `xref.lua`: emit an **empty** `<summary></summary>` (the label now comes from CSS).
2. `osbook-web.css`:
   ```css
   details.answer > summary::after  { content: "Show answer"; }
   details.answer[open] > summary::after { content: "Hide answer"; }
   ```
   (Alongside the existing summary button styling.)

## Verify

Rebuild anatomy HTML: `details.answer > summary` is empty and the `::after` rules are present; open a page and
confirm the button reads "Show answer" collapsed / "Hide answer" expanded. Spot-check the EPUB carries the same
CSS. No JS added.
