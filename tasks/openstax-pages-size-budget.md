# The published site holds a committed list of books that fits GitHub Pages' 1 GB

**Done 2026-11-28** (agent. Created 2026-11-21 as a follow-on of
`tasks/archive/impo/2026/11/21/openstax-publish-books.md`; go-ahead from William Emerison Six
<billsix@gmail.com>, 2026-11-28: "for those three tasks you mention, make a branch, temporarily turn gpg
signing off, do them in the order you'd like").

## What was wrong

`make publish-pages` staged every built web edition and refused to push, because the set was several times
GitHub Pages' 1 GB limit. Nothing said which books the site should hold, so each publish needed a
hand-written `BOOKS="..."`.

## What changed

- **`tools/pages-books.txt`** is the published set: one book name per line. `tools/publish-pages.sh` reads
  it when `BOOKS` is not given; `BOOKS="a b"` still names other books and `BOOKS=all` stages every built
  one. The size check and its refusal are unchanged.
- **The list holds seven books of the mathematics ladder:** Prealgebra 2e, Elementary Algebra 2e,
  Intermediate Algebra 2e, College Algebra 2e and Calculus Volumes 1 to 3, 820 MB together. This is option 1
  of the task ("publish a subset … the math ladder"), which the task recommended; its example set and its
  estimate (0.82 GB) are the ones measured here.
- **`tools/web-edition-sizes.py`** measures the built sites the way they are published (only the files a
  site's pages use), per book, with the part a sibling in the same folder also uses, and the totals;
  `--books tools/pages-books.txt` measures a list.
- **The landing page's footer** no longer says every book is CC BY 4.0 (true of four folders of 45); it
  points at each book's "About This Edition" page.

## Measurements (2026-11-28, all 45 folders built that day)

- 71 sites, 9.0 GB; 7.8 GB if a file shared by two sites of one folder were stored once.
- The ten ladder books are 1,230 MB. The eight the prerequisites map names (the seven plus Precalculus 2e)
  are 972 MB, which is under the limit only on paper: the staged tree is larger than the sum of its files.
  So Precalculus 2e (152 MB), Algebra and Trigonometry 2e (153 MB) and the College Algebra corequisite
  edition (105 MB) are left off, and a link into one of them from a published book is reported by the link
  checker as "not published here".
- The full table: `python3 tools/web-edition-sizes.py`; the figures kept are in
  `tasks/reference/openstax/publishing.md`, "The size limit, and what the site holds".

## Options not taken

Recompressing the JPEGs for the web (option 2), storing a folder's shared media once (option 3: 1.3 GB of
the 9.0, most of it in the College Algebra folder) and hosting the images elsewhere (option 4) each fit
more books, and none fits all 71 sites. They were measured where the tool could (option 3) and not built.

## Verification

- `python3 tools/web-edition-sizes.py --books tools/pages-books.txt` prints 820.2 MB in 7 sites.
- `DRY_RUN=1 bash tools/publish-pages.sh` with no `BOOKS` reads the list: it stops at `not built:
  output/prealgebra-2e/index.html`, because the root `output/` tree holds two other books in this sandbox.
  A staging run of the seven books, which needs `make prealgebra-bundle college-algebra-bundle
  calculus-bundle` first, and the push itself are the maintainer's, on the host.
- `ruff check` and `ruff format --check` pass on the new tool; its doctest passes.

## Left as it is

The choice of books is the agent's, under the go-ahead above. To publish a different set, edit
`tools/pages-books.txt` and measure it.

## Also noted here

Page file names contain `:` (`059-mod:m81444.html`), which Windows cannot unpack from `<book>-html.zip`:
its own task, `tasks/openstax-html-filenames-without-colons.md`.

## Recorded

`tasks/reference/openstax/publishing.md`, the root `CLAUDE.md` (`tools/`), `README.md` ("Publish the web
editions").
