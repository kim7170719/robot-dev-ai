# Dual-boot OS handoff

After every reboot, open this file in the browser first:

https://github.com/kim7170719/robot-dev-ai/blob/develop/docs/os_handoff.md

## Current packet (2026-09-21)

| Field | Value |
|---|---|
| Last writer | Ubuntu |
| Ubuntu branch | `develop` |
| Windows branch | `develop` |
| G0 / G1 / G2 / G3 | ALL PASS |
| Tags | `g0-environment-baseline`, `m2-g2-simple-diff-robot`, `m3-g3-isaac-sim` |
| Next milestone | M4 Nav2 (Ubuntu only) |
| Windows todo | `git fetch --prune; git switch develop; git pull --ff-only; git fetch --tags` |
| Do not do | ROS on Windows; Isaac Sim on Windows; Cosmos |

G3 completed: Isaac Sim 4.5 Docker, cmd_vel→robot odom confirmed via CycloneDDS.

### After reboot → Windows

```powershell
cd C:\dev\robot-dev-ai
git fetch --prune
git switch develop
git pull --ff-only
git fetch --tags
git status
git log -5 --oneline
git tag -l "g*" "m*"
```

Confirm tags: `g0-environment-baseline`, `m2-g2-simple-diff-robot`, `m3-g3-isaac-sim`.  
Read: https://github.com/kim7170719/robot-dev-ai/blob/develop/docs/windows_next.md

### After reboot → Ubuntu

```bash
cd ~/dev/robot-dev-ai
git fetch --prune
git switch develop
git pull --ff-only
git fetch --tags
git status
```

Then open a new Cursor chat and start M4.

## Every reboot

Leave: `git status` → commit/push → `scripts/before_reboot.sh` → reboot.  
Arrive: browser URL above → fetch/switch/pull → clean status before edits.

Clones: Ubuntu `~/dev/robot-dev-ai`, Windows `C:\dev\robot-dev-ai`.
