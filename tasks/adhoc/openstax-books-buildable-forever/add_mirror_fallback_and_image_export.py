"""Give every OpenStax book a mirror fallback in fetch.sh and image export targets in its Makefile.

fetch.sh: the comment that named the maintainer's Pi clone as a manual fallback is replaced, a
MIRROR_URL is added beside UPSTREAM_URL, and the fetch tries upstream first and the mirror second.
Makefile (the OpenStax books and the Trench book): `image-export` and `image-import` targets are
added before `clean:` and listed in .PHONY.

Idempotent: a file that already has the change is left alone, and a second run changes nothing.

    python3 tasks/adhoc/openstax-books-buildable-forever/add_mirror_fallback_and_image_export.py
"""

import pathlib
import re

ROOT: pathlib.Path = pathlib.Path(__file__).resolve().parents[3]

# The comment block is worded two ways across the books; both end with the same line.
OLD_COMMENT: re.Pattern[str] = re.compile(
    r"# Canonical upstream[^\n]*\n(?:#[^\n]*\n)*?"
    r"# is the fallback if GitHub is ever unreachable\.\n"
    r"UPSTREAM_URL=(https://github\.com/openstax/(\S+))\n"
)
NEW_HEAD: str = """# Canonical upstream; the pin is a commit on OpenStax's main history and is
# fetchable there by SHA. If the upstream does not answer or no longer has the
# pin, the fetch falls back to the maintainer's public mirror of the same
# repository (an unmodified copy, upstream's licence and history intact).
UPSTREAM_URL={upstream}
MIRROR_URL=https://github.com/billsix/{name}
"""
OLD_FETCH: str = """    git remote add origin "$UPSTREAM_URL"
    # Fetch just the pinned commit (GitHub allows fetching a reachable SHA).
    git fetch --depth 1 origin "$PIN_SHA"
    git checkout -q FETCH_HEAD
)
"""
NEW_FETCH: str = """    git remote add origin "$UPSTREAM_URL"
    git remote add mirror "$MIRROR_URL"
    # Fetch just the pinned commit (GitHub allows fetching a reachable SHA):
    # upstream first, then the mirror. GIT_TERMINAL_PROMPT=0 makes a repository
    # that is gone fail at once instead of asking for a user name.
    if ! GIT_TERMINAL_PROMPT=0 git fetch --depth 1 origin "$PIN_SHA"; then
        echo "fetch.sh: upstream did not provide $PIN_SHA — trying the mirror $MIRROR_URL ..." >&2
        if ! GIT_TERMINAL_PROMPT=0 git fetch --depth 1 mirror "$PIN_SHA"; then
            echo "fetch.sh: neither the upstream nor the mirror has $PIN_SHA." >&2
            exit 1
        fi
    fi
    git checkout -q FETCH_HEAD
) || {
    # Leave no half-made repository behind: the guard above treats a checkout
    # with a .git as already fetched.
    rm -rf "$CHECKOUT/.git"
    exit 1
}
"""
EXPORT_TARGETS: str = """image-export: ## Save the built image to a timestamped tar here (the toolchain, kept for offline builds)
	$(CONTAINER_CMD) save $(CONTAINER_NAME) -o $(CONTAINER_NAME)-$(shell date +%m-%d-%Y_%H-%M-%S).tar

image-import: ## Load an image tar: make image-import FILE=foo.tar
	@test -n "$(FILE)" || { echo 'usage: make image-import FILE=foo.tar' >&2; exit 1; }
	$(CONTAINER_CMD) load -i $(FILE)

"""


def update_fetch(path: pathlib.Path) -> str:
    """Add the mirror fallback to one fetch.sh; return what happened."""
    text: str = path.read_text()
    if "MIRROR_URL=" in text:
        return "current"
    found: re.Match[str] | None = OLD_COMMENT.search(text)
    if found is None or text.count(OLD_FETCH) != 1:
        return "NOT RECOGNISED"
    text = text[: found.start()] + NEW_HEAD.format(upstream=found.group(1), name=found.group(2)) + text[found.end() :]
    path.write_text(text.replace(OLD_FETCH, NEW_FETCH))
    return "updated"


def update_makefile(path: pathlib.Path) -> str:
    """Add image-export and image-import to one Makefile; return what happened."""
    text: str = path.read_text()
    if "image-export:" in text:
        return "current"
    if text.count("\nclean:") != 1 or text.count(".PHONY: ") != 1 or "$(CONTAINER_CMD)" not in text:
        return "NOT RECOGNISED"
    text = text.replace("\nclean:", "\n" + EXPORT_TARGETS + "clean:")
    path.write_text(text.replace(".PHONY: ", ".PHONY: image-export image-import ", 1))
    return "updated"


def main() -> None:
    """Update every book folder and report one line per file."""
    for folder in sorted(ROOT.glob("openstax/osbooks-*")):
        print(f"{folder.name}: fetch.sh {update_fetch(folder / 'fetch.sh')}, Makefile {update_makefile(folder / 'Makefile')}")
    for folder in sorted(ROOT.glob("trench/*")):
        if (folder / "Makefile").exists():
            print(f"{folder.name}: Makefile {update_makefile(folder / 'Makefile')}")


if __name__ == "__main__":
    main()
