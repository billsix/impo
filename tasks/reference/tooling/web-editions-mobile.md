# Web editions: the mobile/responsive layer (osbook-web.css/.js) — how it works, how it breaks, how to verify

Durable notes on the shared web-edition theme's **mobile behaviour**, distilled from a long debugging
session (2026-09-19) chasing "text too wide on my phone / no right menu" on the OpenStax books. States
what is TRUE, not a work log. Read before touching `openstax/tooling/tools/pandoc/osbook-web.css` or
`osbook-web.js`, or when a book "looks broken on mobile."

## The assets + who uses them

- `openstax/tooling/tools/pandoc/osbook-web.css` + `osbook-web.js` — the shared 3-column "Furo-like"
  theme (left book-TOC | content | right on-this-page), used by **both** families: the OpenStax books
  (pandoc chunked HTML) and the trench book (make4ht HTML, which reads them via its `/osbook-assets`
  build mount + layers `trench-web.css`). Fix a mobile bug here once → both families get it.
- Left book-TOC is baked per page by `build_nav.py`; the right "on this page" + scrollspy + mobile
  drawer are `osbook-web.js`'s job (built from the page's own `h2/h3/h4[id]`).

## PROPAGATION — the #1 cause of "I fixed it but it still looks broken"

An edit to the shared assets does **not** reach a built book until the book's **checkout** is refreshed.
The chain (verified): `apply.sh` copies `../tooling/tools` → `checkout/tools/`; then `html.sh:61,68` copies
`$ROOT/tools/pandoc/osbook-web.css|.js` (where `$ROOT=/book`, the **checkout**) into the output. The
Makefile mounts only `/book` live (+ entrypoint scripts), NOT `tools/pandoc`. So:

- **You MUST `./apply.sh` before `make html`** after editing the shared assets, or the build serves the
  stale pre-edit copy. This bit three times (colophon PDF, colophon web, the mobile fix). The durable fix
  is proposed in `tasks/openstax-build-refresh-overlay.md` (make the build auto-`apply`).
- **Browser cache** is the second stale trap: the stylesheet is always named `osbook-web.css`, so a phone
  that visited before serves the CACHED old CSS even after a correct rebuild → hard-refresh / private tab
  to test. (A cache-buster `?v=<sha>` on the link would end this; not yet done.)
- A green desktop + stale mobile is almost always one of these two, not a code bug.

## Responsive design (as built)

- **Breakpoints** (px, in `osbook-web.css`): `≤1180px` drops the right static sidebar and the layout goes
  2-column (book-TOC + content); `≤900px` goes single-column and the book-TOC becomes a fixed off-canvas
  **drawer** (`transform:translateX(-100%)`) opened by the `☰ Chapters` button (`#nav-toggle`), dimmed by
  `#nav-scrim`. (Furo, for comparison, uses `em` breakpoints and drops the right TOC at ~82em BEFORE the
  left nav at ~67em, and makes the right TOC a second checkbox-driven drawer `#__toc`; we instead surface
  it inline — below.)
