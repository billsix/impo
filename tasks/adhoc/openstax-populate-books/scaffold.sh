#!/bin/bash
# Scaffold the remaining 15 OpenStax book folders under openstax/, on the
# verified anatomy-physiology pilot pattern. Idempotent: it overwrites the six
# generated per-book files (fetch.sh, apply.sh, Makefile, README.md, .gitignore,
# CLAUDE.md) each run, so re-running reproduces the same result from scratch.
#
# Run from the imps repo root:  bash tasks/adhoc/openstax-populate-books/scaffold.sh
#
# Each book's fetch.sh pins the FULL 40-char SHA for the short pin in the task
# table (resolved once, below); apply.sh is the GENERIC form of anatomy's (it
# also copies a committed exercises/ cache into checkout/ when one exists).
set -euo pipefail
cd "$(dirname "$0")/../../.."   # -> imps repo root
ROOT="$(pwd)"
OSDIR="$ROOT/openstax"

# name | full 40-char SHA (from `git -C /foo/opt/openstax/osbooks-<name> rev-parse <shortpin>`)
#      | delta-files (task table) | downloads note (task table)
BOOKS="
astronomy|2b24b8eeb45845d07ce63fb31e1e62627b3e860f|27|no downloads (toolchain-only)
chemistry-bundle|dba91045bc6db7c7286ca63f3a4e92075ec31025|27|no downloads (toolchain-only)
microbiology|ecf34dad129d686703780e87ab5aa2e59c577a6a|27|no downloads (toolchain-only)
psychology|398f50856ca1df97b58cb778659212a1df572bbd|27|no downloads (toolchain-only)
university-physics-bundle|a33cac5de6e771b213debf92265a1b14365ba46a|27|no downloads (toolchain-only)
college-algebra-bundle|789b54099106b071d1d32bfcee454fed72eb4768|46|small download cache
prealgebra-bundle|98074b2c4ca390e62af34d6a6d68fb21e7880fbe|48|small download cache
calculus-bundle|9b6c28b21c723a10ac045bad22b34377b3ff3f89|53|small download cache
writing-guide|7312ec11c4d7f95f2dc0565f9c52393903a4f677|209|some download content
introduction-python-programming|d215dd3b99c33db855c49315152ebd5fbadc8534|641|has os-embed exercises (downloads)
physics|cbf75cb4a18223a788868244be73affe932ef680|904|has os-embed exercises (downloads)
algebra-1|332f78647098a60532a9833b8003dca5da7ff227|1268|has os-embed exercises + SVG figures
biology-bundle|1e74a23833550e6bbe3aa3450c50c9ecb74f3a66|2723|has os-embed exercises (large cache)
contemporary-mathematics|2319ce22654c12c946a7faed3b135f4a2c6f613e|3692|has os-embed exercises (large cache)
organic-chemistry|2a1f82843a8b55cf0e185a3e0a295dd05c07c04e|4062|has os-embed exercises (large: ~2076 jpg + 1959 json)
"

# Human-readable book titles (for the doc headers). Kept minimal/factual.
title_of() {
  case "$1" in
    astronomy) echo "Astronomy 2e" ;;
    chemistry-bundle) echo "Chemistry (bundle)" ;;
    microbiology) echo "Microbiology" ;;
    psychology) echo "Psychology 2e" ;;
    university-physics-bundle) echo "University Physics (bundle)" ;;
    college-algebra-bundle) echo "College Algebra (bundle)" ;;
    prealgebra-bundle) echo "Prealgebra (bundle)" ;;
    calculus-bundle) echo "Calculus (bundle)" ;;
    writing-guide) echo "Writing Guide" ;;
    introduction-python-programming) echo "Introduction to Python Programming" ;;
    physics) echo "Physics" ;;
    algebra-1) echo "Algebra 1" ;;
    biology-bundle) echo "Biology (bundle)" ;;
    contemporary-mathematics) echo "Contemporary Mathematics" ;;
    organic-chemistry) echo "Organic Chemistry" ;;
    *) echo "$1" ;;
  esac
}

echo "$BOOKS" | while IFS='|' read -r name sha delta downloads; do
  [ -n "$name" ] || continue
  slug="osbooks-$name"
  title="$(title_of "$name")"
  dir="$OSDIR/$slug"
  mkdir -p "$dir"

  # --- fetch.sh ---------------------------------------------------------------
  cat > "$dir/fetch.sh" <<EOF
#!/bin/bash
# Fetch the pinned, pristine OpenStax content for $title into checkout/
# (gitignored). This is the OpenStax-owned layer (collections/ + modules/ +
# media/); the maintainer's toolchain is overlaid on top of it by apply.sh.
# Idempotent: an existing checkout/ is left untouched.
#
# Runnable from anywhere (cd to the script's own dir; only relative paths).
set -euo pipefail
cd "\$(dirname "\$0")"

# --- the pin -----------------------------------------------------------------
# The merge-base where the maintainer's \`latex\` port branch diverged from
# OpenStax's \`main\`, i.e. the pristine content the port was made against.
# Resolved from the short pin in tasks/openstax-populate-books.md (2026-09-02).
PIN_SHA=$sha

