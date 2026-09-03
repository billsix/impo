# Verify (and fix) the HTML web edition on mobile / narrow viewports

**Status:** open — needs verification (subtask of the archived HTML-nav work)
**Priority:** 4
**Difficulty:** 2

## BLUF

The desktop three-column nav (sticky book TOC left, content, on-this-page right — see the archived
`openstax-html-sticky-sidebars.md` / `openstax-html-nav-prevnext.md`) has responsive CSS + a JS hamburger drawer,
but **none of it has been verified on an actual phone / narrow viewport**. This task is to check the mobile
experience and fix whatever's off. "Done" = the pages are comfortably usable on a phone: the book TOC is
reachable via the hamburger, Prev/Next are easy to tap, content isn't squeezed, nothing overflows horizontally.

## Context — what's already built (to verify, not re-build)

In `osbook-web.css` / `osbook-web.js` (commit history around `547064f`–`04c22cc`):
- **`@media (max-width: 1180px)`** — drops the right "On this page" sidebar (2-column: book TOC + content).
- **`@media (max-width: 900px)`** — single content column; the left book TOC becomes a **fixed off-canvas
  drawer** (`transform: translateX(-100%)`), opened by the **`☰ Chapters`** button (`#nav-toggle`, fixed
  top-left) which toggles `body.nav-open`; a scrim (`#nav-scrim`) dims the page; tapping a TOC link or the scrim
  closes it (`osbook-web.js` `mobileToggle`).
- Content gets `padding-top` to clear the fixed toggle button.

## What to check (on a real narrow viewport / phone, or a browser at ~375–414px wide)

1. **Hamburger** — `☰ Chapters` visible top-left; tapping opens the drawer; the scrim appears; tapping a chapter
   navigates and closes; tapping the scrim closes without navigating.
2. **No horizontal scroll / overflow** — content, wide tables, code blocks, and math don't force the page wider
   than the screen (tables/code should scroll inside their own box, not the page).
3. **Prev/Next buttons** — still large and easy to tap; they stack or stay side-by-side acceptably at phone width.
4. **Readability** — font size / line length comfortable; the fixed toggle doesn't cover the first heading.
5. **Right TOC** — correctly hidden < 1180px (its content is reachable by scrolling the page).
6. **Landscape + tablet widths** (~768px, ~1024px) — the 2-column and drawer breakpoints feel right; tune the
   `900px` / `1180px` thresholds if a tablet lands awkwardly between them.

## Likely fixes if issues appear

- Horizontal overflow from a wide element → ensure `table`, `pre`, and math wrappers have `max-width:100%` +
  `overflow-x:auto` (some may already; verify per element).
- Toggle button overlapping content → adjust `.content` `padding-top` at the 900px breakpoint.
- Drawer width / tap targets too small → widen `.book-toc` drawer or increase link padding on mobile.
- Prev/Next cramped → `flex-direction: column` for `.prevnext` under ~500px.

## Note

I (the agent) can't drive a real browser in this sandbox (no headless browser installed), so this needs either
the maintainer's eyes on a phone, or a browser resized narrow. The responsive CSS is written and structurally
sound; this task is the empirical check + tuning.
