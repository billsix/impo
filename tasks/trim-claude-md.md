# Trim impo's CLAUDE.md (openstax/ 11.9 KB + root 3.7 KB, loaded every session)

**Status:** Done — trimmed 2026-09-13 (pending archive after the work commit)
**Priority:** 5
**Difficulty:** 3

## Result (2026-09-13)
Applied at TARGET = MODERATE. Two sections moved out of `openstax/CLAUDE.md`:
- § "Books" per-book status inventory (build dates, exercise/image counts, os-embed post-mortems)
  → new `tasks/reference/openstax/book-inventory.md` (dir + `.keep` created); replaced with a lean
  16-book list (slug + one-line identity) + pointer.
- § "How this family differs" point 2 converter-history deep-dive ("5 versions merged", 2026-09-03
  narrative) → existing `tasks/reference/tooling/converters.md` (unique "maintenance smell / weren't
  identical" rationale appended; the rest already covered there); replaced with a 1-line invariant + pointer.

Invariant contracts (content model, licensing, per-book folder contract, adding-a-book) kept inline;
the toolchain map (open question 2) was left fully intact — not part of the MODERATE scope applied.

**Size — `openstax/CLAUDE.md`: 11,866 B → 9,643 B** (−2,223 B, ≈ 19%). Root CLAUDE.md unchanged.

## BLUF
Both CLAUDE.md files splice into the AI's context on every session/turn, so their bytes
are a per-turn tax. The root (3,706 B) is already near-lean; `openstax/CLAUDE.md`
(11,866 B) is the real target — its per-book status inventory and its converter-history
post-mortems are durable *detail* that belongs in `tasks/reference/`, not in a file read
every turn. Moving them should cut the openstax file to roughly 7.5–8 KB while leaving the
operational contract (content model, licensing, per-book contract, toolchain map,
adding-a-book) in place.

## Context
- **Why:** a repo's `CLAUDE.md` is inlined into the model's context every session/turn.
  Measured 2026-09-13: geometricalgebra's 74,732 B CLAUDE.md cost ~18,683 tok/turn (47% of
  Crush's system prompt). Method + numbers:
  runCrushInContainer `tasks/reference/crush-context-assembly.md`.
- **Sizes:** root `/foo/opt/impo/CLAUDE.md` 3,706 B ≈ 0.9K tok;
  `/foo/opt/impo/openstax/CLAUDE.md` 11,866 B ≈ 3.0K tok.
- **@-imports:** none. Neither file has a bare `@path` import, so nothing extra is pulled
  in transitively — the byte counts above are the whole cost.
- **Convention:** `CLAUDE.md` stays lean (what-this-is + brief layout, build/run + gate,
  invariant conventions, pointers) and loads every session; durable detail moves to
  `tasks/reference/<slug>.md`.
- **Existing `tasks/reference/` docs:**
  - `tasks/reference/tooling/converters.md` (9,342 B) — converter landscape, the 5 historical
    per-book converter versions merged into one, gap analysis. **Destination for the converter
    history now inline in openstax/CLAUDE.md § "How this family differs" point 2.**
  - `tasks/reference/tooling/cross-references.md` (5,239 B) — PDF cleveref / HTML xref.lua.
  - New doc proposed below: `tasks/reference/openstax/book-inventory.md` — destination for the
    per-book status/counts/post-mortems now in § "Books".

## Stay vs move — openstax/CLAUDE.md

| section (lines) | ~bytes | Verdict | Destination / note |
|---|---|---|---|
| Header + intro (1–7) | ~600 | STAY | what-this-is; already lean. |
| § How this family differs from N64 (9–29) | ~1,700 | TRIM | Keep points 1 & 3 (personal/never-upstreamed; "apply = overlay") as short invariants. **MOVE** point 2's converter-history deep-dive (the "corrected 2026-09-03 / 5 versions / merges them" narrative) → `tasks/reference/tooling/converters.md` (already exists); leave a one-line "converter is one shared feature-detecting superset — history in converters.md". Saves ~900 B. |
| § The content model — downloaded → commit; generated → ignore (31–48) | ~1,600 | STAY (light trim) | Invariant policy, operational. Trim parenthetical asides only. |
| § Copyright / licensing (50–63) | ~1,300 | STAY (light trim) | Must-know invariant; keep. Could tighten the mirror-of-imps aside. |
| § Per-book folder contract (65–83) | ~1,500 | STAY | Operational contract; keep. |
| § The shared toolchain (openstax/tooling/) (85–113) | ~2,400 | TRIM | Keep the file/dir map + "changing the toolchain" + the reference-docs pointer. Trim the deep per-file mechanics (e.g. exactly what `build_nav.py`/`osbook-web.js`/`xref.lua` do internally) to one clause each; that mechanism detail belongs in the tooling reference docs. Saves ~500–700 B. |
| § Adding a book (115–122) | ~700 | STAY | Operational how-to; keep. |
| § Books (124–159) | ~2,900 | MOVE (mostly) | **MOVE** the per-book status inventory — build-verified dates, exercise/image counts, os-embed scheme post-mortems ("wrongly read as 0 exercises until…"), 2026-09-0x history → **new** `tasks/reference/openstax/book-inventory.md`. Keep in CLAUDE.md only a lean bulleted list of the 16 book folders (slug + one-line identity) and a pointer to the inventory doc. Saves ~2,000–2,200 B. |

## Root CLAUDE.md
Already near-lean (3,706 B) and well-structured (what-it-is, structure, contracts, license).
No section is a candidate for a reference-doc move. Optional micro-trim only: the intro's
"Extracted from imps 2026-09-03 (with its history)…" history sentence could shorten by a
clause, but it is one line and carries useful provenance — recommend leaving the root as-is.

## Projected result
- openstax/CLAUDE.md: ~11,866 B → **~7.5–8.0 KB** (≈ 1.9–2.0K tok), a ~30–35% cut, with the
  full detail preserved (and better placed) in `tasks/reference/`.
- root CLAUDE.md: unchanged (~3.7 KB).
- New reference doc: `tasks/reference/openstax/book-inventory.md` (per-book status/counts/history);
  converter history folded into the existing `tasks/reference/tooling/converters.md`.

## Open questions
1. **Book inventory location** — put the moved per-book status at
   `tasks/reference/openstax/book-inventory.md` (matches the `tasks/reference/<project>/` scheme,
   where `tooling/` already lives)? Recommend yes.
2. **Depth of the toolchain-map trim** — trim the per-file mechanics to one clause each (my
   recommendation), or leave § "The shared toolchain" fully intact and take the savings only from
   § Books + the converter history? Recommend the trim.

## Related
- runCrushInContainer `tasks/reference/crush-context-assembly.md` — measurement + method for the
  per-turn context cost.
- `tasks/reference/tooling/converters.md`, `tasks/reference/tooling/cross-references.md` — existing
  destinations / siblings for moved detail.