# Canonical upstream; the pin is a commit on OpenStax's main history and is
# fetchable there by SHA. The maintainer's Pi mirror
# (pi@192.168.0.186:/mnt/usbdrive2/gitRepos/openstax/**/$slug.git)
# is the fallback if GitHub is ever unreachable.
UPSTREAM_URL=https://github.com/openstax/$slug

CHECKOUT=checkout

if [ -e "\$CHECKOUT/.git" ]; then
    echo "fetch.sh: \$CHECKOUT/ already exists — leaving it untouched."
    echo "          (delete it and re-run to refetch at \$PIN_SHA)"
    exit 0
fi

echo "fetch.sh: fetching \$UPSTREAM_URL @ \$PIN_SHA -> \$CHECKOUT/ ..."
git init -q "\$CHECKOUT"
(
    cd "\$CHECKOUT"
    # Sandbox gitconfig enables commit signing, which fails here and would abort
    # any later git operation; disable it repo-locally (never globally).
    git config commit.gpgsign false
    git remote add origin "\$UPSTREAM_URL"
    # Fetch just the pinned commit (GitHub allows fetching a reachable SHA).
    git fetch --depth 1 origin "\$PIN_SHA"
    git checkout -q FETCH_HEAD
)
echo "fetch.sh: done. Next: ./apply.sh, then make dist."
EOF
  chmod +x "$dir/fetch.sh"

  # --- apply.sh (generic; overlays tooling + any committed exercises/) --------
  cat > "$dir/apply.sh" <<'EOF'
#!/bin/bash
# Apply = overlay the SHARED toolchain (../tooling/) onto the fetched pristine
# checkout/, so the toolchain's scripts find tools/, latex/ (the house .cls/.sty),
# and entrypoint/ sitting beside the OpenStax CNXML. This is the OpenStax family's
# form of "apply" (see ../CLAUDE.md): the delta is a shared file set, not a
# git-am patch series, so we copy rather than replay commits.
#
# Idempotent (plain overwrite) and guarded: run ./fetch.sh first.
#
# Runnable from anywhere (cd to the script's own dir; only relative paths).
set -euo pipefail
cd "$(dirname "$0")"

TOOLING=../tooling
CHECKOUT=checkout

[ -d "$CHECKOUT" ] || {
    echo "apply.sh: $CHECKOUT/ not found — run ./fetch.sh first." >&2
    exit 1
}
[ -d "$TOOLING" ] || {
    echo "apply.sh: $TOOLING/ not found — expected the shared toolchain beside this book." >&2
    exit 1
}

echo "apply.sh: overlaying $TOOLING/ onto $CHECKOUT/ ..."

# The converter + web-edition tools.
cp -R "$TOOLING/tools" "$CHECKOUT/"

# The container entrypoint scripts (the Makefile also bind-mounts these live, but
# overlaying them keeps the checkout self-describing).
cp -R "$TOOLING/entrypoint" "$CHECKOUT/"

# The house document class + style, beside the generated masters that \input them.
mkdir -p "$CHECKOUT/latex"
cp "$TOOLING/latex/osbook.cls" "$TOOLING/latex/osbook-envs.sty" \
   "$TOOLING/latex/osbook-defer.sty" "$CHECKOUT/latex/"

# Converter lint/type/test config (format.sh + test target read it).
cp "$TOOLING/pyproject.toml" "$CHECKOUT/"

# The COPYRIGHT template used by fetch_exercises for books that have exercises.
cp -R "$TOOLING/templates" "$CHECKOUT/"

# If this book carries a committed download cache (os-embed exercises), copy it
# in beside the CNXML so the build finds it offline. Books without exercises
# simply skip this (no exercises/ dir here).
if [ -d exercises ]; then
    echo "apply.sh: copying committed exercises/ cache into $CHECKOUT/ ..."
    cp -R exercises "$CHECKOUT/"
fi

echo "apply.sh: done. Next: make dist  (or make convert / make pdf)."
EOF
  chmod +x "$dir/apply.sh"

  # --- Makefile (anatomy's, CONTAINER_NAME swapped) ---------------------------
  # Generated by sed-substituting the pilot's Makefile so it stays byte-identical
  # except for CONTAINER_NAME and the header comment's book title.
  sed \
    -e "s/^CONTAINER_NAME = osbooks-anatomy-physiology\$/CONTAINER_NAME = $slug/" \
    -e "s/^# Makefile -- OpenStax Anatomy & Physiology 2e LaTeX port (imps pilot book)\.\$/# Makefile -- OpenStax $title LaTeX port (imps)./" \
    "$OSDIR/osbooks-anatomy-physiology/Makefile" > "$dir/Makefile"

  # --- README.md --------------------------------------------------------------
  cat > "$dir/README.md" <<EOF
# OpenStax $title — LaTeX port (imps)

