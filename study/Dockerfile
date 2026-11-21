# Dockerfile -- the study/ family image: the shared OpenStax toolchain image
# (Fedora 45 + TeX Live + pandoc + the house LaTeX class; built from
# ../openstax/tooling by `make image` and tagged osbook-study-base) plus sympy,
# which checks every answer in the question bank and the cliff notes.
ARG BASE=localhost/osbook-study-base:latest
FROM ${BASE}

RUN --mount=type=cache,target=/var/cache/libdnf5 \
    --mount=type=cache,target=/var/lib/dnf \
    dnf install -y python3-sympy && \
    dnf clean dbcache

WORKDIR /impo/study
