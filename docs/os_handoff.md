# Dual-boot OS handoff

Ubuntu and Windows do not share a Cursor chat. Reboot is normal. **GitHub is the handoff.**

After every reboot, open this file in the browser first (even if the local clone is stale):

https://github.com/kim7170719/robot-dev-ai/blob/docs/g0-cross-os-sync/docs/os_handoff.md

Update this file, commit, and `git push` **before** you reboot. Do not use `git stash` to cross OS.

## Current packet (2026-09-17)

| Field | Value |
|---|---|
| Last writer | Ubuntu |
| Safe to reboot? | Yes, if `git status` is clean and this branch is pushed |
| Branch | `docs/g0-cross-os-sync` |
| PR | https://github.com/kim7170719/robot-dev-ai/pull/1 |
| Next OS | Windows |
| Do not do | Install ROS / Isaac / Cosmos on Windows |

### After reboot → Windows

```powershell
cd C:\dev\robot-dev-ai
git fetch --prune
git switch docs/g0-cross-os-sync
git pull --ff-only
git status
```

Then read:

1. This file
2. `docs/windows_next.md`

If `git status` shows almost every file changed, stop. That is CRLF. Do not commit.

Windows work this round:

- Confirm the M1 Windows guide is readable
- Optional: bookmark the GitHub URL above
- Do not install ROS 2
- When finished, if you changed files: commit, push, then reboot back to Ubuntu
- If you changed nothing: still `git status` clean, then reboot to Ubuntu

### After that reboot → Ubuntu

```bash
cd ~/dev/robot-dev-ai
git fetch --prune
git switch docs/g0-cross-os-sync
git pull --ff-only
git status
```

Ubuntu work after Windows returns:

- Merge PR #1 only after you explicitly say to merge
- Tag `g0-environment-baseline` only after `develop` → `main`
- Next real milestone: **M1-01 ROS 2 Jazzy on Ubuntu** (not Cosmos)

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
