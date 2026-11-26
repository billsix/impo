# Keep every book buildable forever: back up the source, close the last outside dependencies, state the licences correctly

**Status:** proposed — needs go-ahead (three questions, at the end)
**Priority:** 3
**Difficulty:** 5 (the licence corrections are small and exact; the backup has parts only the maintainer can do)
**Created:** 2026-11-26 (William Emerison Six <billsix@gmail.com>: "Given what we saw with the algebra git repo being gone from upstream, I want to reconsider any historical decision we made about fetching resources … In general I want these books buildable, at any point in the future, and I want advice … I want to make sure all copyright and licenses are clearly marked". Then: "take all of this information, and write in all as a task, all of it").

## BLUF

The maintainer wants every book in impo to be buildable at any point in the future, whether or not OpenStax's repositories or its exercise server still exist, with copyright and licences marked clearly. Today a book's exercises are committed, but its XML and figures are fetched from upstream at build time, and one upstream has already disappeared. This task records what was found, decides how the source is backed up, closes the remaining outside dependency (the build image), and corrects impo's licence statements, which are wrong for fifteen of sixteen book folders. Done means: every book's pinned source can be fetched from a place the maintainer controls, a book can be built with no access to OpenStax, and every licence statement in impo matches what the source itself declares.

## Context

