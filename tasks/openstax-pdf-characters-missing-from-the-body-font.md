# The PDFs leave out characters the body font has no glyph for

**Status:** proposed — needs go-ahead
**Priority:** 4
**Difficulty:** 5 (one mechanism in the class, then every book's PDF rebuilt and its log checked)
**Created:** 2026-11-27 (agent, found while adding seven book folders; `tasks/openstax-add-remaining-english-books.md`)

## BLUF

LuaLaTeX prints nothing where the font in use has no glyph for a character, and says so only in the log ("Missing character: There is no ⅓ (U+2153) in font …"). The logs of the books built in the working tree on 2026-11-27 hold 7,323 such lines in 27 books: the PDF of each has holes where those characters were. The HTML and EPUB editions are not affected. Done means every built PDF's final log has no "Missing character" line, or the ones left are listed with the reason, and a build reports the count so a new book cannot add holes unseen.

## Context

**Read first:** `openstax/CLAUDE.md` ("The shared toolchain"), `openstax/tooling/latex/osbook.cls` (the font setup: `\setmainfont{Roboto Slab}`, `\setsansfont{Noto Sans}`, `\setmathfont{STIX Two Math}`), and its block of `\newunicodechar` lines, which is the one existing remedy (circled letters and digits mapped to `\textcircled`).

### What is missing (from `openstax/osbooks-*/checkout/output/*.log`, 2026-11-27)

Lines per book, largest first: Life, Liberty, and the Pursuit of Happiness 1,893; Organic Chemistry 1,330; University Physics Volume 3 943; Biology for AP Courses 2e 719; Physics 644; Statistics 578; Microbiology 282; Chemistry 2e 230; Chemistry: Atoms First 2e 227; Healthcare Foundations 68; University Physics Volume 1 60; U.S. History 56; Behavioral Neuroscience 41; Anatomy and Physiology 2e 36; World History Volume 1 35; Introduction to Philosophy 2e 30; University Physics Volume 2, College Physics 2e and its AP edition 25 each; Introductory Business Statistics 2e 14; Principles of Data Science 13; Lifespan Development 12; Nutrition for Nurses 9; Introductory Statistics 2e 9; Biology 2e 8; Contemporary Mathematics 7; World History Volume 2 4. A log holds every pass of a build, so a character counts once per pass.

The characters fall into kinds that may want different remedies:

- **Symbols with a math-font glyph**, met in text: `ℏ` (1,030 lines), `≡`, `→`, `↑`, `↓`, `⇌`, `⟶`, `⟷`, `⇄`, `⇅`, `ℳ`, `⨯`, `☉`, `‖`, `𝜙`.
- **Letters with marks, phonetic letters and transliteration signs:** `ʹ`, `ʿ`, `ʾ`, `ǐ`, `Ḥ`, `ṇ`, `Ṣ`, `ṣ`, `ẑ`, `ɡ`, `ɛ`, `Ʃ`, `Ɵ`, `ǁ`. Introduction to Philosophy 2e loses them in Arabic, Sanskrit and Chinese names.
- **Fractions and subscript digits:** `⅓`, `₁`, `₂`, `₆` (Nutrition for Nurses).
- **Pictographs used as markers:** `🔎`, `✒`, `📝`, `📍`, `📖`, `✏`, `📎` (over 1,800 lines together), and the box-drawing `═` (1,020).
- **Control characters from a mis-encoded source:** U+0085 and U+0092 to U+0097 and U+009D (about 2,000 lines). These are Windows-1252 quotation marks and dashes saved as Latin-1; the right character is known (U+0092 is `’`), so the converter could repair them for all three editions.
- **Others:** `‑` (non-breaking hyphen), `◦`, `‧`, U+0305 (combining overline), and U+F061 from a private-use area.

### Remedies to weigh

- A **fallback font chain** in `osbook.cls` (luaotfload's `\directlua{luaotfload.add_fallback(...)}` with `RawFeature={fallback=…}`), naming fonts the image already holds that cover the gaps (STIX Two Text or Noto Serif for letters, STIX Two Math for symbols, a symbol or emoji font for the pictographs). One mechanism, no per-character list. Which fonts are in the image: `fc-list : family` in the toolchain container.
- **`\newunicodechar` per character**, as for the circled letters. Exact, but a list to maintain.
- **Repair in the converter** for the mis-encoded control characters, since the HTML and EPUB show them wrongly too.

### Related

`tasks/reference/tooling/converters.md` records per-book markup; none of it mentions missing glyphs, so this was not known before 2026-11-27.

## Plan

- [ ] Reproduce on one small book (Nutrition for Nurses or Introduction to Philosophy 2e): `make pdf`, `grep -c "Missing character" checkout/output/<book>.log`.
- [ ] Choose the remedy per kind (questions below), implement it in `openstax/tooling/`, and prove on that book that the count is zero and the characters are in the PDF (`pdftotext`).
- [ ] Make `entrypoint/pdf.sh` print the count of distinct missing characters at the end of a build.
- [ ] Rebuild every book's PDF; record what is left, per book, in `tasks/reference/tooling/converters.md`.

## Open questions

1. For the letters and symbols, shall the class use (a) a fallback font chain, which covers characters nobody has listed, or (b) one `\newunicodechar` line per character? The agent recommends (a).
2. Shall the pictograph markers (`🔎`, `📝`, `✒` and the like) be printed with a symbol font, or replaced by a word or dropped in the PDF?
3. Shall the converter repair the Windows-1252 control characters (U+0092 to `’` and so on) for all three editions?
