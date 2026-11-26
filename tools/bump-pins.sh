#!/usr/bin/env bash
# Move each listed book's PIN_SHA to its upstream default-branch head and bring the
# book's checkout/ to that commit in place (generated outputs in checkout/ are kept).
# Idempotent: a book already at its upstream head is reported and left alone.
#
#   bash tools/bump-pins.sh <book> [<book> ...]
set -uo pipefail
cd "$(git -C "$(dirname "$0")" rev-parse --show-toplevel)" || exit 1

status=0
for book in "$@"; do
    fetch_script="openstax/osbooks-$book/fetch.sh"
    checkout="openstax/osbooks-$book/checkout"
    upstream_url="$(grep -m1 '^UPSTREAM_URL=' "$fetch_script" | cut -d= -f2)"
    old_pin="$(grep -m1 '^PIN_SHA=' "$fetch_script" | cut -d= -f2)"
    new_pin="$(GIT_TERMINAL_PROMPT=0 git ls-remote "$upstream_url" HEAD | cut -f1)"
    if [ -z "$new_pin" ]; then
        echo "$book: upstream did not answer ($upstream_url)"
        status=1
        continue
    fi
    if [ "$old_pin" != "$new_pin" ]; then
        # One dated line above PIN_SHA says where the pin points.
        sed -i -e '/^# Resync [0-9-]* (agent): bumped to upstream HEAD/d' \
            -e '/^# Synced with the upstream default-branch head on /d' "$fetch_script"
        sed -i -e "s|^PIN_SHA=.*|# Synced with the upstream default-branch head on $(date +%F).\nPIN_SHA=$new_pin|" "$fetch_script"
    fi
    if [ -e "$checkout/.git" ] && [ "$(git -C "$checkout" rev-parse HEAD 2>/dev/null)" != "$new_pin" ]; then
        git -C "$checkout" fetch -q --depth 1 origin "$new_pin" &&
            git -C "$checkout" checkout -q --detach FETCH_HEAD || status=1
    fi
    echo "$book: $old_pin -> $new_pin (checkout at $(git -C "$checkout" rev-parse --short HEAD 2>/dev/null))"
done
exit "$status"
