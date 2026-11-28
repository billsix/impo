# Every build refreshes the toolchain overlay (the stale-checkout trap is closed)

**Done 2026-11-28** (agent. Raised 2026-09-19 after the same failure happened three times; go-ahead from
William Emerison Six <billsix@gmail.com>, 2026-11-28: "for those three tasks you mention, make a branch,
temporarily turn gpg signing off, do them in the order you'd like").

## What was wrong

A book's build reads the **checkout copy** of the toolchain (`osbook.cls`, `tools/cnxml2tex/convert.py`,
`tools/pandoc/osbook-web.css` and `.js`), which `apply.sh` copies in from `openstax/tooling/`. The build
targets did not run `apply.sh`, so after a toolchain edit `make html` used the copy from the last manual
`./apply.sh`. Three fixes looked broken on a rebuild for that reason: the About-This-Edition colophon in
the PDF, the colophon in the web editions, and the mobile CSS and JavaScript fix.

## What changed

- **Each book's `Makefile` runs `./apply.sh` before every build.** A rule for the stamp
  `checkout/.applied` runs `./apply.sh` each time `make` is invoked (it depends on a `FORCE` target). The
  converted LaTeX (`checkout/latex/.converted`) depends on the stamp, and `pdf`, `html`, `html-single` and
  `epub` depend on the converted LaTeX, so all of them refresh the overlay first. `shell`, `format`, `test`
  and `fetch-exercises` depend on the stamp directly. `make apply` runs the step alone.
- **`apply.sh` copies only what differs**, and touches `checkout/.applied` only when it copied something
  (or the stamp is missing). An unchanged toolchain therefore forces no reconvert, which a plain
  "always copy, always drop the convert stamp" step would have done on every build. The comparison is
  `diff -rq` from the toolchain to the checkout; files that exist only in the checkout (Python caches,
  `exercises/media-derived/`) are not a difference. `apply.sh` no longer deletes
  `checkout/latex/.converted`: the dependency on the stamp replaces that.
- **Fan-out:** the two files are written once in `tools/book-template/` and filled into all 45
  `openstax/osbooks-*/` folders by `tasks/adhoc/openstax-build-refresh-overlay/regenerate_from_template.py`
  (deleted with the archive commit; rerunning it from the pre-change template changed one file, the
  Anatomy `apply.sh`, whose comment said the book has no exercises and which lacked the exercise-cache
  block the other 44 have; the block does nothing there, since the folder has no `exercises/`).
- **Trench:** `trench/elementary-differential-equations/Makefile` has an `apply` target and `make pdf`
  depends on it. Only the PDF uses the overlay there (the house class and the shim); the web editions do
  not, and that book's `apply.sh` is three plain copies, left as it was.

## Why this option

The task offered (A) build targets depend on an apply step, or (B) mount the live toolchain over the
checkout copies. (A) was chosen as the task recommended: it keeps the checkout self-contained and needs
no new mounts. (B) would shadow the checkout's `tools/` in the container and leave the copies in the
checkout stale for anything read outside the container.

One detail differs from the task's sketch of (A). A phony `apply` prerequisite whose script deletes the
convert stamp would not work: GNU make reads a target's modification time before it updates that
target's prerequisites, so a stamp removed by a prerequisite's recipe is still seen as present. A stamp
file that `apply.sh` touches only on change, behind a rule that always runs, gives make a dependency it
checks after the recipe.

## Verification (2026-11-28, `openstax/osbooks-business-ethics`)

1. `make html` with the new files: reconverted once (the stamp was new).
2. `make html` again: `apply.sh: overlay already current.`, no reconvert.
3. Appended a marker comment to `openstax/tooling/tools/pandoc/osbook-web.css`, then `make html` with no
   manual apply: `apply.sh: refreshed checkout/tools`, and the marker was in
   `checkout/output/osbook-web.css` and `checkout/output/business-ethics/osbook-web.css`.
4. Reverted the marker, `make html`: the marker was gone from the output.

`./apply.sh` run twice in `osbooks-principles-finance` and `osbooks-prealgebra-bundle` (both carry an
exercise cache; the checkout holds derived images the cache does not) reported "already current" the
second time. `make -n pdf` in the trench folder lists `./apply.sh` before the build. The toolchain gate
(`make -C openstax/tooling type-check`) passes. The other 44 folders were not rebuilt for this change;
their two files are the same text as the tested folder's apart from the name.

## Recorded

`openstax/CLAUDE.md` ("Per-book folder contract", `apply.sh`; "The shared toolchain", "Changing the toolchain"),
`tasks/reference/tooling/web-editions-mobile.md` ("PROPAGATION"), each book folder's `CLAUDE.md`
("Changing the toolchain"), `tools/book-template/`, and the trench book's `CLAUDE.md`.

## Related

- `tasks/archive/impo/2026/09/20/openstax-html-mobile-verify.md` (the mobile fix the trap hid).
- `tasks/archive/impo/2026/09/19/openstax-about-this-edition-colophon.md` (the colophon; its partial fix,
  `apply.sh` dropping the convert stamp, covered only the converter and is superseded here).
