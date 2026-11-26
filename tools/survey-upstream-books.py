#!/usr/bin/env python3
"""Survey OpenStax's book repositories on GitHub and print them as a Markdown table.

Lists every public repository of the `openstax` organisation whose name starts with `osbooks`, and
for each one: the books it holds (the slugs in its `META-INF/books.xml`), the language its books
declare, the licence named on the first line of its `LICENSE` file, its size and last push, whether
impo builds it (a folder `openstax/<name>/` with a `fetch.sh`), whether impo could build it and does
not yet, and whether the maintainer's public backup exists (`https://github.com/billsix/<name>`
answers `git ls-remote`).

A book folder impo has whose repository is NOT in that list gets a row too, with "Upstream: gone",
where its source is still held, and the action needed.

Two small files hold what the survey cannot find out by itself, so it survives a refresh:

    tools/upstream-books-rejected.txt   repositories the maintainer decided not to build, and why
    tools/upstream-books-gone.txt       for a vanished upstream: when it was found gone, the state of
                                        the maintainer's private clone, and the action needed

Read-only and unauthenticated: a few GitHub API requests for the repository list, then raw file
requests and `git ls-remote`. The table in tasks/reference/openstax/upstream-book-repositories.md
is this script's output.

    python3 tools/survey-upstream-books.py > /tmp/table.md
"""

import concurrent.futures
import dataclasses
import json
import os
import pathlib
import re
import subprocess
import sys
import urllib.parse
import urllib.request

ROOT: pathlib.Path = pathlib.Path(__file__).resolve().parents[1]
ORGANISATION: str = "openstax"
MIRROR_OWNER: str = "billsix"
REJECTED_FILE: pathlib.Path = ROOT / "tools" / "upstream-books-rejected.txt"
GONE_FILE: pathlib.Path = ROOT / "tools" / "upstream-books-gone.txt"
CLIENT: dict[str, str] = {
    "User-Agent": "generic-client",
    "Accept": "application/vnd.github+json",
}
SHORT_LICENCE: dict[str, str] = {
    "Attribution-NonCommercial-ShareAlike 4.0 International": "CC BY-NC-SA 4.0",
    "Attribution 4.0 International": "CC BY 4.0",
    "http://creativecommons.org/licenses/by-nc-sa/4.0/": "CC BY-NC-SA 4.0",
    "http://creativecommons.org/licenses/by/4.0/": "CC BY 4.0",
}
LANGUAGE: re.Pattern[str] = re.compile(r"<md:language>([^<]+)</md:language>")
LICENCE_URL: re.Pattern[str] = re.compile(r'<md:license url="([^"]*)"')
COLUMNS: tuple[str, ...] = (
    "Repository",
    "Upstream",
    "Books (slugs)",
    "Language",
    "Licence",
    "Size",
    "Last push",
    "Built in impo",
    "Not yet in impo",
    "Backup at github.com/billsix",
    "Rejected",
    "Reason",
    "Source held",
    "Action needed",
)


@dataclasses.dataclass(frozen=True)
class Book:
    """One book repository and what was found about it."""

    name: str
    upstream: str
    slugs: list[str]
    languages: list[str]
    licence: str
    size: str
    pushed: str
    built_here: bool
    mirrored: bool
    rejected_reason: str
    source_held: str
    action: str

    @property
    def pending(self) -> bool:
        """True for a repository impo could build and does not: neither built nor rejected."""
        return not self.built_here and not self.rejected_reason

    def cells(self) -> tuple[str, ...]:
        """The row for the table, in COLUMNS order."""
        return (
            self.name,
            self.upstream,
            ", ".join(self.slugs) or "(none listed)",
            ", ".join(self.languages),
            self.licence,
            self.size,
            self.pushed,
            "yes" if self.built_here else "no",
            "yes" if self.pending else "",
            "yes" if self.mirrored else "no",
            "yes" if self.rejected_reason else "",
            self.rejected_reason,
            self.source_held,
            self.action,
        )


def fetch(url: str) -> str:
    """Return the body of a public URL, or '' when it cannot be read (a slug may be non-ASCII)."""
    try:
        request: urllib.request.Request = urllib.request.Request(
            urllib.parse.quote(url, safe=":/?=&%"), headers=CLIENT
        )
        with urllib.request.urlopen(request, timeout=60) as response:
            return response.read().decode("utf-8", errors="replace")
    except OSError:
        return ""


def repositories() -> list[dict[str, object]]:
    """Every public repository of the organisation whose name starts with osbooks."""
    found: list[dict[str, object]] = []
    page: int = 1
    while True:
        body: str = fetch(
            f"https://api.github.com/orgs/{ORGANISATION}/repos?per_page=100&page={page}&type=public"
        )
        batch: object = json.loads(body) if body else []
        if not isinstance(batch, list) or not batch:
            break
        found.extend(
            entry for entry in batch if str(entry["name"]).startswith("osbooks")
        )
        page += 1
    return sorted(found, key=lambda entry: str(entry["name"]))


def answers(url: str) -> bool:
    """True when a git repository answers at the URL without asking for credentials."""
    listed: subprocess.CompletedProcess[str] = subprocess.run(
        ["git", "ls-remote", url, "HEAD"],
        capture_output=True,
        text=True,
        env=dict(os.environ, GIT_TERMINAL_PROMPT="0"),
        check=False,
    )
    return listed.returncode == 0 and bool(listed.stdout.strip())


