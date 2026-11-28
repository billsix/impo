# Web edition page names without `:`, so the HTML zips unpack on Windows

**Status:** proposed — needs go-ahead
**Priority:** 6
**Difficulty:** 3
**Created:** 2026-11-21 (William Emerison Six <billsix@gmail.com>), split out of
`tasks/archive/impo/2026/11/28/openstax-pages-size-budget.md` ("Also noted here").

## BLUF

The web edition's page files are named like `059-mod:m81444.html`. Windows cannot create a file with
`:` in its name, so `<book>-html.zip` (a download on each book's first page) fails to unpack there.
Done = page names without `:` in every book, the cross-book index regenerated, links still resolve
(0 broken), and a zip unpacks with a Windows-safe name check.

## Context

- The names come from pandoc's `--chunk-template="%n-%i.html"` in `openstax/tooling/entrypoint/html.sh`
  (`%i` is the section id, which carries `mod:`). Options: a template without `%i`, or sanitizing the id
  (e.g. the converter emitting ids without `:`).
- `crossbook/index/*.json` stores page names (`tasks/reference/tooling/cross-book-links.md`), so it must
  be regenerated; the nav builder and the downloads box may also hard-code names — grep for `mod:`.
- A rename breaks any outside link to the old page names; nothing is published yet, so now is cheap.

## Plan

1. Pick the naming; change it in one place; rebuild one book and check every internal link.
2. Regenerate the cross-book index; rebuild the math ladder; run the link check.
3. Add a check (in `tools/` or the build) that no output file name contains `:`.
