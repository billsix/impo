#!/usr/bin/env node
/* tools/check-mobile.js — regression check that a built HTML book renders cleanly
 * on phones: (1) NO horizontal overflow on any page at a phone viewport, and
 * (2) the on-this-page right drawer works (button present, opens, closes).
 *
 * Reusable after any change to the shared web theme (osbook-web.css / osbook-web.js
 * / trench-web.css). Root causes + the manual snippets are in
 * tasks/reference/tooling/web-editions-mobile.md; this is the automated version.
 *
 * REQUIRES a headless browser (deliberately NOT a repo dependency — a dev-only tool):
 *     npm i playwright && npx playwright install chromium
 * then run so `require('playwright')` resolves, e.g. install into a scratch dir and
 * point NODE_PATH at it:
 *     NODE_PATH=/tmp/pw/node_modules node tools/check-mobile.js <built-site-dir> [width]
 *
 * <built-site-dir> = a book's built output site (the dir containing the *.html pages),
 * e.g. openstax/osbooks-college-algebra-bundle/checkout/output/college-algebra-2e.
 * Paths are relative to the CWD/arg, never container-absolute. Exits nonzero if any
 * page overflows, so it can gate a build.
 */
const { chromium } = require("playwright");
const fs = require("fs");
const path = require("path");

(async () => {
  const dir = process.argv[2];
  if (!dir) {
    console.error("usage: check-mobile.js <built-site-dir> [viewportWidth=390]");
    process.exit(2);
  }
  const width = parseInt(process.argv[3] || "390", 10);
  const files = fs.readdirSync(dir).filter((f) => f.endsWith(".html")).sort();
  const browser = await chromium.launch();
  const ctx = await browser.newContext({ viewport: { width, height: 844 } });
  const page = await ctx.newPage();

  const bad = [];
  let clean = 0;
  let drawer = null;
  for (const f of files) {
    await page.goto("file://" + path.resolve(dir, f), { waitUntil: "load" });
    // The user-visible failure is the PAGE scrolling sideways: measure it as the real
    // browser renders it (clip in place). Do NOT disable overflow-x:clip and hunt for
    // wide elements — that over-reports, flagging MathML/table content that correctly
    // scrolls WITHIN its own overflow-x:auto box, and the off-canvas drawers parked
    // off-screen on purpose. (To DIAGNOSE which element is too wide, see the manual
    // clip-disabled snippet in the reference doc; that is for finding a culprit, not
    // a pass/fail gate.)
    const r = await page.evaluate(() => {
      const vw = window.innerWidth;
      const sw = document.documentElement.scrollWidth;
      return { over: sw > vw + 1, sw };
    });
    if (r.over) bad.push({ f, sw: r.sw });
    else clean++;

    // Verify the on-this-page drawer once, on the first page that has one.
    if (!drawer) {
      const d = await page.evaluate(() => {
        const btn = document.getElementById("page-toc-toggle");
        if (!btn) return null;
        btn.click();
        const opens = document.body.classList.contains("toc-open");
        const scrim = document.getElementById("toc-scrim");
        if (scrim) scrim.click();
        const closes = !document.body.classList.contains("toc-open");
        return { links: document.querySelectorAll("#page-toc a").length, opens, closes };
      });
      if (d) drawer = Object.assign({ page: f }, d);
    }
  }
  await browser.close();

  console.log(`check-mobile @${width}px: ${files.length} pages | clean ${clean} | page-overflows ${bad.length}`);
  bad.slice(0, 20).forEach((b) => console.log("  PAGE OVERFLOW", b.f, "scrollWidth=" + b.sw));
  if (drawer) {
    console.log(`on-this-page drawer (${drawer.page}): links ${drawer.links}, opens ${drawer.opens}, closes ${drawer.closes}`);
  } else {
    console.log("on-this-page drawer: no page with >=2 sub-headings found to test");
  }
  process.exit(bad.length ? 1 : 0);
})();