def rejections() -> dict[str, str]:
    """The repositories the maintainer decided not to build, with the reason for each."""
    reasons: dict[str, str] = {}
    for line in REJECTED_FILE.read_text().splitlines():
        if line.strip() and not line.startswith("#"):
            name, _, reason = line.partition(":")
            reasons[name.strip()] = reason.strip()
    return reasons


def gone_records() -> dict[str, dict[str, str]]:
    """What the maintainer recorded about each vanished upstream: `name | key: value | ...`."""
    records: dict[str, dict[str, str]] = {}
    for line in GONE_FILE.read_text().splitlines():
        if line.strip() and not line.startswith("#"):
            name, *fields = [part.strip() for part in line.split("|")]
            records[name] = {
                key.strip(): value.strip()
                for key, _, value in (field.partition(":") for field in fields)
            }
    return records


def survey(entry: dict[str, object], rejected: dict[str, str]) -> Book:
    """Read one upstream repository's books, languages and licence, and check impo and the backup."""
    name: str = str(entry["name"])
    raw: str = f"https://raw.githubusercontent.com/{ORGANISATION}/{name}/{entry['default_branch']}/"
    first_line: str = (fetch(raw + "LICENSE").splitlines() or [""])[0].strip()
    slugs: list[str] = re.findall(r'slug="([^"]+)"', fetch(raw + "META-INF/books.xml"))
    # The language each book declares in its collection XML (<md:language>).
    languages: set[str] = set()
    for slug in slugs:
        declared: re.Match[str] | None = LANGUAGE.search(
            fetch(raw + f"collections/{slug}.collection.xml")
        )
        languages.add(declared.group(1) if declared else "?")
    return Book(
        name=name,
        upstream="present",
        slugs=slugs,
        languages=sorted(languages),
        licence=SHORT_LICENCE.get(first_line, first_line or "no LICENSE file"),
        size=f"{round(int(str(entry['size'])) / 1024)} MB",
        pushed=str(entry["pushed_at"])[:10],
        built_here=(ROOT / "openstax" / name / "fetch.sh").exists(),
        mirrored=answers(f"https://github.com/{MIRROR_OWNER}/{name}"),
        rejected_reason=rejected.get(name, ""),
        source_held="",
        action="",
    )


def gone_book(folder: pathlib.Path, record: dict[str, str]) -> Book:
    """Describe a book impo builds whose upstream repository is no longer listed.

    Its books, language and licence are read from the collection XML in the local checkout, since
    there is no upstream to ask. "Source held" lists every place the source still exists.
    """
    collections: list[pathlib.Path] = sorted(
        (folder / "checkout" / "collections").glob("*.collection.xml")
    )
    texts: list[str] = [path.read_text(errors="replace") for path in collections]
    licence_urls: set[str] = {
        found.group(1) for text in texts if (found := LICENCE_URL.search(text))
    }
    mirrored: bool = answers(f"https://github.com/{MIRROR_OWNER}/{folder.name}")
    module_count: int = len(list((folder / "checkout" / "modules").glob("*")))
    held: list[str] = []
    if mirrored:
        held.append("public backup")
    held.append(f"private clone: {record.get('private-clone', 'not recorded')}")
    if module_count:
        has_commit: bool = (
            subprocess.run(
                [
                    "git",
                    "-C",
                    str(folder / "checkout"),
                    "rev-parse",
                    "--verify",
                    "--quiet",
                    "HEAD",
                ],
                capture_output=True,
                check=False,
            ).returncode
            == 0
        )
        history: str = "one commit" if has_commit else "no git history"
        held.append(f"files in the checkout ({module_count} modules, {history})")
    return Book(
        name=folder.name,
        upstream=f"gone (found {record.get('found-gone', 'date not recorded')})",
        slugs=[path.name[: -len(".collection.xml")] for path in collections],
        languages=sorted(
            {found.group(1) for text in texts if (found := LANGUAGE.search(text))}
        ),
        licence=", ".join(sorted(SHORT_LICENCE.get(url, url) for url in licence_urls))
        or "not declared",
        size="",
        pushed="",
        built_here=True,
        mirrored=mirrored,
        rejected_reason="",
        source_held="; ".join(held),
        action=record.get("action", f"record this book in tools/{GONE_FILE.name}"),
    )


def main() -> int:
    """Print the table: every upstream repository, then the books whose upstream is gone."""
    rejected: dict[str, str] = rejections()
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
        books: list[Book] = list(
            pool.map(lambda entry: survey(entry, rejected), repositories())
        )
    if not books:
        print(
            "no repositories found (GitHub API unreachable or rate-limited)",
            file=sys.stderr,
        )
        return 1
    upstream_names: set[str] = {book.name for book in books}
    records: dict[str, dict[str, str]] = gone_records()
    gone: list[Book] = [
        gone_book(folder, records.get(folder.name, {}))
        for folder in sorted((ROOT / "openstax").glob("osbooks-*"))
        if folder.name not in upstream_names and (folder / "fetch.sh").exists()
    ]
    print("| " + " | ".join(COLUMNS) + " |")
    print("|" + "---|" * len(COLUMNS))
    for book in sorted([*books, *gone], key=lambda entry: entry.name):
        print("| " + " | ".join(book.cells()) + " |")
    print(
        f"\n{len(books)} upstream repositories, {sum(len(book.slugs) for book in books)} books; "
        f"{sum(book.built_here for book in books)} built in impo, {sum(book.pending for book in books)} not yet "
        f"in impo, {sum(bool(book.rejected_reason) for book in books)} rejected; "
        f"{len(gone)} built in impo with the upstream gone; "
        f"{sum(book.mirrored for book in [*books, *gone])} backed up."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
