# Research: can impo build Illustrative Mathematics' high-school Geometry course?

**Status:** proposed — needs go-ahead (research only; no book folder is added by this task)
**Priority:** 5
**Difficulty:** 5
**Created:** 2026-11-27 (William Emerison Six <billsix@gmail.com>: "add a task to impo to research if we can make a build of that illustrative math geometry, and list both versions as candidates")

## BLUF

impo builds no geometry book: the survey of OpenStax's repositories
(`tasks/reference/openstax/upstream-book-repositories.md`) lists none, and the geometry material in
`study/` follows the Common Core groups, not a book. Illustrative Mathematics (IM) publishes a high-school
Geometry course under a Creative Commons licence, in two editions. This task finds out whether impo
can build either edition as PDF, EPUB and HTML, and at what cost. Done means a reference doc under
`tasks/reference/` that answers the questions below for both editions, with a recommendation, and a
follow-on task if the recommendation is to build one.

## Context

**Why now.** The maintainer's book "Geometry 2" (github.com/billsix/geometricalgebra) reads a
standard geometry textbook for topics to connect to geometric algebra. That textbook (Charles et al.,
*Geometry: Common Core*, Pearson, 2012) is all rights reserved, so the book may cite it but not quote
its definitions, figures or exercises at length. An openly licensed geometry course would be a text
the book may quote and adapt with attribution. The wider plan is
github.com/billsix/runClaudeInContainer `tasks/archive/2026/11/27/external-source-outlines-and-coverage-tracking.md`
(its open question 3 is whether to add IM Geometry as a second source).

**The two candidates** (from IM's terms of use, https://www.illustrativemathematics.org/terms-of-use,
"Effective as of May 21, 2026", read 2026-11-27):

| | First edition | Second edition, "v.360" |
| --- | --- | --- |
| Name on the terms page | IM K–12 Math | IM TK–12 Math v.360 |
| Copyright years | 2019–2021 | 2024 (IM TK Math 2025) |
| Licence | CC BY 4.0 | CC BY-NC 4.0 |
| Commercial use | allowed | "expressly prohibited" without written permission |
| Suggested attribution | "Based on IM® K–12 Math authored by Illustrative Mathematics and licensed under CC BY 4.0." | "Based on IM® TK–12 Math v.360 authored by Illustrative Mathematics and licensed under CC BY-NC 4.0." |

- The IM name and marks are outside both licences; a product name must not suggest an association
  with IM (same page, "Brand Guidelines").
- The first edition is hosted at https://im.kendallhunt.com/ (found by search; the Geometry pages
  were not opened).
- **Not confirmed:** that the v.360 high-school Geometry course is published under the v.360 terms
  in the same way as the lower grades. Check the course's own pages.

**What impo already knows about IM.**

- `openstax/osbooks-algebra-1` is OpenStax's Algebra 1, which is "based, in part, on … the IM 6–12
  Math by Illustrative Mathematics" (`tasks/reference/openstax/algebra-1-upstream-removal.md`). That
  doc notes the IM and Desmos material inside the book "may carry terms of its own", and that
  OpenStax withdrew the book's upstream repository (the same doc, "What happened"). Read it before
  assuming an IM source will stay available.
- impo's toolchain converts **CNXML** to LaTeX (`openstax/tooling/`). IM's courses are not known to
  be published as CNXML, so a build is likely a new book family beside `openstax/` and `trench/`,
  with its own converter or importer. Finding the real source format is the first question.
- Licences per book are recorded in `tasks/reference/openstax/book-inventory.md` and the root
  `CLAUDE.md` ("License"); a built book is an adaptation and carries its source's licence. Most book
  folders are CC BY-NC-SA 4.0 and four are CC BY 4.0; a CC BY-NC edition would be a third licence, so
  check what that means for publishing it beside the other books
  (`tasks/reference/openstax/publishing.md`).

## Goal

A written answer, per edition, to "can impo build this, should it, and what would it take", good
enough for the maintainer to choose an edition or decline both.

## Plan

- [ ] **Source format and availability, per edition.** Is there a downloadable source (a repository,
      an export, structured HTML, Word or PDF only)? Does a third party redistribute the first
      edition in a structured form (Open Up Resources, GeoGebra, a state OER site), and under what
      licence statement? Record each URL and whether it was opened.
- [ ] **Stability.** Can the source be pinned and mirrored, as impo does for OpenStax (`fetch.sh`,
      `tools/mirror-upstreams.sh`)? The Algebra 1 removal shows why this matters.
- [ ] **Content shape.** The course is activity-first (warm-up, activity, lesson summary, practice
      problems), with teacher and student materials, images and applets. Which parts make a book a
      student reads, and which parts depend on interactive applets or on teacher materials?
- [ ] **Licence detail.** Confirm the licence on the Geometry course's own pages for each edition;
      list any third-party material inside it with different terms (images, Desmos or GeoGebra
      applets); state the attribution impo would print, and how the naming restriction limits the
      built book's title.
- [ ] **Fit with the toolchain.** Estimate the work for a converter into the `osbook` LaTeX house
      style and the pandoc HTML/EPUB editions, and say what could be reused from `openstax/tooling/`.
- [ ] **Compare the editions** on licence, content quality and currency, source availability and
      build cost, and recommend one, both or neither.
- [ ] Write the findings to `tasks/reference/impo/illustrative-mathematics-geometry.md` and, if the
      recommendation is to build, scaffold the follow-on task.

## Notes / decisions

- 2026-11-27: task created from the geometricalgebra investigation. Nothing about IM's source format
  has been checked yet; the only page read is the terms of use.

## Open questions

1. If only the first edition (CC BY 4.0) turns out to be buildable from a stable source, is the
   older edition acceptable, or does the maintainer want v.360's content enough to accept CC BY-NC?
   The agent recommends the first edition: its licence lets "Geometry 2" quote and adapt it without
   a non-commercial condition.
2. Is a student-facing book the target, or would a structured outline with page-cited definitions
   (enough for citation from "Geometry 2") be sufficient? The agent recommends deciding after the
   content-shape step.
