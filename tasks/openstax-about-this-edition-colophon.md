# OpenStax books — "About This Edition" colophon (impo link + build SHA + prepared by Bill Six)

**Status:** IMPLEMENTED 2026-09-19 (all 6 decisions taken + built/verified at the master level). The
OpenStax colophon ships via the shared `convert.py` + a provenance env in all 16 book Makefiles; the
trench PDF mirror ships via `normalize_master.py`. Remaining: a full-render spot-check (PDF/HTML/EPUB) by
the maintainer, and the trench *web* editions' colophon (a small follow-on) — see "Remaining". Not
archived per the standing "don't archive" instruction.
**Priority:** 5
**Difficulty:** 4

## BLUF

Add an **"About This Edition"** colophon to every OpenStax book's **front matter**, stating the edition was
**prepared by Bill Six** using the **impo** toolchain (https://github.com/billsix/impo), **built from impo
commit `<SHA>`**, on top of OpenStax's CC BY content. **The maintainer is fine with either mechanism**
(2026-09-19): patch each book's CNXML before conversion, or modify the generated LaTeX afterwards — both
land the same result since impo owns the whole pipeline. **Recommended (cleanest): emit the colophon at
generation time in `convert.py`**, into the generated LaTeX master's front matter, because all three
editions (PDF/HTML/EPUB) derive from that **same** master — so a colophon emitted there as **plain LaTeX**
(a heading + an `\href`, so pandoc renders it too) appears in **all three** with no per-format work and no
per-book CNXML patch series to maintain. "Done" = a
book's PDF, HTML, and EPUB all show the colophon with a real, current impo commit SHA + the impo link +
the Bill Six credit, content still credited to OpenStax (CC BY).

## Decisions (2026-09-19) + what shipped

The maintainer answered the open questions: **(1)** title "About This Edition"; **(2)** the recommended
mechanism (generation-time in `convert.py`); **(3)** verb "**Formatted by**" (consistent with the
subtitle); **(4)** include the build date; **(5)** no per-book customization; **(6)** mirror to the trench
family too.

**Implemented + verified at the master level (2026-09-19):**
- **`convert.py`** — new `about_this_edition(title_tex)` emits a `\chapter*{About This Edition}` +
  `\addcontentsline` front-matter colophon as the first front unit, reading `IMPO_COMMIT` / `IMPO_BUILD_DATE`
  from the env (falls back to "(a local development build)"). Uses `\chapter*` deliberately — `\OSfrontmatter`
  ends with `\mainmatter`, so a plain `\chapter` would step the counter and turn "Chapter 1" into "Chapter 2".
  Verified: `make convert` on anatomy-physiology emits the colophon with the real impo HEAD SHA + date +
  interpolated title, and "Levels of Organization" stays a numbered `\chapter` (Chapter 1). ty+pytest gate
  green.
- **All 16 book Makefiles** got an `IMPO_PROVENANCE` block (`IMPO_COMMIT ?= $(shell git rev-parse HEAD)` +
  date, threaded into `RUN`) via the idempotent codemod `tasks/adhoc/openstax-colophon/add_provenance_env.py`
  (15 changed + anatomy done by hand; second run = 0 changed).
- **trench PDF** — `normalize_master.py` gained the same colophon (tailored to Trench's CC BY-NC-SA 3.0
  content), inserted after `\OSfrontmatter`; its `make normalize` target passes `IMPO_COMMIT`/`IMPO_BUILD_DATE`
  (the script also git-falls-back since normalize runs on the host). Verified in the generated master.

## Also done — trench WEB + EPUB colophon (2026-09-19)

The trench HTML/EPUB take the separate `web_preprocess.py` path (not the osbook master), so they got the
colophon there: `web_preprocess.py` prepends a `\chapter*{About This Edition}` (env SHA via the trench
Makefile's new `IMPO_PROVENANCE`) to `bookW.tex`, which flows to BOTH the make4ht HTML and the tex4ebook
EPUB. **Verified (`make html`/`make epub`):** the HTML gets a clean "About This Edition" page
(`002-about-this-edition.html`, in the left nav between Preface and Introduction, with the impo link +
real SHA); "Introduction" stays Chapter 1 (the `\chapter*` doesn't step the counter); the EPUB carries it
too (`OEBPS/bookWli1.xhtml`, impo link present).

## Propagation gotcha + fix (2026-09-19)

The maintainer reported the colophon missing from the college-algebra PDF. **Cause:** a book builds from
its `checkout/tools/convert.py` — a COPY `apply.sh` overlays — not from `openstax/tooling/` directly. That
checkout's converter was stale (its subtitle still read "LaTeX edition"), because `apply.sh` had not been
re-run there since the toolchain change. Worse, `apply.sh` overlaid the new converter but left the
`checkout/latex/.converted` stamp, so `make pdf` could skip regenerating and keep serving the OLD master.
**Fix (applied, all 16 books):** `apply.sh` now ends with `rm -f "$CHECKOUT/latex/.converted"`, so a
re-apply always invalidates the generated LaTeX and the next build reconverts with the fresh converter
(codemod `tasks/adhoc/openstax-colophon/invalidate_converted_on_apply.py`, idempotent). **To get the
colophon into an existing book now:** `./apply.sh && make dist` (or `make pdf`). Verified end-to-end on
college-algebra: after `./apply.sh` (stamp dropped) + `make convert`, `college-algebra-2e.tex` carries the
colophon.

## Remaining
- **OpenStax full-render spot-check** — the maintainer said he'll test the PDF himself (2026-09-19), after
  `./apply.sh && make pdf` (per the propagation fix above). The HTML/EPUB inherit the colophon from the
  shared master; the generated masters are verified.

## Context (cold-start — read these first)

- **Mechanism latitude (maintainer, 2026-09-19).** He's fine with EITHER a CNXML patch (edit each book's
  Preface/front matter before conversion) OR editing the generated LaTeX after conversion. impo owns the
  whole pipeline (CNXML→LaTeX `convert.py` + the pandoc HTML/EPUB legs), so unlike imps/mario64 — which
  must patch the upstream source it COMPILES — impo can just change what it generates. **Recommended:**
  emit it in `convert.py` (one place, per-book output by title interpolation, reaches all three editions
  via the shared master, no per-book patch series). A CNXML-patch approach would instead be per-book and
  need a patch mechanism impo's OpenStax family doesn't currently use — workable, but more moving parts.
- **Each book has its own Preface (verified).** Every book ships a Preface *module* in its CNXML — e.g.
  anatomy-physiology `modules/m46844` , astronomy `m63293`, biology `m46159`, all
  `<md:title>Preface</md:title>`. `convert.py` has **no** special Preface handling today (grep: none); it
  converts the Preface module generically like any other. So a per-book Preface exists to attach to (open
  question 2 = attach to it vs a standalone colophon page).
- **One master → all three editions.** `openstax/tooling/entrypoint/html.sh` + `epub.sh` run pandoc over
  the generated `latex/*.tex` master (see `openstax/CLAUDE.md`). So front-matter *content* in the master
  reaches PDF (LaTeX), HTML, and EPUB — **provided it's pandoc-renderable**: emit plain
  `\section*{About This Edition} … \href{https://github.com/billsix/impo}{…} …`, NOT an `osbook.cls` macro
  (pandoc can't expand `\OSfrontmatter`). This is why it is content, not house style.
- **The credit already partly exists.** `convert.py:2918` emits `\setOSbooksubtitle{Formatted by Bill Six}`
  into every master. The colophon is the fuller provenance version of that one-line credit (adds the impo
  link + the build SHA + the licensing note). Keep the wording consistent (open question 3).
- **No build SHA is captured today.** No `git rev-parse`/`git describe` anywhere in
  `openstax/tooling/entrypoint/`; `\setOSbookversion` exists but is never given a value. The SHA to capture
  is the **impo repo's HEAD** (the toolchain commit that prepared the edition) — not the OpenStax content
  checkout's pin (that's OpenStax's, gitignored at `/book`). Precedent for capturing a build commit:
  github.com/billsix/modelviewprojection `entrypoint/entrypoint.sh` writes `version.txt` via
  `git rev-parse HEAD`.
- **Licensing split — keep it correct.** Content is © OpenStax, CC BY 4.0 (not Bill's); the toolchain +
  formatting are Bill's (MIT). The colophon states both and adds "not endorsed by / affiliated with
  OpenStax." (See `openstax/CLAUDE.md` "Copyright / licensing".)

## Plan

1. **Pick the title + wording** (open questions 1, 3). Working title "About This Edition".
2. **Emit the colophon from `convert.py`** as plain, pandoc-renderable LaTeX in the generated master's
   front matter (near the existing `\setOSbooksubtitle`, `convert.py:2917-2920`). Draft:
   > **About This Edition.** This edition of *\<book title\>* was prepared by William Emerison Six ("Bill
   > Six") from OpenStax's open content using the *impo* toolchain
   > (`\href{https://github.com/billsix/impo}{github.com/billsix/impo}`), built from commit `\texttt{<SHA>}`
   > on `<date>`. The text and figures are © OpenStax, licensed CC BY 4.0
   > (`\href{https://creativecommons.org/licenses/by/4.0/}{CC BY 4.0}`); the LaTeX house style and toolchain
   > are © Bill Six, MIT-licensed. Not endorsed by or affiliated with OpenStax.
   `convert.py` already knows the book title, so the text is per-book by interpolation while the code lives
   in the one generator. Default the SHA to "(development build)" so a book still builds without it.
3. **Capture the impo build SHA (the only real work).** The per-book `Makefile` (which lives in the impo
   repo) captures `IMPO_COMMIT := $(shell git rev-parse HEAD)` (+ a date) and passes it into the
   `convert` container run as `-e IMPO_COMMIT=… -e IMPO_BUILD_DATE=…`; the entrypoint forwards it to
   `convert.py`, which substitutes it into the colophon. (Alternative: bind-mount the impo repo and
   `rev-parse` inside — heavier; not recommended.)
4. **Verify all three editions** (one book, e.g. anatomy-physiology): `make pdf` shows the colophon page;
   `make html` and `make epub` show it too (proving the plain-LaTeX form survived pandoc, with a working
   impo hyperlink). Confirm the SHA is the real current impo HEAD.
5. **All books inherit it** — because it's emitted by the shared generator from each book's own content,
   every book gets a per-book colophon on its next `make convert`/`pdf`/`html`/`epub`. No per-book edits.

## Open questions

1. **Title/phrasing** — "About This Edition" (recommended) vs "About This Version" / "Colophon".
2. **Placement** — a **standalone front-matter colophon** (its own page/section, e.g. right after the
   license page) OR **appended to each book's Preface** (since every book has one)? Recommend a standalone
   front-matter section (cleaner, uniform position, doesn't depend on a book actually having a Preface
   module). If you'd rather it read as part of the Preface, `convert.py` can detect the Preface module and
   append it there instead.
3. **Verb consistency** — subtitle already says "Formatted by Bill Six"; colophon says "prepared by".
   Keep both (recommended) or unify?
4. **Include a build date** with the SHA? Recommend yes.
5. **Per-book customization?** The generator produces the same colophon (title interpolated) for all
   books. If a book should say something different, a book could ship a committed `colophon.tex` override
   that `apply.sh` overlays and `convert.py` includes — more setup, only if wanted.
6. **Trench family too?** The sibling `trench/` books use the same generated-master idea (via
   `normalize_master.py`, which already puts a lighter "formatted by Bill Six" note on the license page).
   Mirror the colophon there in a small follow-on. Recommend: OpenStax first, then trench.

## Related

- `openstax/tooling/tools/cnxml2tex/convert.py` (`:2917-2920`, front-matter/preamble emission — where the
  colophon is added).
- `openstax/tooling/entrypoint/` (where the `IMPO_COMMIT` env would be forwarded to `convert.py`).
- `openstax/CLAUDE.md` — the generate-don't-patch model + the licensing split.
- Precedent: github.com/billsix/modelviewprojection `entrypoint/entrypoint.sh` (`git rev-parse HEAD` →
  `version.txt`).
