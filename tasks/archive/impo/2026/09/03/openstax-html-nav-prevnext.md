# HTML web edition: make Next/Previous navigation easy to find

**Status:** in progress 2026-09-03
**Priority:** 3
**Difficulty:** 2

## BLUF

The chunked HTML pages carry navigation as a cramped run-in flex row — `Up: … Top: … / Next: … Previous: …` —
so a reader has to hunt for "Next". Replace it with **prominent Previous / Next buttons** (large, labeled with
the destination title + a directional arrow) at the **bottom of the content** (and a compact top bar), following
the pattern every good docs site uses (Sphinx Furo, MkDocs Material, Docusaurus: big "← Previous: <title>" /
"Next: <title> →" footer buttons). "Done" = every book's HTML has clear, easy-to-hit Prev/Next controls; done
across all 16 books (shared template + CSS).

## Context

- The nav lives in `tools/pandoc/chunked-template.html`: `<nav id="sitenav">` (top) and `<nav id="sitenav-bottom">`
  (bottom), each a `div.sitenav` flex row of `Up/Top` and `Next/Previous` links using pandoc's chunkedhtml
  template vars `$up$`, `$top$`, `$next$`, `$previous$` (each `.url` + `.title`). The data is already there — only
  the presentation is poor.
- Research (Furo/Material/Docusaurus convention): the primary reading action is Prev/Next; they get **big footer
  buttons** with the neighbor's title, arrows, and generous hit area; Up/Top are secondary (breadcrumb or small).

## Plan (this is bundled with the sidebar task — one layout pass)

1. Rework the bottom nav into two large buttons: `← Previous — <previous.title>` and `<next.title> — Next →`,
   full-width, clearly separated, big padding (a real click target). Keep `accesskey` n/p.
2. Keep a slim top bar (breadcrumb: Up / Top) so the primary Prev/Next is the visually dominant control.
3. Style in `osbook-web.css`; keyboard: `n`/`p` still work.

## Verify

Rebuild anatomy HTML: the Next control is an obvious button (not buried in a text row), reachable at the content
foot; Prev likewise. Spot-check a bundle (multi-collection) page.
