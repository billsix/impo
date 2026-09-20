# Dockerfile -- SHARED build environment for the imps OpenStax LaTeX-port family.
# Book-agnostic: a per-book Makefile builds this image (context = ../tooling) and
# bind-mounts the fetched-and-overlaid book checkout at the fixed path /book.
# Fedora 44 + TeX Live (pdflatex/latexmk) with the font and latex collections
# the house design needs, plus Python (lxml) for the CNXML->LaTeX converter
# (tools/cnxml2tex) and pandoc for the HTML/EPUB web editions.
#
# Lean by design: no plotting notebooks, so it ships no ePiX / Jupyter / meson.

FROM registry.fedoraproject.org/fedora:44

# Whether to install TeX Live + the book-output deps (SVG->PDF via rsvg, the
# Roboto Slab body font, EPUB zip/tidy). Default 1: the book builds
# (pdf/html/epub) need LaTeX. Set 0 for a LEAN image carrying only the
# converter + gate deps (python3-lxml, pandoc, ruff, ty, pytest) -- enough for
# the tooling type-check gate (entrypoint/check-tools.sh) and its CI
# (.github/workflows/checks.yml), which need no LaTeX. Mirrors
# modelviewprojection's BUILD_DOCS=0 lean-CI pattern (`make type-check`).
ARG WITH_TEXLIVE=1

# dnf cache idiom: keep downloaded packages in a build cache mount.
# BASE deps -- ALWAYS installed: the CNXML->LaTeX converter (python3-lxml), the
# HTML/EPUB leg (pandoc), and the Python gate tools (ruff, ty, pytest).
RUN --mount=type=cache,target=/var/cache/libdnf5 \
    --mount=type=cache,target=/var/lib/dnf \
    echo "keepcache=True" >> /etc/dnf/dnf.conf && \
    dnf upgrade -y && \
    dnf install -y \
        make \
        which \
        findutils \
        python3 \
        python3-lxml \
        python3-pytest \
        ruff \
        ty \
        pandoc && \
    dnf clean dbcache

# TeX Live + book-output deps (SVG->PDF via rsvg, the Roboto Slab body font --
# Noto Sans headings + STIX Two Math come with texlive -- and EPUB zip/tidy for
# the sibling trench/ family's make4ht/tex4ebook editions). Installed ONLY when
# WITH_TEXLIVE=1 (the default), so the lean gate image skips them. One
# conditional layer; with WITH_TEXLIVE=1 it is identical across every bundle, so
# it stays cache-shared. `mktexlsr` refreshes the TeX filename DB; `fc-cache -f`
# picks up the new font.
RUN --mount=type=cache,target=/var/cache/libdnf5 \
    --mount=type=cache,target=/var/lib/dnf \
    if [ "$WITH_TEXLIVE" = "1" ]; then \
        dnf install -y \
            latexmk \
            texlive-scheme-medium \
            texlive-collection-latexrecommended \
            texlive-collection-latexextra \
            texlive-collection-mathscience \
            texlive-collection-fontsrecommended \
            texlive-collection-fontsextra \
            texlive-memoir \
            texlive-baskervaldx \
            texlive-newtx \
            texlive-boondox \
            texlive-mathalpha \
            texlive-textgreek \
            texlive-mdframed \
            texlive-thmtools \
            texlive-ntheorem \
            texlive-answers \
            texlive-cleveref \
            texlive-subfiles \
            librsvg2-tools \
            google-roboto-slab-fonts \
            zip \
            tidy && \
        dnf clean dbcache && \
        mktexlsr && \
        fc-cache -f; \
    fi

# entrypoint scripts
COPY entrypoint/shell.sh   /usr/local/bin/shell.sh
COPY entrypoint/pdf.sh     /usr/local/bin/pdf.sh
COPY entrypoint/convert.sh /usr/local/bin/convert.sh
COPY entrypoint/html.sh    /usr/local/bin/html.sh
COPY entrypoint/epub.sh    /usr/local/bin/epub.sh
COPY entrypoint/format.sh  /usr/local/bin/format.sh
COPY entrypoint/check-tools.sh /usr/local/bin/check-tools.sh
RUN chmod +x /usr/local/bin/shell.sh /usr/local/bin/pdf.sh /usr/local/bin/convert.sh \
        /usr/local/bin/html.sh /usr/local/bin/epub.sh \
        /usr/local/bin/format.sh /usr/local/bin/check-tools.sh

# --- converter lint + type + annotation + unit-test gate (HARD: any failure aborts the build) ---
# The whole gate lives in entrypoint/check-tools.sh (ruff check + the
# local/global annotation checker + `ty check` + pytest), so the Dockerfile and
# the CI workflow run IDENTICAL checks. If any fails, `podman build` (hence every
# `make pdf/html/epub`) fails. Copy only tools/ + pyproject.toml so this layer's
# cache invalidates just when they change; at runtime the Makefile bind-mounts
# the live repo over these, so the COPYed copies are used ONLY for this gate.
# `ty check tools/` (directory form) covers whatever .py the repo ships and
# resolves the tests via [tool.ty.environment] in pyproject.toml -- identical
# across all bundles.
COPY pyproject.toml /book/pyproject.toml
COPY tools /book/tools
RUN cd /book && /usr/local/bin/check-tools.sh

WORKDIR /book
