"""Make each OpenStax book's CLAUDE.md name the pin its fetch.sh carries.

A book's CLAUDE.md states the pin in its "The pin" section. When that hash differs from PIN_SHA in
the book's fetch.sh, rewrite the sentence so the current pin leads and the original port base is
kept as history. Idempotent: a second run changes nothing.

    python3 tasks/adhoc/openstax-sync-upstream-pins-2026-11/sync_pin_docs.py
"""

import pathlib
import re

ROOT: pathlib.Path = pathlib.Path(__file__).resolve().parents[3]
ORIGINAL: re.Pattern[str] = re.compile(r"`fetch\.sh` pins \*\*`([0-9a-f]{40})`\*\* — the merge-base where the\n")
CURRENT: re.Pattern[str] = re.compile(r"`fetch\.sh` pins \*\*`([0-9a-f]{40})`\*\*, the head of OpenStax's default branch")
PIN: re.Pattern[str] = re.compile(r"^PIN_SHA=([0-9a-f]{40})", re.MULTILINE)


def main() -> None:
    """Rewrite every book doc whose stated pin is stale and report one line per book."""
    for doc in sorted(ROOT.glob("openstax/osbooks-*/CLAUDE.md")):
        pin_match: re.Match[str] | None = PIN.search((doc.parent / "fetch.sh").read_text())
        assert pin_match is not None, doc
        pin: str = pin_match.group(1)
        text: str = doc.read_text()
        original: re.Match[str] | None = ORIGINAL.search(text)
        current: re.Match[str] | None = CURRENT.search(text)
        if original is not None and original.group(1) != pin:
            lead: str = (
                f"`fetch.sh` pins **`{pin}`**, the head of OpenStax's default branch\n"
                "at the last sync (the pin moves at every sync; `fetch.sh` is the source of truth).\n"
                f"The port was first made against `{original.group(1)}` — the merge-base where the\n"
            )
            doc.write_text(text[: original.start()] + lead + text[original.end() :])
            print(f"{doc.parent.name}: rewritten")
        elif current is not None and current.group(1) != pin:
            doc.write_text(text[: current.start(1)] + pin + text[current.end(1) :])
            print(f"{doc.parent.name}: pin updated")
        elif original is None and current is None:
            print(f"{doc.parent.name}: NO PIN SENTENCE FOUND")
        else:
            print(f"{doc.parent.name}: current")


if __name__ == "__main__":
    main()
