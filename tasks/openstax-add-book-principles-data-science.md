# Added `osbooks-principles-data-science` to impo (one book)

**Done 2026-11-27** (agent, with the exercise fetch run by the maintainer; part of `tasks/openstax-add-remaining-english-books.md`. William Emerison Six <billsix@gmail.com>, 2026-11-27: "for each book, do the work, commit, archive, commit").

## What was added

`openstax/osbooks-principles-data-science/`, created with `tools/add-book.sh principles-data-science "Principles of Data Science"` and pinned at the upstream head `cc5a81d59c7d9b8b153a2297098e89dfaca7b2d3`. It builds one book:

| Book | Collection | Shape | PDF | Web pages |
|---|---|---|---|---|
| *Principles of Data Science* | `principles-data-science` | 59 modules in 10 chapters grouped into 4 units, from "Introducing Data Science and Data Collection" to "Maintaining a Professional and Ethical Data Science Practice"; two levels of nesting | 600 pages | 16 |

- **Licence:** CC BY-NC-SA 4.0 (collection XML and the upstream `LICENSE`); the built PDF states it.
- **Figures:** raster only (232 files, 40 MB); no SVG.
- **Exercises:** 136 embedded links to 136 exercises, all in the `#exercise/<nickname>` scheme, none in `#ost/api/ex/<id>`. The maintainer ran `make fetch-exercises` on 2026-11-27; all 136 are in the committed cache `openstax/osbooks-principles-data-science/exercises/` (6 images) with its `COPYRIGHT` notice.
- **Result:** built as PDF, EPUB and HTML on 2026-11-27 with the exercises in; the converter reports no `exercise-uncached` and the build log has no pandoc warning.

## What the book needed from the toolchain

**One line of code wrapped in line breaks.** The first PDF build stopped with "Paragraph ended before \text@command was complete": the book writes many one-line code samples as `<code class="python">` with a blank line before the code, and the converter put that blank line inside a `\texttt{}`. Such a block standing between paragraphs is now a one-line listing, and inside a sentence it is inline code with the breaks trimmed (`tasks/reference/tooling/converters.md`, "One line of code wrapped in line breaks"). The change also repaired code blocks in Introduction to Python Programming (30 section files), which was rebuilt.

## Left as it is

The web edition has 16 pages for 59 modules, because a book with two levels of nesting is split per chapter. The converter reports `inline:span` (815) and `inline:para` (3) fallbacks; the spans were not examined. The PDF and HTML were not read page by page; that review is the maintainer's.

## Not done

The book needs the maintainer's public backup: `bash tools/mirror-upstreams.sh push principles-data-science`.

## Recorded

`openstax/osbooks-principles-data-science/CLAUDE.md` ("The books this folder builds"), the list in `openstax/CLAUDE.md`, the inventory and its licence table, the survey table and the umbrella's checklist.
