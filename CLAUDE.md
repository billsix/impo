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
folder. Two families exist:

- **`openstax/`** — LaTeX ports of OpenStax open textbooks (16 books) that convert **CNXML→LaTeX**
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

## Contracts (the parts that aren't in `openstax/CLAUDE.md`)

- **Docs live in impo, patches/toolchain carry code.** Prose about a book (this file, `CLAUDE.md`s,
  task docs, reference docs) lives natively in impo; the checkout of OpenStax content is gitignored and
  regenerates from the pin.
- **Self-contained scripts.** Every script starts with `cd "$(dirname "$0")"` and uses only relative
  paths — runnable from anywhere, no hardcoded host paths.
- **Unsigned commits in checkouts are authorized/automated.** The maintainer's gitconfig enables commit
  signing, which fails in the sandbox; each `fetch.sh` sets `commit.gpgsign false` in the checkout it
  manages (never globally). These commits are scaffolding; the durable product is impo's own files.
- **`tasks/`** — task docs at `tasks/*.md`; per-project reference docs under `tasks/reference/<project>/`;
  archives per project at `tasks/archive/<project>/<YYYY>/<MM>/<DD>/`. The `<project>` key is the book
  slug (e.g. `osbooks-anatomy-physiology`); repo-wide tasks use `impo`.
- **`tools/`** — repo-level dev scripts (not copied into any book checkout, unlike
  `openstax/tooling/tools/`):
  - `build-web-editions.sh` — a fan-out that re-applies the toolchain overlay and runs `make html &&
    make epub` across all 16 OpenStax books, logging PASS/FAIL per book (`bash tools/build-web-editions.sh
    [book-slug]`).
  - `check-mobile.js` — a Playwright regression check that a built book has no phone horizontal-scroll
    and a working on-this-page drawer (`NODE_PATH=<pw>/node_modules node tools/check-mobile.js
    <built-site-dir> [width]`; needs `npm i playwright && npx playwright install chromium` — a dev-only
    dep, not a repo dependency). See `tasks/reference/tooling/web-editions-mobile.md`.
- **ROM/asset acquisition is out of scope** — a book's content comes from its pinned OpenStax upstream
  via `fetch.sh`; never commit the upstream `checkout/`.

## License

MIT (`LICENSE`) for impo's original content — the toolchain, scripts, docs. The pinned OpenStax content
(CNXML/`media`) and the committed `exercises/` caches are **© OpenStax, CC BY 4.0, not the maintainer's**
— see `openstax/CLAUDE.md` and each cache's `COPYRIGHT`.
