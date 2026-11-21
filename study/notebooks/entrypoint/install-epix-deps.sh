#!/usr/bin/env bash
#
# Copied from github.com/billsix/geometricalgebra (entrypoint/06-install-epix.sh), the
# maintainer's project whose image first built ePiX this way.
#
# install-epix-deps.sh -- the Fedora packages ePiX needs, both to build it from source
# (install-epix.sh) and to run it: ePiX is a C++ figure library whose `epix`/`elaps`
# drivers compile each figure source (.xp) with g++ at RUN time and typeset it with
# latex -> dvips -> ghostscript, so the compiler and the TeX stack are runtime
# dependencies, not just build ones. Run by study/notebooks/Dockerfile (the study
# gate image needs none of this). Host-runnable: run it, then install-epix.sh.
#
#   git                      fetch the pinned epix-mirror commit (install-epix.sh)
#   meson ninja-build        ePiX's build system
#   gcc-c++ binutils         compile libepix; g++ also compiles .xp figures at runtime
#   python3-devel            Python.h for the nanobind extension (install-epix.sh)
#   bash sed findutils which diffutils   the driver scripts + make_header
#   ghostscript              ps2epsi / ps2pdf: elaps' eps and pdf steps, eps->png
#   ImageMagick              `convert`: flix animations (eps->png->mng/gif)
#   texlive-*                the same set epix-mirror's own entrypoint/02-install-render.sh
#                            installs: latex + eepic + dvips/epstopdf + the PSTricks and
#                            TikZ (pgf) backends some figures emit. Mostly already in
#                            the study image's TeX Live (dnf treats the overlap as a
#                            no-op); listed in full so the script works on a bare host.
#
# A single dnf call, so its own exit status is the gate.
set -uo pipefail

if ! command -v dnf >/dev/null 2>&1; then
    echo "install-epix-deps.sh: needs 'dnf' (this installs Fedora packages), not found." >&2
    exit 1
fi

dnf install -y \
    git \
    meson ninja-build gcc-c++ binutils python3-devel \
    bash sed findutils which diffutils \
    ghostscript ImageMagick \
    texlive-collection-basic \
    texlive-collection-latexrecommended \
    texlive-collection-pictures \
    texlive-collection-fontsrecommended \
    texlive-eepic \
    texlive-epstopdf \
    texlive-dvips \
    texlive-collection-pstricks \
    texlive-pgf
