# Fix the HTML web edition on mobile: horizontal overflow + missing right TOC

**Status:** IMPLEMENTED 2026-09-19 — the fixes below are applied to the shared assets
(`openstax/tooling/tools/pandoc/osbook-web.css` + `osbook-web.js`) and the trench adapter
(`trench/elementary-differential-equations/tools/trench-web.css`), so **both** families get them (the
trench book reads the shared assets via its `/osbook-assets` build mount). JS syntax-checked; the new
rules verified present in a rebuilt site. **Remaining: maintainer phone re-verification** (open the site
on a phone — no sideways scroll, and the "On this page" collapsible appears under each page title). Not
archived pending that check.
**Priority:** 4
**Difficulty:** 3

## What shipped (2026-09-19)
- `osbook-web.css`: `box-sizing:border-box` globally; `html,body{overflow-x:clip}`; `.layout>*{min-width:0}`;
  `.content{overflow-wrap:anywhere}`; `math[display=block]` + `.content pre` + (mobile) `.content table`
  scroll within the column; and the `.page-toc-mobile` `<details>` styles (hidden ≥1180px, shown below).
- `osbook-web.js`: `buildPageToc()` now also clones the right-TOC list into a `<details class="page-toc-mobile">`
  "On this page" inserted just under the page's `<h1>`, closing on link-tap.
