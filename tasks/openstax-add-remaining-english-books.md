# Add the remaining English OpenStax books to impo (umbrella: 29 repositories, 42 books)

**Status:** in progress — 13 of 29 repositories built by 2026-11-27 (6 done and archived, 7 waiting for their exercise caches); 16 not started
**Priority:** 4
**Difficulty:** 7 (each book is small; there are 29 of them, and each can meet markup the converter has not seen)
**Created:** 2026-11-26 (William Emerison Six <billsix@gmail.com>: "I want to add all of the ones you said. look through all reference docs, and look at what we commited to do the porting before, and make a task per book").

## BLUF

impo built 15 of OpenStax's 54 public book repositories, plus Algebra 1, when this task was written (28 with Algebra 1 on 2026-11-27). Nine are rejected as not English and one, `osbooks-playground`, as not a book. The maintainer wants the other 29 added. This umbrella holds the method they all share and the ordered list; each repository has its own step task. Done means every step task is archived and the survey shows no repository as "not yet in impo".

## Context

**Read first:** `openstax/CLAUDE.md` (the family contract), `tasks/reference/openstax/upstream-book-repositories.md` (the survey these tasks came from), `tasks/reference/tooling/converters.md` (what the converter handles) and `tasks/archive/impo/2026/09/03/openstax-populate-books.md` (how the first sixteen were added).

### How the first sixteen were added, and what is different now

The September work scaffolded fifteen folders from the anatomy-physiology pilot with a generator script, build-verified three representative books (a toolchain-only book, an SVG book and a book with downloads), then fetched and committed the exercise caches. It needed no per-book fixes at first, and later found that two books' exercises had been silently dropped because the converter knew only one of the two exercise-link schemes. Lessons carried into these tasks:

- **The pin.** The first sixteen were pinned at the commit where the maintainer's own `latex` port branch left upstream. These books have no such branch; the pin is the upstream default-branch head when the work starts, as at every sync since.
- **Every book is converted and built, not sampled.** Since 2026-11-26 a sync ends with a clean build (`CLAUDE.md`, "Contracts"); the same holds for adding a book.
- **Exercises are checked in both schemes** (`#exercise/<nickname>` and `#ost/api/ex/<id>`), by counting the links in the CNXML, not by trusting the converter's silence.
- **The licence is read from the source.** The converter fails on a collection whose licence it does not know, and the book's row goes into the inventory's licence table. 4 of these repositories are CC BY 4.0 and 25 are CC BY-NC-SA 4.0.
- **Every new `fetch.sh` has the mirror fallback** from the start, and the book is added to the maintainer's backups.
- **The exercise fetch is the maintainer's to run**: it identifies itself to OpenStax's server with his contact address.

### What adding 29 repositories costs beyond the per-book work

- **The release workflow** builds every folder `make list-books` reports, so each new book lengthens a release build by one job.
- **The published site.** GitHub Pages has a 1 GB limit that impo is already managing (`tasks/openstax-pages-size-budget.md`, `tasks/reference/openstax/publishing.md`); 42 more books will not fit as the site is built today. Publishing them is a decision for that task, not for these.
- **Disk.** These repositories total about 4.2 GB on GitHub with history; a one-commit checkout of each is smaller.
- **The toolchain image is shared**, so no new image is needed.

## Steps

Step 0 comes first; after it the books are independent of each other, so the order below is by how close each is to what impo already builds (lowest priority number first), not by necessity.

- [x] `tasks/archive/impo/2026/11/26/openstax-add-book-step-0-scaffold-tool.md` — the scaffold tool (`tools/add-book.sh`), done 2026-11-26

**Mathematics, statistics and physics (closest to what impo builds)**

