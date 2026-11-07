# impo root Makefile — build the books in one call, the way modelviewprojection's
# `make docs` builds its book: every format (PDF, HTML web edition, EPUB), collected
# into output/ at the repo root. The per-book work stays in each book folder's own
# Makefile (`make dist`); this file only fans out and collects, via
# tools/build-books.sh.
#
#   make books                  every book folder -> output/
#   make anatomy-physiology     one folder (any name from `make list-books`)
#   make list-books             the folder names this accepts

.DEFAULT_GOAL := help

# Book folder names: openstax/osbooks-<name> (listed without the osbooks- prefix)
# and trench/<name>. Derived from the tree, so a new book folder needs no edit here.
OPENSTAX_BOOKS := $(patsubst openstax/osbooks-%/Makefile,%,$(wildcard openstax/osbooks-*/Makefile))
TRENCH_BOOKS   := $(patsubst trench/%/Makefile,%,$(wildcard trench/*/Makefile))
BOOKS          := $(OPENSTAX_BOOKS) $(TRENCH_BOOKS)

.PHONY: help books list-books clean-output $(BOOKS)

help: ## Show this help
	@grep -E '^[a-zA-Z0-9_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
	  awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-22s\033[0m %s\n", $$1, $$2}'
	@echo "  <book>                 build one book folder -> output/ (names: make list-books)"

books: ## Build every book (PDF + HTML + EPUB) into output/ — the one-call build
	bash tools/build-books.sh

$(BOOKS):
	bash tools/build-books.sh $@

list-books: ## List the book folder names `make <book>` accepts
	@printf '%s\n' $(BOOKS)

clean-output: ## Remove the collected output/ tree (book folders' own outputs are kept)
	rm -rf output
