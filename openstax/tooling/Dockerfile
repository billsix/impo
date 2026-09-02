# Dockerfile -- SHARED build environment for the imps OpenStax LaTeX-port family.
# Book-agnostic: a per-book Makefile builds this image (context = ../tooling) and
# bind-mounts the fetched-and-overlaid book checkout at the fixed path /book.
# Fedora 44 + TeX Live (pdflatex/latexmk) with the font and latex collections
# the house design needs, plus Python (lxml) for the CNXML->LaTeX converter
# (tools/cnxml2tex) and pandoc for the HTML/EPUB web editions.
#
# Lean by design: no plotting notebooks, so it ships no ePiX / Jupyter / meson.

FROM registry.fedoraproject.org/fedora:44

# dnf cache idiom: keep downloaded packages in a build cache mount.
RUN --mount=type=cache,target=/var/cache/libdnf5 \
    --mount=type=cache,target=/var/lib/dnf \
    echo "keepcache=True" >> /etc/dnf/dnf.conf && \
    dnf upgrade -y && \
    dnf install -y \
        make \
        which \
        findutils \
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
        python3 \
        python3-lxml \
        python3-pytest \
        ruff \
        ty \
        pandoc && \
    dnf clean dbcache

# refresh the TeX filename database so newly installed packages are found
RUN mktexlsr

# rsvg-convert (this book ships SVG figures; pdflatex can't embed SVG, so the
# build converts them to PDF). In its own layer so the big TeX layer above stays
# cache-shared with the other bundles' identical images.
RUN --mount=type=cache,target=/var/cache/libdnf5 \
    --mount=type=cache,target=/var/lib/dnf \
    dnf install -y librsvg2-tools && dnf clean dbcache

# OpenStax house fonts for the LaTeX restyle: Roboto Slab (body serif). Noto Sans
# (headings) and STIX Two Math (texlive) are already present. Own layer so the
# big TeX layer above stays cache-shared with the other bundles.
RUN --mount=type=cache,target=/var/cache/libdnf5 \
    --mount=type=cache,target=/var/lib/dnf \
    dnf install -y google-roboto-slab-fonts && dnf clean dbcache && fc-cache -f

# entrypoint scripts
COPY entrypoint/shell.sh   /usr/local/bin/shell.sh
COPY entrypoint/pdf.sh     /usr/local/bin/pdf.sh
COPY entrypoint/convert.sh /usr/local/bin/convert.sh
COPY entrypoint/html.sh    /usr/local/bin/html.sh
COPY entrypoint/epub.sh    /usr/local/bin/epub.sh
COPY entrypoint/format.sh  /usr/local/bin/format.sh
RUN chmod +x /usr/local/bin/shell.sh /usr/local/bin/pdf.sh /usr/local/bin/convert.sh \
        /usr/local/bin/html.sh /usr/local/bin/epub.sh \
        /usr/local/bin/format.sh

# --- converter type-check + unit-test gate (HARD: any failure aborts the build) ---
# ty must pass clean over tools/ and the pytest suite must be green, or
# `podman build` (hence every `make pdf/html/epub`) fails. Copy only tools/ +
# pyproject.toml so this layer's cache invalidates just when they change; at
# runtime the Makefile bind-mounts the live repo over these, so the COPYed copies
# are used ONLY for this gate. `ty check tools/` (directory form) covers whatever
# .py the repo ships and resolves the tests via [tool.ty.environment] in
# pyproject.toml -- identical across all bundles.
COPY pyproject.toml /book/pyproject.toml
COPY tools /book/tools
RUN cd /book && \
    ty check tools/ && \
    python3 -m pytest tools/tests -q

WORKDIR /book
