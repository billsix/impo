# Makefile -- the study/ family: literacy tests, cliff notes and problem
# notebooks, built in podman containers like the book folders.
#
# The image is the shared OpenStax toolchain image (TeX Live, pandoc, the house
# class osbook.cls), built from ../openstax/tooling and tagged
# osbook-study-base, plus sympy (./Dockerfile). The whole impo checkout is
# mounted at /impo (the generators read ../openstax/tooling for the house class
# and the cross-book index); outputs land in study/output/ (gitignored).
#
#   make literacy-tests   output/literacy/<subject>{,-key,-scoring}.pdf
#   make cliff-notes      output/cliff-notes/<subject>.pdf
#   make bank             regenerate bank/json/ (the quiz server's committed copy)
#   make problem-notebooks BOOK=prealgebra-2e   output/notebooks/<book>/, executed
#   make test             the gate: lint, types, annotations, pytest, every answer checked

.DEFAULT_GOAL := help

CONTAINER_CMD ?= $(shell command -v podman >/dev/null 2>&1 && echo podman || echo docker)
IMAGE = impo-study
BASE_IMAGE = osbook-study-base
NOTEBOOK_IMAGE = impo-study-notebooks
BOOK ?= prealgebra-2e

# Extra flags for every container `run` (never `build`); --cgroups=disabled when
# nested in a runClaude/runCrush sandbox (NESTED_PODMAN=1), empty on a host.
PODMAN_RUN_FLAGS ?= $(if $(filter 1,$(NESTED_PODMAN)),--cgroups=disabled)

# :z (shared label), not :Z, because the whole checkout is mounted.
RUN = $(CONTAINER_CMD) run --rm $(PODMAN_RUN_FLAGS) \
	-v "$(shell cd .. && pwd)":/impo:z -w /impo/study --entrypoint /bin/bash $(IMAGE)

NB_RUN = $(CONTAINER_CMD) run --rm $(PODMAN_RUN_FLAGS) \
	-v "$(shell cd .. && pwd)":/impo:z -w /impo/study --entrypoint /bin/bash $(NOTEBOOK_IMAGE)

.PHONY: help image notebook-image literacy-tests cliff-notes bank problem-notebooks \
	test format shell update-pins clean

help: ## Show this help
	@grep -E '^[a-zA-Z0-9_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
	  awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-18s\033[0m %s\n", $$1, $$2}'

image: ## Build the study image (the OpenStax toolchain image + sympy)
	$(CONTAINER_CMD) build -t $(BASE_IMAGE) ../openstax/tooling
	$(CONTAINER_CMD) build --build-arg BASE=localhost/$(BASE_IMAGE):latest -t $(IMAGE) .

notebook-image: image ## Build the problem-notebook image (study image + Jupyter + ePiX)
	$(CONTAINER_CMD) build --build-arg BASE=localhost/$(IMAGE):latest -t $(NOTEBOOK_IMAGE) notebooks

problem-notebooks: notebook-image ## (container) one executed notebook per section of BOOK -> output/notebooks/BOOK/
	$(NB_RUN) entrypoint/build-notebooks.sh $(BOOK) $(SECTIONS)

update-pins: ## Re-resolve notebooks/constraints.txt from notebooks/requirements.in (needs uv; network)
	cd notebooks && uv pip compile requirements.in -o constraints.txt --python-version 3.15 \
		--custom-compile-command "make -C study update-pins"

literacy-tests: image ## (container) the four literacy tests, keys and scoring sheets -> output/literacy/
	$(RUN) entrypoint/build-pdfs.sh literacy

cliff-notes: image ## (container) the four cliff-notes guides -> output/cliff-notes/
	$(RUN) entrypoint/build-pdfs.sh cliff-notes

bank: image ## (container) regenerate bank/json/<subject>.json from bank/<subject>.toml
	$(RUN) -c 'python3 tools/bank.py export'

test: image ## (container) the gate: ruff, annotations, ty, pytest, every answer checked
	$(RUN) entrypoint/check.sh

format: image ## (container) ruff --fix + ruff format over tools/ and tests/
	$(RUN) -c 'ruff check --fix tools tests; ruff format tools tests'

shell: image ## Interactive shell in the study image
	$(CONTAINER_CMD) run -it --rm $(PODMAN_RUN_FLAGS) \
		-v "$(shell cd .. && pwd)":/impo:z -w /impo/study $(IMAGE) /bin/bash

clean: ## Remove output/
	rm -rf output
