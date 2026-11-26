# Add `osbooks-introduction-business` to impo (one book)

**Status:** ready — approved 2026-11-26 as part of the umbrella; not started
**Part of:** `tasks/openstax-add-remaining-english-books.md`
**Depends on:** `tasks/archive/impo/2026/11/26/openstax-add-book-step-0-scaffold-tool.md` (the scaffold tool, so every new folder is made the same way)
**Priority:** 6
**Difficulty:** 3
**Created:** 2026-11-26 (William Emerison Six <billsix@gmail.com>: "I want to add all of the ones you said … make a task per book"; he then chose all 29 real repositories, one task per repository).

## BLUF

impo does not yet build OpenStax's `osbooks-introduction-business`. This task adds it as a book folder on the shared-toolchain contract, so that `introduction-business-2e` builds as PDF, EPUB and HTML like the books impo already carries. Done means the folder exists, every book in it converts and builds in all three formats, its exercises (if it embeds any) are cached, and impo's docs and the survey list it as built.

## Context

**Read first:** the umbrella (`tasks/openstax-add-remaining-english-books.md`) for the method every one of these tasks follows, and `openstax/CLAUDE.md` ("Per-book folder contract", "Copyright / licensing").

| | |
|---|---|
| Upstream | `https://github.com/openstax/osbooks-introduction-business` |
| Group | Economics, business and law |
| Books (collection slugs) | `introduction-business-2e` |
| Language | English |
| Licence its `LICENSE` file names | CC BY 4.0 |
| Size (GitHub, with history) | 225 MB |
| Last push upstream | 2026-05-20 |
| Default-branch head on 2026-11-26 | `2a839877ab89a207c9b9e501df438173013fa45c` (re-read it when the work starts; the pin is the head at that time) |
| Maintainer's public backup | none yet (`tasks/openstax-books-buildable-forever-source-backup-and-licences.md`) |

Mostly prose and figures, as far as the repository name suggests; not opened yet.

**Not known until the source is fetched:** whether it embeds exercises and in which of the two schemes, whether its figures are raster or SVG, how deeply its collections nest, and whether it uses markup the converter has not met (the converter reports those as "Unknown/fallback elements").

## Plan

- [ ] `bash tools/add-book.sh introduction-business` to create `openstax/osbooks-introduction-business/` with `fetch.sh` (upstream, mirror fallback, the pin), `apply.sh`, `Makefile`, `README.md`, `CLAUDE.md` and `.gitignore`.
- [ ] `./fetch.sh && ./apply.sh`, then `make convert`. Read the converter's report; a licence it does not know stops the conversion, which is intended.
- [ ] If it embeds exercises: the maintainer runs `make fetch-exercises` in the folder (the fetch identifies itself with his contact address, so it is his to run), then the cache is committed with its `COPYRIGHT` notice.
- [ ] `make dist`; open the PDF and one HTML page of each book and note anything that rendered badly.
- [ ] Converter gaps: fix in `openstax/tooling/` what is small and general; anything larger gets its own task, named here.
- [ ] Record the book: `openstax/osbooks-introduction-business/CLAUDE.md` (collections, module counts, nesting, exercises, figure format), the list in `openstax/CLAUDE.md`, and `tasks/reference/openstax/book-inventory.md` including its licence row.
- [ ] `python3 tools/survey-upstream-books.py` and refresh `tasks/reference/openstax/upstream-book-repositories.md`; tick this book in the umbrella.
- [ ] Tell the maintainer the book needs its public backup (`tools/mirror-upstreams.sh push introduction-business`).

## Open questions

None.
