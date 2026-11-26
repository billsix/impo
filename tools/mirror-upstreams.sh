#!/bin/bash
# Keep the maintainer's public mirrors of the OpenStax book repositories current, so a
# book's pinned source stays fetchable when its upstream is gone (fetch.sh falls back to
# the mirror). One mirror per book folder, named like its upstream:
# https://github.com/billsix/<name>, an UNMODIFIED copy with upstream's history and
# LICENSE file. Never commit to a mirror.
#
#   bash tools/mirror-upstreams.sh check              # which mirrors exist and hold their book's pin
#   bash tools/mirror-upstreams.sh push [<book> ...]  # [HOST] update the local clones, push to the mirrors
#
# `check` needs no credentials and runs anywhere. `push` needs push access to the mirrors,
# so it is the maintainer's, on a machine with his GitHub credentials. Book names are
# given without the osbooks- prefix; none means every book.
#
# Environment for `push`:
#   MIRROR_DIR   where the local full-history clones live (default: ~/openstax-mirrors).
#                A clone already there is reused, so a repository whose upstream is gone
#                (algebra-1) can be mirrored from a copy placed there by hand.
#   BUNDLE_DIR   if set, also write <name>.bundle there (every ref, full history): an
#                offline second copy that does not depend on GitHub.
#   CREATE=1     create a missing mirror repository with `gh repo create` (needs gh).
set -u
cd "$(dirname "$0")/.." || exit 1 # tools/ -> repo root

mode="${1:-}"
[ "$#" -gt 0 ] && shift
case "$mode" in
check | push) ;;
*)
    echo "usage: tools/mirror-upstreams.sh check | push [<book> ...]" >&2
    exit 2
    ;;
esac

folders=()
if [ "$#" -ge 1 ]; then
    for name in "$@"; do
        folders+=("openstax/osbooks-${name#osbooks-}")
    done
else
    for folder in openstax/osbooks-*/; do
        folders+=("${folder%/}")
    done
fi

status=0
for folder in "${folders[@]}"; do
    name="$(basename "$folder")"
    [ -f "$folder/fetch.sh" ] || {
        echo "$name: no fetch.sh"
        status=1
        continue
    }
    upstream="$(sed -n 's/^UPSTREAM_URL=//p' "$folder/fetch.sh")"
    mirror="$(sed -n 's/^MIRROR_URL=//p' "$folder/fetch.sh")"
    pin="$(sed -n 's/^PIN_SHA=//p' "$folder/fetch.sh")"

    if [ "$mode" = push ]; then
        clone="${MIRROR_DIR:-$HOME/openstax-mirrors}/$name.git"
        if [ ! -d "$clone" ]; then
            mkdir -p "$(dirname "$clone")"
            GIT_TERMINAL_PROMPT=0 git clone --quiet --mirror "$upstream" "$clone" || {
                echo "$name: upstream gone and no clone at $clone — put a full clone there and re-run"
                status=1
                continue
            }
        elif ! GIT_TERMINAL_PROMPT=0 git -C "$clone" fetch --quiet "$upstream" '+refs/heads/*:refs/heads/*' '+refs/tags/*:refs/tags/*'; then
            echo "$name: upstream did not answer; pushing the clone as it is"
        fi
        if ! git -C "$clone" cat-file -e "$pin^{commit}" 2>/dev/null; then
            echo "$name: the clone at $clone does not contain the pin $pin — not pushed"
            status=1
            continue
        fi
        if [ "${CREATE:-0}" = 1 ] && ! GIT_TERMINAL_PROMPT=0 git ls-remote "$mirror" >/dev/null 2>&1; then
            gh repo create "${mirror#https://github.com/}" --public \
                --description "Unmodified mirror of ${upstream#https://github.com/}; see its LICENSE" || status=1
        fi
        # Branches and tags only: GitHub refuses pushes to its own refs/pull/*.
        if git -C "$clone" push --quiet "$mirror" '+refs/heads/*:refs/heads/*' '+refs/tags/*:refs/tags/*'; then
            echo "$name: pushed to $mirror"
        else
            echo "$name: PUSH FAILED to $mirror"
            status=1
            continue
        fi
        if [ -n "${BUNDLE_DIR:-}" ]; then
            mkdir -p "$BUNDLE_DIR"
            git -C "$clone" bundle create --quiet "$BUNDLE_DIR/$name.bundle" --all || status=1
        fi
    fi

    # Both modes end by asking the mirror itself for the pin, the way fetch.sh will.
    probe="$(mktemp -d)"
    git init --quiet --bare "$probe"
    if GIT_TERMINAL_PROMPT=0 git -C "$probe" fetch --quiet --depth 1 "$mirror" "$pin" 2>/dev/null; then
        echo "$name: mirror holds the pin ${pin:0:8}"
    else
        echo "$name: MIRROR MISSING OR LACKS THE PIN ${pin:0:8} ($mirror)"
        status=1
    fi
    rm -rf "$probe"
done
exit "$status"