- `trench-web.css`: `table.equation, table.tabular { display:block; overflow-x:auto }` (tex4ht wraps
  display math in width:100% tables, which the `math[display=block]` rule can't constrain).

## BLUF

On a phone the desktop 3-column Furo-like nav (left book-TOC, content, right "On this page") has two
problems, both now confirmed: **(1) horizontal overflow** — the page scrolls left/right a few px (content
slightly wider than the viewport); **(2) the right "On this page" TOC is gone** — it's `display:none`
below 1180px, so mobile readers lose in-page navigation (the left chapter drawer works fine). The left
drawer is good and stays. "Done" = no sideways scroll on a phone, and the right TOC is reachable on
mobile (as a collapsible), on both the OpenStax and trench books. The fixes are in the **shared** assets
(so both families benefit) + a trench-specific CSS rule for tex4ht's equation tables.

## Bug 1 — horizontal overflow (diagnose, then fix)

### Diagnose first (run on the actual phone / DevTools device mode)
Paste in the browser console on an offending page — it flags every element wider than the document:
```js
const w = window.innerWidth;
[...document.querySelectorAll('*')].forEach(el => {
  const r = el.getBoundingClientRect();
  if (r.right > w + 1 || r.left < -1) { console.log(Math.round(r.right), w, el); el.style.outline='2px solid red'; }
});
```
(Or the no-console visual sweep: `* { outline: 1px solid red !important; }` — outlines don't affect
layout, so the box poking past the right edge is the culprit.) Walk from the flagged element up its
ancestors and apply the matching fix below.

### Root causes identified (from the CSS, before the phone diagnosis)
- **No global `box-sizing: border-box`** in `osbook-web.css` — padding adds to width, so padded elements
  exceed their column.
- **The off-canvas chapter drawer** (`.book-toc` at ≤900px: `position:fixed; left:0; width:17rem;
  transform:translateX(-100%)`) isn't clipped — a classic "scroll left a few px" cause.
- **Grid child min-width** — grid/flex items default to `min-width:auto` and refuse to shrink below their
  widest unbreakable content (a wide equation, table, long token), blowing past the `1fr` track. `minmax(0,1fr)`
  alone is often not enough; the child needs `min-width:0`.
- **Trench-specific:** tex4ht wraps block equations in `table.equation { width:100% }` (≈427 block-math +
  274 equation-tables per chapter). The `math[display=block]{overflow-x:auto}` rule doesn't catch them
  because the *table* is the constraining box, so a wide equation widens the page.

### The fixes — `osbook-web.css` (shared; add near the top / in the responsive block)
```css
/* padding/border never add to width */
*, *::before, *::after { box-sizing: border-box; }

/* grid children must be allowed to shrink below their content */
.layout > * , .content { min-width: 0; }

/* clip any residual overflow (e.g. the off-canvas drawer); `clip` beats `hidden`
   — it doesn't create a scroll container or break `position:sticky`. */
html, body { overflow-x: clip; }

/* break long unbreakable text (URLs, long identifiers) instead of widening the page */
.content { overflow-wrap: anywhere; }

/* wide blocks scroll WITHIN their column, not the page. overflow-y:hidden avoids a
   spurious vertical scrollbar the x-scrollbar would otherwise trigger. */
math[display="block"] { display:block; max-width:100%; overflow-x:auto; overflow-y:hidden; }
.content pre        { max-width:100%; overflow-x:auto; }
.content table      { display:block; max-width:100%; overflow-x:auto; }   /* or wrap each <table> in a scroll <div> to keep table semantics */
```
Also: **never use `width:100vw`** anywhere (it includes the scrollbar gutter → ~15px overflow on any
scrolling page). Grep the CSS to confirm none crept in (none at time of writing).

### The fix — `trench-web.css` (trench only; tex4ht equation/tabular tables)
```css
/* tex4ht wraps display math in table.equation (width:100%) and arrays in table.tabular;
   let a wide one scroll in its column instead of widening the page. */
table.equation, table.tabular { display:block; max-width:100%; overflow-x:auto; }
```
(Trench's `bookW.css` also has `white-space:nowrap` on `.obeylines-*`/`td.displaylines`; if the diagnosis
flags one, either allow it to scroll via the wrapper above or drop the `nowrap` on mobile.)

## Bug 2 — surface the right "On this page" TOC on mobile

**Don't just `display:none` it.** Furo keeps its right TOC reachable at every width by turning it into a
second checkbox-driven off-canvas drawer (`#__toc`, its own "contents" button, off-canvas right) — pure
CSS, no JS. That's Option B below. But since `osbook-web.js` **already builds the right-TOC `<ul>` from
`h2/h3/h4[id]`**, the simplest robust fix is Option A.

### Option A — collapsible `<details>` "On this page" at the top of content (RECOMMENDED)
Zero drawer state, no overlay/focus-trap/scroll-lock, accessible for free (native disclosure). On mobile
it appears above the article; on desktop it's hidden (the real sidebar shows).

`osbook-web.js` — when building the page TOC, ALSO emit a mobile copy at the top of `main.content`:
```js
// after building the <ul> of heading links (reuse the same list-building code):
if (heads && heads.length >= 2) {
  var det = document.createElement('details');
  det.className = 'page-toc-mobile';
  var sum = document.createElement('summary'); sum.textContent = 'On this page';
  det.appendChild(sum);
  det.appendChild(ul.cloneNode(true));           // clone the generated list
  var main = document.querySelector('main.content');
  main.insertBefore(det, main.firstChild);
  det.addEventListener('click', function (e) {    // tap a link -> jump + close
    if (e.target.closest('a')) det.removeAttribute('open');
  });
}
```
`osbook-web.css`:
```css
.page-toc-mobile { display:none; }                     /* desktop: hidden (real sidebar shows) */
@media (max-width: 1180px) {                           /* the existing right-TOC breakpoint */
  .page-toc { display:none; }                          /* keep hiding the static right column */
  .page-toc-mobile {                                   /* ...surface the same links here */
    display:block; margin:0 0 1.5rem; border:1px solid var(--os-rule);
    border-radius:6px; background:var(--os-lt);
  }
  .page-toc-mobile > summary { cursor:pointer; padding:.6rem .9rem; font-weight:600; color:var(--os-dk);
    font-family:system-ui,sans-serif; list-style:none; }
  .page-toc-mobile[open] > summary { border-bottom:1px solid var(--os-rule); }
  .page-toc-mobile > ul { margin:.4rem 0; padding:.2rem .9rem .6rem 1.4rem; list-style:none; }
  .page-toc-mobile a { display:block; padding:.2rem 0; color:#555; text-decoration:none; }
}
```
Note for **trench**: its per-chapter pages already populate the right TOC from `h3.sectionHead`, so this
gives trench a real "On this page" (the chapter's sections) on mobile too — no trench-specific change needed
beyond the shared asset.

### Option B — second `#__toc`-style drawer (only if the exact Furo feel is wanted)
Mirror the existing left `.book-toc` drawer: a second toggle button in the header, `.page-toc{position:fixed;
right:0; transform:translateX(100%)}`, `body.toc-open .page-toc{transform:none}`, a second overlay/scrim,
and reuse the left drawer's scroll-lock. More moving parts; you then own focus-trap + Esc-to-close that
`<details>` gives free. Furo's mechanism (for reference): hidden `<input id="__toc" type="checkbox">` +
`<label class="toc-overlay-icon" for="__toc">`; `#__toc:checked ~ .page .toc-drawer{right:0}`.

## Breakpoint note (optional tuning)
Furo drops the **right** TOC at ~82em (~1312px) and the **left** nav at ~67em (~1072px) — one before the
other, in `em` (scales with font-size). The current theme uses a single 1180/900 px pair. Consider
switching to `em` and dropping the right column a bit earlier than the left, so tablets (~768–1024px) get
the left sidebar + the collapsible "On this page" rather than an abrupt both-gone state. Not required —
just deliberate.

## Files to edit
- `openstax/tooling/tools/pandoc/osbook-web.css` — box-sizing, `min-width:0`, `overflow-x:clip`,
  `overflow-wrap`, wide-block scroll rules, the `.page-toc-mobile` styles. (Shared → fixes both families.)
- `openstax/tooling/tools/pandoc/osbook-web.js` — emit the `.page-toc-mobile` `<details>` (Option A).
- `trench/elementary-differential-equations/tools/trench-web.css` — the `table.equation`/`table.tabular`
  scroll rule (tex4ht-specific). The trench book reads osbook-web.css/js via the `/osbook-assets` build
  mount, so the shared fixes reach it automatically; only the tex4ht table rule is trench-local.

## Verify
- Re-run the §diagnose snippet on a phone → no element wider than the viewport; no sideways scroll.
- The "On this page" collapsible appears on a phone and its links jump to the right sections.
- Desktop unchanged (the `.page-toc-mobile` is `display:none` ≥1180px; the real sidebars still show).
- Check one OpenStax book AND the trench book (they share the assets).

## Sources (from the 2026-09-19 research)
- Furo mobile mechanism (dual checkbox drawers, breakpoints): github.com/pradyunsg/furo
  (`src/furo/assets/styles/_scaffold.sass`, `variables/_layout.scss`); pradyunsg.me/furo/.
- Grid/flex `min-width:0`: css-tricks.com/preventing-a-grid-blowout/ ; defensivecss.dev/tip/grid-min-content-size/.
- Overflow diagnosis + `100vw`: css-tricks.com/findingfixing-unintended-body-overflow/ ;
  stevefenton.co.uk/blog/2022/12/detect-overflowing-elements/.
- Wide-math/table scrolling: akshat.blog/posts/mathjax-scrollable-box-display-mode/ ;
  MDN `overflow-wrap`, `getBoundingClientRect`.
