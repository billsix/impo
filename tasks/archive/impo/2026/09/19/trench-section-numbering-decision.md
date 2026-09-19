# Trench book — chapter 2's sections started at §2.2 (FIXED 2026-09-19)

**Status:** RESOLVED 2026-09-19 — the maintainer chose to **fix it** ("fix the numbering in a patch if
needed, or just in code"). Fixed **in code** (no patch needed — impo owns the transforms): both
`normalize_master.py` (PDF) and `web_preprocess.py` (web/EPUB) now strip `\setcounter{section}{N}` as
well as `\setcounter{chapter}{N}`, so sections auto-number consecutively from .1. Verified: all 10
chapters number correctly (chapter 2 now 2.1–2.6, chapter 1 unaffected 1.1–1.3). Not archived per the
standing instruction.
**Priority:** 6
**Difficulty:** 2

## Resolution (2026-09-19)

`\newsection{num}{chap}{title}`'s first arg IS the correct section number, but both transforms
auto-number (the shim `\newcommand{\newsection}[3]{\section{#3}}` ignores arg1; web_preprocess rewrites
to `\section{#3}`). Chapter 2's source stamps `\setcounter{section}{1}` *before* its first section
(line 2225 → 2230), bumping it to 2.2; chapter 1's sits *after* its first section (harmless). Stripping
the section setters makes auto-numbering line up with arg1: verified on `make html` — every chapter's
sections run consecutively from `.1` (1.1–1.3, **2.1–2.6**, 3.1–3.3, … 10.1–10.7). The EPUB shares
`bookW.tex` so it's fixed too; the PDF master was regenerated (`make normalize`) and auto-numbers the
same way via the shim. Edited: `tools/{normalize_master.py,web_preprocess.py}` (one regex each,
`chapter` → `(?:chapter|section)`).

---

_Original decision doc (kept for the record):_

## BLUF

In the Trench *Elementary Differential Equations* editions, **Chapter 2 ("First Order Equations") numbers
its sections 2.2, 2.3, … — there is no §2.1** (the first section, "Linear First Order Equations", shows
as 2.2). Every other chapter is fine (sections start at .1). This is a **pre-existing quirk in BOTH the
PDF and the web editions** — not introduced by the recent HTML/EPUB restyle. It comes from a vestigial
`\setcounter{section}{1}` in Trench's source that both build paths currently keep. **Decide whether to
fix it** (make Chapter 2 start at §2.1, matching the other chapters and Trench's actual published book) or
**leave it** (stay byte-faithful to the source's own numbering). Pick an option at the bottom.

## Context (cold-start)

- **Where the numbers come from.** Trench's source stamps manual counter setters before chapters/sections
  (`\setcounter{chapter}{N}`, `\setcounter{section}{N}`) — an artifact of its original hand-numbered
  `\newsection` system. The impo build paths discard the hand-typed section numbers (rewriting
  `\newsection{a}{b}{c}` → `\section{c}`) and let LaTeX auto-number, but they still honor the leftover
  `\setcounter` lines.
- **What each path strips today:**
  - PDF path — `trench/elementary-differential-equations/tools/normalize_master.py` strips
    `\setcounter{chapter}{N}` (so chapters number 1–10) but **keeps** `\setcounter{section}{N}`.
  - Web path — `tools/web_preprocess.py` was updated 2026-09-19 to mirror that (strips chapter setters,
    keeps section setters) **specifically so the web section numbers match the PDF**.
- **The quirk.** Only chapters 1 and 2 carry a `\setcounter{section}{1}` in the source. For chapter 1
  ("Introduction") it happens to be harmless (sections come out 1.1, 1.2, 1.3). For chapter 2 it bumps the
  first section to §2.2 — so §2.1 is missing. All other chapters (no section setter) are correct.
- **Why it was raised as a decision rather than fixed pre-emptively.** The obvious fix (also strip
  `\setcounter{section}{N}`) is correct and low-risk, but it changes the **PDF** numbering too, so it was
  surfaced rather than silently altering the PDF edition (a different task's output —
  `tasks/archive/impo/2026/09/19/add-trench-differential-equations-book.md`) or leaving the two editions numbered differently.

## The options

- **(A) Fix it in BOTH editions (recommended).** Add a `\setcounter{section}{\d+}` full-line strip to
  BOTH `tools/normalize_master.py` (PDF) and `tools/web_preprocess.py` (web), mirroring the existing
  chapter-setter strip. Then every chapter auto-numbers its sections from .1 (Chapter 2 → §2.1) — matching
  Trench's actual published book. Rebuild the PDF (`make pdf`) and the web editions (`make html`/`make
  epub`) and eyeball Chapter 2. Editions stay consistent. Risk: negligible — only chapters 1 & 2 have the
  setter, and chapter 1 already numbers correctly, so stripping it is a no-op there and a fix for chapter 2.
- **(B) Leave it.** Accept §2.2 as the first section of Chapter 2, staying faithful to the source's own
  counter directives. No code change. The editions already match each other.
- **(C) Fix web only.** Not recommended — it would make the web section numbers diverge from the PDF.

## Decision taken (2026-09-19)

**(A)** — fixed in both editions, in code. See the "Resolution" section at the top of this doc.

## Related

- `tasks/archive/impo/2026/09/19/trench-differential-equations-html-epub.md` — the web-edition task (records this quirk under
  "Known residual quirk" in the "DONE — Furo restyle" section).
- `tasks/archive/impo/2026/09/19/add-trench-differential-equations-book.md` — the PDF task (the other edition the fix would touch).
- Files a fix would edit: `trench/elementary-differential-equations/tools/{normalize_master.py,web_preprocess.py}`.