- **Right "On this page" on mobile — an off-canvas RIGHT drawer** (mirror of the left ☰ Chapters drawer,
  Furo's `#__toc` pattern). Below 1180px the static right column is turned into a fixed right drawer
  (`.page-toc { position:fixed; right:0; transform:translateX(100%) }`, `body.toc-open .page-toc
  {transform:none}`), opened by an upper-right **`#page-toc-toggle`** button ("On this page") and dimmed by
  `#toc-scrim`. `osbook-web.js` `buildPageToc()` creates the button + scrim **only when the page has ≥2
  `h2/h3/h4[id]`** (so a chapter *landing* page correctly has no button — same as its empty desktop right
  sidebar). Tapping a link or the scrim closes it. (Earlier this was a `<details>` collapsed at the top of
  the content; the maintainer asked for the symmetric left-button/right-button drawers instead, 2026-09-19.)
  If "no right menu" is reported, first check the page actually has sub-headings, and that the build isn't
  stale.
- **Drawer dismissal:** tapping a chapter link OR the dimming scrim (`#nav-scrim`, tap-outside) closes the
  drawer (`osbook-web.js` `mobileToggle`).

## Horizontal-overflow root causes + fixes (the hard-won part)

Symptom: in **portrait** (~390px) the page scrolls sideways; landscape (~800px) is fine → a fixed-width
element wider than the portrait viewport. On these math books it is almost always a **display equation**.

1. **MathML `<math>` ignores `overflow-x`/`max-width` on its own box** (Chromium MathML Core). A block
   equation renders at its intrinsic width (measured 423px on a 390px screen) regardless of
   `math[display="block"]{max-width:100%;overflow-x:auto}` — that rule is a no-op until its *container* is
   width-definite.
2. **The real amplifier: `.content { margin: 0 auto }` makes the grid item shrink-to-CONTENT.** With
   auto horizontal margins, a grid item is sized to its content (capped by `max-width`), NOT stretched to
   its track. So when the content includes the unbreakable 423px math, `.content` grows PAST its track
   (measured: 358px track, **455px `.content`**) and the whole `.layout`/page overflows. **`min-width:0`
   alone does NOT fix this** (it permits shrinking but the auto-margin content-sizing still wins).
3. **THE FIX (in `osbook-web.css`, `@media max-width:1180px`): `.content { max-width: 100% }`** — pins the
   grid item to its track. Then `.content`=358px, the block-math rule's `max-width:100%` finally binds
   (math capped to the column), and wide equations `overflow-x:auto`-scroll inside their box. Verified on
   a real page: `.content` 455→358, page overflow gone, 9/22 block equations scroll in place.
4. **Supporting rules** (all in `osbook-web.css`): `*{box-sizing:border-box}` (padding never adds width);
   `.content{overflow-wrap:anywhere}` (long URLs/identifiers break); `.content pre` + `.content table`
   (mobile) `overflow-x:auto` (wide code/tables scroll). Trench adds `table.equation, table.tabular
   {display:block;overflow-x:auto}` in `trench-web.css` (tex4ht wraps display math in width:100% tables,
   the same "container isn't a scroll box" problem).
5. **`html,body{overflow-x:clip}` is a BACKSTOP.** It stops the page scrolling sideways even if a scroll
   rule is missed — but it *clips* (cuts off) content that isn't in its own scroll box, so it's a safety
   net, NOT a substitute for the real fixes above (wide content must SCROLL in an `overflow-x:auto` box,
   not be clipped-lost). For testing: clip clamps `document.scrollWidth`, which is exactly right for the
   VERIFY metric (no page scroll = the user's experience — see below) but means a scrollWidth test won't
   reveal a clipped-lost element; so when DIAGNOSING a culprit, disable clip and measure element rects.

## How to VERIFY mobile (there is no browser in the base sandbox by default)

- **Layout/overflow needs a REAL browser.** `jsdom` does NOT do layout (no `getBoundingClientRect`
  widths, no CSS media/visibility), so it can only verify DOM/JS (e.g. that the `#page-toc-toggle` button +
  `#toc-scrim` get injected). For overflow, install a headless browser: `npm i playwright` +
  `npx playwright install chromium` (network is available), then render at a phone viewport and measure.
- **The automated regression check: `tools/check-mobile.js`** (Playwright). Scans every page of a built
  site for **page** horizontal scroll and verifies the on-this-page drawer; exits nonzero on overflow.
  `NODE_PATH=<pw-install>/node_modules node tools/check-mobile.js <built-site-dir> [width]`.
- **VERIFY vs DIAGNOSE — do not confuse them:**
  - **Verify (pass/fail):** measure the **page**, clip in place (the real experience) —
    `document.documentElement.scrollWidth > window.innerWidth`. This is what `check-mobile.js` does. It's
    what the maintainer feels as "scrolls sideways." (On college-algebra after the fix: 0/370 pages.)
  - **Diagnose (find the culprit):** to locate WHAT is too wide, disable clip
    (`addStyleTag('html,body{overflow-x:visible!important}')`) and list elements with `getBoundingClientRect().right
    > innerWidth`, then walk the width chain `html → body → .layout → grid track
    (getComputedStyle(.layout).gridTemplateColumns) → .content → the math's <p> → <math>` (the first box
    wider than the viewport is the break — here it was `.content`). **This over-reports for a gate:** it
    flags MathML/table content that correctly scrolls *within* its own `overflow-x:auto` box, and the
    off-canvas drawers parked off-screen. Use it to find a cause, NOT as pass/fail.
- **Full reproduction from clean** (what to do after a `git clean -fdx`): in a book folder,
  `./fetch.sh && ./apply.sh && make image && make html`, then Playwright-measure the output pages at
  320/360/390/430 px. Result on college-algebra after the fix: **0/370 pages overflow** across the 4
  collections; the mobile "On this page" injects on section pages.
- **jsdom check** (JS injection only): load a built page with `runScripts:'outside-only'`, `eval` the JS,
  then `document.dispatchEvent(new Event('DOMContentLoaded'))` (jsdom leaves `readyState:'loading'`, so
  the IIFE's listener must be fired manually), then assert `#page-toc-toggle` (the drawer button) exists.

## Mobile drawer symmetry (as built)
Two symmetric off-canvas drawers, each with its own fixed toggle button and scrim (Furo's dual-drawer
model): **left** ☰ Chapters (`#nav-toggle` → `body.nav-open` → the book-TOC drawer) and **right**
"On this page" (`#page-toc-toggle` → `body.toc-open` → the on-this-page drawer). The right button/scrim are
JS-created only when the page has an on-this-page. Both close on scrim-tap and link-tap.

## Pointers
- `tasks/archive/impo/2026/09/20/openstax-html-mobile-verify.md` — the fix task (verification record).
- `tasks/openstax-build-refresh-overlay.md` — the proposed durable fix for the stale-checkout trap.
- Furo mechanism reference: github.com/pradyunsg/furo `src/furo/assets/styles/_scaffold.sass`.
