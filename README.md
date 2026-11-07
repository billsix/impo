# impo — Island of Misfit Patches, OpenStax edition

The maintainer's **LaTeX/PDF/EPUB/HTML port of OpenStax open textbooks**, carried on top of pinned,
pristine OpenStax content without maintaining forks of OpenStax's repos. Sibling to
[imps](https://github.com/billsix/imps) (the N64-PC-ports carrier); split into its own repo because the
committed OpenStax exercise content makes it large. Extracted from imps 2026-09-03 with its history.

Each book lives in a self-contained folder under `openstax/`; a single shared toolchain
(`openstax/tooling/`) does the conversion. The upstream OpenStax checkout and all build products are
gitignored — the toolchain, per-book scripts, committed exercise caches, and docs ARE the repo.

## Build every book, or one (one call, like modelviewprojection's `make docs`)

```sh
make books                   # [HOST] every book folder: PDF + HTML + EPUB, collected into ./output/
make anatomy-physiology      # [HOST] one book folder (names: make list-books)
```

- Output: `output/<book>/` (self-contained HTML site), `output/<book>.pdf`, `output/<book>.epub`;
  per-folder logs in `output/logs/`. A failing book doesn't stop the others; the exit status reports it.
- First run fetches each book's pinned content (network) and builds the TeX Live image (large, slow once).
- **Release downloads:** pushing a version tag (`git tag v2026.11.0 && git push github v2026.11.0`) runs
  `.github/workflows/release.yml`, which builds every book and attaches the PDFs + EPUBs to a GitHub
  Release.

## Build a book

```sh
cd openstax/osbooks-anatomy-physiology
./fetch.sh     # clone the pinned OpenStax content into checkout/ (gitignored)
./apply.sh     # overlay the shared ../tooling/ onto the checkout
make dist      # build PDF + EPUB + chunked HTML into checkout/output/  (make image builds first)
```

- `make convert` / `pdf` / `html` / `epub` build individual formats; `make fetch-exercises` refreshes a
  book's downloaded practice-exercise cache (the one networked step; the result is committed).
- The pin (the OpenStax commit the port was made against) lives in each book's `fetch.sh` (`PIN_SHA`).

## License

MIT (`LICENSE`) for impo's own content (toolchain, scripts, docs). The OpenStax content this repo pins
and caches — CNXML source, media, and the committed `exercises/` problem sets — is **© OpenStax,
licensed CC BY 4.0, not the maintainer's**. See `openstax/CLAUDE.md` and each `exercises/COPYRIGHT`.
