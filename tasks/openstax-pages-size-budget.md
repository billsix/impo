# Fit the web editions into GitHub Pages' 1 GB (or decide what to publish)

**Status:** proposed — needs go-ahead
**Priority:** 5
**Difficulty:** 4
**Created:** 2026-11-21 (follow-on of `tasks/archive/impo/2026/11/21/openstax-publish-books.md`)

## BLUF

`make publish-pages` works, but the 28 web editions are 4.5 GB even with only the files their
pages use, and GitHub Pages refuses a site over 1 GB, so the script refuses to push the whole set.
Decide what the published site holds and make it fit. Done = a `make publish-pages` that pushes
the chosen set under the limit, and the choice recorded in `tasks/reference/openstax/publishing.md`.

## Context

- Measurements and the publishing design: `tasks/reference/openstax/publishing.md` ("The size
  problem"). Per-book sizes print when `make publish-pages` refuses (or `DRY_RUN=1`).
- The figures are already web-sized JPEGs; the volume is their count (anatomy-and-physiology-2e
  alone references 722 images, 0.50 GB).
- Cross-book links (`tasks/reference/tooling/cross-book-links.md`) are relative between books on
  the one site; a book left off the site makes its incoming links 404 (the link checker reports
  them as "not published here").

## Options (for the maintainer)

1. **Publish a subset** under 1 GB with `BOOKS="..."` (e.g. the math ladder: prealgebra bundle
   0.49 GB + college-algebra-2e 0.10 GB + calculus volumes 0.23 GB ≈ 0.82 GB) and leave the other
   books as Release downloads only. No code change.
2. **Recompress for the web** (e.g. JPEG quality 70 at the same 825 px) in `publish-pages.sh`; needs
   ImageMagick on the host and a measurement — likely 2–3× smaller, still over 1 GB for all 28.
3. **Deduplicate a bundle's media** into one shared directory per bundle on the site (rewrite
   `src="media/…"` to `../_media/<bundle>/…`): saves the copies shared by volumes (the two
   college-algebra editions and the two chemistry editions are near-identical sets).
4. **Host the images elsewhere** (another Pages repo per family, each under 1 GB, or the Pi), with
   the HTML on impo's Pages. Most moving parts.

Recommendation: 1 now (it needs nothing), then measure 2+3 together if all books should be online.

## Also noted here

- Page file names contain `:` (`059-mod:m81444.html`), which Windows cannot unpack from
  `<book>-html.zip`: its own task now, `tasks/openstax-html-filenames-without-colons.md`.
