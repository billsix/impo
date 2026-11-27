# Tables of prose wrap and break across pages in the PDFs

**Done 2026-11-27** (agent; found the same day while adding the three nursing books. William Emerison Six <billsix@gmail.com>, 2026-11-27: "for the three defect tasks, make a branch, turn gpg signing off, do the work, commit, archive, commit").

## What was wrong

Every table column was set as `l`, which never wraps, and a table wider than the page was scaled down to the text width. A table whose cells hold sentences was thousands of points wide: Table 7.12 of Population Health for Nurses (four columns of paragraphs) was one hairline across the page, and a table holding a link, which cannot be scaled that way, ran off the page. The HTML and EPUB were not affected.

## Decision (William Emerison Six <billsix@gmail.com>, 2026-11-27: "for your questions, whatever you recommend")

A table of prose longer than a page breaks across pages.

## What was done

- `prose_column_shares` in `openstax/tooling/tools/cnxml2tex/convert.py` decides which tables wrap: the widest cells, side by side, come to more than 90 characters and some column holds a phrase of more than 40; mathematics is not counted, and a table of more than seven columns is left alone. The first threshold tried was 120 characters; a two-column table of single sentences in Pharmacology for Nurses fell under it and stayed at about 60% size, so it was lowered.
- `_render_prose_table` sets such a table with ragged-right `p{…}` columns at `\small`, each column's share of the line following its longest cell, with a rule between rows. On its own it is a `longtable` (breaks across pages, repeats its header); inside a note, an example, an exercise, a list or another table it is a `tabular` in one piece. Every other table is set exactly as before.
- `osbook.cls` loads `longtable` and defines `\OScellbreak`, the line break inside a wrapping cell. The first build stopped on a `\par` there, inside `\textbf{…}` in a header cell of Nutrition for Nurses.
- `\addtocounter{table}{-1}` after each `longtable`: without it table numbers jumped (Table 3.33 became 3.59), because a `longtable` steps the counter by itself.
- `tools/pandoc/preprocess.py` turns `\OScellbreak` into `\newline` for the web editions; pandoc reads the rest.
- Tests in `tools/tests/test_helpers.py` (a prose table on its own, one in a note, a numeric table unchanged, a line break in a cell) and a doctest on `prose_column_shares`.

## Result

All 37 book folders (57 books) were rebuilt in the three formats on 2026-11-27. In their section files 1,863 tables are `longtable`s, 968 are wrapped in one piece and 6,919 keep their natural width; the nursing bundle has 657 wrapped tables. Table 7.12 of Population Health for Nurses was read on the page: four wrapped columns at a readable size, across several pages. The three nursing PDFs grew to 1,568, 622 and 1,653 pages (from 1,267, 537 and 1,400). The sibling `trench/` book, which shares the class, still builds.

## Left as it is

Nobody has read every wrapped table. A `p` column cannot break a long unbroken word or shrink an image, so logs still list boxes more than 100 pt too wide (Population Health for Nurses 8, down from 20). Page counts recorded in the books' `CLAUDE.md` files and the inventory before this date are from before the change; only the nursing books' were updated.

## Recorded

`tasks/reference/tooling/converters.md` ("Tables of prose"), the class's line in `openstax/CLAUDE.md`, `openstax/osbooks-nursing-external-bundle/CLAUDE.md` and the inventory.
