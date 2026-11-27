# The OpenStax converters — shared skeleton, the 5 historical versions, and the unified toolchain

**Reference doc — living, never archived.** What the CNXML→LaTeX (+ HTML/EPUB) converter does, how the 16
per-book source converters differed, and how impo's single shared toolchain relates to each. Read this before
touching `openstax/tooling/`. Companion *fix* task (the work that closed the gaps): [[openstax-converter-unification-gaps]].
Written 2026-09-03 from a full cross-repo diff; reflects the toolchain **after** the two-scheme exercise fix landed.

## Why this exists

The 16 OpenStax `latex`-branch source repos were assumed to share one converter. They did **not**:
`tools/cnxml2tex/convert.py` existed in **5 distinct versions**, with further divergence in `preprocess.py`,
`fetch_exercises.py`, `osbook.cls`, and `osbook-envs.sty`. impo hoisted **one** shared toolchain
(`openstax/tooling/`) — a superset. This doc records the common skeleton, every divergence, and where the shared
version stands, so a future session understands the whole landscape without re-diffing 16 repos or re-reading
2900+ lines. (An earlier survey wrongly claimed the converters were "byte-identical except the slug"; that claim
is corrected here and was the reason for the whole investigation.)

**Why hoist one toolchain (the design call, moved from `openstax/CLAUDE.md` 2026-09-13).** The delta is a
SHARED toolchain, not a per-book patch series. The maintainer's converter is fully automatic and
book-agnostic (`convert.py` auto-detects a book's subcollection nesting; `fetch_exercises.py` is
bundle-agnostic; the generated LaTeX is never hand-edited). Corrected 2026-09-03: the per-book
`latex`-branch converters were **not** byte-identical — `convert.py` existed in 5 versions (physics,
organic-chemistry, python-programming, biology each diverged), with further differences in
`preprocess.py`, `fetch_exercises.py`, and `osbook.cls`; the shared `openstax/tooling/` converter merges
them into one feature-detecting superset (both os-embed exercise schemes, math-in-titles, code blocks).
Hoisting one merged toolchain and keeping each book folder thin is still right — 16 near-identical copies
as patches would be a maintenance smell; they simply weren't identical to begin with.

