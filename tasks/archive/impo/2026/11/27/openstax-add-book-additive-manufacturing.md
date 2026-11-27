# Added `osbooks-additive-manufacturing` to impo (one book)

**Done 2026-11-27** (agent, with the exercise fetch run by the maintainer; part of `tasks/openstax-add-remaining-english-books.md`. William Emerison Six <billsix@gmail.com>, 2026-11-27: "for each book, do the work, commit, archive, commit").

## What was added

`openstax/osbooks-additive-manufacturing/`, created with `tools/add-book.sh additive-manufacturing "Additive Manufacturing Essentials"` and pinned at the upstream head `461b9c36ac439a4797fbfe2e41d8f9b1dbf90610`. It builds one book:

| Book | Collection | Shape | PDF | Web pages |
|---|---|---|---|---|
| *Additive Manufacturing Essentials* | `additive-manufacturing-essentials` | 42 modules in 8 chapters, from "Fundamentals of Additive Manufacturing" to "The Business of Additive Manufacturing"; one level of nesting | 246 pages | 52 |

- **Licence:** CC BY-NC-SA 4.0 (collection XML and the upstream `LICENSE`); the built PDF states it.
- **Figures:** raster only (70 files, 20 MB); no SVG.
- **Exercises:** 122 embedded links to 120 exercises (2 of the links repeat an exercise), all in the `#exercise/<nickname>` scheme, none in `#ost/api/ex/<id>`. The maintainer ran `make fetch-exercises` on 2026-11-27; all 120 are in the committed cache `openstax/osbooks-additive-manufacturing/exercises/` (no images) with its `COPYRIGHT` notice.
- **Result:** built as PDF, EPUB and HTML on 2026-11-27 with the exercises in; the converter reports no `exercise-uncached` and the build log has no pandoc warning.

## What the book needed from the toolchain

Nothing: it converted and built in one pass with the toolchain as it stood.

## Left as it is

The converter reports no fallback. The PDF and HTML were not read page by page; that review is the maintainer's.

## Not done

The book needs the maintainer's public backup: `bash tools/mirror-upstreams.sh push additive-manufacturing`.

## Recorded

`openstax/osbooks-additive-manufacturing/CLAUDE.md` ("The books this folder builds"), the list in `openstax/CLAUDE.md`, the inventory and its licence table, the survey table and the umbrella's checklist.
