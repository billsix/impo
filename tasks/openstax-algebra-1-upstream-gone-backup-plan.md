# Algebra 1: the upstream was gone — mirrored from the maintainer's clone and fetched from the mirror

**Done:** 2026-11-28 (the build finished just after midnight UTC; the fetch and comparison were on 2026-11-27).
**Created:** 2026-11-26 (William Emerison Six <billsix@gmail.com>: "make a task to investigate this on a later date and make a decision then, I need a backup plan, I planned for ideas like this (by cloning stuff on my raspberry pi box) but never thought it would happen").

**Background and outcome:** `tasks/reference/openstax/algebra-1-upstream-removal.md` ("Outcome" holds the
durable facts; this record holds the order of events).

## What it was

OpenStax's `osbooks-algebra-1` repository stopped answering on GitHub (found 2026-11-26), so impo could not
fetch that book's source. The only copy reachable from the sandbox was the plain files in
`openstax/osbooks-algebra-1/checkout/`, in no commit and with no git history. The pin was
`332f78647098a60532a9833b8003dca5da7ff227`, the commit where the maintainer's `latex` port branch left
OpenStax's `main`.

## Decisions (William Emerison Six <billsix@gmail.com>, in order)

1. 2026-11-26: **investigate later, with a backup plan.** The task was filed instead of acting at once,
   because the Pi machine with his full-history clone could not be reached.
2. 2026-11-26: **the book lived on the local files for the time being**; the full history was wanted once he
   was on the network with the Pi.
3. 2026-11-26: **the backup was a public mirror under his GitHub account**, for this book and for every book
   impo builds, with `fetch.sh` defaulting to OpenStax and falling back to the mirror. Rejected: committing
   the source into impo (about 4.6 GB across the books), and the Pi as the only fallback (it works only on
   his home network).
4. 2026-11-26: **he intended the Algebra 1 mirror to be public**, and wanted the source material kept for
   his own children.
5. 2026-11-27: he pushed the mirror to `https://github.com/billsix/osbooks-algebra-1` from his home network
   and told the agent to carry out the remaining steps.

## What was done

Put in place on 2026-11-26, before the mirror existed: `fetch.sh` tried the upstream and then the mirror;
`tools/mirror-upstreams.sh` pushed and checked mirrors; the survey table showed the book as a "gone" row from
`tools/upstream-books-gone.txt`. A public fork under the maintainer's account and a Software Heritage archive
of the upstream URL were looked for and not found.

On 2026-11-27, after the maintainer's push:

1. `bash tools/mirror-upstreams.sh check algebra-1` reported "mirror holds the pin 332f7864".
2. The pin was fetched from the mirror into a scratch folder and compared with the old `checkout/` by
   `diff -rq`. `collections/` (1 file), `modules/` (976) and the mirror's 1,493 media files were identical.
   The old `media/` held 930 further files: a PDF and a PNG for each of the 465 SVG figures, written by the
   build on 2026-09-03 (their names without the extension were the same list as the SVGs').
3. The old folder was renamed to `openstax/osbooks-algebra-1/checkout.pre-mirror/`, and `./fetch.sh` made a
   new `checkout/` at the pin: the upstream failed, the mirror answered. `./apply.sh` overlaid the toolchain.
4. `bash tools/build-after-sync.sh <log dir> algebra-1` passed the image build, `make convert` and
   `make dist`: `algebra-1.pdf` (99 MB), `algebra-1.epub` (89 MB) and the HTML edition (159 pages).
5. The docs were brought up to date: the book's line in `tools/upstream-books-gone.txt`, its row and the
   summary in `tasks/reference/openstax/upstream-book-repositories.md` (from a fresh run of
   `tools/survey-upstream-books.py`, in which only that row changed), the "Outcome" section of the reference
   doc, the book's `CLAUDE.md` (the "do not delete `checkout/`" warning no longer held), the root `CLAUDE.md`,
   and the two tasks that pointed at this one.

## Not done, and left as found

- **`openstax/osbooks-algebra-1/checkout.pre-mirror/` (455 MB, untracked) was not deleted.** The agent's
  delete was refused by the session's permission check. Its source files were proved identical to the mirror
  and the rest is build output, so nothing in it is unique; removing it is the maintainer's call.
- The points under "Things to settle before the mirror is public" in the reference doc were the maintainer's;
  nothing was recorded about them beyond his having made the mirror public. The mirror does carry the
  upstream's `LICENSE` file.
- Which clone he pushed from (the Pi's or another) was not recorded.
