# Retitle the book subtitle "LaTeX edition" → an attribution/credit

**Status:** DONE 2026-09-19 — implemented & verified; archive owed after the work commit
**Priority:** 4
**Difficulty:** 1
Created 2026-09-18 (William Emerison Six <billsix@gmail.com>).

> **Decision (William Emerison Six <billsix@gmail.com>, 2026-09-18):** subtitle becomes
> **`Formatted by Bill Six`** — the maintainer deliberately chose the short form "Bill Six" for the
> book cover (it reads better on a math book than the full name). This is a cover-credit style choice,
> distinct from the doc-stamp convention (which still uses the full `William Emerison Six <email>`).
> Open question 1 resolved. Questions 2–3 keep their defaults (use the subtitle slot; leave the
> colophon licensing line) unless the maintainer says otherwise.

## BLUF

Every generated OpenStax book carries the title-page **subtitle "LaTeX edition"**; the maintainer
wants it to read as a personal credit instead (his phrasing: "formatted by Bill Six"). The whole
label is emitted from **one string** in the shared converter, so the change is a one-line edit that
updates all 16 books; the only real decision is the exact wording (open question 1). "Done" = the
chosen subtitle renders on a freshly built book's title page and nothing else regressed.

## Context (cold-start)

`openstax/tooling/` is the maintainer's **native, MIT-licensed** toolchain (CNXML→LaTeX converter +
house LaTeX class) — **not** a patch on OpenStax content — so these are plain file edits, no patch
regeneration, and they apply to every book because the tooling is book-agnostic
(`CLAUDE.md`, "Structure"; `openstax/CLAUDE.md` has the build contract).

The subtitle is set here, then rendered by the class:
- **`openstax/tooling/tools/cnxml2tex/convert.py:2918`** — the volume-master template emits
  `\setOSbooksubtitle{LaTeX edition}` into every book's master `.tex`. **This is the single source of
  the label** — change the string here and all books change.
- **`openstax/tooling/latex/osbook.cls`** — defines `\setOSbooksubtitle` (`:213`) and renders
  `\OSbooksubtitle` in **two** spots on the front matter (`:225–226` and `:234–235`, bold italic —
  the half-title and the title page). No change needed here for a plain retitle; both spots pick up
  the new value automatically.

**Separate, and NOT part of this task** (flagged so they aren't confused with the subtitle):
- `osbook.cls:253` — the colophon sentence *"This LaTeX edition is likewise distributed under
  CC BY-NC-SA 4.0."* This is a **licensing** statement about the rendered artifact; it reads fine
  regardless of the subtitle, so leave it unless open question 3 says otherwise.
- `osbook.cls:256` — *"Typeset in Latin Modern and Computer Modern Sans with \LaTeX."* — the
  typesetting colophon; already carries the "LaTeX" signal, so the subtitle is free to become a credit.

## The change

Edit the one string at `convert.py:2918`:
```python
"\\setOSbooksubtitle{LaTeX edition}\n"
```
→
```python
"\\setOSbooksubtitle{Formatted by Bill Six}\n"
```
(chosen wording, 2026-09-18). No LaTeX-special characters to escape.

## Wording recommendation (open question 1)

The subtitle currently *describes the artifact* ("this is the LaTeX rendering"). Replacing it with a
credit is fine because the "LaTeX" signal already lives in the colophon (`:256`). Two notes on the
maintainer's suggested "formatted by Bill Six":
1. **Name form** — the doc-stamp convention (full canonical name, no bare first name) governs *dated
   decision stamps*, not a book's cover credit. For the cover the maintainer chose the short form
   **"Bill Six"** deliberately (reads better on a math book); that stands.
2. **Verb** — **"Typeset"** is the precise term for LaTeX book production and already appears in the
   colophon ("Typeset … with \LaTeX"); "Formatted" is plainer but less apt for a typeset book.

Options (all render in the subtitle's bold-italic slot):
- **(A)** `Typeset by William Emerison Six` — pure credit, drops the format label.
- **(B, recommended)** `LaTeX edition · typeset by William Emerison Six` — keeps the format signal
  AND adds the credit.
- **(C)** `Formatted by William Emerison Six` — the maintainer's wording, with the full name.

## Verify

Rebuild one book's PDF (the shared toolchain builds identically for all) and eyeball the title page +
half-title for the new subtitle. Per-book build target (podman + TeXLive): `openstax/CLAUDE.md` /
each `osbooks-<subject>/Makefile`.

**Result (2026-09-19):** built `osbooks-physics` (`./apply.sh` to re-overlay the edited tooling into
its checkout, then `make pdf` — one-time TeXLive image build + convert + LuaLaTeX). `physics.pdf`
title page and half-title both render **"Formatted by Bill Six"** under the title; colophon
licensing line unchanged. The single `convert.py` source edit is the whole change — the other 15
books' gitignored checkouts render the new subtitle at their next build (no per-book action needed;
only `physics`'s checkout was re-overlaid for this verification).

## Open questions

1. ~~**Which wording?**~~ **RESOLVED 2026-09-18:** `Formatted by Bill Six` (maintainer's short-form
   cover credit — chosen over the full name because it reads better on a math book).
2. **Subtitle slot, or a dedicated credit line?** Putting a "typeset by …" credit in the *subtitle*
   (large bold italic) reads slightly unusually — subtitles normally describe the work. Fine as-is if
   you want it prominent; alternatively I could keep a short descriptive subtitle and add the credit
   as a smaller line on the title page (a small `osbook.cls` change). Your call — default is the
   subtitle slot per your request.
3. **Touch the colophon too?** Leave `osbook.cls:253` ("This LaTeX edition …") as the licensing line
   (recommended), or harmonize its phrasing with the new subtitle. Default: leave it.

## Aside (noticed, out of scope — not acting on it)

The colophon at `osbook.cls:253` states the LaTeX edition is **CC BY-NC-SA 4.0**, but
`CLAUDE.md`/`openstax/CLAUDE.md` describe OpenStax content as **CC BY 4.0** (and the toolchain as
MIT). The `NC`/`SA` may be inaccurate. Not part of this subtitle task — parked here so it isn't lost.
