# Added `osbooks-neuroscience` to impo (one book)

**Done 2026-11-27** (agent, with the exercise fetch run by the maintainer; part of `tasks/openstax-add-remaining-english-books.md`. William Emerison Six <billsix@gmail.com>, 2026-11-27: "for each book, do the work, commit, archive, commit").

## What was added

`openstax/osbooks-neuroscience/`, created with `tools/add-book.sh neuroscience "Introduction to Behavioral Neuroscience"` and pinned at the upstream head `6164a769d700843059a11fdd5e505e1c0efe1443`. It builds one book:

| Book | Collection | Shape | PDF | Web pages |
|---|---|---|---|---|
| *Introduction to Behavioral Neuroscience* | `introduction-behavioral-neuroscience` | 106 modules in 19 chapters; one level of nesting | 1 pages | 127 |

- **Licence:** CC BY-NC-SA 4.0 (collection XML and the upstream `LICENSE`); the built PDF states it.
- **Figures:** raster only (541 files, 310 MB); no SVG. One file name holds an en dash (`Image-12.04_Stress–critical-periods.png`).
- **Exercises:** 568 embedded links to 568 exercises, all in the `#exercise/<nickname>` scheme, none in `#ost/api/ex/<id>`. The maintainer ran `make fetch-exercises` on 2026-11-27; all 568 are in the committed cache `openstax/osbooks-neuroscience/exercises/` (no images) with its `COPYRIGHT` notice.
- **Result:** built as PDF, EPUB and HTML on 2026-11-27 with the exercises in; the converter reports no `exercise-uncached` and the build log has no pandoc warning.

## What the book needed from the toolchain

**A UTF-8 locale for pandoc.** The first HTML build stopped with "File media/Image-12.04_Stress–critical-periods.png not found in resource path", and the EPUB build before it had left the same figure out with only a warning. The file exists; its name holds an en dash, and in the image's POSIX locale pandoc cannot decode such a name. `openstax/tooling/entrypoint/html.sh` and `epub.sh` now set `LANG=C.UTF-8`. No other fetched book has a non-ASCII figure name (checked in every checkout's `media/`), so no other book's output changes. After the change the HTML build passed with the figure in it and the build log has no pandoc warning.

## Left as it is

Its 40 embedded frames were dropped in the first build and are labelled links since the fix of the same day (`tasks/archive/impo/2026/11/27/openstax-embedded-frame-links-are-dropped.md`). The converter reports no fallback. The PDF and HTML were not read page by page; that review is the maintainer's.

## Not done

The book needs the maintainer's public backup: `bash tools/mirror-upstreams.sh push neuroscience`.

## Recorded

`openstax/osbooks-neuroscience/CLAUDE.md` ("The books this folder builds"), the list in `openstax/CLAUDE.md`, the inventory and its licence table, the survey table and the umbrella's checklist.
