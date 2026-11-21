# Publishing the books — GitHub Pages site and GitHub Release downloads

**Reference doc — living.** How impo's books are published: where, by which commands, what each
book's first page links, and the size limit that the full site does not fit. Decided in
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
  commit does not descend from the old one. `BOOKS="a b"` publishes a subset; `DRY_RUN=1`
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

## The size problem (open: `tasks/openstax-pages-size-budget.md`)

GitHub Pages refuses a published site over 1 GB. The web editions do not fit:

- Measured 2026-11-21 over the 28 built sites (all 16 OpenStax folders): **10.1 GB** copied whole,
  **4.5 GB** with only the referenced files. Largest: anatomy-and-physiology-2e 0.50 GB,
  biology-2e 0.43 GB, microbiology 0.35 GB, chemistry-2e and chemistry-atoms-first-2e 0.29 GB each;
  smallest: introduction-python-programming 8.5 MB.
- The figures are already web-sized (anatomy-and-physiology-2e: 722 referenced images, nearly
  all JPEGs 825 px wide, 0.25–0.55 MB in a sample of three); the size is their number.
- So `publish-pages.sh` refuses to push over the limit and prints the per-book sizes; a subset
  under 1 GB can be published with `BOOKS=`. The choice of what to do (publish a subset, recompress
  the JPEGs for the web, deduplicate media shared by a bundle's volumes, or host the images
  elsewhere) is the maintainer's: `tasks/openstax-pages-size-budget.md`.

## Gotchas

- **Page file names contain `:`** (`059-mod:m81444.html`, pandoc's chunk template `%n-%i` with
  the module id). Browsers and GitHub Pages handle it (a URL scheme must start with a letter, so
  `059-mod:` reads as a relative path), but **Windows cannot unpack such names** from
  `<book>-html.zip`. Changing the chunk template would rename every page and break every
  cross-book index (`crossbook/index/*.json`), so it is left as is; noted in the size-budget task.
- The page index files of the cross-book links are generated from built sitemaps; a converter
  change that renumbers pages needs `crossbook_index.py` re-run (see the cross-book links doc).
