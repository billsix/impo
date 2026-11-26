# impo — Island of Misfit Patches, OpenStax edition

Patch carrier for the maintainer's **LaTeX/PDF/EPUB/HTML port of OpenStax open textbooks**, on top of
pristine, pinned OpenStax content — the same idea as its sibling **imps**
(https://github.com/billsix/imps, the N64-PC-ports carrier), but for books, and kept in its own repo
because the committed OpenStax content makes it large. **Extracted from imps 2026-09-03** (with its
history) so imps itself stays small; the OpenStax work's commit history is preserved here.

The maintainer has book-porting work he wants carried on top of OpenStax's own repos without
maintaining forks of them: impo stores the shared conversion toolchain plus, per book, the scripts
that fetch pristine upstream content at a pinned commit, overlay the toolchain, and build the book —
in an ephemeral podman container. One folder per book; the family is self-contained under `openstax/`.

## Structure — families under the repo root

impo groups books into **families** (a family = books of the same source/kind), each a top-level
folder. Two book families exist, plus the `study/` family of material built from the books:

- **`openstax/`** — LaTeX ports of OpenStax open textbooks (19 book folders on 2026-11-26, more being added:
  `tasks/openstax-add-remaining-english-books.md`) that convert **CNXML→LaTeX**
  with a shared python converter. **The pilot family; read `openstax/CLAUDE.md` first.** Layout:
  - **`openstax/CLAUDE.md`** — the family contract: the shared toolchain, the per-book folder
    contract (fetch → apply-overlay → build), the *downloaded → commit / generated → ignore* content
    model, and the **licensing split** (toolchain is the maintainer's MIT; OpenStax content is CC BY,
    not the maintainer's).
  - **`openstax/tooling/`** — the shared, book-agnostic toolchain (CNXML→LaTeX converter, exercise
    fetcher, house LaTeX class/styles `osbook.cls`+envs+defer, pandoc web templates, tests,
    Fedora+TeXLive Dockerfile). Each book mounts at the fixed path `/book` so nothing hardcodes a slug.
  - **`openstax/osbooks-<subject>/`** — one thin folder per book: `fetch.sh`, `apply.sh` (overlays
    `../tooling/`), `Makefile`, `CLAUDE.md`, `README.md`, and — for os-embed books — a committed
    `exercises/` cache **with its `COPYRIGHT` NOTICE**.
- **`trench/`** — open textbooks that ship as **native LaTeX source** (not CNXML), restyled to the
  same osbook house look via a per-book LaTeX shim, **reusing `openstax/tooling/`** (its `osbook.cls`
  layer + the Fedora/TeXLive/pandoc image) rather than a converter. Read `trench/CLAUDE.md`. First
  book: `trench/elementary-differential-equations/` (William F. Trench, CC BY-NC-SA 3.0). Added
  2026-09-19; tracked in `tasks/archive/impo/2026/09/19/add-trench-differential-equations-book.md`.
- **`study/`** — not books: literacy tests, cliff-notes study guides, problem notebooks and a Go
  quiz server (`study/quiz/`), built in the OpenStax toolchain image (plus sympy; the notebooks add
  Jupyter + ePiX) and generated from data (`study/bank/*.toml`, `study/cliffnotes/*.toml`, the
  converter's section LaTeX) with every answer sympy-checked. Read `study/CLAUDE.md`. Added 2026-11-21.

## Contracts (the parts that aren't in `openstax/CLAUDE.md`)

- **Docs live in impo, patches/toolchain carry code.** Prose about a book (this file, `CLAUDE.md`s,
  task docs, reference docs) lives natively in impo; the checkout of OpenStax content is gitignored and
  regenerates from the pin.
- **Self-contained scripts.** Every script starts with `cd "$(dirname "$0")"` and uses only relative
  paths — runnable from anywhere, no hardcoded host paths.
- **"Sync with upstream" (or "rebase my patches") means: move each pin to current upstream and prove the
  project still works** (William Emerison Six <billsix@gmail.com>, 2026-11-26). impo carries no patch
  series, so there is nothing to rebase: set each book's `PIN_SHA` in `fetch.sh` to the upstream
  default-branch head, refetch, re-apply the overlay, then convert and **build every moved book in all
  formats** (`make convert`, `make dist`; `tools/build-after-sync.sh` does both). The agent makes that build
  itself as part of the sync (the maintainer, 2026-11-26: a sync or rebase ends with a clean build);
  `make convert` alone is the step that breaks when upstream's markup changes, but it is not enough. Recon is read-only; the method and the last run are in
  `tasks/archive/impo/2026/10/20/openstax-resync-upstream-pins.md`; the 2026-11-26 run, which also built every
  moved book, is `tasks/archive/impo/2026/11/26/openstax-sync-upstream-pins-2026-11.md`.
- **Every pin must stay fetchable without the upstream** (William Emerison Six <billsix@gmail.com>, 2026-11-26; OpenStax's `osbooks-algebra-1`
  disappeared from GitHub and no copy was reachable). The backup for each book is a public mirror on the
  maintainer's GitHub account (`github.com/billsix/<book>`), pushed from his private clones. A sync is
  finished only when each moved pin can be fetched from its mirror; anything that does not resolve in the
  same sitting (a missing mirror, a vanished upstream, a book that no longer converts) gets a task, never a
  note in passing. `fetch.sh` falls back to the mirror by itself; `tools/mirror-upstreams.sh check` reports
  which mirrors exist and hold their pin, and `tools/mirror-upstreams.sh push` (the maintainer's, with his
  GitHub credentials) updates them. After a sync, also `make image-export` in one book folder and keep the
  tar: the image is the build's last outside dependency. The mirrors are being set up in
  `tasks/openstax-algebra-1-upstream-gone-backup-plan.md`.
- **Unsigned commits in checkouts are authorized/automated.** The maintainer's gitconfig enables commit
  signing, which fails in the sandbox; each `fetch.sh` sets `commit.gpgsign false` in the checkout it
  manages (never globally). These commits are scaffolding; the durable product is impo's own files.
- **`tasks/`** — task docs at `tasks/*.md`; per-project reference docs under `tasks/reference/<project>/`;
  archives per project at `tasks/archive/<project>/<YYYY>/<MM>/<DD>/`. The `<project>` key is the book
  slug (e.g. `osbooks-anatomy-physiology`); repo-wide tasks use `impo`.
- **`tools/`** — repo-level dev scripts (not copied into any book checkout, unlike
  `openstax/tooling/tools/`):
  - **`build-books.sh`** (behind the root `Makefile`: `make books`, `make <book>`, `make list-books`) —
    the one-call build: per book folder, fetch (if no checkout) → `apply.sh` → `make dist` → collect into
    the root `output/` (`<book>/` HTML with the media its pages use copied in, `<book>.pdf`,
    `<book>.epub`, `<book>-html.zip`). Non-fatal per
    folder, exit 1 if any failed. `.github/workflows/release.yml` runs `make <book>` per folder on a `v*`
    tag push and attaches the PDFs/EPUBs/HTML zips to a GitHub Release.
  - **`publish-pages.sh`** (behind `make publish-pages`, run by the maintainer on the host) — stages
    the collected `output/<book>/` sites plus a landing page into `output/pages/` and pushes them with
    `ghp-import --no-history` to impo's `gh-pages` branch (billsix.github.io/impo/<book>/); refuses to
    push over the 1 GB Pages limit (`BOOKS="..."` publishes a subset, `DRY_RUN=1` only stages). Each
    book's first page links its PDF/EPUB/`<book>-html.zip` on the latest GitHub Release. Design and the
    size problem: `tasks/reference/openstax/publishing.md`.
  - **The pin-sync scripts** (promoted 2026-11-26 from the sync recorded in
    `tasks/archive/impo/2026/11/26/openstax-sync-upstream-pins-2026-11.md`): `bump-pins.sh <book> …` sets each
    book's `PIN_SHA` to its upstream head and moves the existing `checkout/` to it in place;
    `build-after-sync.sh <log dir> <book> …` re-applies the overlay and runs `make convert` then `make dist`,
    three books at a time, with a PASS/FAIL line per step; `sync-pin-docs.py` makes each book's `CLAUDE.md`
    name the pin its `fetch.sh` carries. Book names are given without the `osbooks-` prefix.
  - `add-book.sh <name> "<Title>"` — creates a new `openstax/osbooks-<name>/` folder from
    `tools/book-template/`, pinned at the upstream head (the steps are "Adding a book" in `openstax/CLAUDE.md`).
  - `survey-upstream-books.py` — lists every public `osbooks*` repository of the `openstax` organisation on
    GitHub with its books, language, licence, size, whether impo builds it, whether the maintainer's mirror
    exists, and whether he has rejected it (decisions and reasons: `tools/upstream-books-rejected.txt`). A
    book impo builds whose upstream has vanished gets a row marked "gone", with where its source is still
    held and the action needed (`tools/upstream-books-gone.txt` records what the tool cannot check).
    Its output is the table in `tasks/reference/openstax/upstream-book-repositories.md` (54 repositories, 88
    books on 2026-11-26; impo builds 15 of them plus the vanished algebra-1).
  - `build-web-editions.sh` — a fan-out that re-applies the toolchain overlay and runs `make html &&
    make epub` across every OpenStax book folder, logging PASS/FAIL per book (`bash tools/build-web-editions.sh
    [book-slug]`).
  - `check-mobile.js` — a Playwright regression check that a built book has no phone horizontal-scroll
    and a working on-this-page drawer (`NODE_PATH=<pw>/node_modules node tools/check-mobile.js
    <built-site-dir> [width]`; needs `npm i playwright && npx playwright install chromium` — a dev-only
    dep, not a repo dependency). See `tasks/reference/tooling/web-editions-mobile.md`.
- **ROM/asset acquisition is out of scope** — a book's content comes from its pinned OpenStax upstream
  via `fetch.sh`; never commit the upstream `checkout/`.

## License

MIT (`LICENSE`) for impo's original content — the toolchain, scripts, docs. The pinned OpenStax content
(CNXML/`media`) and the committed `exercises/` caches are **not the maintainer's**. Each book is under the
licence its own source declares: **CC BY 4.0 for `osbooks-physics` and `osbooks-statistics`, CC BY-NC-SA 4.0
for every other book folder** (the table is in `tasks/reference/openstax/book-inventory.md`). The built books are
adaptations and carry the same licence as their source. See `openstax/CLAUDE.md` and each cache's
`COPYRIGHT`.
