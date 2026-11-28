#!/bin/bash
# Publish the collected web editions (output/<book>/, built by `make books` or
# `make <book>`) to impo's gh-pages branch, served by GitHub Pages at
# https://billsix.github.io/impo/<book>/ — the manual publish step behind
# `make publish-pages`, run by the maintainer on the host.
#
#   bash tools/publish-pages.sh                        # the books tools/pages-books.txt lists
#   BOOKS="prealgebra-2e algebra-1" bash tools/publish-pages.sh   # these books
#   BOOKS=all bash tools/publish-pages.sh              # every built book (over the limit)
#   DRY_RUN=1 bash tools/publish-pages.sh              # stage only, no push
#
# All the web editions together are several times the GitHub Pages limit, so the
# published set is a committed list, tools/pages-books.txt (one book per line;
# tools/web-edition-sizes.py --books tools/pages-books.txt measures it).
#
# Stages output/pages/ (every chosen output/<book>/ plus a landing index.html
# listing the books and their Release downloads), checks the staged size against
# the GitHub Pages limit (1 GB; PAGES_LIMIT_MB overrides), then runs
#   ghp-import --no-history --no-jekyll --force --push --remote $PAGES_REMOTE
# so gh-pages always holds ONE commit (a clone of impo does not grow with every
# publish). PAGES_REMOTE defaults to `github` (the github.com remote; origin is
# the maintainer's own box). Needs `ghp-import` on PATH (pip install ghp-import).
# The downloads (PDF/EPUB/zipped HTML) are GitHub Release assets, not on Pages.
set -u
cd "$(dirname "$0")/.." || exit 1          # tools/ -> repo root
OUT=output
STAGE="$OUT/pages"
LIMIT_MB="${PAGES_LIMIT_MB:-1000}"
REMOTE="${PAGES_REMOTE:-github}"
RELEASE="https://github.com/billsix/impo/releases/latest/download"

LIST=tools/pages-books.txt
if [ -z "${BOOKS:-}" ]; then
    # The committed list, without comments and blank lines.
    BOOKS="$(sed -e 's/#.*//' "$LIST" | tr -s ' \t\n' ' ')"
fi
books=()
if [ "$BOOKS" != all ]; then
    for b in $BOOKS; do
        [ -f "$OUT/$b/index.html" ] || { echo "not built: $OUT/$b/index.html (run make <folder>)" >&2; exit 2; }
        books+=("$b")
    done
else
    for d in "$OUT"/*/; do
        b=$(basename "$d")
        [ "$b" = pages ] || [ "$b" = logs ] && continue
        [ -f "$d/index.html" ] && books+=("$b")
    done
fi
[ "${#books[@]}" -gt 0 ] || { echo "no built books in $OUT/ (run make books)" >&2; exit 2; }

rm -rf "$STAGE" && mkdir -p "$STAGE"
for b in "${books[@]}"; do
    cp -rL "$OUT/$b" "$STAGE/$b"
done

# Landing page: one entry per book with its title and download links.
{
    cat <<'HTML'
<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>impo books</title>
<style>
body { font-family: Georgia, serif; max-width: 46rem; margin: 2rem auto; padding: 0 1rem;
  line-height: 1.5; color: #1a1a1a; background: #fff; }
h1 { color: #00507d; } li { margin: .5rem 0; } a { color: #00507d; }
.dl { font-size: .9rem; } footer { margin-top: 2rem; font-size: .85rem; color: #555; }
</style></head><body>
<h1>Open textbooks — LaTeX/HTML/EPUB editions</h1>
<p>Web editions of open textbooks, rebuilt from their pinned sources by
<a href="https://github.com/billsix/impo">impo</a>.</p>
<ul>
HTML
    for b in "${books[@]}"; do
        title=$(grep -m1 -oP '(?<=<title>)[^<]+' "$STAGE/$b/index.html" || echo "$b")
        printf '<li><a href="%s/index.html">%s</a> <span class="dl">(<a href="%s/%s.pdf">PDF</a>, <a href="%s/%s.epub">EPUB</a>, <a href="%s/%s-html.zip">HTML zip</a>)</span></li>\n' \
            "$b" "$title" "$RELEASE" "$b" "$RELEASE" "$b" "$RELEASE" "$b"
    done
    cat <<'HTML'
</ul>
<footer>The book content is © OpenStax and the respective authors (sourced from
<a href="https://openstax.org">openstax.org</a>), except <em>Elementary Differential
Equations</em> © William F. Trench, CC BY-NC-SA 3.0. Each book is under the Creative
Commons licence its own "About This Edition" page states, with its attribution. The conversion toolchain is MIT-licensed. Not affiliated
with or endorsed by OpenStax.</footer>
</body></html>
HTML
} > "$STAGE/index.html"

size_mb=$(( $(du -sk "$STAGE" | cut -f1) / 1024 ))
echo "staged ${#books[@]} book(s) in $STAGE: ${size_mb} MB (limit ${LIMIT_MB} MB)"
if [ "$size_mb" -gt "$LIMIT_MB" ]; then
    echo "over the GitHub Pages size limit; per book (MB):" >&2
    for b in "${books[@]}"; do echo "  $(( $(du -sk "$STAGE/$b" | cut -f1) / 1024 ))  $b" >&2; done
    echo "publish fewer books: BOOKS=\"...\" or $LIST (see tasks/reference/openstax/publishing.md)" >&2
    exit 1
fi

if [ -n "${DRY_RUN:-}" ]; then
    echo "DRY_RUN: not pushing; open $STAGE/index.html to check"
    exit 0
fi
command -v ghp-import >/dev/null 2>&1 || { echo "ghp-import not found (pip install ghp-import)" >&2; exit 1; }
ghp-import --no-history --no-jekyll --force --push --remote "$REMOTE" --branch gh-pages \
    -m "Publish ${#books[@]} book web edition(s) from impo $(git rev-parse --short HEAD)" "$STAGE"
