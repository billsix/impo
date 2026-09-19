# Decision needed: Trench book — chapter 2's sections start at §2.2 (a shared PDF/web quirk)

**Status:** needs maintainer decision (a cold-start question for William Emerison Six
<billsix@gmail.com> to answer later; raised 2026-09-19 while he was away). No code change until he picks
an option below.
**Priority:** 6
**Difficulty:** 2 (the fix itself is a one-line regex in two files + a PDF rebuild; the decision is yours)

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
- **Why I didn't just fix it while you were away.** The obvious fix (also strip `\setcounter{section}{N}`)
  is correct and low-risk, but it changes the **PDF** numbering too, and I didn't want to silently alter
  the PDF edition (a different task's output — `tasks/add-trench-differential-equations-book.md`) or leave
  the two editions numbered differently. So: your call.

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

## What I need from you

**Pick A, B, or C.** If (A), I'll add the one-line strip to both tools, rebuild all three editions, verify
Chapter 2 reads §2.1…§2.7, and stage. If (B), I'll close this task with a note in the book `CLAUDE.md`
recording the quirk as intentional.

## Related

- `tasks/trench-differential-equations-html-epub.md` — the web-edition task (records this quirk under
  "Known residual quirk" in the "DONE — Furo restyle" section).
- `tasks/add-trench-differential-equations-book.md` — the PDF task (the other edition the fix would touch).
- Files a fix would edit: `trench/elementary-differential-equations/tools/{normalize_master.py,web_preprocess.py}`.
