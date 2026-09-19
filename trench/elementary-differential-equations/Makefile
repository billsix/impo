# Makefile -- Trench "Elementary Differential Equations", restyled to the OpenStax
# house style (impo, trench family). Thin, per the impo family contract: the
# shared toolchain image is built from ../../openstax/tooling, and this book's
# source + shim are mounted into it at /book. Unlike the OpenStax books, the
# source is native LaTeX (no CNXML converter) -- see the task doc
# tasks/add-trench-differential-equations-book.md.
#
# First run:  ./fetch.sh && ./apply.sh && make pdf   (pdf needs phases 2-3)
#
# STATUS: Phase 1 scaffold. `image`/`shell`/`clean`/`help` work now; `figures`
# and `pdf` are honest stubs that fail until phases 2-3/5 land.

.DEFAULT_GOAL := help

CONTAINER_CMD ?= $(shell command -v podman >/dev/null 2>&1 && echo podman || echo docker)
CONTAINER_NAME = trench-elementary-differential-equations

TOOLING  = ../../openstax/tooling
CHECKOUT = checkout

# Auto-set nested (--cgroups=disabled) under NESTED_PODMAN=1; empty on a normal
# host. On `run` lines only, never `build` (podman build rejects --cgroups).
PODMAN_RUN_FLAGS ?= $(if $(filter 1,$(NESTED_PODMAN)),--cgroups=disabled)

# Mount the fetched+applied checkout at the fixed path /book. (The OpenStax
# CNXML entrypoint scripts are NOT mounted -- trench uses its own build steps,
# added in phases 2-3, not the convert/pdf entrypoints.) The shared web-theme
# assets (osbook-web.css/.js + build_nav.py) are mounted READ-ONLY straight from
# openstax/tooling/tools/pandoc so the HTML/EPUB restyle reads the single source
# of truth -- no vendored copy in this book, no drift. (A committed repo symlink
# into the sibling openstax/ tree can't resolve here: the two projects are
# separate container mounts, so a build-time RO mount is the working equivalent.)
FILES_TO_MOUNT = -v "$(shell pwd)/$(CHECKOUT)":/book/:Z \
	-v "$(shell pwd)/tools":/toolsrc:Z \
	-v "$(abspath $(TOOLING))/tools/pandoc":/osbook-assets:ro,Z

# impo provenance for the web/EPUB "About This Edition" colophon (web_preprocess.py
# reads IMPO_COMMIT / IMPO_BUILD_DATE from the env; the impo .git isn't mounted in the
# build container, so the SHA must come from the host here). See
# ../../tasks/openstax-about-this-edition-colophon.md.
IMPO_COMMIT ?= $(shell git rev-parse HEAD 2>/dev/null)
IMPO_BUILD_DATE ?= $(shell date +%Y-%m-%d)
IMPO_PROVENANCE = -e IMPO_COMMIT="$(IMPO_COMMIT)" -e IMPO_BUILD_DATE="$(IMPO_BUILD_DATE)"

RUN = $(CONTAINER_CMD) run --rm $(PODMAN_RUN_FLAGS) $(IMPO_PROVENANCE) $(FILES_TO_MOUNT) \
	--entrypoint /bin/bash $(CONTAINER_NAME)

.PHONY: image check-tools shell normalize figures pdf html epub clean help

# Gate for THIS book's tools/*.py. The shared image bakes a ty+pytest gate over
# openstax/tooling's OWN tools, but this book's tools are mounted at /toolsrc at
# runtime and aren't in that set -- so gate them here. Runs ruff (lint) + ty
# (types) in the image, discovering tools/pyproject.toml (mounted at /toolsrc).
# Any failure aborts, so a dirty tool fails `make image` -> pdf/html/epub.
CHECK_TOOLS = $(CONTAINER_CMD) run --rm $(PODMAN_RUN_FLAGS) \
	-v "$(shell pwd)/tools":/toolsrc:Z --entrypoint /bin/bash $(CONTAINER_NAME) \
	-c 'cd /toolsrc && ruff check *.py && ty check *.py'

image: ## Build the shared toolchain image (from ../../openstax/tooling) + gate this book's tools
	$(CONTAINER_CMD) build -t $(CONTAINER_NAME) $(TOOLING)
	$(CHECK_TOOLS)

check-tools: ## Re-run the tools gate (ruff + ty) without rebuilding the image
	$(CHECK_TOOLS)

normalize: ## PHASE 2: Trench master -> checkout/TRENCH_DIFFEQ-osbook.tex (pure python, no image)
	IMPO_COMMIT="$(shell git rev-parse HEAD 2>/dev/null)" \
		IMPO_BUILD_DATE="$(shell date +%Y-%m-%d)" \
		python3 tools/normalize_master.py

shell: image ## Interactive shell in the build container (book mounted at /book)
	$(CONTAINER_CMD) run -it --rm $(PODMAN_RUN_FLAGS) $(FILES_TO_MOUNT) \
		$(CONTAINER_NAME) /bin/bash

figures: image ## PHASE 3: convert EPS/*.eps -> checkout/EPS-pdf/*.pdf (epstopdf, in-container)
	$(RUN) -c 'cd /book && bash /toolsrc/eps2pdf.sh EPS EPS-pdf'

pdf: image normalize figures ## Typeset the osbook-styled PDF -> checkout/output/TRENCH_DIFFEQ-osbook.pdf
	$(RUN) -c 'cd /book && latexmk -pdflua -interaction=nonstopmode -outdir=output TRENCH_DIFFEQ-osbook.tex'

# The web editions take a SEPARATE path from the PDF: tools/build_web.sh feeds the
# PRISTINE master (TRENCH_DIFFEQ.tex) through tools/web_preprocess.py into a
# make4ht/tex4ebook-ready bookW.tex, with math as native MathML. They reuse the
# phase-3 figures (EPS-pdf/, from `figures`), rasterized to PNG by build_web.sh
# (tex4ht embeds PNG, not PDF). They do NOT use normalize_master.py or osbook.cls.
html: image figures ## Build the HTML web edition -> checkout/output/html/bookW.html
	$(RUN) -c 'cd /book && bash /toolsrc/build_web.sh html'

epub: image figures ## Build the EPUB web edition -> checkout/output/epub/bookW.epub
	$(RUN) -c 'cd /book && bash /toolsrc/build_web.sh epub'

clean: ## Remove build artifacts (checkout/output)
	rm -rf $(CHECKOUT)/output/*

help: ## Show this help
	@grep --extended-regexp '^[a-zA-Z0-9_-]+:.*?## .*$$' $(MAKEFILE_LIST) \
		| awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'