- [x] `tasks/archive/impo/2026/11/26/openstax-add-book-college-physics-bundle.md` — 2 books: `college-physics-2e`, `college-physics-ap-courses-2e` (CC BY-NC-SA 4.0, 394 MB), done 2026-11-26
- [x] `tasks/archive/impo/2026/11/26/openstax-add-book-introductory-statistics-bundle.md` — 2 books: `introductory-statistics-2e`, `introductory-business-statistics-2e` (CC BY-NC-SA 4.0, 104 MB), done 2026-11-26
- [x] `tasks/archive/impo/2026/11/27/openstax-add-book-principles-data-science.md` — one book: `principles-data-science` (CC BY-NC-SA 4.0, 38 MB), done 2026-11-27
- [x] `tasks/archive/impo/2026/11/26/openstax-add-book-statistics.md` — one book: `statistics` (CC BY 4.0, 34 MB), done 2026-11-26

**Computing and technology**

- [x] `tasks/archive/impo/2026/11/27/openstax-add-book-additive-manufacturing.md` — one book: `additive-manufacturing-essentials` (CC BY-NC-SA 4.0, 36 MB), done 2026-11-27
- [x] `tasks/archive/impo/2026/11/27/openstax-add-book-foundations-information-systems.md` — one book: `foundations-information-systems` (CC BY-NC-SA 4.0, 35 MB), done 2026-11-27
- [ ] `tasks/openstax-add-book-workplace-software-skills.md` — one book: `workplace-software-skills` (CC BY-NC-SA 4.0, 360 MB)

**History and government**

- [x] `tasks/archive/impo/2026/11/27/openstax-add-book-american-government.md` — one book: `american-government-4e` (CC BY-NC-SA 4.0, 219 MB), done 2026-11-27
- [x] `tasks/archive/impo/2026/11/27/openstax-add-book-introduction-political-science.md` — one book: `introduction-political-science` (CC BY-NC-SA 4.0, 97 MB), done 2026-11-27
- [ ] `tasks/openstax-add-book-life-liberty-and-pursuit-happiness.md` — one book: `life-liberty-and-pursuit-happiness` (CC BY 4.0, 314 MB); **built 2026-11-27 without its exercises, open until the maintainer runs `make fetch-exercises` there**
- [x] `tasks/archive/impo/2026/11/27/openstax-add-book-us-history.md` — one book: `us-history` (CC BY-NC-SA 4.0, 131 MB), done 2026-11-27
- [x] `tasks/archive/impo/2026/11/27/openstax-add-book-world-history.md` — 2 books: `world-history-volume-1`, `world-history-volume-2` (CC BY-NC-SA 4.0, 382 MB), done 2026-11-27

**Science and health**

- [ ] `tasks/openstax-add-book-neuroscience.md` — one book: `introduction-behavioral-neuroscience` (CC BY-NC-SA 4.0, 402 MB); **built 2026-11-27 without its exercises, open until the maintainer runs `make fetch-exercises` there**
- [ ] `tasks/openstax-add-book-lifespan-development.md` — one book: `lifespan-development` (CC BY-NC-SA 4.0, 102 MB)
- [ ] `tasks/openstax-add-book-nursing-external-bundle.md` — 3 books: `pharmacology`, `nutrition`, `population-health` (CC BY-NC-SA 4.0, 225 MB)

**Economics, business and law**