A hand-owned LaTeX/PDF/EPUB/HTML port of OpenStax **$title**, built on pristine,
pinned OpenStax content with the shared toolchain in [\`../tooling/\`](../tooling).
Part of the imps OpenStax family — see [\`../CLAUDE.md\`](../CLAUDE.md) for the
family model and [\`CLAUDE.md\`](./CLAUDE.md) for this book's facts.

## Build

\`\`\`sh
./fetch.sh        # [HOST] clone pinned OpenStax content into checkout/  (gitignored)
./apply.sh        # [HOST] overlay ../tooling/ onto checkout/
make image        # build the shared toolchain container image once
make dist         # PDF + EPUB + chunked HTML  (the converter runs as needed)
\`\`\`

Individual formats:

\`\`\`sh
make convert      # regenerate the LaTeX masters/sections from the CNXML
make pdf          # typeset PDF   -> checkout/output/
make epub         # EPUB          -> checkout/output/
make html         # chunked HTML  -> checkout/output/
make help         # list all targets
\`\`\`

Nested podman: \`PODMAN_RUN_FLAGS\` auto-applies \`--cgroups=disabled\` inside a
\`NESTED_PODMAN=1\` sandbox and expands empty on a normal host.

## Content & license

The OpenStax content (\`collections/\`, \`modules/\`, \`media/\`) is fetched at a pin
into \`checkout/\` and is **not** part of this repository — it is © OpenStax, CC BY
4.0, sourced from <https://openstax.org>. Any committed \`exercises/\` download cache
is likewise © OpenStax, CC BY 4.0 (see its \`COPYRIGHT\`). The toolchain in
[\`../tooling/\`](../tooling) is the maintainer's, MIT (see the repo \`LICENSE\`).
Design details: [\`../CLAUDE.md\`](../CLAUDE.md).
EOF

  # --- .gitignore (identical to anatomy's) ------------------------------------
  cp "$OSDIR/osbooks-anatomy-physiology/.gitignore" "$dir/.gitignore"

  # --- CLAUDE.md (concise per-book; no fabricated book facts) -----------------
  cat > "$dir/CLAUDE.md" <<EOF
# $slug — OpenStax $title (imps)

An imps OpenStax-family book on the shared-toolchain contract. Read the family
doc [\`../CLAUDE.md\`](../CLAUDE.md) first (the fetch → apply-overlay → build model,
the content/copyright rules) and the shared toolchain it points at,
[\`../tooling/\`](../tooling). This file records only what is specific to *this book*.

## What lives here (thin per-book folder)

No OpenStax content and no toolchain are committed — both are pulled in on demand:

- \`fetch.sh\` — clones the pinned pristine OpenStax content into \`checkout/\` (gitignored).
- \`apply.sh\` — overlays \`../tooling/\` onto \`checkout/\` (and copies a committed
  \`exercises/\` cache in, if this book has one).
- \`Makefile\` — builds the image from \`../tooling/Dockerfile\` (context \`../tooling\`) and
  runs it against \`checkout/\` mounted at the fixed path \`/book\`.
- \`README.md\`, \`.gitignore\`.

## The pin

\`fetch.sh\` pins **\`$sha\`** — the merge-base where the
maintainer's \`latex\` port branch diverged from OpenStax's \`main\` (the pristine
content the port was made against), from the survey table in
\`tasks/openstax-populate-books.md\`. Canonical upstream:
\`https://github.com/openstax/$slug\`. Fallback mirror if GitHub is
unreachable: \`pi@192.168.0.186:/mnt/usbdrive2/gitRepos/openstax/**/$slug.git\`.

## This book (from the survey; build-time facts pending)

- **Delta size:** $delta port-branch files; **$downloads**
  (per the \`tasks/openstax-populate-books.md\` survey table).
- **Book specifics — single- vs multi-collection, subcollection nesting depth,
  whether \`os-embed\` exercises are actually present, and SVG vs raster figures —
  are verified on the first build**, not asserted here. The converter auto-detects
  collection structure and nesting; only the *downloaded* exercise images (not
  upstream \`media/\` figures) belong in a committed \`exercises/\` cache.

## Build

\`\`\`
./fetch.sh        # pristine OpenStax content -> checkout/  (idempotent)
./apply.sh        # overlay ../tooling/ onto checkout/      (idempotent)
make image        # build the shared toolchain image once
make dist         # PDF + EPUB + chunked HTML  (convert runs as needed)
\`\`\`

\`pdf\`/\`html\`/\`epub\` depend on the \`checkout/latex/.converted\` stamp, so the
converter auto-runs when the CNXML changed. Nested podman: \`PODMAN_RUN_FLAGS\`
auto-applies \`--cgroups=disabled\` under a \`NESTED_PODMAN=1\` sandbox, empty on a
normal host; threaded into every \`run\`, never \`build\`.

## Changing the toolchain

Edit \`../tooling/\` once (shared by every book), then re-run \`./apply.sh\` here to
pick it up. Do not edit the generated LaTeX or the overlaid copies inside
\`checkout/\` — a reconvert or a re-apply overwrites them.
EOF

  echo "scaffolded $slug (pin ${sha:0:10}, delta $delta)"
done
