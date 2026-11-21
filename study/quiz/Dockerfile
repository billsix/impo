# Dockerfile -- build and gate environment for the quiz server (Go, standard
# library only): Fedora 45 + the golang toolchain. The source is bind-mounted
# at /impo/study/quiz by the Makefile, so this image holds no code.
FROM registry.fedoraproject.org/fedora:45

RUN --mount=type=cache,target=/var/cache/libdnf5 \
    --mount=type=cache,target=/var/lib/dnf \
    dnf install -y golang && \
    dnf clean dbcache

ENV GOPATH=/tmp/go GOCACHE=/tmp/go-cache GOTOOLCHAIN=local
WORKDIR /impo/study/quiz
