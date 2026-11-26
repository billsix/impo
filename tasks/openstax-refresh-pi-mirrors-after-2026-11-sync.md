# Refresh the Pi mirrors so they hold the content synced on 2026-11-26 (maintainer, at home)

**Status:** blocked
**Blocked on:** the maintainer being on the home network with the Pi machine (`192.168.0.186`). The agent cannot reach it; this task changes nothing in impo.
**Recheck:** the maintainer says it is done. There is no check the sandbox can run.
**Priority:** 4
**Difficulty:** 1 (a fetch per mirror)
**Created:** 2026-11-26 (William Emerison Six <billsix@gmail.com>: a task "for me at home … so that I can mirror clone that, so I'll always have a copy on my backup pi system … no repo changes, I need to do it myself and tell you that I've done it").

## BLUF

The 2026-11-26 sync moved nine books to newer upstream commits, and two of those brought content the Pi mirrors do not have yet unless they were fetched since: a new book, Healthcare Foundations, and the renamed Biology for AP Courses. The maintainer refreshes the Pi mirrors so the backup holds everything impo now builds. Done means he reports that each mirror below contains its pin.

## Context

- **No new repository appeared.** Both changes arrived inside repositories that are already mirrored: Healthcare Foundations is a fourth collection in `osbooks-prealgebra-bundle`, and Biology for AP Courses was renamed (`biology-ap-courses` to `biology-ap-courses-2e`) inside `osbooks-biology-bundle`. So nothing needs a new `git clone --mirror`, unless a mirror turns out to be missing; an existing mirror only needs a fetch.
- The mirrors live on the Pi under `/mnt/usbdrive2/gitRepos/openstax/` (each `openstax/*/fetch.sh` names the path with a `**` in the middle, so the exact subfolder is not recorded in impo).
- Related: `tasks/openstax-algebra-1-upstream-gone-backup-plan.md` (publishing the mirrors on GitHub and the algebra-1 upstream that disappeared) and `tasks/openstax-sync-upstream-pins-2026-11.md` (the sync). The sooner the mirrors are refreshed the better: algebra-1 showed an upstream can vanish.

## What to do (maintainer, on the Pi or over ssh)

1. In each mirror, fetch everything from upstream:
   ```
   git -C <mirror>.git remote update --prune
   ```
   Leave out `--prune` for `osbooks-algebra-1`: its upstream is gone, and pruning against a dead remote must not be allowed to remove anything.
2. Confirm each mirror holds its book's current pin (prints `present`):
   ```
   git -C <mirror>.git cat-file -e <pin>^{commit} && echo present
   ```

   | Repository | Pin after the 2026-11-26 sync |
   |---|---|
   | osbooks-anatomy-physiology | `f273762340768a5f50e833c876e40b5a9c565da1` |
   | osbooks-biology-bundle | `bc1be223bd23a00cc68efb6195dc183f4e1e228a` |
   | osbooks-calculus-bundle | `018da4da252bb9c56759e34396efea91852bcf5a` |
   | osbooks-chemistry-bundle | `78b742a7fed1379705c5d882cee1ebfab7f58dc9` |
   | osbooks-college-algebra-bundle | `709c7417a68293f40a42531c727fbb41877afed5` |
   | osbooks-microbiology | `ccd8e2339acd2a31c0008eef93bb9f71eb2e57c7` |
   | osbooks-organic-chemistry | `72cb625c8ffd62c4eecf04fbe2389ae4e8db2f14` |
   | osbooks-prealgebra-bundle | `efab2179afac4df11c6bbd5a9392391937836d06` |
   | osbooks-psychology | `43035bcc5dd238f2e236ef532a01f11d6a59fc9d` |

   The other seven books did not move in this sync; their pins are the `PIN_SHA` lines of their `fetch.sh`.
3. If a mirror does not exist, create it: `git clone --mirror https://github.com/openstax/<repository> <mirror>.git`.
4. Tell the agent it is done, and which mirrors (if any) were missing or lacked a pin. The agent then archives this task and records the result in `tasks/openstax-algebra-1-upstream-gone-backup-plan.md`.

## Open questions

None.
