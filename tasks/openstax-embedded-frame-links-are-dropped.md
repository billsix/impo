# Fixed: links in embedded frames (simulations, videos) were dropped from the built books

**Done 2026-11-27** (agent; go-ahead and both decisions from William Emerison Six <billsix@gmail.com>, 2026-11-27. Found 2026-11-26 while adding College Physics).

## The defect

Where an OpenStax module embeds an outside page in a frame (`<media><iframe src="https://…"/></media>`), usually an interactive simulation or a video, the converter emitted nothing. The surrounding text survived ("Visualize the gravitational force that two objects exert on each other …") and the address it referred to was gone, in the PDF, the EPUB and the HTML alike.

## Decisions (William Emerison Six <billsix@gmail.com>, 2026-11-27)

1. **An outside frame reads as a labelled line**, not a bare address ("2 b").
2. **Local frames stay left out** ("3 a"): Algebra 1's 177 Desmos graph files, Introduction to Python Programming's 129 code-runner pages and Writing Guide's 11. Embedding them in the HTML edition would be a task of its own; none exists.

## The fix

`render_media` in `openstax/tooling/tools/cnxml2tex/convert.py` now hands a media element with no image to `_frame_link`, which emits `\textbf{<label>:} \url{<address>}` for a frame whose address starts with `http://` or `https://`. The label is the enclosing note's title when it has one ("Gravity Force Lab"), else "Interactive" when the note's class contains `interactive`, else "Online resource" (the agent's wording for the untitled cases, many of which are videos and documents). Three tests in `openstax/tooling/tools/tests/test_helpers.py`. Described in `tasks/reference/tooling/converters.md`, "Outside pages embedded in frames".

## Proof

- **Only links were added.** `tools/compare-converter-output.sh` converted all 30 fetched books with the old and the new converter. 19 were identical. In the other 11, a comparison of the generated LaTeX token by token found 323 inserted links and nothing else, apart from line breaks; in one paragraph of *Life, Liberty, and the Pursuit of Happiness* the link took the place of two forced line breaks that had surrounded the empty frame.
- **The counts match the frames in the source:** Introduction to Political Science 115, Biology 51, Behavioral Neuroscience 40, Life, Liberty, and the Pursuit of Happiness 33, Physics 28, College Physics 18, University Physics 15, Introduction to Intellectual Property 9, World History 8, Algebra 1 3, Prealgebra 3. The task's table had said 29 for Physics; the 29th frame is inside an XML comment in module `m54437`.
- **The 11 book folders were rebuilt in all three formats on 2026-11-27 and all passed** (`tools/build-after-sync.sh`).
- The toolchain gate (`make -C openstax/tooling type-check`) passed, 63 tests.

## Not done

The rebuilt PDFs and HTML were not read page by page. The seven books that wait for their exercise caches were rebuilt without exercises, as before.
