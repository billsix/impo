# Step 0: wrote the scaffold tool for new book folders (`tools/add-book.sh`)

**Done 2026-11-26** (agent; part of `tasks/openstax-add-remaining-english-books.md`, approved by William Emerison Six <billsix@gmail.com> the same day).

## What it was for

Twenty-nine more OpenStax repositories are to be added to impo. Made by hand they would be twenty-nine slightly different folders, so the folders are generated from one set of templates.

## What was built

- **`tools/add-book.sh <name> "<Title>"`** creates `openstax/osbooks-<name>/` from `tools/book-template/` (`fetch.sh`, `apply.sh`, `Makefile`, `README.md`, `CLAUDE.md`, `.gitignore`). It refuses an existing folder, reads the upstream default-branch head with `git ls-remote` and pins it, reads the licence from the upstream `LICENSE` file for the README, keeps the executable bits, and runs `bash -n` on the scripts it wrote.
- **The templates** were taken from `openstax/osbooks-psychology/`. `apply.sh` and the `Makefile` are that folder's with the name replaced. `fetch.sh` has a new comment above the pin (the upstream head when the book was added, not a port branch's merge-base). `README.md` and `CLAUDE.md` were rewritten for a book with no port history, with a "The books this folder builds" section to fill in after the first build.
- The September generator (`tasks/adhoc/openstax-populate-books/scaffold.sh`, in history at commit `a54a8bf`) was read but not reused: it wrote neither the mirror fallback nor the image export targets.

## Proof

- **No drift from the existing folders.** `ADD_BOOK_OUTPUT=<scratch> ADD_BOOK_PIN=<psychology's pin> bash tools/add-book.sh psychology "Psychology 2e"` produced an `apply.sh` and a `Makefile` identical to the real ones, and a `fetch.sh` differing only in the four comment lines above the pin.
- **Used for a real book.** `bash tools/add-book.sh statistics "Statistics"` created the folder from which Statistics was fetched, converted and built in all three formats (`tasks/archive/impo/2026/11/26/openstax-add-book-statistics.md`).

## Found on the way

- A first version read the licence with `curl | head -1` under `set -o pipefail`; `head` closing the pipe made `curl` fail and the licence fell back to a generic phrase. It now reads the file into a variable first.
- The sixteen existing READMEs still said the content was "© OpenStax, CC BY 4.0", missed by the licence corrections earlier that day. They now give each book's own licence, in the same wording as the template.

## Docs

"Adding a book" in `openstax/CLAUDE.md` was rewritten around the tool (it had described pinning at the `latex` merge-base); `CLAUDE.md` lists the tool.