- [ ] `tasks/openstax-add-book-business-ethics.md` — one book: `business-ethics` (CC BY-NC-SA 4.0, 93 MB)
- [x] `tasks/archive/impo/2026/11/27/openstax-add-book-business-law.md` — one book: `business-law-i-essentials-2e` (CC BY-NC-SA 4.0, 12 MB), done 2026-11-27
- [ ] `tasks/openstax-add-book-entrepreneurship.md` — one book: `entrepreneurship` (CC BY-NC-SA 4.0, 123 MB)
- [ ] `tasks/openstax-add-book-introduction-business.md` — one book: `introduction-business-2e` (CC BY 4.0, 225 MB)
- [x] `tasks/archive/impo/2026/11/27/openstax-add-book-introduction-intellectual-property.md` — one book: `introduction-intellectual-property` (CC BY 4.0, 30 MB), done 2026-11-27
- [ ] `tasks/openstax-add-book-principles-accounting-bundle.md` — 2 books: `principles-financial-accounting`, `principles-managerial-accounting` (CC BY-NC-SA 4.0, 258 MB)
- [ ] `tasks/openstax-add-book-principles-economics-bundle.md` — 5 books: `principles-economics-3e`, `principles-macroeconomics-3e`, `principles-microeconomics-3e`, `principles-macroeconomics-ap-courses-2e`, `principles-microeconomics-ap-courses-2e` (CC BY-NC-SA 4.0, 84 MB)
- [ ] `tasks/openstax-add-book-principles-finance.md` — one book: `principles-finance-2e` (CC BY-NC-SA 4.0, 38 MB)
- [ ] `tasks/openstax-add-book-principles-marketing.md` — one book: `principles-marketing` (CC BY-NC-SA 4.0, 61 MB)
- [ ] `tasks/openstax-add-book-principles-of-management-bundle.md` — 2 books: `principles-management`, `organizational-behavior` (CC BY-NC-SA 4.0, 79 MB)

**Social sciences and humanities**

- [ ] `tasks/openstax-add-book-introduction-anthropology.md` — one book: `introduction-anthropology` (CC BY-NC-SA 4.0, 115 MB)
- [ ] `tasks/openstax-add-book-introduction-philosophy.md` — one book: `introduction-philosophy-2e` (CC BY-NC-SA 4.0, 67 MB)
- [ ] `tasks/openstax-add-book-introduction-sociology.md` — one book: `introduction-sociology-3e` (CC BY-NC-SA 4.0, 160 MB)

**Study skills**

- [ ] `tasks/openstax-add-book-college-success-bundle.md` — 3 books: `college-success-2e`, `college-success-concise`, `preparing-for-college-success` (CC BY-NC-SA 4.0, 50 MB)

## Progress

- **2026-11-26:** step 0 and three repositories done (Statistics, the Introductory Statistics bundle, College Physics): five books. The maintainer stopped there for the day to merge and push. **Next: `tasks/openstax-add-book-principles-data-science.md`**, the last of the mathematics and physics group. Its folder is already scaffolded and fetched in the working tree (untracked), it converts, and it embeds 136 exercises, so it starts with the maintainer running `make -C openstax/osbooks-principles-data-science fetch-exercises`.
- **2026-11-27:** ten more repositories built and committed (eleven books): Business Law, U.S. History and American Government are done and archived; Additive Manufacturing, Foundations of Information Systems, Introduction to Intellectual Property, Introduction to Political Science, Behavioral Neuroscience, World History (2 volumes) and Life, Liberty, and the Pursuit of Happiness are built without their exercises and their tasks are `blocked` on the maintainer's `make fetch-exercises`, as is Principles of Data Science (still untracked). The converter learned block quotations and reference notes on the way (`tasks/reference/tooling/converters.md`). **Next after the fetches:** the 16 repositories still unticked below, none started.
- Two converter defects found on the way have their own tasks: `tasks/archive/impo/2026/11/27/openstax-degree-sign-inside-math-text-is-escaped.md` (fixed 2026-11-27) and `tasks/archive/impo/2026/11/27/openstax-embedded-frame-links-are-dropped.md` (fixed 2026-11-27).

## Decisions (William Emerison Six <billsix@gmail.com>, 2026-11-26)

- **Incrementally, mathematics and physics first**: one book at a time, each committed, archived and marked in the survey table before the next starts.
- **Repository and site size are not a concern until GitHub complains** ("we will only be concerned about repo size if and when github complains").

- **Add all 29**, not only the four closest to what impo builds.
- **One task per repository**, not per book: a bundle is one folder and one build.
- **`osbooks-playground` is rejected**: its README calls it "a playground to try out the OpenStax's POET editing plugin". Recorded in `tools/upstream-books-rejected.txt`.
- **Non-English repositories stay rejected** (decided earlier the same day).

## Open questions

None.
