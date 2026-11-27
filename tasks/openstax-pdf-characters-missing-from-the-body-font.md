# The PDFs print the characters the body font lacks

**Done 2026-11-27** (agent; found the same day while adding seven book folders. William Emerison Six <billsix@gmail.com>, 2026-11-27: "for the three defect tasks, make a branch, turn gpg signing off, do the work, commit, archive, commit").

## What was wrong

LuaLaTeX prints nothing where the font in use has no glyph for a character and says so only in the log. The logs of the books built on 2026-11-27 held 7,323 "Missing character" lines in 27 books: letters with marks in names (Introduction to Philosophy 2e), `ℏ` and arrows met in prose (the physics and chemistry books), fractions and subscript digits (Nutrition for Nurses), pictographs that mark kinds of resource (Life, Liberty, and the Pursuit of Happiness), and quotation marks and dashes saved in the wrong encoding (Statistics, Biology, Physics).

## Decisions (William Emerison Six <billsix@gmail.com>, 2026-11-27: "for your questions, whatever you recommend")

- **A fallback font chain**, not one `\newunicodechar` line per character, so a character nobody has listed is covered too.
- **Pictographs are printed from a font in the image where one has the glyph.** None has the five emoji, so each prints as the nearest symbol the fallback fonts do have (`🔎 📝 📍 📖 📎` as `⌕ ✎ ⚑ ☰ ❖`). An emoji font in the image would print the real ones; that changes what the image ships and was left for the maintainer to decide.
- **The converter repairs the mis-encoded characters** for all three editions, since the right character is known.

## What was done

- `openstax/tooling/latex/osbook.cls`: `luaotfload.add_fallback("osfallback", …)` with FreeSerif, STIX Two Math, TeX Gyre DejaVu Math and Libertinus Serif (all in the image), passed to the body and heading fonts as `RawFeature={fallback=osfallback}`; five `\newunicodechar` lines for the pictographs. `openstax/osbooks-calculus-bundle/bookstyle.tex` passes the same feature to its own body font. The chain was chosen by setting every missing character in a test document and reading its log.
- `convert.py`: `_MISENCODED` (U+0080 to U+009F read as Windows-1252; the Symbol font's alpha and dash) and `_TWICE_ENCODED` (three quotation marks encoded twice), applied by `esc_text`.
- `openstax/tooling/entrypoint/pdf.sh` ends each book with "no character is missing from the fonts" or a WARNING listing the code points.

## Result

All 57 books were rebuilt on 2026-11-27: 56 PDFs report no missing character. Contemporary Mathematics reports one, `𝜙` (U+1D719), 7 log lines, where it is asked of the slanted body font; the PDF's text holds the character in its other places. The sibling `trench/` book, which shares the class, still builds. Introduction to Philosophy 2e was checked with `pdftotext`: the six letters it had lost are in the PDF.

## Left as it is

The one character above. The stand-in symbols for the five pictographs are the agent's choice and easy to change (one line each in `osbook.cls`). Nobody looked at every repaired character on the page.

## Recorded

`tasks/reference/tooling/converters.md` ("Characters no font has") and the class's line in `openstax/CLAUDE.md`.
