# Dockerfile -- the problem-notebook image: the study image (TeX Live, pandoc,
# osbook.cls, sympy; ../Dockerfile) plus Jupyter (nbconvert/nbclient/ipykernel),
# jupytext and ePiX, the maintainer's C++ figure library
# (github.com/billsix/epix-mirror), built from source at EPIX_COMMIT with its
# Python front-end, the way github.com/billsix/geometricalgebra's image builds it.
#
# Every Python package goes into /venv with uv, pinned by constraints.txt (also
# the ones Fedora ships), so the notebooks' kernel and the jupyter scripts all
# run the venv's copies.
ARG BASE=localhost/impo-study:latest
FROM ${BASE}

# The commit of epix-mirror to build (the same pin as geometricalgebra's image).
ARG EPIX_COMMIT=5f7a8c29f86c26dcc9fc1670cc99b0b32878a399

COPY entrypoint/install-epix-deps.sh entrypoint/install-epix.sh /usr/local/bin/
RUN --mount=type=cache,target=/var/cache/libdnf5 \
    --mount=type=cache,target=/var/lib/dnf \
    dnf install -y uv && \
    /usr/local/bin/install-epix-deps.sh && \
    dnf clean dbcache

ENV UV_LINK_MODE=copy
COPY requirements.in constraints.txt /opt/notebooks/
RUN --mount=type=cache,target=/root/.cache/uv \
    uv venv /venv && \
    uv pip install --python /venv/bin/python -c /opt/notebooks/constraints.txt \
        -r /opt/notebooks/requirements.in && \
    /venv/bin/python -m ipykernel install --sys-prefix --name python3

RUN --mount=type=cache,target=/root/.cache/uv \
    CONSTRAINTS=/opt/notebooks/constraints.txt EPIX_COMMIT="$EPIX_COMMIT" \
    /usr/local/bin/install-epix.sh

ENV PATH=/venv/bin:$PATH
WORKDIR /impo/study
