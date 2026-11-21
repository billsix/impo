# Makefile -- the quiz server (study/quiz/): a Go standard-library web app that
# serves timed multiple-choice quizzes from the literacy-test question bank.
# Builds and gates run in a small Fedora + golang image (./Dockerfile); the
# study/ directory is mounted so `bank` can copy ../bank/json/*.json in.
#
#   make test     gofmt check + go vet + go test (the gate)
#   make build    ./quiz, a static binary with the banks embedded
#   make run      serve on port $(PORT) from the container (set QUIZ_ADMIN_PASSWORD)

.DEFAULT_GOAL := help

CONTAINER_CMD ?= $(shell command -v podman >/dev/null 2>&1 && echo podman || echo docker)
IMAGE = impo-quiz
PORT ?= 8080
PODMAN_RUN_FLAGS ?= $(if $(filter 1,$(NESTED_PODMAN)),--cgroups=disabled)

RUN = $(CONTAINER_CMD) run --rm $(PODMAN_RUN_FLAGS) \
	-v "$(shell cd .. && pwd)":/impo/study:z -w /impo/study/quiz $(IMAGE)

.PHONY: help image bank test format build run clean

help: ## Show this help
	@grep -E '^[a-zA-Z0-9_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
	  awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-10s\033[0m %s\n", $$1, $$2}'

image: ## Build the Go image
	$(CONTAINER_CMD) build -t $(IMAGE) .

bank: ## Copy the generated question banks (../bank/json/) in, for embedding
	cp ../bank/json/*.json bank/

test: image bank ## (container) the gate: gofmt -l (must be empty), go vet, go test
	$(RUN) bash -c 'status=0; out=$$(gofmt -l .); [ -z "$$out" ] || { echo "gofmt: $$out"; status=1; }; go vet ./... || status=1; go test ./... || status=1; exit $$status'

format: image ## (container) gofmt -w
	$(RUN) gofmt -w .

build: image bank ## (container) build ./quiz with the banks embedded
	$(RUN) env CGO_ENABLED=0 go build -o quiz .

run: image bank ## (container) serve on port $(PORT); results in ./data; set QUIZ_ADMIN_PASSWORD
	$(CONTAINER_CMD) run -it --rm $(PODMAN_RUN_FLAGS) -p $(PORT):8080 \
		-e QUIZ_ADMIN_PASSWORD -v "$(shell cd .. && pwd)":/impo/study:z -w /impo/study/quiz \
		$(IMAGE) go run . -addr :8080 -data data

clean: ## Remove the binary and the copied banks (keeps data/)
	rm -f quiz bank/*.json
