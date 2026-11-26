# Algebra 1: the upstream source repository disappeared — what happened, what is known about why, and the plan

**Reference doc.** Written 2026-11-26 for William Emerison Six <billsix@gmail.com> ("make a reference document
about what happened, and why, and that I intend to make a public mirror … I want the source material").
Update it in place when something new is learned, in particular the reason, which is **not known**.

## What happened

- impo builds OpenStax's **Algebra 1** from the repository `https://github.com/openstax/osbooks-algebra-1`,
  pinned at commit `332f78647098a60532a9833b8003dca5da7ff227`.
- On **2026-11-26**, during a routine check of every book's pin, that repository returned **HTTP 404**, and
  `git ls-remote` asked for a user name, which is what GitHub does for a repository that is private, deleted
  or renamed. The response does not say which of the three it is.
- It is no longer among the public repositories of the `openstax` organisation
  (`tasks/reference/openstax/upstream-book-repositories.md` lists the 54 that are). A search engine still
  indexed it by name on that day, so it had been public not long before. When it stopped being public is not
  known; impo last had reason to fetch it on 2026-10-19, when it was found already at the pinned commit by
  `git ls-remote`, so it was public then.
- **The book itself was not withdrawn.** It is live on openstax.org
  (https://openstax.org/books/algebra-1/pages/about-this-course) with a publish date of June 4, 2025, under
  CC BY-NC-SA 4.0, and OpenStax promotes it: the Texas State Board of Education approved it unanimously
  (Rice News, 2025-02-13), and a 2026 Rice News item reports a district expanding its use. Only the public
  source repository is gone.

## What impo still has

Everything the build needs, in `openstax/osbooks-algebra-1/`:

| What | Where | Amount | In git? |
|---|---|---|---|
| Book structure | `checkout/collections/algebra-1.collection.xml` | 1 file | no (`checkout/` is ignored) |
| Chapters and sections (CNXML) | `checkout/modules/` | 976 modules, 18 MB | no |
| Figures and embedded Desmos files | `checkout/media/` | 2,354 files, 124 MB | no |
| Practice exercises | `exercises/` | 932 files | **yes**, committed |
| A PDF and an EPUB built 2026-09-03 | `checkout/output/` | 2 files | no |

Three weaknesses of this copy:

- **It is in no commit and no remote.** Losing the folder loses the source. `fetch.sh` cannot recreate it.
- **It has no git history**, so nothing proves the files are exactly the pinned commit. They were copied in
  from the original port working copy; the files are dated 2026-04-23.
- **It has no `LICENSE` file.** The collection XML does declare CC BY-NC-SA 4.0.

A full-history clone is believed to exist on the maintainer's Pi machine (`192.168.0.186`). That has not
been verified, because the sandbox cannot reach it.

## Why: not known

**OpenStax has published no explanation that could be found.** Searched on 2026-11-26: the book's pages on
openstax.org, its Texas curriculum page, the Rice News items, and the web generally for an announcement,
forum thread or issue. None mentions GitHub, source files or repositories. One page could not be read:
https://openstax.org/license, titled "An update on OpenStax licensing", returned only its title to the
tool. It may hold an answer and should be read in a browser.

**What makes Algebra 1 different from the books whose repositories are still public** (all 54 of the others
looked like college-level books by their names). These are observations from impo's local copy and from
openstax.org; that any of them is the reason is the agent's inference, not a fact:

| Difference | Algebra 1 | For comparison: College Algebra | Why it might matter |
|---|---|---|---|
| Audience | a K-12 school curriculum: 116 "Lesson Overview" modules, teacher-facing text in 59 modules | a college textbook | school materials often keep teacher guides and assessments from students |
| Third-party basis | "based, in part, on … the IM 6–12 Math by Illustrative Mathematics" (their trademark) | OpenStax's own content | another party's content can come with conditions |
| Embedded tools | 90 modules embed Desmos graphing files | none | third-party software inside the source |
| Commercial channel | print copies sold as a "Texas Edition" through Kendall Hunt | none found | a paid edition alongside an open one |
| Licence wording | adds: "may not be used in the training of large language models or otherwise be ingested into large language models" or generative AI offerings without OpenStax's written permission | not checked | a public repository is the easiest thing to collect automatically |
| Gated materials | teacher guide, slides and assessments need an instructor account | not applicable | part of the course is meant to be gated |

The likeliest explanation, on this evidence, is something specific to it being a school product. Which of
the above, or something else entirely, cannot be told from outside. **The way to find out is to ask
OpenStax**; the book's page gives a content-reuse request form (https://openstax.org/r/content-reuse-request).

## What the maintainer intends

(William Emerison Six <billsix@gmail.com>, 2026-11-26.)

- **To keep the source material**, because he wants it available for his own children, who are around the
  age the course is written for.
- **To make a public mirror** of it under his GitHub account, `https://github.com/billsix/osbooks-algebra-1`,
  like the mirrors planned for every book impo builds. `openstax/osbooks-algebra-1/fetch.sh` already falls
  back to that address.

## Things to settle before the mirror is public

- **Which copy is mirrored.** The goal is the Pi clone with its full history, after confirming it contains
  the pin. If no clone with history exists, the files in `checkout/` can seed the mirror as a single commit;
  the upstream commit id is then lost, and the mirror should say so.
- **The licence, read for this book specifically.** As the agent reads CC BY-NC-SA 4.0 (not legal advice), an
  unmodified public copy is permitted when it is non-commercial, attributed, and under the same licence, and
  the book's page asks for the attribution line "Access for free at
  https://openstax.org/books/algebra-1/pages/about-this-course". The mirror should carry a `LICENSE` file
  (the checkout has none) and that attribution.
- **That OpenStax took the source out of public view.** The licence on the published book is what governs
  reuse, and it was not changed to forbid copies; but OpenStax evidently no longer wants this repository
  public, for a reason not known. The maintainer may prefer to ask them first, or to keep the mirror private
  until `https://openstax.org/license` has been read.
- **The Illustrative Mathematics and Desmos material** inside the book may carry terms of its own. The book's
  page gives no separate licence statement for either.
- **A second copy now.** Until a mirror exists, an archive of `openstax/osbooks-algebra-1/checkout/` kept
  somewhere else removes the single point of failure.

## Where the work is tracked

- `tasks/openstax-algebra-1-upstream-gone-backup-plan.md`: the steps (confirm the Pi clone, push the mirror,
  build from it).
- `tools/upstream-books-gone.txt`: this book's line; `tools/survey-upstream-books.py` shows it as a "gone"
  row in `tasks/reference/openstax/upstream-book-repositories.md`.
- `tasks/openstax-books-buildable-forever-source-backup-and-licences.md`: the wider decision to mirror every
  book, and the licence corrections.

## Sources (read 2026-11-26)

- https://openstax.org/books/algebra-1/pages/about-this-course (authorship, basis, licence and its added terms)
- https://openstax.org/texas-algebra-curriculum (Texas approval, gated teacher materials)
- https://news.rice.edu/news/2025/openstax-algebra-curriculum-receives-unanimous-approval-texas
- https://news.rice.edu/news/2026/spring-isd-posts-houston-regions-largest-algebra-1-gain-openstax-curriculum-expands
- https://k12.kendallhunt.com/product/openstax-algebra-1-texas-edition-student-textbook-set (found by search; not opened)
- https://github.com/openstax/osbooks-algebra-1 (404)
