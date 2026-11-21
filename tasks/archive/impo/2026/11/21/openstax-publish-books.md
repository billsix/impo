# Publish the OpenStax books (PDF / HTML / EPUB) — gh-pages site + Release downloads

**Done 2026-11-21** (branch `study-and-publishing`), except the publish itself, which is the
maintainer's manual step, and the 1 GB Pages limit, which the full site does not fit: follow-on
`tasks/openstax-pages-size-budget.md`. Design and commands: `tasks/reference/openstax/publishing.md`.

## Decisions (William Emerison Six <billsix@gmail.com>, 2026-11-21: "go with your recommendations")

- GitHub Pages from a **`gh-pages` branch of impo** (no new repo), at `billsix.github.io/impo/<book>/`;
  one combined site so links between books are relative. `ghp-import --no-history` keeps the branch
  one commit.
- **Downloads are GitHub Release assets** (PDF, EPUB, zipped HTML), linked from a box on each book's
  first page plus a side-nav "Downloads" entry.
- `make publish-pages` is manual, on the host (this task took it over from
  `tasks/impo-make-target-per-book-and-publish.md`, which still waits on its first tag push).

## What was built

- `openstax/tooling/tools/pandoc/build_nav.py`: the "Download this book" box on `index.html` and the
  side-nav "Downloads" entry, linking `https://github.com/billsix/impo/releases/latest/download/<book>.{pdf,epub}`
  and `<book>-html.zip` (`OSBOOK_DOWNLOAD_BASE` overrides; empty disables). `chunked-template.html`
  has the `<!--DOWNLOADS-->` placeholder; `osbook-web.css` styles both.
- `openstax/tooling/tools/pandoc/site_files.py`: the files a built site uses. `entrypoint/html.sh`
  zips exactly those into `checkout/output/<book>-html.zip` (a `make html` / `make dist` output);
  `tools/build-books.sh` copies exactly those into `output/<book>/` (instead of the whole bundle
  `media/`) and collects the zip (trench: zipped in `collect`). `.github/workflows/release.yml`
  attaches `*-html.zip` with the PDFs and EPUBs.
- `tools/publish-pages.sh` + root `make publish-pages`: stage `output/pages/` (the built books + a
  landing page with each book's downloads and the CC BY / CC BY-NC-SA attribution), refuse over
  `PAGES_LIMIT_MB` (1000), then `ghp-import --no-history --no-jekyll --force --push --remote github
  --branch gh-pages`; `BOOKS=`, `DRY_RUN=1`, `PAGES_REMOTE`.
- `openstax/tooling/tools/pandoc/check_links.py`: checks the local links of a directory of built
  sites (used by the cross-book task).
- Docs: `CLAUDE.md`, `openstax/CLAUDE.md`, `README.md`, `tasks/reference/openstax/publishing.md`.

## Findings

- **The site does not fit Pages' 1 GB:** the 28 built web editions measure 10.1 GB copied whole and
  4.5 GB with only the referenced files (the referenced-only copy alone cut prealgebra-2e from 945 MB
  to 125 MB). The task's earlier "~0.3 GB of HTML" was the pages without their figures. Options are
  in the follow-on task; `publish-pages.sh` refuses the full set and publishes a subset with `BOOKS=`.
- Page names contain `:` (`059-mod:m81444.html`): fine on the web, unpackable on Windows; recorded in
  the follow-on.

## Verification

- `make introduction-python-programming` (nested podman, fresh Fedora-45 TeX Live image): PASS in
  101 s; `output/introduction-python-programming/` is 8.4 MB (96 MB before the referenced-only copy),
  its `index.html` has the downloads box and every page the side-nav entry, and
  `introduction-python-programming-html.zip` (164 files) unpacks to a site with 0 broken links
  (`check_links.py`).
- `DRY_RUN=1 make publish-pages`: staged that book plus the existing trench build (27 MB) with the
  landing page; with `PAGES_LIMIT_MB=10` it refused (exit 1) and listed the per-book sizes.
- The push itself, against a throwaway clone of impo whose `github` remote was a local bare repo
  (ghp-import 2.x from PyPI in a scratch venv): exit 0, `gh-pages` holds `.nojekyll`, `index.html` and
  the two book directories; a second publish left the branch at one parentless commit. (This caught
  a wrong flag: ghp-import spells it `--no-jekyll`.)
- `make -C openstax/tooling type-check` (ruff, annotations, ty, 46 pytest incl. doctests): exit 0.
- **Not verified:** a real push to GitHub and the Pages settings (the maintainer's step); the
  Release links (they resolve after the first `v*` tag); `make books` over all 17 folders (hours,
  ~4 GB; the three math bundles' HTML were rebuilt in the cross-book task); the release workflow on
  GitHub (still waiting on the tag push tracked in `tasks/impo-make-target-per-book-and-publish.md`).
