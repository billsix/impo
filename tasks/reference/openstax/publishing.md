# Publishing the books — GitHub Pages site and GitHub Release downloads

**Reference doc — living.** How impo's books are published: where, by which commands, what each
book's first page links, and the size limit that decides which books the site holds. Decided in
`tasks/archive/impo/2026/11/21/openstax-publish-books.md` (William Emerison Six
<billsix@gmail.com>, 2026-11-21: "go with your recommendations"; no new repo).

## The layout

- **Site:** the `gh-pages` branch of impo, served by GitHub Pages at
  `https://billsix.github.io/impo/<book>/` (one directory per collection slug, e.g.
  `prealgebra-2e/`, `calculus-volume-1/`, `elementary-differential-equations/`), with a landing
  page at `https://billsix.github.io/impo/` listing every published book. One site for all books,
  so a link between books is the relative path `../<other-book>/<page>.html`
  (`tasks/reference/tooling/cross-book-links.md`).
- **Downloads:** GitHub Release assets, attached by `.github/workflows/release.yml` on a `v*` tag
  push: `<book>.pdf`, `<book>.epub` and `<book>-html.zip` (the web edition, zipped). Each book's
  first page (`index.html`) has a "Download this book" box linking
  `https://github.com/billsix/impo/releases/latest/download/<book>.{pdf,epub}` and
  `<book>-html.zip`, and every page's left side-nav has a "Downloads" entry pointing at that box.
  `releases/latest/download/` always resolves to the newest release, so the links never change.
  The base URL is `DEFAULT_DOWNLOAD_BASE` in `openstax/tooling/tools/pandoc/build_nav.py`
  (`OSBOOK_DOWNLOAD_BASE` overrides it; empty disables the box). Trench's make4ht web edition
  has no download box (it does not use the osbook web template).

## The commands

- `make <book>` / `make books` (root `Makefile`, `tools/build-books.sh`) collect into `output/`:
  `<book>/` (only the files its pages use — see below), `<book>.pdf`, `<book>.epub`,
  `<book>-html.zip`.
- `make publish-pages` (`tools/publish-pages.sh`, run by the maintainer on the host): stages
  every built `output/<book>/` plus the landing page into `output/pages/`, checks the size, and
  runs `ghp-import --no-history --no-jekyll --force --push --remote github --branch gh-pages`.
  `--no-history` makes the branch one parentless commit, so it does not grow with each publish
  (but a clone of impo still downloads the current site); `--force` is required because that
  commit does not descend from the old one. Without `BOOKS` it publishes the books `tools/pages-books.txt`
  lists; `BOOKS="a b"` publishes those; `BOOKS=all` every built book; `DRY_RUN=1`
  stages without pushing; `PAGES_LIMIT_MB` (default 1000) is the refusal threshold;
  `PAGES_REMOTE` (default `github`) the remote.
- One-time maintainer steps: `pip install ghp-import` on the host; in the GitHub repo settings,
  Pages → "Deploy from a branch" → `gh-pages` / root; push a `v*` tag so the download links
  resolve (until the first release exists they 404).

## Only the files the pages use

A bundle folder's site directories link a `media/` that holds the **whole bundle's** figures
(raw SVGs, originals and every volume's images), so copying it per volume multiplied the size.
`openstax/tooling/tools/pandoc/site_files.py <site>` lists the site's own pages/css/js/json plus
every local `src`/`href` target; `html.sh` zips exactly that list (`<book>-html.zip`) and
`build-books.sh` copies exactly that list into `output/<book>/`. Measured 2026-11-21 on
prealgebra-2e: 3049 files, 125 MB, against 945 MB for the dereferenced directory.

## The size limit, and what the site holds

GitHub Pages refuses a published site over 1 GB. The web editions do not fit, so the site holds a chosen
set and every other book is a Release download only.

- **Measured 2026-11-28** with `python3 tools/web-edition-sizes.py` over the 71 built sites of the 45 OpenStax
  folders: **9.0 GB** counting only the files each site's pages use (7.8 GB if a file two sites of one
  folder share were stored once). Largest: anatomy-and-physiology-2e 489 MB, principles-financial-accounting
  479 MB, biology-2e 419 MB, life-liberty-and-pursuit-happiness 360 MB, microbiology 339 MB, us-history
  333 MB. (2026-11-21, when there were 28 sites in 16 folders: 4.5 GB, and 10.1 GB copied whole.)
- The figures are already web-sized (anatomy-and-physiology-2e: 722 referenced images, nearly all JPEGs
  825 px wide, 0.25–0.55 MB in a sample of three); the size is their number.
- **The published set is the committed list `tools/pages-books.txt`**, which `tools/publish-pages.sh` reads
  when `BOOKS` is not given. On 2026-11-28 it holds seven books of the mathematics ladder (Prealgebra 2e,
  Elementary Algebra 2e, Intermediate Algebra 2e, College Algebra 2e, Calculus Volumes 1 to 3): **820 MB**
  (`python3 tools/web-edition-sizes.py --books tools/pages-books.txt`). They are the books whose pages link
  each other's sections, so the set keeps those links working on the site.
- **Left off, and what that costs:** Precalculus 2e (152 MB), Algebra and Trigonometry 2e (153 MB) and the
  College Algebra corequisite edition (105 MB) belong to the same ladder; all ten are 1,230 MB. The eight
  books the prerequisites map names (the seven plus Precalculus 2e) are 972 MB, too close to the limit to
  rely on: the staged tree is larger than the sum of its files. A link from a published book into a book
  left off is reported by the link checker as "not published here".
- `publish-pages.sh` still measures the staged tree and refuses to push over the limit, printing the size
  of each book. `BOOKS="a b"` publishes other books; `BOOKS=all` stages every built book.
- **Ways to fit more, not done:** recompress the JPEGs for the web (needs ImageMagick on the host and a
  measurement of what quality costs); store a folder's shared media once (it would save 1.3 GB of the 9.0,
  most of it in the College Algebra folder, whose four books share 92 to 131 MB each); or host the images
  elsewhere. None of them brings all 71 sites under 1 GB. The choice of the seven is the agent's, made under
  the maintainer's go-ahead of 2026-11-28 and following the recommendation of the task; change the list to
  change it. Record: `tasks/archive/impo/2026/11/28/openstax-pages-size-budget.md`.
- **The landing page states no single licence.** Its footer said every book was CC BY 4.0, which is true of
  four folders; it now points at each book's own "About This Edition" page.

## Gotchas

- **Page file names contain `:`** (`059-mod:m81444.html`, pandoc's chunk template `%n-%i` with
  the module id). Browsers and GitHub Pages handle it (a URL scheme must start with a letter, so
  `059-mod:` reads as a relative path), but **Windows cannot unpack such names** from
  `<book>-html.zip`. Changing the chunk template would rename every page and break every
  cross-book index (`crossbook/index/*.json`), so it is left as is; its task is
  `tasks/openstax-html-filenames-without-colons.md`.
- The page index files of the cross-book links are generated from built sitemaps; a converter
  change that renumbers pages needs `crossbook_index.py` re-run (see the cross-book links doc).
