# Added `osbooks-foundations-information-systems` to impo (one book)

**Done 2026-11-27** (agent, with the exercise fetch run by the maintainer; part of `tasks/openstax-add-remaining-english-books.md`. William Emerison Six <billsix@gmail.com>, 2026-11-27: "for each book, do the work, commit, archive, commit").

## What was added

`openstax/osbooks-foundations-information-systems/`, created with `tools/add-book.sh foundations-information-systems "Foundations of Information Systems"` and pinned at the upstream head `057882c68a7867af80c42e86937d3a2454bfd86a`. It builds one book:

| Book | Collection | Shape | PDF | Web pages |
|---|---|---|---|---|
| *Foundations of Information Systems* | `foundations-information-systems` | 59 modules in 12 chapters; one level of nesting | 615 pages | 73 |

- **Licence:** CC BY-NC-SA 4.0 (collection XML and the upstream `LICENSE`); the built PDF states it.
- **Figures:** raster only (181 files, 28 MB); no SVG.
- **Exercises:** 410 embedded links to 410 exercises, all in the `#exercise/<nickname>` scheme, none in `#ost/api/ex/<id>`. The maintainer ran `make fetch-exercises` on 2026-11-27; all 410 are in the committed cache `openstax/osbooks-foundations-information-systems/exercises/` (1 image) with its `COPYRIGHT` notice.
- **Result:** built as PDF, EPUB and HTML on 2026-11-27 with the exercises in; the converter reports no `exercise-uncached` and the build log has no pandoc warning.

## What the book needed from the toolchain

**A footnote in a note's title.** The first PDF build stopped with "Use of \@item doesn't match its definition": module `m00014` has a note titled "The Rise of Data and AI Ethics" with a `<footnote>` in the title, and the title is the optional argument of the note's box. Such a footnote is now given in parentheses after the title (`tasks/reference/tooling/converters.md`, "Block quotations, reference notes and footnotes in titles"). Two of its sections also hold block quotations with lists inside, which the change made for U.S. History keeps as lists.

## Left as it is

The converter reports `inline:item` (8) and `inline:list` (1) fallbacks. The PDF and HTML were not read page by page; that review is the maintainer's.

## Not done

The book needs the maintainer's public backup: `bash tools/mirror-upstreams.sh push foundations-information-systems`.

## Recorded

`openstax/osbooks-foundations-information-systems/CLAUDE.md` ("The books this folder builds"), the list in `openstax/CLAUDE.md`, the inventory and its licence table, the survey table and the umbrella's checklist.
