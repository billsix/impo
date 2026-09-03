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

## Structure — one family, `openstax/`

impo currently carries a single family, so the layout is `openstax/<the family>`:

- **`openstax/CLAUDE.md`** — **the family contract; read it first.** How the shared toolchain works, the
  per-book folder contract (fetch → apply-overlay → build), the *downloaded → commit / generated →
  ignore* content model, and the **licensing split** (toolchain is the maintainer's MIT; OpenStax
  content is CC BY, not the maintainer's).
- **`openstax/tooling/`** — the shared, book-agnostic toolchain (CNXML→LaTeX converter, exercise
  fetcher, house LaTeX class/styles, pandoc web templates, tests, Fedora+TeXLive Dockerfile), maintained
  once. Each book mounts at the fixed path `/book` so nothing hardcodes a slug.
- **`openstax/osbooks-<subject>/`** — one thin folder per book: `fetch.sh` (pins pristine OpenStax
  content into a gitignored `checkout/`), `apply.sh` (overlays `../tooling/`), a thin `Makefile`,
  `CLAUDE.md`, `README.md`, and — for books with `os-embed` exercises — a committed `exercises/`
  download cache **with its `COPYRIGHT` NOTICE**.

(If a second, non-OpenStax book family is ever added, it becomes a sibling family folder and this
master doc grows a family index — mirroring how imps carries `n64/`.)

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
- **ROM/asset acquisition is out of scope** — a book's content comes from its pinned OpenStax upstream
  via `fetch.sh`; never commit the upstream `checkout/`.

## License

MIT (`LICENSE`) for impo's original content — the toolchain, scripts, docs. The pinned OpenStax content
(CNXML/`media`) and the committed `exercises/` caches are **© OpenStax, CC BY 4.0, not the maintainer's**
— see `openstax/CLAUDE.md` and each cache's `COPYRIGHT`.
