# Dual-boot OS handoff

Ubuntu and Windows do not share a Cursor chat. Reboot is normal. **GitHub is the handoff.**

After every reboot, open this file in the browser first (even if the local clone is stale):

https://github.com/kim7170719/robot-dev-ai/blob/feature/m1-ros-baseline/docs/os_handoff.md

Until that branch is merged, **do not** use the `develop` copy of this file; it is stale. Always open the `feature/m1-ros-baseline` URL above.

Update this file, commit, and `git push` **before** you reboot. Do not use `git stash` to cross OS.

## Current packet (2026-09-17)

| Field | Value |
|---|---|
| Last writer | Ubuntu |
| Safe to reboot? | Yes after this packet is pushed |
| Ubuntu branch | `feature/m1-ros-baseline` |
| Windows branch | `develop` until M1 PR merges |
| G0 | PASS — tag `g0-environment-baseline` on `main` (`c771bf1`) |
| Next OS | Windows (this reboot) then back to Ubuntu for Jazzy sudo |
| Windows todo | `docs/windows_next.md` — fetch `develop` + tags; no ROS install |
| Do not do | ROS / Isaac / Cosmos on Windows; Cosmos on Ubuntu; develop on `main` |

Gate 0 closed:

- PR #1 → `develop`, PR #2 → `main`
- Tag: `g0-environment-baseline`

M1-01 blocked on `sudo` in a local Ubuntu terminal. Commands: `docs/m1_ros_jazzy.md`

### After reboot → Windows

Browser first: https://github.com/kim7170719/robot-dev-ai/blob/feature/m1-ros-baseline/docs/windows_next.md

Then:

```powershell
cd C:\dev\robot-dev-ai
git fetch --prune
git switch develop
git pull --ff-only
git fetch --tags
git status
git tag -l "g0-*"
```

Expect tag `g0-environment-baseline`. Read `docs/windows_next.md`. Do not install ROS 2. If you did not edit files, reboot back to Ubuntu.

### After reboot → Ubuntu

```bash
cd ~/dev/robot-dev-ai
git fetch --prune
git switch feature/m1-ros-baseline
git pull --ff-only
git status
```

Then run the sudo install in `docs/m1_ros_jazzy.md` if `/opt/ros/jazzy` is still missing.

## Every reboot (both OS)

**Leaving this OS:** `git status` → commit if needed → `git push` → `scripts/before_reboot.sh` or `.ps1` → reboot.

**Arriving:** open the GitHub URL at the top → fetch / switch / `git pull --ff-only` → clean `git status` before edits.

Clones: Ubuntu `~/dev/robot-dev-ai`, Windows `C:\dev\robot-dev-ai`.