**Source of truth for the originals:** each source repo's `latex` branch at `/foo/opt/openstax/osbooks-<subject>`
(an **upstream-only, read-only** checkout — the `latex` branch is the maintainer's own work; never edit it). Read
with `git -C <repo> cat-file -p latex:<path>`. All `file:line` anchors below point at impo's maintained copy under
`openstax/tooling/` (that's what you edit); line numbers drift — the function names and section titles are the
stable anchors.

## The shared skeleton — `openstax/tooling/tools/cnxml2tex/convert.py`

Book-agnostic: `ROOT` is always `/book`; per-book structure is **auto-derived**, so the same converter serves every
book. Major phases (section banners in the file):

| ~line | phase | what it does |
|------|------|------|
| 48 | per-book configuration | auto-derives collection/subcollection nesting; no hardcoded slug |
| 120 | text escaping | LaTeX special-char escaping |
| 352 | MathML → LaTeX | Presentation-MathML → math (and Content MathML, see below); includes the obsolete-font map (see gap #4) at ~757 |
| 1191 | continued-equality promotion | `a=b=c` chains → aligned display |
| 1375 | inline content | `inline()` (1378), `inline_element()` (1390) |
| 1484 | labels | module-scoped label state (CNXML reuses `fs-id`s across modules) |
| 1558 | source-line wrapping | wraps prose in the emitted `.tex` for readable diffs |
| 1655 | block content | `block_element()` (2055), `inline_block()` (2204) |
| 1761 | **injected os-embed exercises** | `_os_embed_nickname()` (1778), `render_injected_exercise()` (2013), `render_exercise()` (2367) |
| 2631 | label discovery | which ids are referenced (so only those get `\label`) |
| 2643 | module conversion | `convert_module()` (2653) |
| 2748 | collection assembly | `convert_collection()` (2751) — Phase 2 |
| 2912 | entry | `main()` (2913) |

## Content MathML (added 2026-11-26, with the Statistics book)

The converter was written for Presentation MathML (`<mfrac>`, `<msup>`, …), which says how a formula looks.
A few modules use **Content MathML** instead, which says what it means, in prefix notation:
`<apply><divide/><apply><plus/><cn>6.8</cn><cn>7.2</cn></apply><cn>2</cn></apply>`. Until this date `mml()`
fell back on those tags (`m:apply`, `m:ci`, `m:cn` in the "Unknown/fallback elements" report) and emitted the
operands run together with the operators lost, or nothing at all.

- `mml()` now renders `<cn>`, `<ci>`, `<infinity/>`, `<apply>` and the older `<reln>`; `_content_apply` handles `eq`, `neq`,
  `lt`, `gt`, `leq`, `geq`, `approx`, `plus`, `minus` (unary and binary), `times`, `divide`, `power`,
  `conjugate` (an overline, as in the sample mean) and `sum`. A sum or difference inside a product or a power
  is parenthesised, because prefix notation carries grouping that infix has to spell out. An operator it does
  not know is reported as `m:apply:<name>` and its operands are joined.
- **Where it occurs:** six modules of Statistics, and one of Psychology 2e, where the scrambled word "AETPL"
  in a memory exercise had been missing from every edition impo built.
- **Proof it changed nothing else:** every existing book was converted with the converter before and after
  the change and the generated LaTeX compared file by file: 15 books identical, Psychology different in that
  one place. No existing book contains `<m:reln>` or `<m:infinity/>`.
- Tests: the `test_content_mathml_*` cases in `tools/tests/test_mathml.py`.

A related fix from the same book: `render_table` took `int()` of the CALS `cols` attribute and crashed on
`cols=""`; a value that is not a number now counts as undeclared and the observed row width decides.

## Block quotations, reference notes and footnotes in titles (added 2026-11-27, with the history and government books)

Three kinds of prose markup that the mathematics and science books barely use and the humanities books lean on.

- **Block quotations.** A `<quote>` that holds `<para>` children, or that the source marks `class="block"` or
  `display="block"`, is a passage set off from the prose: a speech, a constitutional clause, a letter. It
  becomes a LaTeX `quote` environment with its paragraphs and lists kept (`_is_block_quote`, used by
  `is_block`). Any other `<quote>` is a few quoted words inside a sentence and stays inline with quotation
  marks. Before this date every `<quote>` was inline: a multi-paragraph passage was run together into its
  surrounding paragraph between one pair of quotation marks, and a list inside it lost its items. In a table
  cell a quote is always inline.
- **Reference notes.** American Government and Introduction to Political Science cite sources as
  `<cite><note class="reference">source</note></cite>` in the middle of a sentence (1,342 and 1,522 times).
  Each is a `\footnote`; in a table cell, a caption or a title, where a footnote cannot be relied on, the
  source follows in parentheses. Before this date the source's text was printed inline in the sentence.
- **A `<footnote>` in a note's title** is given in parentheses, because the title is the optional argument of
  the note's box and a `\footnote` there stops LaTeX ("Use of \@item doesn't match its definition"; one case,
  in Foundations of Information Systems). Footnotes in captions, table titles and table cells are unchanged.
- **Which existing books changed** (`tools/compare-converter-output.sh`, 2026-11-27; all block quotations):
  Algebra 1 (6 section files), Astronomy 2e (7), Organic Chemistry (3), Physics (1), Psychology 2e (16) and
  Writing Guide (33, mostly example sentences that are now set off one per line). The other 14 were identical.
- **A `<quote>` that holds a list and no paragraph** is a block quotation too (added 2026-11-27, with
  Introduction to Philosophy, where the three numbered premises of an argument are quoted that way). It had
  stayed inline, so its items ran together between quotation marks with their numbers lost. The same change
  restored the lists in five section files of Algebra 1 and one of Foundations of Information Systems; the
  other 34 fetched book folders were identical (`tools/compare-converter-output.sh`).
- **`<span>` and an empty `<label/>` are known markup** (same date). A `<span>` carries only a presentation
  class (`class="blue-text"`, 3,375 times in the nursing books' tables) and its words are set like the text
  around them. An empty `<label/>` asks OpenStax's web edition to print no label on a note or a solution (437
  times in Introduction to Sociology 3e) and sets nothing. Both gave that output before; they no longer fill
  the "Unknown/fallback elements" report. A `<label>` with text in it, even a lone space, is still reported.
- **A paragraph that holds nothing but `<newline/>`s** (eight of them, used as vertical space in the preface
  of Population Health for Nurses) sets nothing (added 2026-11-27). `cleanup_latex` dropped a lone `\\` on a
  line but not a run of them separated by spaces, and LaTeX stopped with "There's no line here to end". No
  other fetched book has one.
- **`\surd` in the web editions** (same date): the converter writes a bare `√` in prose as `$\surd$`, which
  pandoc's math reader does not know and printed as TeX. `tools/pandoc/preprocess.py` puts the character back
  for the HTML and EPUB. College Success uses it as a tick mark; Introductory Statistics and Principles of Data
  Science have one each.
- **Related, in the build scripts:** `entrypoint/html.sh` and `entrypoint/epub.sh` set `LANG=C.UTF-8`. In the
  image's POSIX locale pandoc could not find a figure whose file name holds a non-ASCII character (Behavioral
  Neuroscience has one, with an en dash): the EPUB build left the figure out with a warning and the HTML build
  stopped.

## Outside pages embedded in frames (added 2026-11-27)

Where a module embeds an outside page in a frame, `<media><iframe src="https://…"/></media>` (a simulation, a
video, a document), `render_media` emits a labelled link: `\textbf{<label>:} \url{<address>}`, which pandoc
carries into the HTML and EPUB. Until this date it emitted nothing, and the sentence around the frame ("Watch
this video …") pointed at an address that was not there.

- **The label** (`_frame_link`) is the title of the enclosing note when it has one ("Gravity Force Lab"), else
  "Interactive" when the note's class contains `interactive`, else "Online resource". The wording was the
  maintainer's choice of a labelled line over a bare address (William Emerison Six <billsix@gmail.com>,
  2026-11-27).
- **A frame on a local file is left out**, as before (the same decision): Algebra 1 has 177 (Desmos graph files
  under `media/desmos/`), Introduction to Python Programming 129 (code-runner pages) and Writing Guide 11.
  They cannot work in a PDF; embedding them in the HTML edition would be its own task.
- **Counts on 2026-11-27 (323 links in 11 book folders):** Introduction to Political Science 115, Biology 51,
  Behavioral Neuroscience 40, Life, Liberty, and the Pursuit of Happiness 33, Physics 28 (a 29th frame in its source is
  commented out), College Physics 18, University Physics 15,
  Introduction to Intellectual Property 9, World History 8, Algebra 1 3, Prealgebra 3.

## One line of code wrapped in line breaks (added 2026-11-27, with Principles of Data Science)

A `<code>` element whose single line of code is surrounded by line breaks in the source
(`<code class="python">⏎⏎  data.iloc[:, 1]⏎</code>`) used to become a `\texttt{}` holding a blank line, which
stops LaTeX ("Paragraph ended before \text@command was complete") as a multi-line listing would. Standing
between blocks it is now a one-line `oscode` listing; inside a sentence, a list item or a table cell it is
`\texttt{}` with the line breaks trimmed. Principles of Data Science has 166 `<code class="python">` blocks
and could not be typeset without this. It also changed Introduction to Python Programming (30 section files:
such blocks were typeset inline, running into the text around them), one listing in Foundations of
Information Systems and the wrapping of one line in Introductory Statistics; the other books were identical.

## Tables of prose (added 2026-11-27, with the nursing books)

A table column is set as `l`, which never wraps, and a table wider than the line is scaled down to it
(`\resizebox`; a table holding a link, which cannot go through `\resizebox`, is set smaller instead). That suits a
table of numbers. A table whose cells hold sentences was thousands of points wide: scaled, it could not be read
(Table 7.12 of Population Health for Nurses was a hairline), and with a link in it, it ran off the page.

- **Which tables wrap** (`prose_column_shares`): one whose widest cells, side by side and unwrapped, come to more
  than 90 characters, with a phrase of more than 40 in some column. Mathematics is not counted, so a table of
  long formulas keeps its natural width; neither is a table of more than seven columns. Every other table is set
  exactly as before.
- **How** (`_render_prose_table`): each column is a ragged-right `p{…}` column whose share of the line follows its
  longest cell, between its longest word and 45 characters; the type is `\small`, and a rule separates the rows.
  Standing on its own the table is a `longtable`, which breaks across pages and repeats its header row. Inside a
  note, an example, an exercise, a list or another table, where a `longtable` cannot go, it is a `tabular` in one
  piece. The caption and number stay below the table, and `\addtocounter{table}{-1}` undoes the step a
  `longtable` gives the table counter by itself.
- **Line breaks in a wrapping cell:** a `<newline/>` or a list item starts a new line with `\OScellbreak`
  (`osbook.cls`), which is safe inside `\textbf{…}` and at the start of a cell; `\par` there stopped LaTeX. For
  the web editions `tools/pandoc/preprocess.py` turns it into `\newline`.
- **Web editions:** pandoc reads `longtable` and the `p{…}` widths, so the HTML and EPUB tables now carry column
  widths in the same proportions.
- **Counts on 2026-11-27, in the section files of the 37 book folders:** 1,863 tables are `longtable`s and 968 are
  wrapped in one piece; 6,919 keep their natural width. The nursing bundle has 657 wrapped tables, Life, Liberty,
  and the Pursuit of Happiness 180, the Biology bundle 168, Writing Guide 95.
- **Page counts rose** where tables had been shrunk: Pharmacology for Nurses 1,267 to 1,568, Nutrition for Nurses
  537 to 622, Population Health for Nurses 1,400 to 1,653. The page counts recorded in the books' `CLAUDE.md` files and
  the inventory were re-read from the rebuilt PDFs the same day.
- **Still too wide:** a `p` column cannot break a long unbroken word or an image wider than its share, so logs
  still list some boxes more than 100 pt too wide (Population Health for Nurses 8, down from 20; Writing Guide 39
  and College Physics 38, which were not measured before). Nobody has read every wrapped table in the PDFs.

## Characters no font has (added 2026-11-27)

LuaTeX prints nothing for a character the font in use has no glyph for and says so only in the log ("Missing
character: There is no ⅓ (U+2153) in font …"). On 2026-11-27 the logs of the built books held 7,323 such lines
in 27 books; after the three changes below a rebuild of all 57 books left 7 lines, one character in one book.

- **A fallback font chain** (`osbook.cls`): `luaotfload.add_fallback("osfallback", …)` names FreeSerif, STIX Two
  Math, TeX Gyre DejaVu Math and Libertinus Serif, all in the image already, and the body and heading fonts are
  loaded with `RawFeature={fallback=osfallback}`. It covers letters with marks and phonetic letters (the Arabic,
  Sanskrit and Chinese names of Introduction to Philosophy 2e), arrows and operators met in prose (`ℏ` alone was
  1,030 lines), fractions and subscript digits, and box-drawing characters. A book-style that re-sets
  `\setmainfont` passes the same feature (`osbooks-calculus-bundle/bookstyle.tex` does). The chain was chosen by
  setting every missing character in a test document and reading its log.
- **Five pictographs no font in the image has** (`🔎 📝 📍 📖 📎`, which mark the kind of a resource in the titles
  of Life, Liberty, and the Pursuit of Happiness) print as the nearest symbol the fallback fonts do have
  (`⌕ ✎ ⚑ ☰ ❖`), through `\newunicodechar` lines in `osbook.cls`. The HTML and EPUB keep the pictograph.
  Installing an emoji font in the image would print the real ones; that is a change to what the image ships
  and was not made.
- **Mis-encoded characters are repaired in the converter** (`_MISENCODED` and `_TWICE_ENCODED`, applied by
  `esc_text`), so all three editions get the right character: U+0080 to U+009F are Windows-1252 punctuation
  saved as Latin-1 control codes (about 980 curly quotes and dashes in Statistics, Biology, Physics, U.S.
  History and College Physics); `â€œ`, `â€` followed by U+009D, and `â€™` are quotation marks encoded twice
  (5 places); U+F061 and U+F0BE are an alpha and a dash from the Symbol font (7 places).
- **A build reports what is left:** `entrypoint/pdf.sh` ends each book with either "no character is missing from
  the fonts" or a WARNING line listing the code points, so a new book cannot add holes unseen.
- **Left:** `𝜙` (U+1D719) in Contemporary Mathematics, where it is asked of the slanted body font (7 log lines);
  the PDF's text holds the character in its other places.

## Links with words of their own, and references to exercises (added 2026-11-27)

- **A link that has words keeps them.** `<link target-id="…">the map</link>` and `<link document="…">Electoral
  College</link>` became `\cref{…}`, which prints the target's kind and number in place of the author's words:
  American Government 4e read "Drafted by Thomas Jefferson, the section 5.3.25 officially proclaimed …" for "the
  Declaration of Independence". 7,157 internal links in 30 book folders carry words (Life, Liberty, and the
  Pursuit of Happiness 2,581, Organic Chemistry 635, Astronomy 458). Such a link is now
  `\hyperref[label]{words}`: the words, linked to the target. An empty link is still `\cref`.
- **An exercise that something points at carries a label** (`render_exercise`). It had none, so the PDF printed
  "??" for 1,193 exercises in 14 book folders (874 of them in Life, Liberty, and the Pursuit of Happiness, where
  most are worded links that now show their words).
- **Web editions** (`tools/pandoc/xref.lua`): exercises are numbered as in the PDF, from 1 after every heading,
  with the number printed in front, and a reference to one reads "Exercise 3"; until this date the web editions
  showed no exercise numbers and a reference to one showed its raw label in brackets. The filter rewrites the
  text of a link only when pandoc marks it as a `\cref` (a `reference-type` attribute), so a worded link keeps
  its words.
- **Still undefined:** about 20 references in 9 books point at ids that get no label for other reasons (a figure
  or table in a place the converter does not label); each prints "??" in the PDF.

## The 5 historical `convert.py` versions and their deltas

Verified by hashing `latex:tools/cnxml2tex/convert.py` across all 16 repos. 12 books shared one version; four
diverged. impo's converter (2930 lines) is larger than every original — a merged superset.

| Version | Books | What it added over the majority | In impo now? |
|------|------|------|------|
| **majority** (2856 ln) | the other 12 | — the base | — |
| **physics** (2863) | physics | 2nd os-embed URL scheme `#ost/api/ex/<id>` → query `tag:<id>` | ✅ (fixed 2026-09-03) |
| **organic** (2873) | organic-chemistry | `_pdfsafe(title)` — wrap math-in-headings in `\texorpdfstring` (else hyperref aborts on `$…$` in a PDF bookmark) | ✅ (build-all fix #2) |
| **python** (2906) | introduction-python-programming | `render_code_block` — multi-line `<code>` → a verbatim block env (inline `\texttt` can't hold a paragraph) | ✅ (build-all fix #1, as `oscode`) |
| **biology** (2889) | biology-bundle | `_pdfsafe` **and** the 2nd os-embed scheme (union of organic + physics) | ✅ (both) |

### The two os-embed exercise schemes (the subtle one)

OpenStax practice exercises are referenced in CNXML as `<link class="os-embed" url="…">`, sole content of a
`<para>`. **Two URL schemes exist:**

- `#exercise/<nickname>` — most books; API query `nickname:<nickname>` (e.g. anatomy would use this if it had any).
- `#ost/api/ex/<id>` — **physics and biology only**; API query `tag:<id>` (e.g. `k12phys-ch04-ex017`,
  `apbio-ch01-ex001`). The trailing token is the cache key (`exercises/<key>.json`) either way.

The unified converter originally recognized only the first scheme, so **physics (846 exercises) and biology
silently rendered zero** — the "physics/biology have 0 exercises" reading was the bug hiding itself. Both
`convert.py` (`_os_embed_nickname`, and the inline-link fallback at ~1425) and `fetch_exercises.py`
(`discover_targets` → `nickname:`/`tag:` queries, `fetch_one(key, query)`) now handle both. Unit tests:
`tools/tests/test_helpers.py::test_os_embed_{nickname,tag}_scheme`.

## The other divergent files

| File | versions | who diverged | what it was | impo |
|------|------|------|------|------|
| `tools/pandoc/preprocess.py` | 2 | python | rename `codeblock`→`verbatim` so pandoc (HTML/EPUB) reads the code env | ✅ **DONE 2026-09-03** — impo's env is `oscode`; `preprocess.py` renames `oscode`→`verbatim` for pandoc, so python HTML/EPUB code blocks render (gap #6 closed) |
| `tools/cnxml2tex/fetch_exercises.py` | 2 | physics, biology | `discover_targets` — both `nickname:` and `tag:` queries | ✅ (fixed 2026-09-03) |
| `latex/osbook.cls` | 3 | organic+biology; calculus | organic/biology: `\DeclareOldFontCommand{\rm…\mathrm}` (+`\bf\it\sf\tt\cal`) — robust obsolete-font fix for chem formulae. calculus: `\setmainfont{TeX Gyre Termes}` (Times) + a **blue** palette | ⚠️ impo uses majority `.cls`; the `{\rm}` case is handled a different way in `convert.py` (~757, `{\rm X}`→`{\mathrm X}` substitution, build-all fix #3) — less general than the `.cls` form; calculus's Times+navy theme is ✅ **DONE 2026-09-03** via the per-book style hook (`bookstyle.tex` for PDF, `bookstyle-web.css` for HTML/EPUB); the `{\rm}` case is handled in `convert.py` (build-all fix #3), the more-general `\DeclareOldFontCommand` (gap #4) is deferred |
| `latex/osbook-envs.sty` | 2 | python | the code env | ✅ impo has `oscode` (new hash; build-all fix #1) |
| `latex/osbook-defer.sty` | 1 | — | identical across all 16 | ✅ (confirmed same) |

## The unification model (the reusable lesson)

Divergences split into two kinds, unified differently:

- **Logic divergences** (exercise schemes, math-in-titles, code blocks) → fold **all** variants into one
  feature-detecting converter. This is how the physics/biology originals already modeled the two schemes
  (`discover_targets` returning both queries). The right answer is a superset, not "pick one."
- **Presentation divergences** (calculus's Times+blue theme) → do **not** belong in a universal converter. The
  clean unification is a **per-book style hook**: `osbook.cls` `\InputIfFileExists{book-style.tex}`, defaulting to
  the shared Roboto-Slab+teal theme, so a book can override only its font+palette. **Implemented 2026-09-03:**
  `osbook.cls` `\InputIfFileExists{osbook-bookstyle.tex}` for the PDF + `html.sh`/`epub.sh` appending a book's
  `bookstyle-web.css` for the web edition; calculus ships both (Times + navy).

## Per-book quick reference

Figure format and os-embed scheme are the durable facts; exercise counts are as of 2026-09-03. The rows from
`statistics` down are the books added 2026-11-26 and 2026-11-27, counted on the raw CNXML in both schemes on
the day each was added.

| Book | collections | os-embed scheme | exercises cached | figures |
|------|------|------|------|------|
| anatomy-physiology | 1 | none | 0 | raster |
| astronomy | 1 | none (survey) | 0 | raster |
| algebra-1 | 1 | `#exercise/` | 932 | SVG |
| organic-chemistry | 1 | `#exercise/` | 1959 | raster+exercise imgs |
| contemporary-mathematics | 1 | `#exercise/` | 3073 | mixed |
| introduction-python-programming | 1 | `#exercise/` | 613 | none |
| writing-guide | 1 | `#exercise/` | 182 (0 img) | — |
| **physics** | 1 | **`#ost/api/ex/`** | **846** (fixed 2026-09-03) | raster |
| **biology-bundle** | 3 | **`#ost/api/ex/`** | **2337** (fixed 2026-09-03) | raster |
| chemistry-bundle | 2 | none/survey | 0 | — |
| calculus-bundle | 3 | none | 0 | Times+navy theme (bookstyle.tex + bookstyle-web.css) |
| college-algebra-bundle | 4 | survey | 0 | — |
| prealgebra-bundle | 3 | survey | 0 | — |
| university-physics-bundle | 3 | survey | 0 | — |
| microbiology | 1 | survey | 0 | — |
| psychology | 1 | survey | 0 | — |
| statistics | 1 | none | 0 | raster |
| introductory-statistics-bundle | 2 | none | 0 | raster |
| college-physics-bundle | 2 | none | 0 | raster |
| principles-data-science | 1 | `#exercise/` | 136 | raster + 6 exercise imgs |
| additive-manufacturing | 1 | `#exercise/` | 120 | raster |
| foundations-information-systems | 1 | `#exercise/` | 410 | raster + 1 exercise img |
| american-government | 1 | none | 0 | raster |
| introduction-political-science | 1 | `#exercise/` | 308 | raster |
| life-liberty-and-pursuit-happiness | 1 | `#exercise/` | 1895 | raster + 95 exercise imgs |
| us-history | 1 | none | 0 | raster |
| world-history | 2 | `#exercise/` | 1158 | raster + 4 exercise imgs |
| neuroscience | 1 | `#exercise/` | 568 | raster |
| business-law | 1 | none | 0 | raster |
| introduction-intellectual-property | 1 | `#exercise/` | 185 | raster |
| introduction-sociology | 1 | none | 0 | raster |
| college-success-bundle | 3 | none | 0 | raster |
| lifespan-development | 1 | `#exercise/` | 872 | raster |
| workplace-software-skills | 1 | `#exercise/` | 682 | raster + 20 exercise imgs |
| introduction-anthropology | 1 | `#exercise/` | 150 | raster |
| introduction-philosophy | 1 | `#exercise/` | 228 | raster |
| nursing-external-bundle | 3 | `#exercise/` | 1156 | raster |

("survey" = the scheme wasn't re-audited on the raw CNXML for that book; verify on first exercise-bearing build,
the same way physics/biology turned out to have `#ost/api/ex/`.)

## See also

- [[openstax-converter-unification-gaps]] — the fix task (gap table, plan, status).
- [[openstax-html-exercise-rendering]] — HTML/EPUB presentation of exercises (collapsible answers; the `oscode`
  HTML rename, gap #6, is tracked here).
- `openstax/CLAUDE.md` — the family contract (had the "byte-identical" error this doc corrects).
