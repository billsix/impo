# Keep every book buildable forever: back up the source, close the last outside dependencies, state the licences correctly

**Status:** in progress — the agent's part is done and committed (2026-11-26); the maintainer's part, pushing the public backups, is open
**Priority:** 3
**Difficulty:** 5
**Created:** 2026-11-26 (William Emerison Six <billsix@gmail.com>: "Given what we saw with the algebra git repo being gone from upstream, I want to reconsider any historical decision we made about fetching resources … In general I want these books buildable, at any point in the future, and I want advice … I want to make sure all copyright and licenses are clearly marked". Then: "take all of this information, and write in all as a task, all of it").

## BLUF

The maintainer wants every book in impo to be buildable at any point in the future, whether or not OpenStax's repositories or its exercise server still exist, with copyright and licences marked clearly. The decided answer is a public backup of each upstream repository under his GitHub account, which `fetch.sh` falls back to, plus an exported build image; and the licence statements, which were wrong for fifteen of sixteen book folders, are corrected. Done means every book's pinned source can be fetched from a place he controls. The tooling and the licence work are finished; what remains is pushing the backups.

## What was asked, and the answers

1. **Does `make fetch-exercises` download the exercises that are committed, so a book builds without the network?** Yes. It is the one networked step; the build reads only the committed `exercises/` cache. OpenStax's Exercises API returns questions only and withholds answer keys.
2. **If the source were also kept under the maintainer's control, could a book be built with upstream and the exercise server gone?** Yes, and it was proven: see "Offline build". The one remaining outside dependency is the build image, which installs Fedora and TeX Live packages when it is built.
3. **Could there be a `make fetch-xml-source`?** It already exists: each book's `fetch.sh` downloads the pinned source (`collections/`, `modules/`, `media/`) into `checkout/`, which is git-ignored. The decision was where a second copy of that source lives, not whether it can be fetched.

## What was found

- **The old reasoning failed.** `openstax/CLAUDE.md` said the source is never committed because "it regenerates from the pin". On 2026-11-26 `github.com/openstax/osbooks-algebra-1` returned 404 (`tasks/reference/openstax/algebra-1-upstream-removal.md`).
- **No checkout holds history.** Every `fetch.sh` fetches one commit (`--depth 1`). Four checkouts have no commit at all (algebra-1, contemporary-mathematics, introduction-python-programming, writing-guide): their content was copied in as files on 2026-09-03.
- **Sizes, sixteen book folders:** XML about 175 MB; figures about 4.4 GB; committed exercise caches about 220 MB. A book cannot be built without its figures, so committing only the XML into impo would not have met the goal.
- **How upstream fits on GitHub:** one repository per book or bundle; the largest is 719 MB (`tasks/reference/openstax/upstream-book-repositories.md`). GitHub's documented guidance (read 2026-11-26): "ideally less than 1 GB, and less than 5 GB is strongly recommended" per repository; a warning above 50 MiB per file and a block above 100 MiB.
- **The licences were stated wrongly.** Each book's own source declares its licence (the collection XML's `<md:license url>` and the upstream `LICENSE` file): CC BY-NC-SA 4.0 for fifteen of the sixteen folders, CC BY 4.0 for `osbooks-physics`. impo's docs, and the notice in every exercise cache, said CC BY 4.0 for all of it. The table is in `tasks/reference/openstax/book-inventory.md` ("Licences").
- **The built books contradicted themselves.** Every book's "About This Edition" page said the content was CC BY 4.0, while the class's licence page said CC BY-NC-SA 4.0 for every book, physics included.
- **The module files carry no licence metadata** (0 of 4127 module folders). The licence is stated only in the collection XML and the `LICENSE` file, and four checkouts have no `LICENSE` file.
- **The exercises have no single stated licence.** OpenStax Exercises' copyright page (https://exercises.openstax.org/copyright, read 2026-11-26) says the content is copyright Rice University or used with permission, that "many" questions are under a Creative Commons Attribution licence, and that each question carries its own terms. The API's JSON has no licence field and names Rice University as copyright holder.
- **What CC BY-NC-SA appears to require**, as the agent read it (not legal advice): an unmodified public copy is permitted when it is non-commercial, attributed and under the same licence; the built books are adaptations and carry the book's licence; impo's MIT licence covers only the maintainer's toolchain.

## Decisions (William Emerison Six <billsix@gmail.com>, 2026-11-26, in order)

1. **Correct the licence statements: yes.**
2. **Source backup: public mirrors of each OpenStax repository under `github.com/billsix`, with `fetch.sh` defaulting to OpenStax and falling back to the mirror.** In his words: "make github mirrors to github.com/billsix for each of the openstax repos, in case they take them away in the future … we could make fetch.sh default to the openstax repo but if not exist, use the github.com/billsix one". Nothing more is committed into impo. The agent had offered (a) mirrors plus offline bundles or (b) also committing the XML and `LICENSE` files into impo, and recommended (a).
3. **Image export and an offline bundle step: yes** ("whatever you recommend").
4. **Non-English books are not added to the build**, decided while reading the survey of upstream repositories. Recorded in `tools/upstream-books-rejected.txt`.
5. **Whether to back up all 54 upstream repositories or only the ones impo builds: not decided.** He is reading the survey first.

He asked for the plan to be rethought, and these points came out of that:

