#!/usr/bin/env python3
r"""Add the impo-provenance env block to every OpenStax book Makefile (idempotent).

Part of tasks/openstax-about-this-edition-colophon.md. `convert.py` emits an
"About This Edition" colophon whose build commit SHA + date come from the
IMPO_COMMIT / IMPO_BUILD_DATE env vars. Those must be captured on the host (the
impo repo HEAD) and passed into the container. Every `openstax/osbooks-*/Makefile`
shares one identical `RUN = ...` line; this inserts the provenance vars before it
and threads `$(IMPO_PROVENANCE)` into it.

Idempotent: a Makefile that already defines IMPO_PROVENANCE is left untouched, so
re-running changes nothing (prove with a second run -> "0 changed").

Paths are relative to the repo root (git toplevel), never container-absolute.
Run from anywhere:  python3 tasks/adhoc/openstax-colophon/add_provenance_env.py
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

OLD_RUN: str = (
    "RUN = $(CONTAINER_CMD) run --rm $(PODMAN_RUN_FLAGS) $(FILES_TO_MOUNT) \\"
)
NEW_BLOCK: str = (
    "# impo provenance for the converter's \"About This Edition\" colophon: the impo repo\n"
    "# HEAD + build date, captured on the host and passed into the container (convert.py\n"
    "# reads IMPO_COMMIT / IMPO_BUILD_DATE from the env). See\n"
    "# ../../tasks/openstax-about-this-edition-colophon.md.\n"
    "IMPO_COMMIT ?= $(shell git rev-parse HEAD 2>/dev/null)\n"
    "IMPO_BUILD_DATE ?= $(shell date +%Y-%m-%d)\n"
    "IMPO_PROVENANCE = -e IMPO_COMMIT=\"$(IMPO_COMMIT)\" -e IMPO_BUILD_DATE=\"$(IMPO_BUILD_DATE)\"\n"
    "\n"
    "RUN = $(CONTAINER_CMD) run --rm $(PODMAN_RUN_FLAGS) $(IMPO_PROVENANCE) $(FILES_TO_MOUNT) \\"
)


def repo_root() -> Path:
    out: str = subprocess.check_output(
        ["git", "rev-parse", "--show-toplevel"], text=True
    ).strip()
    return Path(out)


def main() -> int:
    root: Path = repo_root()
    makefiles: list[Path] = sorted(root.glob("openstax/osbooks-*/Makefile"))
    if not makefiles:
        print("no openstax/osbooks-*/Makefile found", file=sys.stderr)
        return 1
    changed: int = 0
    for mf in makefiles:
        text: str = mf.read_text(encoding="utf-8")
        rel: str = mf.relative_to(root).as_posix()
        if "IMPO_PROVENANCE" in text:
            print(f"  skip (already done): {rel}")
            continue
        if OLD_RUN not in text:
            print(f"  WARN: RUN line not found, skipping: {rel}", file=sys.stderr)
            continue
        mf.write_text(text.replace(OLD_RUN, NEW_BLOCK, 1), encoding="utf-8")
        print(f"  updated: {rel}")
        changed += 1
    print(f"add_provenance_env: {changed} changed of {len(makefiles)} Makefiles")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
