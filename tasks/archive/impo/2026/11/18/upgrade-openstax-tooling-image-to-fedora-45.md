# Upgrade the OpenStax tooling image from Fedora 44 to Fedora 45 (done)

**Done:** 2026-11-18 (William Emerison Six <billsix@gmail.com>)

`openstax/tooling/Dockerfile` (the shared image every `openstax/osbooks-*` port builds) moved from
`FROM registry.fedoraproject.org/fedora:44` to `fedora:45`. Its header comment and
`openstax/CLAUDE.md` now say Fedora 45. No book Makefile names a Fedora version, so this one change
covers every book.

**A breakage found on the way, which predated the upgrade:** the image no longer built on Fedora 44
either. ty comes from dnf, and a Fedora 44 update (ty 0.0.99) renamed the rule
`unresolved-import` to `import-not-found`. The four `# ty: ignore[unresolved-import]` comments
(`tools/cnxml2tex/convert.py`, `tools/cnxml2tex/fetch_exercises.py`, `tools/tests/test_helpers.py`,
`tools/tests/test_mathml.py`) then raised `renamed-rule-in-ignore-comment`, and the
`check-tools.sh` step in the image build failed. They were renamed in their own commit, before the
upgrade. ty is a dnf package here, so a future rename can break the build the same way.

Verified nested on 2026-11-18 with `osbooks-introduction-python-programming` (the smallest
checkout), building first on Fedora 44 (after the ty fix) and then on 45:

| | Fedora 44 | Fedora 45 |
| --- | --- | --- |
| `make image` / `make test` / `make dist` | pass | pass |
| ty, TeX Live | 0.0.99, 20260301-111 | 0.0.99, 20260301-113 |
| PDF | 268 pages, 6,685,662 bytes | 268 pages, 6,685,662 bytes |

The PDF text (`pdftotext`) and the multipage HTML were identical. The EPUB differed only in its
per-build `dc:identifier` UUID and timestamps. Both runs used the checkout's existing converted
LaTeX and its existing `tools/` copy (from an earlier `apply.sh`), so the comparison isolates the
base image. The lean `WITH_TEXLIVE=0` image was not built separately; its packages are a subset of
the full image's base layer, which resolved.
