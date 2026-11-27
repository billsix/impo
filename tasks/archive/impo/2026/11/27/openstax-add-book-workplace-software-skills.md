# Added `osbooks-workplace-software-skills` to impo (one book)

**Done 2026-11-27** (agent, with the exercise fetch run by the maintainer; part of `tasks/openstax-add-remaining-english-books.md`. William Emerison Six <billsix@gmail.com>, 2026-11-27: "you can make a branch, temporarily turn off gpg signing, and start working on all of them (minus the business ones for now)").

## What was added

`openstax/osbooks-workplace-software-skills/`, created with `tools/add-book.sh workplace-software-skills "Workplace Software and Skills"` and pinned at the upstream head `4ec59c186873eccfd21234586c6bfd9682532ead`. It builds one book:

| Book | Collection | Shape | PDF | Web pages |
|---|---|---|---|---|
| *Workplace Software and Skills* | `workplace-software-skills` | 105 modules in 15 chapters; one level of nesting | 1,215 pages | 122 |

- **Licence:** CC BY-NC-SA 4.0 (collection XML and the upstream `LICENSE`); the built PDF states it.
- **Figures:** raster only (1,213 files, 349 MB); no SVG. The PDF is 282 MB and the EPUB 242 MB.
- **Exercises:** 682 embedded links to 682 exercises, all in the `#exercise/<nickname>` scheme, none in `#ost/api/ex/<id>`. The maintainer ran `make fetch-exercises` on 2026-11-27; all 682 are in the committed cache `openstax/osbooks-workplace-software-skills/exercises/` (20 images) with its `COPYRIGHT` notice, copied in from `openstax/tooling/templates/exercises-COPYRIGHT` because the fetch does not write it.
- **Result:** built as PDF, EPUB and HTML on 2026-11-27 with the exercises in; the converter reports no `exercise-uncached` and the build log has no pandoc warning. The first build of the day, without the exercises, is the commit that added the folder.

## What the book needed from the toolchain

Nothing: it converted and built in one pass.

## Left as it is

Its 349 MB of figures give a 282 MB PDF and a 242 MB EPUB; what that means for the published site is `tasks/openstax-pages-size-budget.md`'s to decide. The converter reports no fallback. The PDF and HTML were not read page by page; that review is the maintainer's.

## Not done

The book needs the maintainer's public backup: `bash tools/mirror-upstreams.sh push workplace-software-skills`.

## Recorded

`openstax/osbooks-workplace-software-skills/CLAUDE.md` ("The books this folder builds"), the lists and counts in `openstax/CLAUDE.md` and the root `CLAUDE.md`, the inventory and its licence table, the converter quick reference, the survey table and the umbrella's checklist.
