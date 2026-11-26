# Refresh the Pi clones so the private copy holds what impo builds (maintainer, at home)

**Status:** blocked
**Blocked on:** the maintainer being on the home network with the Pi machine (`192.168.0.186`). The agent cannot reach it; this task changes nothing in impo.
**Recheck:** the maintainer says it is done. There is no check the sandbox can run.
**Priority:** 5
**Difficulty:** 1 (a fetch per clone)
**Created:** 2026-11-26 (William Emerison Six <billsix@gmail.com>: a task "for me at home … so that I can mirror clone that, so I'll always have a copy on my backup pi system … no repo changes, I need to do it myself and tell you that I've done it").

## BLUF

The maintainer keeps full-history clones of the OpenStax book repositories on his Pi. The 2026-11-26 sync moved nine books to newer upstream commits, so those clones are behind unless they were fetched since. He refreshes them so the private copy holds everything impo now builds. Done means he reports that each clone contains its book's pin.

## Context

- **What changed since this task was filed.** It was first written as the only route to a backup. Later the same day the backup became public mirrors under `github.com/billsix` (`tasks/openstax-books-buildable-forever-source-backup-and-licences.md`), and fifteen of those can be pushed from any machine, because their upstreams still answer. The Pi clones are now the **second** copy, the one that does not depend on GitHub, and the only source of history for algebra-1.
- **No new repository appeared in the sync.** Healthcare Foundations is a fourth collection inside `osbooks-prealgebra-bundle`, and Biology for AP Courses was renamed inside `osbooks-biology-bundle`. An existing clone needs only a fetch.
- **Where the clones are:** under `/mnt/usbdrive2/gitRepos/openstax/` on the Pi. Anatomy & Physiology's is at `…/openstax/science/osbooks-anatomy-physiology.git`; the subfolders of the others were never recorded in impo.

## What to do (maintainer, on the Pi or over ssh)

1. In each clone, fetch from upstream: `git -C <clone>.git remote update --prune`. Leave out `--prune` for `osbooks-algebra-1`: its upstream is gone, and a prune against a dead remote must not be allowed to remove anything.
2. Confirm each clone holds its book's pin (prints `present`): `git -C <clone>.git cat-file -e <pin>^{commit} && echo present`. The pin of every book is the `PIN_SHA` line of its `openstax/<name>/fetch.sh`. The nine that moved on 2026-11-26:

   | Repository | Pin |
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

3. If a clone does not exist, create it: `git clone --mirror https://github.com/openstax/<repository> <clone>.git`.
4. Alternatively, let the tool do steps 1 to 3 and the public push in one run, with the clones kept on the Pi: `MIRROR_DIR=/mnt/usbdrive2/gitRepos/openstax-mirrors CREATE=1 bash tools/mirror-upstreams.sh push`.
5. Tell the agent it is done, and which clones (if any) were missing or lacked a pin. The agent archives this task and records the result.

## Open questions

None.
