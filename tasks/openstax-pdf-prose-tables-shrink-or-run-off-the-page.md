# In the PDFs a table of prose is shrunk to a hairline or runs off the page

**Status:** proposed — needs go-ahead
**Priority:** 3
**Difficulty:** 6 (a column-width rule in the converter that has to leave the mathematics books' narrow tables as they are; then every PDF rebuilt)
**Created:** 2026-11-27 (agent, found while adding the three nursing books; `tasks/openstax-add-remaining-english-books.md`)

## BLUF

The converter sets every table column as `l`, which never wraps, and then scales a table that is wider than the page down to the text width. For a table of numbers that is right. A table whose cells hold sentences is thousands of points wide, so it is scaled down until it cannot be read, and a table that holds a link is not scaled at all and runs off the page. The HTML and EPUB are not affected. Done means a table whose cells hold prose is set with wrapping columns at a readable size in the PDF, and the narrow tables of the books already built are unchanged.

## Context

**Read first:** `render_table` in `openstax/tooling/tools/cnxml2tex/convert.py` (the comment "Fit wide tables to the text width" explains the two fitting methods and why a table with `\href` cannot go through `\resizebox`) and `tasks/reference/tooling/converters.md`.

### What was seen (2026-11-27)

- *Population Health for Nurses*, PDF page 1371: Table 7.12 (nursing theorists, four columns of paragraphs) is one hairline across the page. Its natural width is over 11,000 pt ("Overfull \hbox (11006.97083pt too wide)" in `population-health.log`, from section file `m00376.tex`).
- *Pharmacology for Nurses*, PDF page 307: Table 3.33 (two columns, one sentence per row) is scaled to roughly half the body size. It is legible; tables with longer rows are not.
- The logs of the books added that day list boxes more than 100 pt too wide: Population Health for Nurses 20 (the worst 11,006 pt), College Success Concise 8 and Preparing for College Success 8 (worst 1,949 pt), Lifespan Development 8, Nutrition for Nurses 3, Introduction to Sociology 3e 1. A scaled table gives no warning, so the log undercounts.

### How many tables (counted in the CNXML of every fetched book, 2026-11-27)

Tables with a row whose cells hold more than 250 characters together, which cannot fit a page unwrapped: 1,114 of 11,160 in 57 books. The most affected: Pharmacology for Nurses 320 of 431, Life, Liberty, and the Pursuit of Happiness 149 of 436, Population Health for Nurses 132 of 170, Biology for AP Courses 2e 92 of 205, Writing Guide 63 of 121, Nutrition for Nurses 47 of 113, Preparing for College Success 27 of 119, College Success Concise 26 of 109, Anatomy and Physiology 2e 25 of 104. The three algebra books of the Prealgebra bundle have about 1,000 tables each and at most 14 such tables. The count is a proxy; nobody has looked at each table.

### Approaches to weigh

- Choose the column type per column from its content: `l` when the longest cell is short, a `p{…}` or `tabularx` `X` column when it holds prose, with widths shared in proportion to content. `longtable` or `xltabular` would also let a long table break across pages, which a `tabular` in a `\resizebox` cannot.
- Keep `\resizebox` only for tables that are still too wide after wrapping (many narrow numeric columns).
- `tools/pandoc/preprocess.py` strips the `\resizebox` wrapper for the web editions; a new table environment has to pass through pandoc too.

## Plan

- [ ] Decide the rule for "this column holds prose" and the environment; write tests for a numeric table (unchanged output), a prose table, and a table with a link.
- [ ] `tools/compare-converter-output.sh`: list which tables change in the books already built, and read a sample of them in the PDF.
- [ ] Rebuild the affected books; record the rule in `tasks/reference/tooling/converters.md`.

## Open questions

1. Shall a prose table that is longer than a page break across pages (`longtable`-style), or stay in one piece as now? The agent recommends breaking: several nursing tables are longer than a page once their cells wrap.
