# Makefile -- the SHARED OpenStax toolchain (openstax/tooling/).
#
# The per-book Makefiles (../osbooks-*/Makefile) build this same Dockerfile to
# produce/run book PDFs/HTML/EPUB. This Makefile is for the toolchain ITSELF:
# the lint/type/annotation/test GATE over tools/*.py, plus a shell into the
# image. Modeled on github.com/billsix/modelviewprojection's `make type-check`
# (CI is a thin wrapper over `make`; all logic lives in the Makefile/Dockerfile
# and entrypoint/check-tools.sh, so CI and the image can't drift).
#
# The gate needs no LaTeX, so it builds a LEAN image (WITH_TEXLIVE=0) -- the
# analogue of mvp's BUILD_DOCS=0 CI image.

.DEFAULT_GOAL := help

CONTAINER_CMD ?= $(shell command -v podman >/dev/null 2>&1 && echo podman || echo docker)
IMAGE = osbook-tooling

# 0 = lean image (converter + gate deps only, no TeX Live) -- the default here,
# since every target in this Makefile is a gate/shell that needs no LaTeX. The
# book Makefiles leave it at the Dockerfile default of 1.
WITH_TEXLIVE ?= 0

# Extra flags for every container `run` (never `build`). Auto-set to
# --cgroups=disabled when nested inside a runClaude/runCrush sandbox
# (NESTED_PODMAN=1); empty on a normal host. Overridable.
PODMAN_RUN_FLAGS ?= $(if $(filter 1,$(NESTED_PODMAN)),--cgroups=disabled)

# shell and shell-exec share this run block so they cannot drift (mvp's
# SHELL_RUN_FLAGS convention). The live tools/ + pyproject.toml are bind-mounted
# over the image's baked copies at /book, so a tooling edit is checked WITHOUT an
# image rebuild. :Z relabels for SELinux (matches the book Makefiles' mounts).
SHELL_RUN_FLAGS = $(PODMAN_RUN_FLAGS) --rm --entrypoint /bin/bash \
	-v "$(shell pwd)/tools":/book/tools:Z \
	-v "$(shell pwd)/pyproject.toml":/book/pyproject.toml:Z \
	$(IMAGE)

.PHONY: image type-check check shell shell-exec help

image: ## Build the (lean) toolchain image; WITH_TEXLIVE=1 for the full book image
	$(CONTAINER_CMD) build --build-arg WITH_TEXLIVE=$(WITH_TEXLIVE) -t $(IMAGE) .

type-check: image ## (container) the full tooling gate: ruff + annotation checker + ty + pytest
	$(CONTAINER_CMD) run $(SHELL_RUN_FLAGS) -c 'cd /book && /usr/local/bin/check-tools.sh'

check: type-check ## Alias for type-check

shell: image ## Interactive shell in the toolchain image (tooling mounted at /book)
	$(CONTAINER_CMD) run -it $(SHELL_RUN_FLAGS) -c 'cd /book && exec bash'

shell-exec: image ## Batch twin of shell (no TTY): make shell-exec CMD='...'
	@[ -n "$(CMD)" ] || { echo 'usage: make shell-exec CMD="<command>"'; exit 2; }
	$(CONTAINER_CMD) run $(SHELL_RUN_FLAGS) -c 'cd /book && $(CMD)'

help: ## Show this help
	@grep --extended-regexp '^[a-zA-Z0-9_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "} {printf "\033[36m%-16s\033[0m %s\n", $$1, $$2}'
