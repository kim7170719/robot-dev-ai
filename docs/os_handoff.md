# Dual-boot OS handoff

Ubuntu and Windows do not share a Cursor chat. Reboot is normal. **GitHub is the handoff.**

After every reboot, open this file in the browser first (even if the local clone is stale):

https://github.com/kim7170719/robot-dev-ai/blob/develop/docs/os_handoff.md

Update this file, commit, and `git push` **before** you reboot. Do not use `git stash` to cross OS.

## Current packet (2026-09-17)

| Field | Value |
|---|---|
| Last writer | Ubuntu |
| Safe to reboot? | Yes, after this packet is pushed |
| Branch | `develop` |
| PR | https://github.com/kim7170719/robot-dev-ai/pull/1 **MERGED** into `develop` |
| Next OS | Ubuntu (stay here) until `develop` → `main` + tag; Windows should pull `develop` |
| Do not do | Install ROS on Windows; do not start Cosmos; do not develop on `main` |

- Squash merge: `c951015` `docs: Gate 0 dual-OS Git sync (#1)`
- Remote branch `docs/g0-cross-os-sync` was deleted
- Tag `g0-environment-baseline` still waits for `develop` → `main`
- Next milestone after tag: **M1-01 ROS 2 Jazzy on Ubuntu**

### After reboot → Windows

```powershell
cd C:\dev\robot-dev-ai
git fetch --prune
git switch develop
git pull --ff-only
git status
```

Then read this file and `docs/windows_next.md`. If almost every file changed, stop (CRLF). Do not install ROS 2.

### After reboot → Ubuntu

```bash
cd ~/dev/robot-dev-ai
git fetch --prune
git switch develop
git pull --ff-only
git status
```

Ubuntu next: `develop` → `main` PR, annotated tag `g0-environment-baseline`, then M1-01. Not Cosmos.

## Every reboot (both OS)

**Leaving this OS**

1. `git status`
2. Commit if there is real work (`wip:` only if you must reboot mid-task)
3. `git push`
4. Confirm `git status` is clean and not “ahead of origin”
5. Reboot

**Arriving on the other OS**

1. Browser: open the GitHub URL at the top of this file
2. Local clone: fetch / switch to the branch named in the packet / `git pull --ff-only`
3. `git status` must be clean before new edits
4. New Cursor chat is OK; do not expect the previous chat to exist

Clones stay separate: Ubuntu `~/dev/robot-dev-ai`, Windows `C:\dev\robot-dev-ai`.
