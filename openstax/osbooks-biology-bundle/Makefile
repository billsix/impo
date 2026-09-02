# Makefile -- OpenStax Biology (bundle) LaTeX port (imps).
#
# Thin, per the imps OpenStax family contract (../CLAUDE.md): the shared
# toolchain lives in ../tooling/. The container image is built from
# ../tooling/Dockerfile (context ../tooling) and every target runs it against the
# fetched-and-overlaid book checkout, bind-mounted at the fixed path /book.
#
# First run:  ./fetch.sh && ./apply.sh && make dist

.DEFAULT_GOAL := help

CONTAINER_CMD  = podman
CONTAINER_NAME = osbooks-biology-bundle

TOOLING  = ../tooling
CHECKOUT = checkout

# Extra flags for every container `run`. Auto-set when running nested inside a
# runClaudeInContainer/runCrushInContainer sandbox (which exports NESTED_PODMAN=1,
# making --cgroups=disabled apply so podman-in-podman works); empty -- and
# byte-identical behavior -- on a normal host. Overridable:
#   make dist PODMAN_RUN_FLAGS='--cgroups=disabled --network=host'
# On `run` lines only, never `build` (podman build rejects --cgroups).
PODMAN_RUN_FLAGS ?= $(if $(filter 1,$(NESTED_PODMAN)),--cgroups=disabled)

# Mount the book checkout at /book, plus the shared entrypoint scripts over
# /usr/local/bin so a toolchain edit takes effect without an image rebuild
# (html-single.sh and fetch-exercises.sh are NOT baked into the image, so they
# rely on these mounts). :Z relabels for SELinux.
FILES_TO_MOUNT = \
	-v "$(shell pwd)/$(CHECKOUT)":/book/:Z \
	-v "$(shell pwd)/$(TOOLING)/entrypoint/shell.sh":/usr/local/bin/shell.sh:Z \
	-v "$(shell pwd)/$(TOOLING)/entrypoint/pdf.sh":/usr/local/bin/pdf.sh:Z \
	-v "$(shell pwd)/$(TOOLING)/entrypoint/convert.sh":/usr/local/bin/convert.sh:Z \
	-v "$(shell pwd)/$(TOOLING)/entrypoint/html.sh":/usr/local/bin/html.sh:Z \
	-v "$(shell pwd)/$(TOOLING)/entrypoint/html-single.sh":/usr/local/bin/html-single.sh:Z \
	-v "$(shell pwd)/$(TOOLING)/entrypoint/epub.sh":/usr/local/bin/epub.sh:Z \
	-v "$(shell pwd)/$(TOOLING)/entrypoint/fetch-exercises.sh":/usr/local/bin/fetch-exercises.sh:Z \
	-v "$(shell pwd)/$(TOOLING)/entrypoint/format.sh":/usr/local/bin/format.sh:Z

RUN = $(CONTAINER_CMD) run --rm $(PODMAN_RUN_FLAGS) $(FILES_TO_MOUNT) \
	--entrypoint /bin/bash $(CONTAINER_NAME)

# Every CNXML input the converter reads; a change re-triggers convert. Guarded
# with 2>/dev/null so a pre-fetch `make` (no checkout/ yet) doesn't error.
CNXML_SOURCES := $(shell find $(CHECKOUT)/collections $(CHECKOUT)/modules -type f \
	\( -name '*.cnxml' -o -name '*.collection.xml' \) 2>/dev/null)

.PHONY: all image shell pdf convert html html-single epub dist fetch-exercises \
	format test clean help

all: image pdf ## Build the image and the collection PDF

dist: pdf epub html ## Build every output format (PDF, EPUB, HTML)

image: ## Build the shared toolchain image (context ../tooling)
	$(CONTAINER_CMD) build -t $(CONTAINER_NAME) $(TOOLING)

shell: image ## Interactive shell in the build container (book at /book)
	$(CONTAINER_CMD) run -it --rm $(PODMAN_RUN_FLAGS) $(FILES_TO_MOUNT) \
		$(CONTAINER_NAME) /usr/local/bin/shell.sh

pdf: image $(CHECKOUT)/latex/.converted ## Build the collection master PDF into checkout/output/
	$(RUN) /usr/local/bin/pdf.sh

# Stamp guarding the generated tex: reconvert only when a CNXML source (or the
# converter) is newer. Order-only '| image' builds the image first without
# coupling the stamp to the image's (phony) state.
$(CHECKOUT)/latex/.converted: $(CNXML_SOURCES) $(TOOLING)/tools/cnxml2tex/convert.py $(TOOLING)/entrypoint/convert.sh | image
	$(RUN) /usr/local/bin/convert.sh
	@touch $@

convert: $(CHECKOUT)/latex/.converted ## Regenerate the LaTeX masters/sections when the CNXML changed

html: image $(CHECKOUT)/latex/.converted ## Build the multipage HTML web edition -> checkout/output/<master>/
	$(RUN) /usr/local/bin/html.sh

html-single: image $(CHECKOUT)/latex/.converted ## Build the legacy single-file HTML -> checkout/output/<master>.html
	$(RUN) /usr/local/bin/html-single.sh

epub: image $(CHECKOUT)/latex/.converted ## Build the EPUB edition -> checkout/output/<master>.epub
	$(RUN) /usr/local/bin/epub.sh

fetch-exercises: image ## Download os-embed exercises (network; anatomy has none -> no-op)
	$(RUN) /usr/local/bin/fetch-exercises.sh

format: image ## (container) ruff --fix + ruff format + ty check over tools/*.py
	$(RUN) /usr/local/bin/format.sh

test: image ## (container) run the converter unit tests (pytest tools/tests)
	$(RUN) -c 'cd /book && python3 -m pytest tools/tests -q'

clean: ## Remove build artifacts (checkout/output and the convert stamp)
	rm -rf $(CHECKOUT)/output/* $(CHECKOUT)/latex/.converted

help: ## Show this help
	@grep --extended-regexp '^[a-zA-Z0-9_-]+:.*?## .*$$' $(MAKEFILE_LIST) \
		| awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'
