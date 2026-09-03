# HTML web edition: Furo-style sticky sidebars (book TOC left, on-page TOC right)

**Status:** DONE 2026-09-03 — sticky collapsible left book-TOC + right on-this-page + scrollspy; anchors already existed; verified anatomy (commit `547064f`)
**Priority:** 3
**Difficulty:** 5

## BLUF

Give the chunked HTML a Sphinx-Furo-style three-column layout: a **left sidebar** with the whole book's
chapter/section tree (current page highlighted), the **content** centered, and a **right sidebar** ("On this
page") listing the current page's sections — both sidebars **sticky** (fixed as you scroll). Responsive: collapse
to a hamburger on narrow screens. "Done" = every book's HTML has persistent left (book) + right (page) navigation
that don't scroll away, linking to real anchors; shared template/CSS/JS, done across all 16 books.

## Context / findings (verified 2026-09-03)

- **Anchors already exist** — the maintainer's "are there hrefs to sections/subsections?" question: **yes**.
  Content headings carry `id`s (`<h2 id="an-introduction-to-the-human-body">`, `<h3 id="mod:m45981">`, …), so the
  on-page (right) TOC can link straight to them. No converter change needed for anchors.
- **The book tree is in `sitemap.json`** (pandoc chunkedhtml emits it beside the pages): a nested
  `{section:{id,level,number,path,title}, subsections:[…]}` where `path` is `NNN-page.html#anchor`. This drives
  the left sidebar.
- Page structure is set by `tools/pandoc/chunked-template.html`; each page is one section (split-level 2).

## Design (researched: Sphinx Furo / MkDocs Material)

Three-column CSS **grid**: `[book-toc | content | page-toc]`. Sidebars `position: sticky; top:0; height:100vh;
overflow:auto`. Content `max-width` and centered. Responsive: hide the right TOC < ~1100px; turn the left TOC
into a hamburger-toggled drawer < ~900px.

**Left (book) TOC — build-time injection, NOT client fetch.** A `fetch('sitemap.json')` breaks under `file://`
(browsers block same-dir fetch), and readers open these locally. So a post-process step (`build_nav.py`, run by
`html.sh` after pandoc) reads `sitemap.json`, builds the nested TOC HTML once, and injects it into each page's
left-sidebar placeholder, marking the current page active. Robust offline, no JS needed for the tree.

**Right (page) TOC + scrollspy — JS from the page's own headings** (`osbook-web.js`). Reads `h2–h6[id]` in the
document (no fetch — the headings are in the page), builds the "On this page" list, and highlights the current
section on scroll (IntersectionObserver). Also wires the mobile sidebar toggle. Degrades gracefully with JS off
(sidebars still render; scrollspy just doesn't highlight).

## Plan (one layout pass, shared with the prev/next task)

1. `chunked-template.html`: 3-column layout wrapper around `$body$`; left `<nav class="book-toc">` placeholder;
   right `<nav class="page-toc">` placeholder; big Prev/Next footer buttons; `<script src="osbook-web.js">`.
2. `osbook-web.css`: grid, sticky sidebars, TOC styling (active highlight), buttons, responsive breakpoints,
   hamburger.
3. `tools/pandoc/build_nav.py`: inject the book TOC (from sitemap.json) into each page; run from `html.sh`.
4. `tools/pandoc/osbook-web.js`: page TOC + IntersectionObserver scrollspy + mobile toggle.
5. `html.sh`: after pandoc, run `build_nav.py`; copy `osbook-web.js` into each outdir (like the css).

## Verify

Rebuild anatomy HTML: left sidebar shows the full book tree with the current page marked and stays put on scroll;
right sidebar lists this page's sections and highlights while scrolling; anchors jump correctly; narrow-width
collapses cleanly. Then confirm a multi-collection bundle. EPUB is unaffected (no sidebars there — it's the
reader's own nav).
