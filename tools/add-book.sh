#!/bin/bash
# Add an OpenStax book repository to impo: create openstax/osbooks-<name>/ from the
# templates in tools/book-template/, pinned at the upstream default-branch head.
#
#   bash tools/add-book.sh <name> "<Title>"     # e.g. statistics "Statistics"
#
# <name> is the repository name without the osbooks- prefix; <Title> is the book's (or
# the bundle's) title as it should read in the folder's README and CLAUDE.md. Refuses a
# folder that already exists. The licence written into the README is read from the
# upstream LICENSE file. Afterwards: ./fetch.sh && ./apply.sh && make dist in the new
# folder, then fill in "The books this folder builds" in its CLAUDE.md.
set -euo pipefail
cd "$(dirname "$0")/.." # tools/ -> repo root

[ "$#" -eq 2 ] || {
    echo 'usage: tools/add-book.sh <name> "<Title>"' >&2
    exit 2
}
short="${1#osbooks-}"
name="osbooks-$short"
title="$2"
folder="${ADD_BOOK_OUTPUT:-openstax}/$name"
template=tools/book-template
upstream="https://github.com/openstax/$name"

[ ! -e "$folder" ] || {
    echo "add-book.sh: $folder already exists." >&2
    exit 1
}
# With ADD_BOOK_PIN set (used to compare the templates with an existing folder) the
# upstream is not asked.
pin="${ADD_BOOK_PIN:-$(GIT_TERMINAL_PROMPT=0 git ls-remote "$upstream" HEAD | cut -f1)}"
[ -n "$pin" ] || {
    echo "add-book.sh: $upstream did not answer." >&2
    exit 1
}
branch="$(GIT_TERMINAL_PROMPT=0 git ls-remote --symref "$upstream" HEAD | sed -n 's|^ref: refs/heads/\(.*\)\tHEAD$|\1|p')"
licence_text="$(curl -fsS -A generic-client "https://raw.githubusercontent.com/openstax/$name/${branch:-main}/LICENSE")" || licence_text=""
# The first non-blank line names the licence; some LICENSE files start with a blank line
# or carry Windows line endings.
first_line="$(printf '%s\n' "$licence_text" | tr -d '\r' | sed -n '/[^[:space:]]/{s/^[[:space:]]*//;s/[[:space:]]*$//;p;q;}')"
case "$first_line" in
"Attribution-NonCommercial-ShareAlike 4.0 International") licence="CC BY-NC-SA 4.0" ;;
"Attribution 4.0 International") licence="CC BY 4.0" ;;
*) licence="the licence in its LICENSE file" ;;
esac

mkdir -p "$folder"
for file in fetch.sh apply.sh Makefile README.md CLAUDE.md gitignore; do
    target="$folder/$file"
    [ "$file" = gitignore ] && target="$folder/.gitignore"
    sed -e "s|@NAME@|$name|g" -e "s|@SHORT@|$short|g" -e "s|@TITLE@|$title|g" \
        -e "s|@PIN@|$pin|g" -e "s|@DATE@|$(date +%F)|g" -e "s|@LICENCE@|$licence|g" \
        "$template/$file" >"$target"
done
chmod +x "$folder/fetch.sh" "$folder/apply.sh"
bash -n "$folder/fetch.sh"
bash -n "$folder/apply.sh"
echo "add-book.sh: created $folder (pin $pin, $licence)."
echo "             next: cd $folder && ./fetch.sh && ./apply.sh && make dist"