**Read first:** `openstax/CLAUDE.md` ("The content model" and "Copyright / licensing"), `CLAUDE.md` ("Contracts": the sync and the every-pin-fetchable rules), `tasks/openstax-algebra-1-upstream-gone-backup-plan.md` (the upstream that vanished; the mirror decision) and `tasks/openstax-refresh-pi-mirrors-after-2026-11-sync.md` (the maintainer's at-home mirror refresh). Everything below was measured or read on 2026-11-26 unless it says otherwise.

### The three questions the maintainer asked, and the answers

1. **Does `make fetch-exercises` download the exercises that are committed so the book builds without the network?** Yes. `openstax/tooling/tools/cnxml2tex/fetch_exercises.py` is the one networked step; the build (convert, PDF, HTML, EPUB) reads only the committed `exercises/` cache. Limit: OpenStax's Exercises API returns questions only and withholds answer keys.
2. **If the XML source were fetched and committed too, could a book be built entirely in impo's pipeline with upstream and the exercise server gone?** Yes. No other network dependency was found in the build: the web templates under `openstax/tooling/templates/` load nothing from a CDN (the only URLs in the templates and entrypoint scripts are links to openstax.org, creativecommons.org and the published site). The one remaining outside dependency is the build image, which installs Fedora and TeX Live packages when it is built.
3. **Could there be a `make fetch-xml-source`, like `make fetch-exercises`?** It already exists: each book's `fetch.sh` downloads the pinned source (`collections/`, `modules/`, `media/`) into `checkout/`. The only difference from the exercises is that `checkout/` is git-ignored. The decision is whether to keep what it downloads, not whether it can be fetched.

### The historical decision being reconsidered

`openstax/CLAUDE.md` states the content model as "downloaded → commit; generated → ignore", with one exception: the pinned upstream source is "gitignored … never committed — it's OpenStax's, and it regenerates from the pin". The exercises were committed for the opposite reason, stated in the same file: "a build never touches the network and a book always has all of its content (offline-reproducible, even if OpenStax's servers are down)" (decided 2026-09-02, `tasks/archive/impo/2026/09/03/openstax-populate-books.md`).

"It regenerates from the pin" failed on 2026-11-26: `github.com/openstax/osbooks-algebra-1` returns 404. The book's content survives only as plain files in its `checkout/` folder.

### What a checkout actually holds

- Every `fetch.sh` runs `git fetch --depth 1 origin <PIN_SHA>`, so a checkout is one commit with no history.
- Four checkouts have no commit at all (algebra-1, contemporary-mathematics, introduction-python-programming, writing-guide): their content was copied in as files on 2026-09-03 and their `.git` folders are empty.
- So nothing under impo can stand in for an upstream repository. Full history exists only in the maintainer's Pi clones (`192.168.0.186`) or an old working copy, and whether each Pi clone exists and is current has not been verified.

### Sizes

Across the sixteen book folders:

| What | Size |
|---|---|
| XML (`modules/` and `collections/`) | about 175 MB |
| Figures (`media/`) | about 4.4 GB |
| Exercise caches (already committed) | about 220 MB |

The five largest books, figures on disk and the git data of their single commit: prealgebra-bundle 959 MB / 305 MB; biology-bundle 706 MB / 642 MB; anatomy-physiology 516 MB / 433 MB; microbiology 343 MB / 314 MB; chemistry-bundle 319 MB / 245 MB. No single figure file is over 20 MB.

**How upstream fits on GitHub:** OpenStax keeps one repository per book or bundle, so no single repository is near 4.4 GB; that total exists only if the books are put together in one repository, such as impo. GitHub's guidance, as the agent recalled it and did **not** verify on 2026-11-26: keep a repository under about 1 GB, strongly under 5 GB, and no file over 100 MB. Verify before relying on it.

A book cannot be built without its figures, so committing only the XML into impo would not meet the goal.

### The licence finding

What each book's own source declares (the `license url` in the collection XML, and the first line of the upstream `LICENSE` file where the checkout has one):

| Book folder | Collections | Declared licence | Upstream `LICENSE` file in the checkout |
|---|---|---|---|
| osbooks-algebra-1 | algebra-1 | CC BY-NC-SA 4.0 | none (files copied in without git) |
| osbooks-anatomy-physiology | anatomy-and-physiology-2e | CC BY-NC-SA 4.0 | yes, BY-NC-SA |
| osbooks-astronomy | astronomy-2e | CC BY-NC-SA 4.0 | yes, BY-NC-SA |
| osbooks-biology-bundle | biology-2e, biology-ap-courses-2e, concepts-biology | CC BY-NC-SA 4.0 | yes, BY-NC-SA |
| osbooks-calculus-bundle | calculus-volume-1, -2, -3 | CC BY-NC-SA 4.0 | yes, BY-NC-SA |
| osbooks-chemistry-bundle | chemistry-2e, chemistry-atoms-first-2e | CC BY-NC-SA 4.0 | yes, BY-NC-SA |
| osbooks-college-algebra-bundle | algebra-and-trigonometry-2e, college-algebra-2e, college-algebra-corequisite-support-2e, precalculus-2e | CC BY-NC-SA 4.0 | yes, BY-NC-SA |
| osbooks-contemporary-mathematics | contemporary-mathematics | CC BY-NC-SA 4.0 | none |
| osbooks-introduction-python-programming | introduction-python-programming | CC BY-NC-SA 4.0 | none |
| osbooks-microbiology | microbiology | CC BY-NC-SA 4.0 | yes, BY-NC-SA |
| osbooks-organic-chemistry | organic-chemistry | CC BY-NC-SA 4.0 | yes, BY-NC-SA |
| **osbooks-physics** | physics | **CC BY 4.0** | yes, BY |
| osbooks-prealgebra-bundle | prealgebra-2e, elementary-algebra-2e, intermediate-algebra-2e, healthcare-foundations | CC BY-NC-SA 4.0 | yes, BY-NC-SA |
| osbooks-psychology | psychology-2e | CC BY-NC-SA 4.0 | yes, BY-NC-SA |
| osbooks-university-physics-bundle | university-physics-volume-1, -2, -3 | CC BY-NC-SA 4.0 | yes, BY-NC-SA |
| osbooks-writing-guide | writing-guide | CC BY-NC-SA 4.0 | none |

- **Fifteen of the sixteen folders are CC BY-NC-SA 4.0** (non-commercial, share-alike). Only `osbooks-physics` is CC BY 4.0.
- **impo's docs say CC BY 4.0 for all of it.** The places: `CLAUDE.md` ("License": "© OpenStax, CC BY 4.0"), `README.md` (the same sentence), `openstax/CLAUDE.md` ("Copyright / licensing", three statements), the template `openstax/tooling/templates/exercises-COPYRIGHT`, the seven committed `openstax/osbooks-*/exercises/COPYRIGHT` notices written from it, and `tasks/openstax-algebra-1-upstream-gone-backup-plan.md` (the agent repeated the error there on 2026-11-26: "The content is CC BY 4.0, so redistribution with attribution is allowed").
- **What licence the exercises themselves carry has not been checked.** The cached JSON came from OpenStax's Exercises API; the notices assert CC BY 4.0 for them. That may be right for the exercises even where it is wrong for the book. It must be read from the API's own terms or the JSON before the notices are rewritten.
- **The XML does not mark each file.** No module's `index.cnxml` carries licence metadata (0 of 4127 module folders). The licence is stated only in each collection XML and in the repository's `LICENSE` file. A copy of the XML without those two things is unmarked.
- **The built books already print the right page.** `openstax/CLAUDE.md` says the house class's defaults "reproduce the OpenStax CC BY-NC-SA 4.0 page". That should be verified for `osbooks-physics`, which is CC BY.

What the licence appears to require, as the agent read it (not legal advice): keeping and mirroring the source publicly is permitted when it is non-commercial, attributed and under the same licence; the built books are adaptations and must be shared under CC BY-NC-SA; impo's MIT licence covers only the maintainer's toolchain. One thing to check under "non-commercial": where and how the built books are published (`make publish-pages`, GitHub Releases).

### What is already decided and in motion

- **Public mirrors, one repository per book, under the maintainer's GitHub account** (`github.com/billsix/<book>`), pushed from the Pi clones, for all sixteen books; every `fetch.sh` gets an automatic fallback to its mirror; a sync is finished only when each moved pin is fetchable from its mirror (`CLAUDE.md`, "Contracts"; `tasks/openstax-algebra-1-upstream-gone-backup-plan.md`).
- **The maintainer refreshes the Pi mirrors at home** (`tasks/openstax-refresh-pi-mirrors-after-2026-11-sync.md`).

### The remaining outside dependency: the build image

The book images are built from `openstax/tooling/Dockerfile` (`FROM registry.fedoraproject.org/fedora:45`, then `dnf install` of TeX Live collections and tools). Rebuilding one needs Fedora's package servers. The book Makefiles have no `image-export` target (other repos of the maintainer's do). An exported image tar is what makes the toolchain independent of the network.

