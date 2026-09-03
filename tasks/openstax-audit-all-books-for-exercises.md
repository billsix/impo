# Audit all OpenStax books for os-embed exercises needing the same fetch fix

**Status:** DONE (audit complete 2026-09-03; physics+biology remediation tracked in [[openstax-converter-unification-gaps]])
**Priority:** 2
**Difficulty:** 1

## BLUF

After finding that physics + biology silently dropped their practice exercises (the converter only knew the
`#exercise/<nickname>` os-embed scheme, not their `#ost/api/ex/<id>` scheme), double-check **every** book for
exercises that were being missed. **Result: only physics and biology were affected; both are fixed.** Every other
book either uses the already-handled `#exercise/` scheme (and already has its cache) or has genuinely **zero**
os-embed exercises. There is **no third scheme**. Nothing further to pull.

## Method (converter-independent — raw CNXML grep, so a converter bug can't hide the answer)

For each `osbooks-*/checkout/modules`: (1) count `class="os-embed"` links; (2) extract every os-embed URL and
reduce to its scheme prefix; (3) confirm every prefix is one of the two known schemes. Run 2026-09-03.

## Result — the definitive table

| Book | os-embed exercise links | scheme | cache status |
|------|------|------|------|
| algebra-1 | 932 | `#exercise/` | cached (932) ✓ |
| contemporary-mathematics | 3073 | `#exercise/` | cached (3073) ✓ |
| organic-chemistry | 1959 | `#exercise/` | cached (1959) ✓ |
| introduction-python-programming | 613 | `#exercise/` | cached (613) ✓ |
| writing-guide | 182 | `#exercise/` | cached (182) ✓ |
| **physics** | 1802 (→846 unique) | **`#ost/api/ex/`** | **FIXED 2026-09-03** — fetched 846, rebuilt, renders ✓ |
| **biology-bundle** | 2458 (→2337 unique) | **`#ost/api/ex/`** | **FIXED 2026-09-03** — fetched 2333 (4 missing), rebuild verifying |
| anatomy-physiology, astronomy, calculus-bundle, chemistry-bundle, college-algebra-bundle, microbiology, prealgebra-bundle, psychology, university-physics-bundle | **0** | none | genuinely no os-embed exercises ✓ |

**Non-exercise os-embed links:** physics also carries ~46 `class="os-embed"` links to `http://openstax.org/l/<id>`
— external interactive-simulation links, NOT practice exercises. The converter correctly renders these as links
(they fall through to the `\href`/`\url` path); they are not fetched. No action.

## Conclusion

- **Two os-embed schemes total**, both now handled: `#exercise/<nickname>` (query `nickname:`) and
  `#ost/api/ex/<id>` (query `tag:`). No third scheme exists in any book.
- **Only physics + biology** needed the fix; remediation (converter fix, re-fetch, rebuild, cache commit) is done
  for physics and finishing for biology, tracked in [[openstax-converter-unification-gaps]].
- The 9 zero-exercise books are genuine zeros (raw-grep confirmed in both schemes), not converter artifacts — so
  the earlier "0 exercises" readings for them, unlike physics/biology, were correct.

## Archive note

This is a completed audit with a durable finding; its result is folded into
`tasks/reference/tooling/converters.md` (the per-book scheme/exercise table). Archive to
`tasks/archive/impo/2026/09/03/` once biology's rebuild verifies (the last open remediation step).
