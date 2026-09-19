# Fix the HTML web edition on mobile: overflow + on-this-page drawer

**Status:** DONE (2026-09-19) — fixes implemented in the shared web assets and browser-verified; the only
remaining item is the maintainer's final phone confirmation after a rebuild. Affects **both** families
(OpenStax + trench) — they share `openstax/tooling/tools/pandoc/osbook-web.css` + `osbook-web.js` (trench
reads them via its `/osbook-assets` build mount). Not archived pending the phone check.
**Priority:** 4
**Difficulty:** 3

## BLUF

On a phone the desktop 3-column theme had two problems, both now fixed: **(1) horizontal overflow** in
portrait (page scrolled sideways), and **(2) no on-this-page navigation**. Fixed by constraining the
content column and scrolling wide equations/tables, and by adding an upper-right **"On this page" drawer**
that mirrors the upper-left "☰ Chapters" drawer. Verified with a real headless browser. **Full analysis,
root causes, and the how-to-verify method are in the reference doc
`tasks/reference/tooling/web-editions-mobile.md`** — read that before touching the assets; this task is
just the work record.

## What shipped (2026-09-19)

- **Overflow fix** (`osbook-web.css`): `*{box-sizing:border-box}`; `.content{overflow-wrap:anywhere}`;
  and the key one — `@media(max-width:1180px){ .content{max-width:100%} }`. Root cause (see the reference
  doc): a block MathML equation renders at its intrinsic width (Chromium ignores `overflow-x`/`max-width`
  on `<math>`), and `.content{margin:0 auto}` makes the grid item shrink-to-content, so `.content` grew
  past its track (455px in a 358px track) and the page scrolled. Capping `.content` at the track fixes it;
  the block-math + `.content pre`/`table` (mobile) `overflow-x:auto` then keep wide content scrolling in
  place. Trench adds `table.equation, table.tabular{display:block;overflow-x:auto}` in `trench-web.css`.
- **On-this-page as an upper-right drawer** (`osbook-web.js` + `osbook-web.css`): `buildPageToc()` creates
  a `#page-toc-toggle` button ("On this page", upper-right) + `#toc-scrim` when the page has ≥2
  sub-headings; CSS (`≤1180px`) turns `#page-toc` into a fixed off-canvas RIGHT drawer
  (`translateX(100%)` → `body.toc-open` → `none`). Mirrors the left `#nav-toggle`/book-TOC drawer. Both
  drawers close on scrim-tap and link-tap.

## Verified (Playwright headless Chromium, at 320–430px)

Full clean reproduction (`fetch→apply→image→make html` on college-algebra): **0 of 370 pages overflow**
across the 4 collections. On a real content page (022, 390px): page does not overflow; 9/22 block
equations scroll within their box; the "On this page" button shows and opens the right drawer (23 links,
slides in to on-screen); scrim/link taps close both drawers.

## Remaining
- **Maintainer phone confirmation** after `./apply.sh && make html` **and a hard-refresh** (the CSS/JS
  filenames are unchanged, so a phone caches the old versions — a very common "still looks broken").
- The durable "build auto-refreshes the overlay" fix (so `apply.sh` can't be forgotten) is proposed in
  `tasks/openstax-build-refresh-overlay.md`.

## Related
- `tasks/reference/tooling/web-editions-mobile.md` — the durable reference (root causes, propagation trap,
  drawer symmetry, verification method).
- `tasks/openstax-build-refresh-overlay.md` — the proposed stale-checkout durable fix.