## The agent's advice

1. **Mirrors are the backup: one repository per book, full history.** They keep upstream's own `LICENSE` file and commit history intact, which is the clearest licence marking available, and they keep 4.4 GB of figures out of impo.
2. **Every `fetch.sh` falls back to its mirror automatically, and each sync checks the mirror holds the new pin.** (Already decided.)
3. **A second, offline copy on the Pi of each pinned commit**, as a `git bundle` per book, so that losing GitHub as well still leaves a buildable source.
4. **Export the build image after each sync** and keep the tar with the bundles.
5. **Correct the licence statements before anything is mirrored publicly.**
6. **Do not commit the source into impo itself.** It is possible (about 4.6 GB in one repository), but it duplicates what the mirrors hold; and committing only the 175 MB of XML does not make a book buildable.

## Plan (once the questions are answered)

**Licences (agent):**

- [ ] Find the licence of the exercise content (the API's terms, or a field in the cached JSON) and record it.
- [ ] Replace the blanket "CC BY 4.0" with the per-book truth in `CLAUDE.md`, `README.md` and `openstax/CLAUDE.md`, pointing at the table above (moved into `tasks/reference/openstax/book-inventory.md`).
- [ ] Make the exercise `COPYRIGHT` template state the right licence per book (or per content kind, depending on the first step), and regenerate the seven committed notices.
- [ ] Correct the sentence in `tasks/openstax-algebra-1-upstream-gone-backup-plan.md`.
- [ ] Verify what licence page each built book prints, `osbooks-physics` in particular.
- [ ] Decide with the maintainer whether the four checkouts without a `LICENSE` file get one copied in from the mirror once it exists.

**Source backup (maintainer, at home; agent afterwards):**

- [ ] Mirrors refreshed and pushed (the two existing tasks).
- [ ] If approved (question 3): a `git bundle` of each pinned commit kept on the Pi; a `tools/` script writes them.
- [ ] `fetch.sh` fallback and the per-sync mirror check (in the algebra-1 task).

**Build image (agent):**

- [ ] If approved (question 3): add `image-export` and `image-import` targets to the book Makefiles, following the maintainer's other repos, and add "export the image" to the sync method in `CLAUDE.md`.
- [ ] Prove the claim in answer 2: build one book in a container started with `--network=none`, from a checkout fetched beforehand.

**Docs:**

- [ ] Rewrite "The content model" in `openstax/CLAUDE.md`: the reason the source is not committed is now "it lives in a mirror the maintainer controls", not "it regenerates from the pin".

## Open questions

1. Should the agent correct the licence statements in impo now (the docs, the exercise `COPYRIGHT` template and the seven committed notices, the algebra-1 task), after first checking what licence the exercises carry? The agent recommends yes.
2. For the source backup: (a) mirrors plus Pi bundles, with nothing more committed in impo, or (b) also commit the XML and each book's `LICENSE` file into impo? The agent recommends (a).
3. Should image export and the per-book `git bundle` step be added to the tooling and the sync method? The agent recommends yes.
