# Added `osbooks-introduction-anthropology` to impo (one book)

**Done 2026-11-27** (agent, with the exercise fetch run by the maintainer; part of `tasks/openstax-add-remaining-english-books.md`. William Emerison Six <billsix@gmail.com>, 2026-11-27: "you can make a branch, temporarily turn off gpg signing, and start working on all of them (minus the business ones for now)").

## What was added

`openstax/osbooks-introduction-anthropology/`, created with `tools/add-book.sh introduction-anthropology "Introduction to Anthropology"` and pinned at the upstream head `e466666414f1900a783141339dc5ef3106dba5dd`. It builds one book:

| Book | Collection | Shape | PDF | Web pages |
|---|---|---|---|---|
| *Introduction to Anthropology* | `introduction-anthropology` | 121 modules in 20 chapters; one level of nesting | 866 pages | 143 |

- **Licence:** CC BY-NC-SA 4.0 (collection XML and the upstream `LICENSE`); the built PDF states it.
- **Figures:** raster only (350 files; `media/` is 130 MB). `media/Interactive/` holds 197 more files, 24 of them SVG icons; no module references an SVG.
- **Exercises:** 150 embedded links to 150 exercises, all in the `#exercise/<nickname>` scheme, none in `#ost/api/ex/<id>`. The maintainer ran `make fetch-exercises` on 2026-11-27; all 150 are in the committed cache `openstax/osbooks-introduction-anthropology/exercises/` (no images) with its `COPYRIGHT` notice, copied in from `openstax/tooling/templates/exercises-COPYRIGHT` because the fetch does not write it.
- **Result:** built as PDF, EPUB and HTML on 2026-11-27 with the exercises in; the converter reports no `exercise-uncached` and the build log has no pandoc warning. The first build of the day, without the exercises, is the commit that added the folder.

## What the book needed from the toolchain

Nothing: it converted and built in one pass.

## Left as it is

The converter reports no fallback. The PDF and HTML were not read page by page; that review is the maintainer's.

## Not done

The book needs the maintainer's public backup: `bash tools/mirror-upstreams.sh push introduction-anthropology`.

## Recorded

`openstax/osbooks-introduction-anthropology/CLAUDE.md` ("The books this folder builds"), the lists and counts in `openstax/CLAUDE.md` and the root `CLAUDE.md`, the inventory and its licence table, the converter quick reference, the survey table and the umbrella's checklist.
