# Added `osbooks-lifespan-development` to impo (one book)

**Done 2026-11-27** (agent, with the exercise fetch run by the maintainer; part of `tasks/openstax-add-remaining-english-books.md`. William Emerison Six <billsix@gmail.com>, 2026-11-27: "you can make a branch, temporarily turn off gpg signing, and start working on all of them (minus the business ones for now)").

## What was added

`openstax/osbooks-lifespan-development/`, created with `tools/add-book.sh lifespan-development "Lifespan Development"` and pinned at the upstream head `ebed4ae43c261041030f752eb49d92d0411608db`. It builds one book:

| Book | Collection | Shape | PDF | Web pages |
|---|---|---|---|---|
| *Lifespan Development* | `lifespan-development` | 100 modules in 17 chapters; one level of nesting | 1,430 pages | 119 |

- **Licence:** CC BY-NC-SA 4.0 (collection XML and the upstream `LICENSE`); the built PDF states it.
- **Figures:** raster only (450 files, 79 MB); no SVG.
- **Exercises:** 872 embedded links to 872 exercises, all in the `#exercise/<nickname>` scheme, none in `#ost/api/ex/<id>`. The maintainer ran `make fetch-exercises` on 2026-11-27; all 872 are in the committed cache `openstax/osbooks-lifespan-development/exercises/` (no images) with its `COPYRIGHT` notice, copied in from `openstax/tooling/templates/exercises-COPYRIGHT` because the fetch does not write it.
- **Result:** built as PDF, EPUB and HTML on 2026-11-27 with the exercises in; the converter reports no `exercise-uncached` and the build log has no pandoc warning. The first build of the day, without the exercises, is the commit that added the folder.

## What the book needed from the toolchain

Nothing: it converted and built in one pass.

## Left as it is

The PDF leaves out two characters the body font has no glyph for, `ɡ` (two places, for a plain g) and `ɛ` (once, in "APOE ɛ4"); the HTML and EPUB have them. Every book impo builds has this gap, so it has its own task: `tasks/archive/impo/2026/11/27/openstax-pdf-characters-missing-from-the-body-font.md`. The converter reports no fallback. The PDF and HTML were not read page by page; that review is the maintainer's.

## Not done

The book needs the maintainer's public backup: `bash tools/mirror-upstreams.sh push lifespan-development`.

## Recorded

`openstax/osbooks-lifespan-development/CLAUDE.md` ("The books this folder builds"), the lists and counts in `openstax/CLAUDE.md` and the root `CLAUDE.md`, the inventory and its licence table, the converter quick reference, the survey table and the umbrella's checklist.
