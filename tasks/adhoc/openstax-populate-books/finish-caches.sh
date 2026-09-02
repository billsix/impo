#!/bin/bash
# Finish the OpenStax exercise-cache job the subagent left incomplete:
# wait for the in-flight fetches to drain, then per exercise book ensure it's
# fetched and commit its cache (with COPYRIGHT). One commit per book. Idempotent:
# skips books whose cache is already committed; treats no-exercise books as no-ops.
set -uo pipefail
cd /foo/opt/imps
FOOT='Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>'
COPY=openstax/tooling/templates/exercises-COPYRIGHT

log(){ echo "[$(date +%H:%M:%S)] $*"; }

# 1) Wait for any running fetch_exercises to finish (the two big ones), up to ~30 min.
log "waiting for in-flight fetches to drain ..."
for i in $(seq 1 90); do
  pgrep -f 'fetch_exercises.py' >/dev/null 2>&1 || { log "no fetch running"; break; }
  sleep 20
done

# 2) Per exercise book (big first), ensure fetched + commit the cache.
BOOKS="organic-chemistry biology-bundle contemporary-mathematics college-algebra-bundle prealgebra-bundle calculus-bundle writing-guide physics algebra-1"
for book in $BOOKS; do
  dir=openstax/osbooks-$book
  if git ls-files "$dir/exercises" 2>/dev/null | grep -q .; then
    log "SKIP $book — cache already committed"; continue
  fi
  [ -d "$dir" ] || { log "MISSING folder $dir"; continue; }
  ( cd "$dir"
    # ensure the checkout has CNXML content (needed to discover exercise nicknames)
    if [ ! -d checkout/collections ] && [ ! -d checkout/modules ]; then
      log "  $book: fetching content ..."
      ./fetch.sh >/dev/null 2>&1 || true
    fi
    if [ ! -d checkout/modules ]; then   # fetch failed/slow -> seed from the local mirror at the pin
      pin=$(grep -oE 'PIN_SHA=[0-9a-f]+' fetch.sh | head -1 | cut -d= -f2)
      src=/foo/opt/openstax/osbooks-$book
      if [ -n "$pin" ] && [ -d "$src/.git" ]; then
        log "  $book: seeding content from local mirror @ $pin"
        mkdir -p checkout
        git -C "$src" archive "$pin" collections modules 2>/dev/null | tar -x -C checkout 2>/dev/null || \
        git -C "$src" archive "$pin" 2>/dev/null | tar -x -C checkout 2>/dev/null || true
        ( cd checkout && [ -d .git ] || { git init -q; git config commit.gpgsign false; } )
      fi
    fi
    [ -d checkout/tools ] || ./apply.sh >/dev/null 2>&1 || true
    NESTED_PODMAN=1 make image >/dev/null 2>&1 || true
    # Always run fetch-exercises: it's idempotent (skips already-cached, tops up
    # any partial fetch the stalled agent left). A no-exercise book fetches nothing.
    log "  $book: make fetch-exercises (top-up) ..."
    NESTED_PODMAN=1 timeout 1500 make fetch-exercises >/dev/null 2>&1 || true
  )
  # commit whatever landed
  if ls "$dir"/checkout/exercises/*.json >/dev/null 2>&1; then
    rm -rf "$dir/exercises"
    cp -R "$dir/checkout/exercises" "$dir/exercises"
    cp "$COPY" "$dir/exercises/COPYRIGHT"
    j=$(find "$dir/exercises" -maxdepth 1 -name '*.json' | wc -l)
    m=$(find "$dir/exercises/media" -type f 2>/dev/null | wc -l)
    committed=0
    for try in 1 2 3; do
      git add "$dir/exercises" 2>/dev/null && \
      git commit -q -m "openstax: fetch+commit $book exercises (CC BY, marked)" -m "$FOOT" 2>/dev/null \
        && { committed=1; break; }
      sleep 5   # retry on a transient index.lock
    done
    [ "$committed" = 1 ] && log "COMMITTED $book — json=$j media=$m" || log "COMMIT FAILED $book (json=$j)"
  else
    log "NO-OP $book — no os-embed exercises fetched"
  fi
done

log "=== done. exercise-cache commits: ==="
git log --oneline | grep -iE 'exercises \(CC BY' | sed 's/^/  /'
