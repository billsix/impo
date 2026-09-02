# OpenStax Anatomy & Physiology 2e — LaTeX port (imps)

A hand-owned LaTeX/PDF/EPUB/HTML port of OpenStax **Anatomy & Physiology 2e**, built on
pristine, pinned OpenStax content with the shared toolchain in [`../tooling/`](../tooling).
The pilot book for the imps OpenStax family — see [`../CLAUDE.md`](../CLAUDE.md) for the
family model and [`CLAUDE.md`](./CLAUDE.md) for this book's facts.

## Build

```sh
./fetch.sh        # [HOST] clone pinned OpenStax content into checkout/  (gitignored)
./apply.sh        # [HOST] overlay ../tooling/ onto checkout/
make image        # build the shared toolchain container image once
make dist         # PDF + EPUB + chunked HTML  (the converter runs as needed)
```

Individual formats:

```sh
make convert      # regenerate the LaTeX masters/sections from the CNXML
make pdf          # typeset PDF   -> checkout/output/anatomy-and-physiology-2e.pdf
make epub         # EPUB          -> checkout/output/anatomy-and-physiology-2e.epub
make html         # chunked HTML  -> checkout/output/anatomy-and-physiology-2e/
make help         # list all targets
```

Nested podman: `PODMAN_RUN_FLAGS` auto-applies `--cgroups=disabled` inside a
`NESTED_PODMAN=1` sandbox and expands empty on a normal host.

## Content & license

The OpenStax content (`collections/`, `modules/`, `media/`) is fetched at a pin into
`checkout/` and is **not** part of this repository — it is © OpenStax, CC BY 4.0, sourced
from <https://openstax.org>. The toolchain in `../tooling/` is the maintainer's, MIT (see the
repo `LICENSE`). Design details: [`../CLAUDE.md`](../CLAUDE.md).
