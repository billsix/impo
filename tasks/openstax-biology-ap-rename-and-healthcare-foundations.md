# Follow up two upstream changes: Biology for AP Courses renamed, Healthcare Foundations added

**Status:** ready — decisions recorded 2026-11-26; step 1 done
**Priority:** 5
**Difficulty:** 2
**Created:** 2026-11-26 (agent, from the pin sync recorded in `tasks/archive/impo/2026/11/26/openstax-sync-upstream-pins-2026-11.md`; a sync item that does not resolve gets a task: `CLAUDE.md`, "Contracts").

## BLUF

The 2026-11-26 pin sync built every book, and two upstream changes came with it that impo's outputs and docs do not account for yet: one book changed its name and one new book appeared. Done means the stale old-named outputs are gone, the published site and release assets carry the names the maintainer wants, and the docs list the books each bundle now produces.

## Context

**Read first:** `tasks/archive/impo/2026/11/26/openstax-sync-upstream-pins-2026-11.md` ("What upstream changed that matters"), `tools/build-books.sh` (its `collect` function copies every `checkout/output/<book>/` that has an `index.html`), and `tasks/reference/openstax/publishing.md`.

- **Renamed.** In `osbooks-biology-bundle` the collection `biology-ap-courses` is now `biology-ap-courses-2e`. The book builds under the new name. Because the checkout was updated in place, the October outputs under the old name were left behind (`checkout/latex/biology-ap-courses.tex`, `checkout/output/biology-ap-courses/`, `checkout/output/biology-ap-courses.epub`), where `collect` would have copied the stale site into the root `output/`. They were deleted on 2026-11-26 with the maintainer's approval. The published address changes too: `billsix.github.io/impo/biology-ap-courses/` becomes `…/biology-ap-courses-2e/`. The committed exercise cache is keyed by exercise nickname and still carries `book-slug:biology-ap-courses` tags; the new EPUB is larger than the old one (290 MB against 264 MB), so no content loss shows, but exercise injection was not compared exercise by exercise.
- **Added.** `osbooks-prealgebra-bundle` now has a fourth collection, `healthcare-foundations` (30 modules). It built in all three formats with no change to impo, so `make prealgebra-bundle`, the release workflow and `make publish-pages` will now produce and publish a fourth book from that folder.

## Plan

1. Done 2026-11-26: the three stale old-named outputs were removed from the biology checkout.
2. Check AP Biology's exercises at the new name: count injected exercises in the new build against the cache.
3. Healthcare Foundations stays in the build; the old AP Biology address is left to disappear (see Decisions). Nothing to implement beyond the docs in step 4.
4. Update the docs that list each bundle's books: `openstax/CLAUDE.md` (the book list), `openstax/osbooks-biology-bundle/CLAUDE.md`, `openstax/osbooks-prealgebra-bundle/CLAUDE.md`, `tasks/reference/openstax/book-inventory.md`.

## Decisions (William Emerison Six <billsix@gmail.com>, 2026-11-26)

- **Healthcare Foundations is kept**: built and published with the other three books of the prealgebra bundle.
- **The old AP Biology address is left to disappear** at the next `make publish-pages`; no redirect page (the agent's recommendation, accepted with "whatever you recommend").
- **The stale October outputs may be deleted** ("sure"); done the same day.

## Open questions

None.