- **The mirrors do not need the Pi.** Fifteen upstreams still answer, so a full clone can be taken from OpenStax and pushed from any machine with his GitHub credentials. Only algebra-1 needs the Pi clone. The tasks written earlier that day had made all sixteen wait for his home network.
- **A pushed copy, not a GitHub fork**, so the backup is an independent repository.
- **A mirror goes stale**: it must be pushed again after every sync, and the sync contract in `CLAUDE.md` requires checking it.
- **GitHub is then the single point of failure**, so the Pi clones stay as the second copy and the tool can write an offline bundle of each.
- **The mirrors do not cover** the exercise server (covered by the committed caches) or the build image (covered by `make image-export`).

## What was done (agent, 2026-11-26)

- **`fetch.sh`, all sixteen:** a `MIRROR_URL=https://github.com/billsix/<name>` beside `UPSTREAM_URL`; the fetch tries the upstream, then the mirror, and removes the half-made `.git` if both fail (a leftover empty `.git` is what had made four checkouts look fetched). Tested on a copy: with a dead upstream and a live second source it fetched the pin; with both dead it exited 1 with a clear message and left nothing behind. The Pi path was removed from the scripts and from each book's `CLAUDE.md`. Codemod: `tasks/adhoc/openstax-books-buildable-forever/add_mirror_fallback_and_image_export.py` (a second run changes nothing).
- **`tools/mirror-upstreams.sh`:** `check` needs no credentials and reports per book whether the mirror holds the pin; `push` is the maintainer's: it clones or updates, refuses a clone that lacks the pin, optionally creates the repository with `gh` (`CREATE=1`) and writes an offline bundle (`BUNDLE_DIR`).
- **`make image-export` and `make image-import`** in all sixteen book Makefiles and the Trench book's. (Since 2026-11-28 every folder builds one image, `impo-openstax-toolchain`, so the tar is the same from any of them; a tar saved earlier loads under its old per-book name and needs `podman tag <old name> impo-openstax-toolchain`.)
- **Licences in the built books:** the converter reads each collection's `<md:license url>` (`licence_from_url` in `openstax/tooling/tools/cnxml2tex/convert.py`, with doctests) and states it on the class's licence page (`\setOSbooklicense`) and in the colophon. A collection with no licence the converter knows fails the conversion. Gate: `make format` (ruff, ty) and `make test` (47 passed) in the physics container. Read back from rebuilt PDFs: psychology states CC BY-NC-SA 4.0 in both places, physics CC BY 4.0 in both.
- **Licences in the docs:** `CLAUDE.md`, `README.md`, `openstax/CLAUDE.md` and the algebra-1 task state the per-book truth; "The content model" in `openstax/CLAUDE.md` now gives the mirror, not "it regenerates from the pin", as what keeps the source available.
- **Exercise notices:** the template `openstax/tooling/templates/exercises-COPYRIGHT` and the seven committed `COPYRIGHT` notices say whose the files are and what OpenStax Exercises states about their terms; they no longer assert CC BY 4.0.
- **A survey of every upstream book repository:** `tools/survey-upstream-books.py` and `tasks/reference/openstax/upstream-book-repositories.md` (54 repositories, 88 books; 15 built in impo, 30 not yet, 9 rejected as not English, 1 built with the upstream gone, 0 backed up).

## Offline build

`make -C openstax/osbooks-psychology dist PODMAN_RUN_FLAGS='--cgroups=disabled --network=none'` built Psychology 2e as PDF, EPUB and HTML on 2026-11-26. All three container runs carried `--network=none`; the conversion had been run just before from the checkout already on disk. So with the source fetched and the image present, a book builds with no network at all. It does not prove two things: building the image itself (its layers came from the local cache; a from-scratch image build needs Fedora's package servers, which is what `make image-export` is for), and a book with embedded exercises (psychology has none; those read the committed cache, and no code path fetches during a build).

## Still open

- **Maintainer:** `CREATE=1 bash tools/mirror-upstreams.sh push` for the 44 book folders whose upstream answers (15 when this task was written; 29 added 2026-11-26 to 2026-11-28), from any machine with his GitHub credentials. Algebra-1's mirror was pushed and verified 2026-11-27 (`tasks/reference/openstax/algebra-1-upstream-removal.md`, "Outcome").
- **Maintainer:** decision 5, how many of the 54 repositories to back up. `tools/mirror-upstreams.sh` handles only the books impo builds; backing up others needs it to accept repository names.
- **Agent, after the push:** `bash tools/mirror-upstreams.sh check`, then refresh the survey table.
- **A wording point for the maintainer:** the colophon says the toolchain "and this LaTeX formatting" are under the MIT License, while the licence page says the edition is distributed under the book's licence. For a share-alike book the edition as a whole carries the book's licence; whether his own formatting is additionally offered under MIT is his statement to make. The wording was left as it was. The agent's suggestion: say only the toolchain is MIT, for the fifteen share-alike books.
- **The three checkouts without a `LICENSE` file** (contemporary-mathematics, introduction-python-programming, writing-guide) get one when they are refetched from a mirror. Algebra-1 was the fourth; its refetch from the mirror on 2026-11-27 brought the file.
- **At archive:** `git rm` the one-shot codemod under `tasks/adhoc/openstax-books-buildable-forever/`.

## Open questions

1. How many upstream repositories should get a public backup: (a) the fifteen impo builds plus algebra-1, or (b) all 54? The agent recommends (a) now, extending the tool when more books are built. (Waiting for the maintainer to read the survey.)
2. Should the "About This Edition" sentence say only the toolchain is MIT, or keep saying the formatting is MIT too? The agent recommends the first.
