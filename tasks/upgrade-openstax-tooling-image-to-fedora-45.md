# Upgrade the OpenStax tooling image from Fedora 44 to Fedora 45

**Status:** proposed — needs go-ahead
**Priority:** 5
**Difficulty:** 3
**Started:** 2026-11-18 (William Emerison Six <billsix@gmail.com>)

## BLUF

`openstax/tooling/Dockerfile` (the shared build image for every `openstax/osbooks-*` port) is
`FROM registry.fedoraproject.org/fedora:44`; the container template is on Fedora 45. Move it to
45. Done = `make image` builds on 45 and at least one book's `make dist` (PDF, HTML and EPUB)
builds and looks the same as before.

## Context

- References to update: `openstax/tooling/Dockerfile` (the `FROM`, and the header comment
  "Fedora 44 + TeX Live …") and `openstax/CLAUDE.md` ("`Dockerfile` — Fedora 44 + TeX Live …").
- Risk is mostly in TeX Live and the fonts: a Fedora release can rename or split `texlive-*`
  packages, and a newer TeX Live can change layout. Compare one book's PDF page count and spot-check a
  few pages before and after. Also check `python3-lxml`, `pandoc` and `rsvg-convert`
  resolve on 45. (runClaudeInContainer found `shfmt` and `procs` dropped from Fedora 45, which
  is the kind of break to watch for.)
- Every `openstax/osbooks-*/Makefile` builds this one image (context `../tooling`), so a single
  change covers all books. None of them names a Fedora version itself (checked 2026-11-18).

## Plan

1. Before: build one book's `make dist` on the current image and record the PDF page count.
2. Change the `FROM` to `fedora:45`; `make image`; fix any package that no longer resolves.
3. After: rebuild the same book, compare, and build the lean `WITH_TEXLIVE=0` image too (the
   Dockerfile's "Whether to install TeX Live" flag).
4. Update the two doc mentions.
