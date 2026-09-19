# Stop the stale-checkout trap: make the build refresh the toolchain overlay

**Status:** proposed — needs go-ahead. Raised 2026-09-19 after the SAME failure mode bit three times.
**Priority:** 4 (recurring, wastes a build + a phone/desktop check each time)
**Difficulty:** 3

## BLUF

An OpenStax (or trench) build serves the book's **checkout copy** of the toolchain — `osbook.cls`,
`tools/cnxml2tex/convert.py`, `tools/pandoc/osbook-web.css`/`.js` — which `apply.sh` copies in from
`../tooling/`. `make convert/pdf/html/epub` do **not** re-run `apply.sh`, so after any toolchain edit the
build silently uses the STALE checkout copy until someone remembers `./apply.sh`. This has now caused
three "the fix isn't there" surprises (the About-This-Edition colophon in the PDF, the colophon in the
web editions, and the mobile CSS/JS fix — each looked broken on a rebuild that had actually copied
pre-fix assets). Fix it so a toolchain edit **can't** fail to reach the build. "Done" = editing a shared
asset then running `make html` (no manual `apply.sh`) produces output with the edit.

## Why it happens (verified 2026-09-19)

- OpenStax `entrypoint/html.sh:61,68` copy `$ROOT/tools/pandoc/osbook-web.css|.js` where `$ROOT=/book`
  (the checkout). `pdf.sh`/`convert.sh` likewise use the checkout's `osbook.cls`/`convert.py`. The
  Makefile mounts only the checkout at `/book` (+ entrypoint scripts live); it does NOT mount
  `../tooling/tools/` live.
- `apply.sh` is the only thing that refreshes `checkout/tools/`, `checkout/latex/*.cls`, etc. — and it's a
  manual host step. So `make html` after a `../tooling/` edit, without `apply.sh`, uses last-apply's copy.
- Symptom seen: college-algebra's `output/.../osbook-web.css` had `box-sizing=0` right after a fresh
  `make html`, because the checkout's copy predated the mobile fix. `./apply.sh && make html` fixed it.
- (The earlier `apply.sh` change that drops `checkout/latex/.converted` only forces a *reconvert*; it does
  nothing for the always-copied web assets or `osbook.cls`, so it doesn't cover this.)

## Options

- **(A) Build targets depend on an `apply` step (recommended).** Add a `.PHONY: apply` that runs
  `./apply.sh`, and make `convert`/`pdf`/`html`/`epub` (and their `.converted` stamp) depend on it.
  `apply.sh` is idempotent + cheap (`cp -R`), so re-running per build is fine. One small edit per book
  Makefile (16) + the trench Makefile. Pros: simplest mental model ("build always uses current
  toolchain"); no container-mount changes. Cons: an extra `cp` sweep per build (sub-second).
- **(B) Mount the live toolchain over the checkout copies.** Add `-v .../tooling/tools:/book/tools:ro`
  (and the `latex/*.cls`) to `FILES_TO_MOUNT`, like the entrypoint scripts already are, so the container
  reads live `../tooling/` assets and `apply.sh` becomes unnecessary for propagation. Pros: no per-build
  cp; edits are instantly live. Cons: shadows the checkout's `tools/` wholesale (also the converter),
  which muddies the "checkout is self-contained" model; `:Z`/SELinux + read-only nuances; bigger change.
- **(C) Do nothing, document harder.** Rejected — three misses shows documentation isn't enough.

**Recommendation: (A)** — make the overlay a build prerequisite. It matches the maintainer's existing
"apply = overlay the toolchain" model, just automatically, and is a mechanical fan-out (a codemod like the
recent Makefile ones).

## Plan (if A)
1. Add to each `openstax/osbooks-*/Makefile` (codemod, idempotent): `apply: ; ./apply.sh` (`.PHONY`), and
   add `apply` as a prerequisite of `convert`/`html`/`epub`/`pdf` (or of the `.converted` stamp + the
   html/epub/pdf targets). Mind that `apply.sh` runs on the HOST (it's a host script), so it's a normal
   recipe line, not a container `RUN`.
2. Same for `trench/elementary-differential-equations/Makefile` (its `apply.sh` overlays osbook.cls + the
   shim; `normalize`/`figures`/`pdf`/`html`/`epub` should depend on it).
3. Verify: edit a shared asset, run `make html` (no manual apply), confirm the output has the edit; run
   twice to confirm idempotent + no needless rebuild churn.

## Related
- `tasks/openstax-html-mobile-verify.md` (the mobile fix this trap hid).
- `tasks/archive/impo/2026/09/19/openstax-about-this-edition-colophon.md` (the colophon, hit by the same
  trap; its partial fix — apply.sh dropping `.converted` — only covers the converter).
