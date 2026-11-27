# Add an emoji font to the toolchain image, so the PDFs print five pictographs as themselves

**Status:** proposed — needs go-ahead
**Priority:** 7
**Difficulty:** 3 (a package in the Dockerfile, one entry in the class's fallback chain, an image rebuild and one book's PDF)
**Created:** 2026-11-27 (William Emerison Six <billsix@gmail.com>: "make a task about the emoji font")

## BLUF

No font in the toolchain image has the pictographs `🔎 📝 📍 📖 📎`, so since 2026-11-27 the PDFs print a stand-in symbol for each (`⌕ ✎ ⚑ ☰ ❖`). An emoji font in the image and in the class's fallback chain would print the real ones. Done means the font is installed by `openstax/tooling/Dockerfile`, the five `\newunicodechar` stand-ins are gone from `osbook.cls`, and the PDF of *Life, Liberty, and the Pursuit of Happiness* shows the pictographs with no "Missing character" line in its log.

## Context

**Read first:** `tasks/reference/tooling/converters.md` ("Characters no font has") and the done-record `tasks/archive/impo/2026/11/27/openstax-pdf-characters-missing-from-the-body-font.md`.

- **Where the pictographs are:** only in *Life, Liberty, and the Pursuit of Happiness* among the 57 books built on 2026-11-27. They open module titles and mark the kind of resource: `🔎` a narrative (366 places in the source), `📝` a lesson (170), `📍` a decision point (88), `📖` a chapter's introductory essay (48), `📎` an inquiry organizer (46). `✒` and `✏`, which mark primary sources and unit essay activities, are already printed by the fallback fonts.
- **Why it was not done with the fallback chain:** adding a package changes what the image ships, which is the maintainer's decision; the chain uses only fonts the image already had (FreeSerif, STIX Two Math, TeX Gyre DejaVu Math, Libertinus Serif).
- **The HTML and EPUB** keep the source's pictographs and need nothing.

### What has to be found out

- **Which font.** It has to be one LuaTeX can use for a single glyph in running text. A monochrome outline font is the safe kind (Fedora packages to look at: Noto Emoji in its monochrome form, Symbola). A colour font (Noto Color Emoji) needs luaotfload's HarfBuzz mode and a renderer for its colour tables; whether that works inside a `fallback` chain is untested here. `dnf search emoji font` in the image lists what Fedora 45 offers.
- **Bold and heading faces.** The pictographs sit in module titles, which are set in bold Noto Sans; the fallback has to answer for that face too (the chain is already passed to the heading font).
- **Image size and the pinned image.** `CLAUDE.md` ("Contracts") keeps an exported image tar as the build's last outside dependency; after the change `make image-export` is due again.

## Plan

- [ ] In the toolchain container: `dnf install` the candidate, set the five characters in a test document with the font appended to `osfallback`, and read the log (the method that chose the chain).
- [ ] Add the package to `openstax/tooling/Dockerfile` and the font to the chain in `openstax/tooling/latex/osbook.cls`; delete the five `\newunicodechar` stand-in lines.
- [ ] Rebuild the image and `make pdf` in `openstax/osbooks-life-liberty-and-pursuit-happiness`; `pdf.sh` must end with "no character is missing from the fonts", and one title page is read.
- [ ] Record it in `tasks/reference/tooling/converters.md` ("Characters no font has").

## Open questions

1. Is a monochrome pictograph acceptable in the PDF, or should it be in colour as on the web? The agent recommends monochrome: it is the kind known to work in a fallback chain, and the PDF's titles are one colour.
