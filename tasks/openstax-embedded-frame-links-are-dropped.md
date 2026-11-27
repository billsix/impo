# Links in embedded frames (simulations, videos) are dropped from the built books

**Status:** approved 2026-11-27 (William Emerison Six <billsix@gmail.com>: "3 yes"); not started, because its two open questions below were not answered with the go-ahead
**Priority:** 5
**Difficulty:** 3
**Created:** 2026-11-26 (agent, found while adding College Physics; parked as its own task because fixing it changes the output of books impo already builds).

## BLUF

Where an OpenStax module embeds an outside page in a frame (`<media><iframe src="https://…"/></media>`), usually an interactive simulation or a video, the converter emits nothing for it. The surrounding text survives ("Visualize the gravitational force that two objects exert on each other …") and the address it refers to is gone. Done means every such frame becomes a visible link in the PDF, EPUB and HTML, and the before-and-after comparison shows only those additions.

## Context

**Read first:** `render_media` in `openstax/tooling/tools/cnxml2tex/convert.py`, and `tasks/reference/tooling/converters.md`.

**Counts (2026-11-26, frames whose `src` is an `http(s)` address):**

| Book folder | Frames with an outside address | Frames with a local file |
|---|---|---|
| osbooks-biology-bundle | 51 | 0 |
| osbooks-physics | 29 | 0 |
| osbooks-college-physics-bundle | 18 | 0 |
| osbooks-introduction-political-science (added 2026-11-27) | 115 | 0 |
| osbooks-neuroscience (added 2026-11-27) | 40 | 0 |
| osbooks-life-liberty-and-pursuit-happiness (added 2026-11-27) | 33 | 0 |
| osbooks-introduction-intellectual-property (added 2026-11-27) | 9 | 0 |
| osbooks-world-history (added 2026-11-27) | 8 | 0 |
| osbooks-university-physics-bundle | 15 | 0 |
| osbooks-algebra-1 | 3 | 177 |
| osbooks-prealgebra-bundle | 3 | 0 |
| osbooks-introduction-python-programming | 0 | 129 |
| osbooks-writing-guide | 0 | 11 |

- **Example:** College Physics, the note "Gravity Force Lab": `<iframe width="660" height="371.4" src="https://openstax.org/l/gravity-force"/>`. The generated LaTeX for that module contains no link.
- **Local frames are a different case.** Algebra 1's are Desmos graph files under `media/desmos/`, and Introduction to Python Programming's are code-runner pages. They cannot work in a PDF; what the web edition should do with them is a separate question (question 2).

## Plan

1. In `render_media`, when the media element holds an `<iframe>` with an `http(s)` `src`, emit a short line with the address as a link (`\url{…}`), which pandoc carries into the HTML and EPUB.
2. Prove the change with the method used on 2026-11-26 for Content MathML: convert every book with the old and the new converter and compare the generated LaTeX; the only differences should be the added links, and their count per book should match the table.
3. Rebuild the books that changed; record the behaviour in `tasks/reference/tooling/converters.md`.

## Open questions

1. How should an outside frame read in the book: (a) the bare address as a link, or (b) a labelled line such as "Interactive: https://…"? The agent recommends (b), using the enclosing note's title when there is one.
2. Local frames (Algebra 1's Desmos files, Python Programming's code runners): (a) leave them out as today, or (b) in the HTML edition, embed the local file as a frame? The agent recommends (a) for now and a separate task if (b) is wanted.
